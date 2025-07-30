# mypy: ignore-errors
from typing import List, Tuple, Union, Optional

import numpy as np
import tensorflow as tf  # type: ignore
import torch  # type: ignore
from numpy.typing import NDArray
from code_loader.helpers.detection.utils import true_coords_labels, ciou, xywh_to_xyxy_format
from code_loader.helpers.detection.yolo.utils import match
from code_loader.helpers.detection.yolo.pytorch_utils import build_targets
from code_loader.helpers.instancesegmentation.utils import crop_mask
import collections.abc


class YoloLoss:
    """
    num classes - the number of classes to detect
    default_boxes - the anchors at all heads
    overlap_thresh - the threshold of IOU overwhich a match is positive
    neg_pos - the ratio of negative:positive samples
    background_label - should be the last idx
    """

    def __init__(self, num_classes: int, default_boxes: List[NDArray[np.int32]],
                 overlap_thresh: float, background_label: int, features: List[Tuple[int, int]] = [],
                 anchors: Optional[NDArray[np.int32]] = None,
                 from_logits: bool = True, weights: List[float] = [4.0, 1.0, 0.4],
                 max_match_per_gt: int = 10, image_size: Union[Tuple[int, int], int] = (640, 640),
                 cls_w: float = 0.3, obj_w: float = 0.7, box_w: float = 0.05,
                 yolo_match: bool = False, semantic_instance: bool = False,
                 filter_ratio_match: bool = True):
        self.background_label = background_label
        self.default_boxes = [tf.convert_to_tensor(box_arr) for box_arr in default_boxes]
        self.num_classes = num_classes
        self.threshold = overlap_thresh
        self.variance = (1, 1)
        self.from_logits = from_logits
        self.weights = weights  # Following yolov7 weights
        scale_factor = 3. / len(weights)
        class_factor = self.num_classes / 80
        if not isinstance(image_size, collections.abc.Sequence):
            image_size = (image_size, image_size)
        image_factor = (image_size[0] + image_size[1]) / 2 / 640.
        self.obj_w = obj_w * scale_factor
        self.cls_w = cls_w * class_factor * scale_factor
        self.box_w = box_w * image_factor ** 2 * scale_factor
        self.max_match_per_gt = max_match_per_gt
        self.feature_maps = features
        self.anchors = anchors
        self.image_size = image_size
        self.yolo_match = yolo_match
        self.semantic_instance = semantic_instance
        self.filter_ratio_match = filter_ratio_match
        self.bce = tf.keras.losses.BinaryCrossentropy(from_logits=False, reduction='none')
        if self.semantic_instance:
            if self.yolo_match is False:
                raise Exception("YoloLoss: For instance segmentation tasks, the 'yolo_match' paramater "
                                 "must be set to true creating the loss object")
        if self.yolo_match:
            if self.anchors is None:
                raise Exception("YoloLoss: When yolo_match flag is set to true, the anchors shape has to be "
                                "supplied by setting the anchors paramater when creating the loss object")
            if self.feature_maps is None:
                raise Exception("YoloLoss: When yolo_match flag is set to true, feature maps has to be "
                                "supplied by setting the feature_maps paramater when creating the loss object")
            if not len(self.weights) == len(self.feature_maps) == self.anchors.shape[0]:
                raise Exception("YoloLoss: there is a mismatched configuration. Number of weights supplied must"
                                 "equal feature_maps length, and the first channel of the anchors when creating"
                                "the loss object")

    def __call__(self, y_true: tf.Tensor, y_pred: Tuple[List[tf.Tensor], List[tf.Tensor]],
                 instance_true: Optional[tf.Tensor] = None, instance_seg: Optional[tf.Tensor] = None) -> \
            Union[Tuple[List[tf.Tensor], List[tf.Tensor], List[tf.Tensor]],
                  Tuple[List[tf.Tensor], List[tf.Tensor], List[tf.Tensor], List[tf.Tensor]]]:

        """
        Computes
        :param y_true:  Tensor, shape: (batch_size, MAX_BOXES_PER_IMAGE, 5(x, y, w, h, class_index))
        :param y_pred:  Tuple, (loc, conf) loc:
        :return: l_loss a list of NUM_FEATURES, each item a tensor with BATCH_SIZE legth
        :return: c_loss a list of NUM_FEATURES, each item a tensor with BATCH_SIZE legth
        """
        loc_data, conf_data = y_pred
        non_bg_gt = y_true[..., -1] != self.background_label
        if not tf.math.reduce_all((y_true[..., -1][non_bg_gt] < self.num_classes)):
            raise Exception("YoloLoss: Some class values in the provided GT are not smaller than number"
                            "of samples. Make sure all of your GT class values are less than your defined"
                            f"num classes: {self.num_classes}")
        if self.semantic_instance:
            if instance_seg is None:
                raise Exception("YoloLoss: For instance segmentation tasks, the 'instace_seg' parameter "
                                 "that contains mask predictions must be set")
            if instance_true is None:
                raise Exception("YoloLoss: For instance segmentation tasks, the 'instace_true' parameter "
                                 "that contains mask GTs must be set in each loss call")
        else:
            conf_channels = conf_data[0].shape[-1] - 1
            if self.num_classes != conf_channels:
                raise Exception("YoloLoss: Number of classes set for OD loss does not correspond to the predicted channels."
                                f"num_classes in YoloLoss: {self.num_classes}, number of classes prediction from model:"
                                f" {conf_channels}")
        if not self.yolo_match:
            for i in range(len(self.default_boxes)):
                if self.default_boxes[i].shape != loc_data[i].shape[1:]:
                    raise Exception(
                        "YoloLoss: Number of predictions does not match to the grid configured in YoloLoss."
                        f"Fix self.default_boxes configured in YoloLoss such that"
                        f" its shape(self.default_boxes[i]).shape[0] would equal shape(prediction)[1]"
                        f" {conf_channels}")
            raise Exception("")
        num = y_true.shape[0]
        l_losses = []
        c_losses = []
        o_losses = []
        m_losses = []
        bb_idx, b, a, gj, gi, target = None, None, None, None, None, None
        anchor_num = len(self.default_boxes)
        if self.semantic_instance:
            conf_no_masks = [conf_data[i][..., :self.num_classes + 1] for i in range(len(conf_data))]
            masks_maps = [conf_data[i][..., self.num_classes + 1:] for i in range(len(conf_data))]
        else:
            conf_no_masks = conf_data
        if self.yolo_match:
            bb_idx, b, a, gj, gi, target, _ = self.get_yolo_match(batch_size=num,
                                                          y_true=y_true,
                                                          loc_data=loc_data,
                                                          conf_data=conf_no_masks,
                                                          filter_ratio_match=self.filter_ratio_match)
        for i in range(len(self.default_boxes)):
            default_box_layer = self.default_boxes[i]
            loc_data_layer = loc_data[i]
            conf_data_layer = conf_no_masks[i][..., 1:]  # remove the "object confidence"
            priors = default_box_layer[:loc_data_layer.shape[1], :]
            # GT boxes
            loc_t: List[tf.Tensor] = []
            conf_t: List[tf.Tensor] = []
            priors = tf.cast(priors, dtype=tf.float32)  #
            y_true = tf.cast(y_true, dtype=tf.float32)
            if not self.yolo_match:
                for idx in range(num):
                    truths, labels = true_coords_labels(idx, y_true, self.background_label)
                    loc, conf = match(
                        threshold=self.threshold, truths=truths, priors=priors,
                        labels=labels,
                        background_label=self.background_label,
                        max_match_per_gt=self.max_match_per_gt)  # encoded_gt_loc, label_pred, ciou between gt and pred
                    loc_t.append(loc)
                    conf_t.append(conf)
                loc_t_tensor: tf.Tensor = tf.stack(values=loc_t,
                                                   axis=0)  # this is the location predictions (relative and logged)
                conf_t_tensor = tf.stack(values=conf_t, axis=0)
            else:
                assert (b is not None) and (a is not None) and (gj is not None) and (gi is not None) and\
                       (target is not None) # for typing - how do we remove?
                loc_t_tensor, conf_t_tensor = self.get_scale_matched_gt_tf(i, num, b, a, gj, gi, target)
            # these are the labels
            pos = conf_t_tensor != self.background_label
            num_pos = tf.reduce_sum(tf.cast(pos, dtype=tf.int32))

            # loss: Smooth L1 loss
            pos_idx = tf.expand_dims(pos, axis=-1)
            pos_idx = tf.broadcast_to(pos_idx, shape=loc_data_layer.shape)
            # apply per sample
            loss_b_list = []
            loss_c_list = []
            loss_o_list = []
            loss_m_list = []
            if self.yolo_match:
                assert b is not None and a is not None and gj is not None and gi is not None
                match_indices = torch.stack([b[i], a[i], gj[i], gi[i]]).T.numpy()
            for j in range(num):
                loc_p = tf.boolean_mask(tensor=loc_data_layer[j, ...], mask=pos_idx[j, ...])
                object_p = conf_no_masks[i][j, :, 0]  # object confidence
                targets_iou = tf.zeros_like(object_p)
                if self.from_logits:
                    sigmoid_obj = tf.sigmoid(object_p)
                else:
                    sigmoid_obj = object_p

                if loc_p.shape[0] and num_pos:  # GT exists
                    ious = ciou(xywh_to_xyxy_format(loc_data_layer[j, ...]),
                                xywh_to_xyxy_format(loc_t_tensor[j, ...]))
                    targets_iou = tf.where(pos_idx[j, :, 0], ious,
                                           tf.cast(tf.zeros_like(conf_t_tensor[j, ...]), tf.float32))
                    matched_iou = ious[pos_idx[j, :, 0]]
                    lbox = tf.reduce_mean(1. - matched_iou) * self.box_w
                    targets_iou = tf.convert_to_tensor(tf.maximum(targets_iou, 0).numpy())
                    # targets_iou = tf.stop_gradient(tf.maximum(targets_iou, 0))
                    if self.num_classes > 1:
                        if self.from_logits:
                            sig_pos_conf = tf.sigmoid(conf_data_layer[j])
                        else:
                            sig_pos_conf = conf_data_layer[j]

                        one_hot_preds = tf.one_hot(tf.boolean_mask(conf_t_tensor[j], pos[j]), self.num_classes)
                        matched_prediction = tf.boolean_mask(sig_pos_conf, pos[j, ...], axis=0)
                        matched_prediction = tf.clip_by_value(matched_prediction, 1e-7, 1 - 1e-7)
                        single_loss_cls = tf.reduce_mean(-(
                                one_hot_preds * tf.math.log(matched_prediction) + (1 - one_hot_preds) * tf.math.log(
                            1 - matched_prediction))) * self.cls_w
                    else:
                        single_loss_cls = tf.constant(0, dtype=tf.float32)
                    if self.semantic_instance:
                        assert self.yolo_match and self.anchors is not None and bb_idx \
                               is not None and target is not None
                        dedup_matched: NDArray[np.int64]
                        dedup_matched, dedup_indice = \
                            np.unique(match_indices[match_indices[..., 0] == j], return_index=True, axis=0)
                        unsqueezed_shape = (
                            masks_maps[i].shape[0], self.anchors.shape[1], *self.feature_maps[i],
                            masks_maps[i].shape[-1])
                        masks_coeffs = tf.gather_nd(tf.reshape(masks_maps[i], unsqueezed_shape),
                                                    dedup_matched)
                        predicted_maps = tf.linalg.matmul(instance_seg, masks_coeffs, transpose_b=True)
                        permuted_predicted = tf.transpose(predicted_maps[j], [2, 0, 1])  # instance,map
                        gt_maps = tf.gather_nd(instance_true, np.stack([np.ones(len(bb_idx[i][dedup_indice]),
                                                                                dtype=int) * j,
                                                                        bb_idx[i][dedup_indice].numpy().astype(int)]).T)
                        if gt_maps.shape[1] != predicted_maps.shape[1] or gt_maps.shape[2] != predicted_maps.shape[2]:
                            gt_maps = tf.image.resize(tf.transpose(gt_maps, [1, 2, 0]), (permuted_predicted.shape[1:]),
                                                      method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
                            print("reshaping gt")
                            gt_maps = tf.transpose(gt_maps, [2, 0, 1])
                        gt_maps = gt_maps[None, :]
                        unmasked_loss = self.bce(gt_maps[0, ...][..., None], tf.sigmoid(permuted_predicted)[..., None])
                        gt_box_loc = target[i][:, -4:][dedup_indice, :]
                        mask_area = gt_box_loc[:, 2:].prod(1)
                        gt_box_loc[:, [0, 2]] = gt_box_loc[:, [0, 2]] * gt_maps.shape[3]
                        gt_box_loc[:, [1, 3]] = gt_box_loc[:, [1, 3]] * gt_maps.shape[2]
                        xyxy_gt: NDArray[np.float32] = xywh_to_xyxy_format(gt_box_loc)
                        masked_loss = crop_mask(unmasked_loss, xyxy_gt)
                        masks_loss_reduced = tf.reduce_mean(tf.reduce_mean(masked_loss, axis=1), axis=1) / mask_area
                        mask_loss = tf.reduce_mean(masks_loss_reduced) * self.box_w
                    else:
                        mask_loss = tf.constant(0, dtype=tf.float32)
                else:  # No GT
                    lbox = tf.zeros(1, dtype=tf.float32)
                    single_loss_cls = tf.constant(0, dtype=tf.float32)
                    mask_loss = tf.constant(0, dtype=tf.float32)

                sigmoid_obj = tf.clip_by_value(sigmoid_obj, 1e-7, 1 - 1e-7)

                obj_loss = -(targets_iou * tf.math.log(sigmoid_obj) + (1 - targets_iou) * tf.math.log(1 - sigmoid_obj))
                mean_obj_loss = tf.reduce_mean(obj_loss) * self.obj_w * self.weights[i]

                loss_o_list.append(tf.expand_dims(mean_obj_loss, axis=0))
                loss_c_list.append(tf.expand_dims(single_loss_cls, axis=0))
                loss_b_list.append(tf.reshape(lbox, loss_c_list[-1].shape))
                loss_m_list.append(tf.expand_dims(mask_loss, axis=0))

            loss_b_tensor = tf.stack(values=loss_b_list, axis=0)
            loss_o_tensor = tf.stack(values=loss_o_list, axis=0)
            loss_c_tensor = tf.stack(values=loss_c_list, axis=0)
            l_losses.append(loss_b_tensor)
            c_losses.append(loss_c_tensor)
            o_losses.append(loss_o_tensor)
            if self.semantic_instance:
                loss_m_tensor = tf.stack(values=loss_m_list, axis=0)
                m_losses.append(loss_m_tensor)
        if not self.semantic_instance:
            return l_losses, c_losses, o_losses
        else:
            return l_losses, c_losses, o_losses, m_losses

    def get_scale_matched_gt_tf(self, i: int, batch_size: int, b: List[torch.Tensor], a: List[torch.Tensor],
                                gj: List[torch.Tensor], gi: List[torch.Tensor],
                                target: List[torch.Tensor]) -> Tuple[tf.Tensor, tf.Tensor]:
        # temp
        assert self.anchors is not None
        gt_class = tf.ones((batch_size,
                            self.anchors.shape[1], *self.feature_maps[i]), dtype=tf.int32) * self.background_label
        if len(b[i]) > 0:
            gt_class = tf.tensor_scatter_nd_update(gt_class, torch.stack([b[i], a[i], gj[i], gi[i]]).T.numpy(),
                                                   target[i][:, 1])
        conf_t_tensor = tf.reshape(gt_class, [gt_class.shape[0], -1])
        gt_loc = tf.zeros((batch_size, len(self.anchors[i]), *self.feature_maps[i], 4), dtype=tf.float32)
        if len(b[i]) > 0:
            gt_loc = tf.tensor_scatter_nd_update(gt_loc, torch.stack([b[i], a[i], gj[i], gi[i]]).T.numpy(),
                                                 target[i][:, -4:])
        loc_t_tensor = tf.reshape(gt_loc, [gt_class.shape[0], -1, 4])
        return loc_t_tensor, conf_t_tensor

    def get_yolo_match(self, batch_size: int, y_true: tf.Tensor, loc_data: List[tf.Tensor], conf_data: List[tf.Tensor],
                       filter_ratio_match: bool) \
            -> Tuple[List[torch.Tensor], ...]:
        assert self.anchors is not None
        yolo_targets: List[NDArray[np.float32]] = []
        scales_num = len(loc_data)
        for i in range(batch_size):
            batch_gt = y_true[i][y_true[i, ..., -1] != self.background_label]
            yolo_targets.append(
                np.concatenate([np.ones((batch_gt.shape[0], 1)) * i, batch_gt[:, 4:], batch_gt[:, :4]], axis=1))
        yolo_targets_cat: NDArray[np.float32] = np.concatenate(yolo_targets, axis=0)
        orig_pred = [torch.from_numpy(tf.concat([loc_data[i], conf_data[i]], axis=-1).numpy()) for i in
                     range(scales_num)]
        fin_pred = [pred.reshape([pred.shape[0], self.anchors.shape[1], *self.feature_maps[i], -1]) for i, pred in
                    enumerate(orig_pred)]
        yolo_anchors = np.array(self.anchors) * np.swapaxes(np.array([*self.feature_maps])[..., None], 1, 2) / self.image_size #y,x
        bb_idx, b, a, gj, gi, target, anch = build_targets(fin_pred, torch.from_numpy(yolo_targets_cat.astype(np.float32)),
                                                   torch.from_numpy(yolo_anchors.astype(np.float32)), self.image_size,
                                                   self.num_classes, filter_ratio_match)
        return bb_idx, b, a, gj, gi, target, anch
