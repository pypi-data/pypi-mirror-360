import numpy as np

from ._camera import CameraIntrinsics


def get_vec_len_map_mult_unchecked(
    input_im: np.ndarray, d: float, cam: CameraIntrinsics
) -> np.ndarray:
    """
    Calculate an array that can multiply each pixel of an ``Im_Scalar`` or an ``Ims_Scalar`` array with the distances points at each pixel with depth ``d``.

    Parameters
    ----------
    input_im
        The input image. Format: ``Im`` or ``Ims``
    d
        The depth of the points.
    cam
        The camera intrinsics.

    Returns
    -------
    v
        The multiplier array. Format: ``Immult`` or ``Imsmult`` depending on ``input_im``.
    """
    if len(input_im.shape) == 3:
        _, h, w = input_im.shape
    else:
        _, _, h, w = input_im.shape

    x, y = np.meshgrid(
        np.arange(w, dtype=input_im.dtype),
        np.arange(h, dtype=input_im.dtype)[::-1],
        indexing="xy",  # this is the default at Numpy
    )

    x_im = np.expand_dims(x, axis=0).astype(input_im.dtype)
    y_im = np.expand_dims(y, axis=0).astype(input_im.dtype)

    d = 1
    x_s = (x_im * d - cam.c_x) / cam.f_x
    y_s = (y_im * d - cam.c_y) / cam.f_y

    vec_lens = np.sqrt((x_s**2) + (y_s**2) + (d**2))

    if len(input_im.shape) == 4:
        vec_lens = np.expand_dims(vec_lens, axis=0)

    return vec_lens
