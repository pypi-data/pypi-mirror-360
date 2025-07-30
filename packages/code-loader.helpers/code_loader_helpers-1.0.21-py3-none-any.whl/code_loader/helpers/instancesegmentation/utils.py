import tensorflow as tf # type: ignore
from numpy.typing import NDArray
import numpy as np


def crop_mask(masks: tf.Tensor, boxes: NDArray[np.float32]) -> tf.Tensor:
    """
    "Crop" predicted masks by zeroing out everything not in the predicted bbox.
    Vectorized by Chong (thanks Chong).

    Args:
        - masks should be a size [n, h, w] tensor of masks
        - boxes should be a size [n, 4] tensor of bbox coords in relative point form
    """

    n, h, w = masks.shape
    x1, y1, x2, y2 = boxes[:, :, None][:,[0],:], boxes[:, :, None][:,[1],:],\
                     boxes[:, :, None][:,[2],:], boxes[:, :, None][:,[3],:]  # x1 shape(1,1,n)
    r = tf.range(w, dtype=x1.dtype)[None, None, :]  # rows shape(1,w,1)
    c = tf.range(h, dtype=x1.dtype)[None, :, None]  # cols shape(h,1,1)

    return masks*tf.cast(r >= x1, float) * tf.cast(r < x2, float)*\
           tf.cast(c >= y1, float) * tf.cast(c < y2, float)