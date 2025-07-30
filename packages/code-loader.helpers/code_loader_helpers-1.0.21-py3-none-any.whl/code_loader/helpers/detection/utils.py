import math
from typing import Tuple
from typing import Union

import numpy as np
import tensorflow as tf  # type: ignore
from numpy.typing import NDArray


def xyxy_to_xywh_format(boxes: Union[NDArray[np.float32], tf.Tensor]) -> Union[NDArray[np.float32], tf.Tensor]:
    """
    This gets bb in a [X,Y,W,H] format and transforms them into an [Xmin, Ymin, Xmax, Ymax] format
    :param boxes: [Num_boxes, 4] of type ndarray or tensor
    :return:
    """
    min_xy = (boxes[..., :2] + boxes[..., 2:]) / 2
    max_xy = (boxes[..., 2:] - boxes[..., :2])
    if isinstance(boxes, tf.Tensor):
        result = tf.concat([min_xy, max_xy], -1)
    else:
        result = np.concatenate([min_xy, max_xy], -1)
    return result


def xywh_to_xyxy_format(boxes: Union[NDArray[np.float32], tf.Tensor]) -> Union[NDArray[np.float32], tf.Tensor]:
    """
    This gets bb in a [X,Y,W,H] format and transforms them into an [Xmin, Ymin, Xmax, Ymax] format
    :param boxes: [Num_boxes, 4] of type ndarray or tensor
    :return:
    """
    min_xy = boxes[..., :2] - boxes[..., 2:] / 2
    max_xy = boxes[..., :2] + boxes[..., 2:] / 2
    if isinstance(boxes, tf.Tensor):
        result = tf.concat([min_xy, max_xy], -1)
    else:
        result = np.concatenate([min_xy, max_xy], -1)
    return result


def intersect(box_a: tf.Tensor, box_b: tf.Tensor) -> tf.Tensor:
    """

    :param box_a: Tensor, shape: (A, 4)
    :param box_b: Tensor, shape: (B, 4)
    :return: intersetction of box_a and box_b shape: (A, B)
    """
    min_xy = tf.math.minimum(tf.expand_dims(box_a[:, 2:], axis=1),
                             tf.expand_dims(box_b[:, 2:], axis=0))  # (right_bottom)
    max_xy = tf.math.maximum(tf.expand_dims(box_a[:, :2], axis=1),
                             tf.expand_dims(box_b[:, :2], axis=0))  # (left_top)
    inter = tf.math.maximum(min_xy - max_xy, 0)
    return inter[:, :, 0] * inter[:, :, 1]


def jaccard(box_a: tf.Tensor, box_b: tf.Tensor) -> tf.Tensor:
    """
    computes the IOU scores between two set of bb (box_a, box_b)
    :param box_a: Tensor, GT bounding boxes, shape: (a, 4)
    :param box_b: Tensor, other bounding boxes, shape: (b, 4)
    :return: Tensor, shape: (a, b)
    """
    inter = intersect(box_a, box_b)
    area_a = (box_a[:, 2] - box_a[:, 0]) * (box_a[:, 3] - box_a[:, 1])
    area_a = tf.expand_dims(area_a, axis=1)
    area_b = (box_b[:, 2] - box_b[:, 0]) * (box_b[:, 3] - box_b[:, 1])
    area_b = tf.expand_dims(area_b, axis=0)
    union = area_a + area_b - inter
    ratio = inter / union
    non_negativ_ratio = tf.where(inter > 0, x=ratio, y=0)
    return non_negativ_ratio


def true_coords_labels(idx: int, y_true: tf.Tensor, background_label: int) -> Tuple[tf.Tensor, tf.Tensor]:
    """
    y_true shape  Tensor, shape: (batch_size, MAX_BOXES_PER_IMAGE, 5) (5 last channels are (xmin, ymin, xmax, ymax, class_index))
    This removes the background_class class from the ground_truth_labels
    :param idx:
    :param y_true:
    :return:
    """
    y_true = y_true[idx]
    mask = y_true[:, -1] != background_label  # class index should be greater than 0
    masked_true = tf.boolean_mask(y_true, mask)
    true_coords = masked_true[:, :-1]
    true_labels = masked_true[:, -1]
    return true_coords, true_labels


