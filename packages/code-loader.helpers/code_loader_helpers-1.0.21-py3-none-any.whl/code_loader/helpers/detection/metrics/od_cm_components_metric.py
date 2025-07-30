import tensorflow as tf  # type: ignore
from typing import Dict, List, Tuple
import numpy as np
from numpy.typing import NDArray

from code_loader.helpers.detection.utils import jaccard


def od_detection_metrics(
    pred_bboxes: List[NDArray[np.float32]],
    gt_bboxes: NDArray[np.float32],
    label_id_to_name: Dict[int, str],
    threshold: float,
    background_label: int,
) -> Tuple[Dict[str, NDArray[np.float32]], Dict[str, NDArray[np.float32]]]:
    """
    Calculate detection metrics for a batch of predicted and ground truth
    bounding boxes.

    Args:
        pred_bboxes (List[np.ndarray]): A list of tensors containing predicted
            bounding boxes for each image in the batch. Each tensor should have
            shape [num_predictions, 6], where the last dimension represents
            [x_min, y_min, x_max, y_max, conf, class_id].
            if there are no predictions an empty numpy array of shape (0, 6) per batch is expected
        gt_bboxes (np.ndarray): A tensor containing ground truth bounding boxes
            for each image in the batch. The tensor should have shape [batch_size,
            num_ground_truths, 5], where the last dimension represents [x_min,
            y_min, x_max, y_max, class_id].
        label_id_to_name (Dict): A dictionary mapping label IDs to their
            corresponding class names.
        threshold (float): The IoU threshold to determine whether a predicted
            bounding box matches a ground truth bounding box.
        background_label (int): The label ID for the background class, used to
            filter out background bounding boxes.

    Returns:
        Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]: A tuple containing two
            dictionaries. The first dictionary contains the true detection
            metrics, including true positives (TP) and their normalized versions
            (TP_norm) for each class and for the batch. The second dictionary
            contains the false detection metrics, including false positives (FP),
            false negatives (FN), and their normalized versions (FP_norm, FN_norm)
            for each class and for the batch.
    """
    # input validation
    if not isinstance(pred_bboxes, list):
        raise ValueError(
            f"pred_bboxes should be a list of numpy arrays, got {type(pred_bboxes)}"
        )
    if not isinstance(gt_bboxes, np.ndarray):
        raise ValueError(f"gt_bboxes should be a numpy array, got {type(gt_bboxes)}")
    if np.concatenate(pred_bboxes, axis=0).shape[1] != 6:
        raise ValueError("The last dimension of pred_bboxes should be 6")
    if gt_bboxes.shape[2] != 5:
        raise ValueError(
            f"The last dimension of gt_bboxes should be 5, got {gt_bboxes.shape[2]}"
        )

    # convert gt bboxes to numpy array
    gt_bboxes = np.asarray(gt_bboxes, dtype=np.float32)
    pred_bboxes = [np.asarray(pb, dtype=np.float32) for pb in pred_bboxes]
    batch_size = gt_bboxes.shape[0]
    # Initialize dictionaries to store counts of true positives, false positives, and false negatives
    results = generate_results_dict(batch_size, label_id_to_name)
    # iterate over each image in the batch
    for b_i in range(batch_size):
        # get predicted and ground truth bboxes for the current batch
        pred_bboxes_batch = pred_bboxes[b_i]
        gt_bboxes_batch = gt_bboxes[b_i]
        # filter out background labels - remove padding
        gt_bboxes_batch = gt_bboxes_batch[gt_bboxes_batch[..., -1] != background_label]
        # check if there are no gt objects and no predictions - return empty list
        if pred_bboxes_batch.shape[0] == 0 and gt_bboxes_batch.shape[0] == 0:
            continue
        elif (
            pred_bboxes_batch.shape[0] == 0 and gt_bboxes_batch.shape[0] > 0
        ):  # all gt objects are false negatives (FN)
            for i in range(gt_bboxes_batch.shape[0]):
                results[f"{label_id_to_name[gt_bboxes_batch[i, -1]]}_FN"][b_i] += 1
                results["sample_FN"][b_i] += 1
        elif (
            pred_bboxes_batch.shape[0] > 0 and gt_bboxes_batch.shape[0] == 0
        ):  # all predictions are false positives (FP)
            for i in range(pred_bboxes_batch.shape[0]):
                results[f"{label_id_to_name[pred_bboxes_batch[i, -1]]}_FP"][b_i] += 1
                results["sample_FP"][b_i] += 1
        else:  # there are both predictions and gt objects
            iou_matrix = jaccard(
                gt_bboxes_batch[:, :4], pred_bboxes_batch[:, :4]
            ).numpy()
            gt_matched_indices, pred_matched_indices = np.where(iou_matrix >= threshold)
            unmatched_gt_indices = np.setdiff1d(
                np.arange(gt_bboxes_batch.shape[0]), gt_matched_indices
            )
            unmatched_pred_indices = np.setdiff1d(
                np.arange(pred_bboxes_batch.shape[0]), pred_matched_indices
            )
            matched_gt_bboxes = gt_bboxes_batch[gt_matched_indices]
            matched_pred_bboxes = pred_bboxes_batch[pred_matched_indices]
            unmatched_gt_bboxes = gt_bboxes_batch[unmatched_gt_indices]
            unmatched_pred_bboxes = pred_bboxes_batch[unmatched_pred_indices]
            # add confusion matrix elements for matched objects
            for i in range(matched_gt_bboxes.shape[0]):
                if matched_gt_bboxes[i, -1] == matched_pred_bboxes[i, -1]:  # TP
                    results[f"{label_id_to_name[matched_gt_bboxes[i, -1]]}_TP"][
                        b_i
                    ] += 1
                    results["sample_TP"][b_i] += 1
                else:  # FP for pred label and FN for gt label
                    # FP for pred label
                    results[f"{label_id_to_name[matched_pred_bboxes[i, -1]]}_FP"][
                        b_i
                    ] += 1
                    results["sample_FP"][b_i] += 1
                    # FN for gt label
                    results[f"{label_id_to_name[matched_gt_bboxes[i, -1]]}_FN"][
                        b_i
                    ] += 1
                    results["sample_FN"][b_i] += 1

            # add confusion matrix elements for unmatched gt objects - FN
            for i in range(unmatched_gt_bboxes.shape[0]):
                results[f"{label_id_to_name[unmatched_gt_bboxes[i, -1]]}_FN"][b_i] += 1
                results["sample_FN"][b_i] += 1
            # add confusion matrix elements for unmatched predictions - FP
            for i in range(unmatched_pred_bboxes.shape[0]):
                results[f"{label_id_to_name[unmatched_pred_bboxes[i, -1]]}_FP"][
                    b_i
                ] += 1
                results["sample_FP"][b_i] += 1

            # add normalized values
            lable_counts = get_class_counts(
                pred_bboxes_batch, gt_bboxes_batch, label_id_to_name
            )
            for class_name in label_id_to_name.values():
                gt_count = lable_counts.get(f"{class_name}_gt", 0)
                pred_count = lable_counts.get(f"{class_name}_pred", 0)
                if gt_count > 0:
                    results[f"{class_name}_FN_norm"][b_i] = (
                        results[f"{class_name}_FN"] / gt_count
                    )
                    results[f"{class_name}_TP_norm"][b_i] = (
                        results[f"{class_name}_TP"] / gt_count
                    )
                if pred_count > 0:
                    results[f"{class_name}_FP_norm"][b_i] = (
                        results[f"{class_name}_FP"] / pred_count
                    )
            if lable_counts.get("total_gt", 0) > 0:
                results["sample_FN_norm"][b_i] = (
                    results["sample_FN"] / lable_counts["total_gt"]
                )
                results["sample_TP_norm"][b_i] = (
                    results["sample_TP"] / lable_counts["total_gt"]
                )
            if lable_counts.get("total_pred", 0) > 0:
                results["sample_FP_norm"][b_i] = (
                    results["sample_FP"] / lable_counts["total_pred"]
                )

    results = {
        k: (
            tf.convert_to_tensor(v, dtype=tf.int32)
            if np.issubdtype(v.dtype, np.integer)
            else tf.convert_to_tensor(v, dtype=tf.float32)
        )
        for k, v in results.items()
    }
    true_detection_metrics = {k: v for k, v in results.items() if "tp" in k.lower()}
    false_detection_metrics = {
        k: v for k, v in results.items() if "fp" in k.lower() or "fn" in k.lower()
    }
    return true_detection_metrics, false_detection_metrics


