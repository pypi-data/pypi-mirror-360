# Taken from Yolov7 https://github.com/WongKinYiu/yolov7
# mypy: ignore-errors
import numpy as np
import torch  # type: ignore
import torch.nn.functional as F  # type: ignore
from code_loader.helpers.detection.utils import xywh_to_xyxy_format
from typing import List, Tuple


def find_3_positive(p: List[torch.Tensor], targets: torch.Tensor, anchors: torch.Tensor,
                    filter_ratio_match: bool) ->\
        Tuple[List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]], List[torch.Tensor]]:
    # Build targets for compute_loss(), input targets(x,y,w,h)
    # p.shape = [B,3, GX, GW, 5+CLASSES]
    # targers.shape = [B,6=[image, class, x, y, w, h,]]
    # targets=torch.from_numpy(truths.numpy())
    targets = torch.concat([torch.Tensor(np.arange(targets.shape[0]))[:, None], targets], axis=1)
    na, nt = anchors.shape[1], targets.shape[0]  # number of anchors, targets
    indices, anch = [], []
    gain = torch.ones(8, device=targets.device).long()  # normalized to gridspace gain
    ai = torch.arange(na, device=targets.device).float().view(na, 1).repeat(1, nt)  # same as .repeat_interleave(nt)
    targets = torch.cat((targets.repeat(na, 1, 1), ai[:, :, None]), 2)  # append anchor indices

    g = 0.5  # bias
    off = torch.tensor([[0, 0],
                        [1, 0], [0, 1], [-1, 0], [0, -1],  # j,k,l,m
                        # [1, 1], [1, -1], [-1, 1], [-1, -1],  # jk,jm,lk,lm
                        ], device=targets.device).float() * g  # offsets
    for i in range(len(p)):
        gain[3:7] = torch.tensor(p[i].shape)[[3, 2, 3, 2]]  # xyxy gain
        layer_anchors = anchors[i]

        # Match targets to anchors
        t = targets * gain
        if nt:
            # Matches
            if filter_ratio_match:
                r = t[:, :, 3:5] / layer_anchors[:, None]  # wh ratio
                j = torch.max(r, 1. / r).max(2)[0] < 4  # compare
            else:
                j = torch.ones(t.shape[:-1], dtype=bool)
                # j = wh_iou(anchors, t[:, 4:6]) > model.hyp['iou_t']  # iou(3,n)=wh_iou(anchors(3,2), gwh(n,2))
            t = t[j]  # filter only relevant anchors
            # Offsets
            gxy = t[:, 3:5]  # grid xy
            gxi = gain[[3, 4]] - gxy  # inverse offset in the feature space
            j, k = ((gxy % 1. < g) & (gxy > 1.)).T  # x closer to left, y closest to up
            l, m = ((gxi % 1. < g) & (gxi > 1.)).T  # x closer to right, y closet to down
            j = torch.stack((torch.ones_like(j), j, k, l, m))  # [True, x-left, y-up, x-right, y-down]
            t = t.repeat((5, 1, 1))[j]
            offsets = (torch.zeros_like(gxy)[None] + off[:, None])[j]
        else:
            t = targets[0]
            offsets = 0

            # Define
        b, c = t[:, 1:3].long().T  # image, class
        gxy = t[:, 3:5]  # grid xy
        gwh = t[:, 5:7]  # grid wh
        gij = (gxy - offsets).long()
        gi, gj = gij.T  # grid xy indices
        bb_index = t[:, 1]

        # Append
        a = t[:, 7].long()  # anchor indices
        indices.append(
            (
            bb_index, b, a, gj.clamp_(0, gain[4] - 1), gi.clamp_(0, gain[3] - 1)))  # image, anchor, grid indices [y,x]]
        anch.append(layer_anchors[a])  # anchors

    return indices, anch


def box_iou(box1: torch.Tensor, box2: torch.Tensor) -> torch.Tensor:
    # https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py
    """
    Return intersection-over-union (Jaccard index) of boxes.
    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    Arguments:
        box1 (Tensor[N, 4])
        box2 (Tensor[M, 4])
    Returns:
        iou (Tensor[N, M]): the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    """

    def box_area(box: torch.Tensor) -> torch.Tensor:
        # box = 4xn
        return (box[2] - box[0]) * (box[3] - box[1])

    area1 = box_area(box1.T)
    area2 = box_area(box2.T)

    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    inter = (torch.min(box1[:, None, 2:], box2[:, 2:]) - torch.max(box1[:, None, :2], box2[:, :2])).clamp(0).prod(2)
    return inter / (area1[:, None] + area2 - inter)  # iou = inter / (area1 + area2 - inter)


