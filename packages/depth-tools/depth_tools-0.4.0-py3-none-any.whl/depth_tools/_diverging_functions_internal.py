from typing import Any

import numpy as np


def nanmedian(a: np.ndarray, along_all_dims_except_0: bool) -> np.ndarray:
    """
    A nanmedian function that works similarly for both Numpy and Pytorch.

    Parameters
    ----------
    a
        The array on which the nanmedian calculation should be done.
    along_all_dims_except_0
        If true, then the median calculation is done along all dimensions, except 0. Otherwise, the median calculation is done alongside all dimensions.

    Returns
    -------
    v
        The calculated median.
    """
    if along_all_dims_except_0:
        a_reshaped = a.reshape(len(a), -1, order="C")
        nanmedian_values = np.nanmedian(a_reshaped, axis=1)
        new_shape: list[int] = [len(nanmedian_values)] + [1] * (len(a.shape) - 1)
        return np.reshape(nanmedian_values, new_shape, order="C")
    else:
        return np.array(np.nanmedian(a))


def nanmean(a: np.ndarray, along_all_dims_except_0: bool) -> np.ndarray:
    """
    A nanmean function that works similarly for both Numpy and Pytorch

    Parameters
    ----------
    a
        The array on which the nanmedian calculation should be done.
    along_all_dims_except_0
        If true, then the mean calculation is done along all dimensions, except 0. Otherwise, the mean calculation is done alongside all dimensions.

    Returns
    -------
    v
        The calculated median.
    """
    if along_all_dims_except_0:
        a_reshaped = a.reshape(len(a), -1, order="C")
        nanmean_values = np.nanmean(a_reshaped, axis=1)
        new_shape: list[int] = [len(nanmean_values)] + [1] * (len(a.shape) - 1)
        return np.reshape(nanmean_values, new_shape, order="C")
    else:
        return np.array(np.nanmean(a))


def new_full(
    like: np.ndarray,
    value: Any,
    shape: tuple[int, ...] | None = None,
) -> np.ndarray:
    """
    Implements a ``full_like`` operation that plays nicely with tensor subclassing in Pytorch.

    Parameters
    ----------
    like
        The original array. Format: any array.
    value
        The value.
    shape
        The shape of the created array.
    """
    return np.full_like(like, value, shape=shape)
