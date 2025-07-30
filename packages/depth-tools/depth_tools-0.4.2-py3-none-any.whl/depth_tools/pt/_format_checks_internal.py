import torch


def is_floating_array(arr: torch.Tensor, /) -> bool:
    return arr.dtype.is_floating_point


def is_bool_array(arr: torch.Tensor, /) -> bool:
    return arr.dtype == torch.bool


def is_dim_sel_ok(
    arr: torch.Tensor, dim_sel: int | tuple[int, ...] | list[int] | None, /
) -> bool:
    if dim_sel is None:
        return True

    n_axes = len(arr.shape)

    if isinstance(dim_sel, int):
        if not (-n_axes <= dim_sel < n_axes):
            return False
    else:
        for dim_sel_val in dim_sel:
            if not (-n_axes <= dim_sel_val < n_axes):
                return False

        if len(set(dim_sel)) != len(dim_sel):
            return False

    return True
