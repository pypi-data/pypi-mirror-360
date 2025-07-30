from typing import Dict, List
import numpy as np
import tensorflow as tf  # type: ignore
from code_loader.contract.datasetclasses import (  # type: ignore
    ConfusionMatrixElement,
    ConfusionMatrixValue,
)
from code_loader.helpers.detection.utils import jaccard
from numpy.typing import NDArray


def od_confusion_matrix_metric(
    pred_bboxes: List[NDArray[np.float32]],
    gt_bboxes: NDArray[np.float32],
    label_id_to_name: Dict[int, str],
    threshold: float,
    background_label: int,
) -> List[List[ConfusionMatrixElement]]:
    """
    Calculates the confusion matrix metric for object detection.

    Args:
        pred_bboxes (List[np.ndarray]): A list of Tensors containing predicted bounding boxes
            for each batch. Each Tensor has shape [num_predictions, 5], where the last dimension
            represents [x_min, y_min, x_max, y_max, conf, class_id].
            if there are no predictions an empty numpy array of shape (0, 6) per batch is expected
        gt_bboxes (np.ndarray): A Tensor containing ground truth bounding boxes with shape
            [batch_size, num_objects, 5], where the last dimension represents
            [x_min, y_min, x_max, y_max, class_id].
        label_id_to_name (Dict): A dictionary mapping class ids to class names.
        threshold (float): The IoU threshold to consider a prediction as a true positive.
        background_label (int): The label id representing the background class.

    Returns:
        List[List[ConfusionMatrixElement]]: A list of lists containing ConfusionMatrixElement
            instances for each image in the batch. Each ConfusionMatrixElement represents
            a single entry in the confusion matrix with attributes 'label', 'expected_outcome',
            and 'predicted_probability'.

    Description:
        The function computes a confusion matrix for object detection by comparing predicted
        bounding boxes (pred_bboxes) with ground truth bounding boxes (gt_bboxes) on a
        per-batch basis. It follows these steps:

        1. Converts ground truth bounding boxes to a numpy array.
        2. Iterates over each image in the batch.
        3. Filters out background labels from the ground truth bounding boxes.
        4. Depending on the presence of predicted and ground truth bounding boxes, it handles
           four scenarios:
            a. No predictions and no ground truth: Adds an empty list for this image.
            b. No predictions but ground truth exists: Marks all ground truth objects as
               false negatives (FN).
            c. Predictions exist but no ground truth: Marks all predictions as false positives (FP).
            d. Both predictions and ground truth exist: Computes the IoU matrix and matches
               predictions to ground truth using the given threshold.
                - Adds matched predictions as true positives (TP) or false positives (FP) based
                  on class label matching.
                - Adds unmatched ground truth objects as false negatives (FN).
                - Adds unmatched predictions as false positives (FP).
        5. Collects and returns the confusion matrix elements for each image in the batch.

    Note:
        - The function expects that the bounding boxes coordinates are in the format [x_min, y_min, x_max, y_max].
        - The function assumes that the last dimension of the bounding box tensors represents the class label.
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
    gt_bboxes = np.asarray(gt_bboxes)
    batch_size = gt_bboxes.shape[0]
    results = []
    # iterate over each image in the batch
    for b_i in range(batch_size):
        confusion_matrix_elements = []
        # get predicted and ground truth bboxes for the current batch
        pred_bboxes_batch = pred_bboxes[b_i]
        gt_bboxes_batch = gt_bboxes[b_i]
        # filter out background labels - remove padding
        gt_bboxes_batch = gt_bboxes_batch[gt_bboxes_batch[..., -1] != background_label]
        # check if there are no gt objects and no predictions - return empty list
        if pred_bboxes_batch.shape[0] == 0 and gt_bboxes_batch.shape[0] == 0:
            confusion_matrix_elements.append(
                ConfusionMatrixElement(
                    label="",
                    expected_outcome=ConfusionMatrixValue.Positive,
                    predicted_probability=0.0,
                )
            )
        elif (
            pred_bboxes_batch.shape[0] == 0 and gt_bboxes_batch.shape[0] > 0
        ):  # all gt objects are false negatives (FN)
            for i in range(gt_bboxes_batch.shape[0]):
                confusion_matrix_elements.append(
                    ConfusionMatrixElement(
                        label=label_id_to_name[gt_bboxes_batch[i, -1]],
                        expected_outcome=ConfusionMatrixValue.Positive,
                        predicted_probability=0.0,
                    )
                )
        elif (
            pred_bboxes_batch.shape[0] > 0 and gt_bboxes_batch.shape[0] == 0
        ):  # all predictions are false positives (FP)
            for i in range(pred_bboxes_batch.shape[0]):
                confusion_matrix_elements.append(
                    ConfusionMatrixElement(
                        label=label_id_to_name[pred_bboxes_batch[i, -1]],
                        expected_outcome=ConfusionMatrixValue.Negative,
                        predicted_probability=pred_bboxes_batch[i, 4],
                    )
                )
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
                    confusion_matrix_elements.append(
                        ConfusionMatrixElement(
                            label=label_id_to_name[matched_gt_bboxes[i, -1]],
                            expected_outcome=ConfusionMatrixValue.Positive,
                            predicted_probability=matched_pred_bboxes[i, 4],
                        )
                    )
                else:  # FP for gt label and FN for pred label
                    confusion_matrix_elements.append(
                        ConfusionMatrixElement(
                            label=label_id_to_name[matched_gt_bboxes[i, -1]],
                            expected_outcome=ConfusionMatrixValue.Negative,
                            predicted_probability=matched_pred_bboxes[i, 4],
                        )
                    )
                    confusion_matrix_elements.append(
                        ConfusionMatrixElement(
                            label=label_id_to_name[matched_pred_bboxes[i, -1]],
                            expected_outcome=ConfusionMatrixValue.Positive,
                            predicted_probability=matched_pred_bboxes[i, 4],
                        )
                    )

            # add confusion matrix elements for unmatched gt objects - FN
            for i in range(unmatched_gt_bboxes.shape[0]):
                confusion_matrix_elements.append(
                    ConfusionMatrixElement(
                        label=label_id_to_name[unmatched_gt_bboxes[i, -1]],
                        expected_outcome=ConfusionMatrixValue.Positive,
                        predicted_probability=0.0,
                    )
                )
            # add confusion matrix elements for unmatched predictions - FP
            for i in range(unmatched_pred_bboxes.shape[0]):
                confusion_matrix_elements.append(
                    ConfusionMatrixElement(
                        label=label_id_to_name[unmatched_pred_bboxes[i, -1]],
                        expected_outcome=ConfusionMatrixValue.Negative,
                        predicted_probability=unmatched_pred_bboxes[i, 4],
                    )
                )
        results.append(confusion_matrix_elements)
    return results