def ciou(box_a: tf.Tensor, box_b: tf.Tensor) -> tf.Tensor:
    """
    computes the IOU scores between two set of bb (box_a, box_b)
    :param box_a: Tensor, GT bounding boxes, shape: (a, 4)
    :param box_b: Tensor, other bounding boxes, shape: (a, 4)
    :return: Tensor, shape: a
    """
    eps = 1e-7
    # Intersection area
    inter = tf.maximum((tf.minimum(box_a[:, 2], box_b[:, 2]) - tf.maximum(box_a[:, 0], box_b[:, 0])), 0) * \
            tf.maximum((tf.minimum(box_a[:, 3], box_b[:, 3]) - tf.maximum(box_a[:, 1], box_b[:, 1])), 0)
    w1, h1 = box_a[:, 2] - box_a[:, 0], box_a[:, 3] - box_a[:, 1] + eps
    w2, h2 = box_b[:, 2] - box_b[:, 0], box_b[:, 3] - box_b[:, 1] + eps
    area_a = w1 * h1
    area_b = w2 * h2
    union = area_a + area_b - inter + eps
    iou = inter / union
    cw = tf.maximum(box_a[:, 2], box_b[:, 2]) - tf.minimum(box_a[:, 0],
                                                           box_b[:, 0])  # convex (smallest enclosing box) width
    ch = tf.maximum(box_a[:, 3], box_b[:, 3]) - tf.minimum(box_a[:, 1], box_b[:, 1])  # convex height
    c2 = cw ** 2 + ch ** 2 + eps  # convex diagonal squared
    rho2 = ((box_b[:, 0] + box_b[:, 2] - box_a[:, 0] - box_a[:, 2]) ** 2 +
            (box_b[:, 1] + box_b[:, 3] - box_a[:, 1] - box_a[:, 3]) ** 2) / 4  # center distance squared
    v = (4 / math.pi ** 2) * tf.pow(tf.atan(w2 / (h2 + eps)) - tf.atan(w1 / (h1 + eps)), 2)
    alpha = tf.stop_gradient(v / (v - iou + (1 + eps)))
    return iou - (rho2 / c2 + v * alpha)  # CIoU


def match(threshold: float, truths: tf.Tensor, priors: tf.Tensor, labels: tf.Tensor, background_label: int) \
        -> Tuple[tf.Tensor, tf.Tensor]:
    """
    Matches between the GT and the anchors
    :param threshold:
    :param truths: (N_truths,4) - (X,Y,W,H)
    :param priors: (N_priors,4) - (X,Y,W,H)
    :param labels: (N_truths) GT class
    :param background_label: int - the background label
    :return: loc (Tensor) [Npriors, 4], pred_label (Tensor) [Npriors]
    """
    # compute jaccard and best prior overlap and truth overlap
    overlaps = jaccard(xywh_to_xyxy_format(truths), xywh_to_xyxy_format(priors))  # (N_TRUTHS, N_PRIORS)
    best_prior_idx = tf.math.argmax(overlaps, axis=1)  # (NTRUTHS,)
    best_truth_overlap = tf.math.reduce_max(overlaps, axis=0, keepdims=True)  # (1, N_PRIORS)
    best_truth_idx = tf.math.argmax(overlaps, axis=0)  # (N_PRIORS,)
    # rates priors by GT overlap
    tf.squeeze(best_truth_overlap)
    tf.expand_dims(best_prior_idx, axis=1)
    tf.fill(dims=[tf.shape(best_prior_idx)[0]], value=2.0)
    best_truth_overlap = tf.tensor_scatter_nd_update(tensor=tf.squeeze(best_truth_overlap),
                                                     indices=tf.expand_dims(best_prior_idx, axis=1),
                                                     updates=tf.fill(dims=[tf.shape(best_prior_idx)[0]],
                                                                     value=2.0))  # (N_PRIORS)
    best_truth_overlap = tf.expand_dims(best_truth_overlap, axis=0)
    tf.expand_dims(best_prior_idx, axis=1)
    tf.range(start=0, limit=tf.shape(best_prior_idx)[0], delta=1,
             dtype=tf.int64)
    # For every PRIOR what is the best GT IDX
    best_truth_idx = tf.tensor_scatter_nd_update(tensor=best_truth_idx,
                                                 indices=tf.expand_dims(best_prior_idx, axis=1),
                                                 updates=tf.range(start=0, limit=tf.shape(best_prior_idx)[0], delta=1,
                                                                  dtype=tf.int64))
    # FOR EACH GT, replace the value of the best fitting prior with the GT INDEX
    # THIS RATES ALL GT ACCORDING TO WHICH RESULT IN HIGHEST JACACRD
    matches = tf.gather(params=truths, indices=best_truth_idx)  # GT for each PRIOR (N_PRIOR, 4)
    pred_label = tf.gather(params=labels, indices=best_truth_idx)  # THIS IS THE BEST LABELS
    pred_label = tf.where(condition=best_truth_overlap < threshold, x=background_label, y=tf.cast(pred_label,
                                                                                                  tf.int32))  # eliminates low threshold
    pred_label = tf.squeeze(pred_label)  # (Nprior)
    return matches, pred_label