def build_targets(p: List[torch.Tensor], targets: torch.Tensor, anchors: torch.Tensor,
                  image_size: Tuple[int, int], num_classes: int,
                  filter_ratio_match: bool) -> Tuple[List[torch.Tensor], ...]:
    # targets [Image, class, x, y, w, h]
    # anchors [scale x anchor-per-scale]
    # P == LIST[[B,ANCHORS,H_scale_i,W_scale_i,CLASSES+5]...]
    # len(p) == scales

    # indices, anch = self.find_positive(p, targets)
    indices, anch = find_3_positive(p, targets, anchors, filter_ratio_match)
    # indices, anch = self.find_4_positive(p, targets)
    # indices, anch = self.find_5_positive(p, targets)
    # indices, anch = self.find_9_positive(p, targets)

    matching_bs: List[torch.Tensor] = [[] for pp in p]
    matching_as: List[torch.Tensor] = [[] for pp in p]
    matching_gjs: List[torch.Tensor] = [[] for pp in p]
    matching_gis: List[torch.Tensor] = [[] for pp in p]
    matching_bb_index: List[torch.Tensor] = [[] for pp in p]
    matching_targets: List[torch.Tensor] = [[] for pp in p]
    matching_anchs: List[torch.Tensor] = [[] for pp in p]

    nl = len(p)

    for batch_idx in range(p[0].shape[0]):

        b_idx = targets[:, 0] == batch_idx
        this_target = targets[b_idx]
        if this_target.shape[0] == 0:
            continue

        txywh = this_target[:, 2:6] * np.array([*image_size[::-1], *image_size[::-1]], dtype=np.float32)
        txyxy = torch.from_numpy(xywh_to_xyxy_format(txywh).astype(np.float32))

        pxyxys = []
        p_cls = []
        p_obj = []
        from_which_layer = []
        all_b = []
        all_a = []
        all_gj = []
        all_gi = []
        all_anch = []
        all_bb_idx = []

        for i, pi in enumerate(p):
            bb_idx, b, a, gj, gi = indices[i]
            idx = (b == batch_idx)
            bb_idx, b, a, gj, gi = bb_idx[idx], b[idx], a[idx], gj[idx], gi[idx]
            all_b.append(b)
            all_a.append(a)
            all_gj.append(gj)
            all_gi.append(gi)
            all_anch.append(anch[i][idx])
            all_bb_idx.append(bb_idx)
            from_which_layer.append(torch.ones(size=(len(b),)) * i)

            fg_pred = pi[b, a, gj, gi]
            p_obj.append(fg_pred[:, 4:5])
            p_cls.append(fg_pred[:, 5:])

            grid = torch.stack([gi, gj], dim=1)
            pxy = fg_pred[:, :2] * torch.from_numpy(np.array([*image_size[::-1]]).astype(np.float32))
            pwh = fg_pred[:, 2:4] * torch.from_numpy(np.array([*image_size[::-1]]).astype(np.float32))
            pxywh = torch.cat([pxy, pwh], dim=-1)
            pxyxy = torch.from_numpy(xywh_to_xyxy_format(pxywh).astype(np.float32))
            pxyxys.append(pxyxy)

        pxyxys_cat = torch.cat(pxyxys, dim=0)
        if pxyxys_cat.shape[0] == 0:
            continue
        p_obj_cat = torch.cat(p_obj, dim=0)
        p_cls_cat = torch.cat(p_cls, dim=0)
        from_which_layer_cat = torch.cat(from_which_layer, dim=0)
        all_b = torch.cat(all_b, dim=0)
        all_a = torch.cat(all_a, dim=0)
        all_gj = torch.cat(all_gj, dim=0)
        all_gi = torch.cat(all_gi, dim=0)
        all_anch = torch.cat(all_anch, dim=0)
        all_bb_idx = torch.cat(all_bb_idx, dim=0)

        pair_wise_iou = box_iou(txyxy, pxyxys_cat)  # (BB-matched,4), BB-matches(scale)=#anchors-matches*3

        pair_wise_iou_loss = -torch.log(pair_wise_iou + 1e-8)

        top_k, _ = torch.topk(pair_wise_iou, min(10, pair_wise_iou.shape[1]), dim=1)
        dynamic_ks = torch.clamp(top_k.sum(1).int(), min=1)

        gt_cls_per_image = (
            F.one_hot(this_target[:, 1].to(torch.int64), num_classes)
            .float()
            .unsqueeze(1)
            .repeat(1, pxyxys_cat.shape[0], 1)
        )

        num_gt = this_target.shape[0]
        cls_preds_ = (
                p_cls_cat.float().unsqueeze(0).repeat(num_gt, 1, 1).sigmoid_()
                * p_obj_cat.unsqueeze(0).repeat(num_gt, 1, 1).sigmoid_()
        )

        y = cls_preds_.sqrt_()
        pair_wise_cls_loss = F.binary_cross_entropy_with_logits(
            torch.log(y / (1 - y)), gt_cls_per_image, reduction="none"
        ).sum(-1)
        del cls_preds_

        cost = (
                pair_wise_cls_loss
                + 3.0 * pair_wise_iou_loss
        )

        matching_matrix = torch.zeros_like(cost)

        for gt_idx in range(num_gt):
            _, pos_idx = torch.topk(
                cost[gt_idx], k=dynamic_ks[gt_idx].item(), largest=False
            )
            matching_matrix[gt_idx][pos_idx] = 1.0

        del top_k, dynamic_ks
        anchor_matching_gt = matching_matrix.sum(0)  # sum of the matches per anchor
        if (anchor_matching_gt > 1).sum() > 0:
            _, cost_argmin = torch.min(cost[:, anchor_matching_gt > 1], dim=0)
            matching_matrix[:, anchor_matching_gt > 1] *= 0.0
            matching_matrix[cost_argmin, anchor_matching_gt > 1] = 1.0
        fg_mask_inboxes = matching_matrix.sum(0) > 0.0
        matched_gt_inds = matching_matrix[:, fg_mask_inboxes].argmax(0)

        from_which_layer_cat = from_which_layer_cat[fg_mask_inboxes]
        all_b = all_b[fg_mask_inboxes]
        all_a = all_a[fg_mask_inboxes]
        all_gj = all_gj[fg_mask_inboxes]
        all_gi = all_gi[fg_mask_inboxes]
        all_anch = all_anch[fg_mask_inboxes]
        all_bb_idx = all_bb_idx[fg_mask_inboxes]

        this_target = this_target[matched_gt_inds]

        for i in range(nl):
            layer_idx = from_which_layer_cat == i
            matching_bs[i].append(all_b[layer_idx])
            matching_as[i].append(all_a[layer_idx])
            matching_gjs[i].append(all_gj[layer_idx])
            matching_gis[i].append(all_gi[layer_idx])
            matching_targets[i].append(this_target[layer_idx])
            matching_anchs[i].append(all_anch[layer_idx])
            matching_bb_index[i].append(all_bb_idx[layer_idx])

    for i in range(nl):
        if matching_targets[i] != []:
            matching_bs[i] = torch.cat(matching_bs[i], dim=0)
            matching_as[i] = torch.cat(matching_as[i], dim=0)
            matching_gjs[i] = torch.cat(matching_gjs[i], dim=0)
            matching_gis[i] = torch.cat(matching_gis[i], dim=0)
            matching_targets[i] = torch.cat(matching_targets[i], dim=0)
            matching_anchs[i] = torch.cat(matching_anchs[i], dim=0)
            matching_bb_index[i] = torch.cat(matching_bb_index[i], dim=0)

        else:
            matching_bs[i] = torch.tensor([], dtype=torch.int64)
            matching_as[i] = torch.tensor([], dtype=torch.int64)
            matching_gjs[i] = torch.tensor([], dtype=torch.int64)
            matching_gis[i] = torch.tensor([], dtype=torch.int64)
            matching_targets[i] = torch.tensor([], dtype=torch.int64)
            matching_anchs[i] = torch.tensor([], dtype=torch.int64)
            matching_bb_index[i] = torch.tensor([], dtype=torch.int64)

    return matching_bb_index, matching_bs, matching_as, matching_gjs, matching_gis, matching_targets, matching_anchs  # SCALE*[bb_idx, B,anchor-idx, j, i,  GTs, anchors]
