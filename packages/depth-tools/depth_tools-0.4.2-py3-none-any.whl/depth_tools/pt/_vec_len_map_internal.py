import torch

from .._camera import CameraIntrinsics


def get_vec_len_map_mult_unchecked(
    input_im: torch.Tensor, d: float, cam: CameraIntrinsics
) -> torch.Tensor:
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

    x, y = torch.meshgrid(
        torch.arange(w, dtype=input_im.dtype).to(input_im.device),
        torch.arange(h - 1, -1, -1).to(input_im.dtype).to(input_im.device),
        indexing="xy",  # this is the default at Numpy
    )

    x_im = torch.unsqueeze(x, dim=0).to(input_im.dtype)
    y_im = torch.unsqueeze(y, dim=0).to(input_im.dtype)

    x_s = (x_im * d - cam.c_x) / cam.f_x
    y_s = (y_im * d - cam.c_y) / cam.f_y

    vec_lens = torch.sqrt((x_s**2) + (y_s**2) + (d**2))

    if len(input_im.shape) == 4:
        vec_lens = torch.unsqueeze(vec_lens, dim=0)

    return vec_lens