def generate_results_dict(
    batch_size: int, label_id_to_name: Dict[int, str]
) -> Dict[str, NDArray[np.float32]]:
    results = {}
    for class_name in label_id_to_name.values():
        results[f"{class_name}_FN"] = np.zeros((batch_size,), dtype=int)
        results[f"{class_name}_FN_norm"] = np.zeros((batch_size,), dtype=float)
        results[f"{class_name}_FP"] = np.zeros((batch_size,), dtype=int)
        results[f"{class_name}_FP_norm"] = np.zeros((batch_size,), dtype=float)
        results[f"{class_name}_TP"] = np.zeros((batch_size,), dtype=int)
        results[f"{class_name}_TP_norm"] = np.zeros((batch_size,), dtype=float)

    results["sample_FN"] = np.zeros((batch_size,), dtype=int)
    results["sample_FN_norm"] = np.zeros((batch_size,), dtype=float)
    results["sample_FP"] = np.zeros((batch_size,), dtype=int)
    results["sample_FP_norm"] = np.zeros((batch_size,), dtype=float)
    results["sample_TP"] = np.zeros((batch_size,), dtype=int)
    results["sample_TP_norm"] = np.zeros((batch_size,), dtype=float)
    return results


def get_class_counts(
    pred_bboxes: NDArray[np.float32],
    gt_bboxes: NDArray[np.float32],
    label_id_to_name: Dict[int, str],
) -> Dict[str, int]:
    """
    Calculate the count of ground truth and predicted bounding boxes for each
    class.

    Args:
        pred_bboxes (np.ndarray): An array of predicted bounding boxes with shape
            [num_predictions, 6], where the last dimension represents
            [x_min, y_min, x_max, y_max, conf, class_id].
        gt_bboxes (np.ndarray): An array of ground truth bounding boxes with shape
            [num_ground_truths, 5], where the last dimension represents
            [x_min, y_min, x_max, y_max, class_id].
        label_id_to_name (Dict[int, str]): A dictionary mapping label IDs to their
            corresponding class names.

    Returns:
        Dict[str, int]: A dictionary containing the counts of ground truth and
            predicted bounding boxes for each class, along with the total counts.
            The keys are in the format "{class_name}_gt" for ground truth counts
            and "{class_name}_pred" for predicted counts, as well as "total_gt"
            and "total_pred" for overall counts.
    """

    counts = {}
    gt_labels = gt_bboxes[..., -1]
    pred_labels = pred_bboxes[..., -1]

    unique_labels, counts = np.unique(gt_labels, return_counts=True)
    counts = {
        f"{label_id_to_name[label]}_gt": count
        for label, count in zip(unique_labels, counts)
    }

    unique_labels, counts = np.unique(pred_labels, return_counts=True)
    counts = {
        f"{label_id_to_name[label]}_gt": count
        for label, count in zip(unique_labels, counts)
    }

    counts["total_gt"] = gt_labels.shape[0]
    counts["total_pred"] = pred_labels.shape[0]
    return counts
