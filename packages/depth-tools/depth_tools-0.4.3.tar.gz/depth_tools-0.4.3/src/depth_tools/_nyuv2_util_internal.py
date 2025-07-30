from typing import TYPE_CHECKING, Any, cast

import numpy as np

if TYPE_CHECKING:
    import h5py


def decode_nyuv2_split_idx_list_unchecked(split_idx_array: np.ndarray) -> list[int]:
    """
    Decode the array of sample indices at NyuDepth v2.


    NyuDepth v2 stores the index arrays as Numpy arrays. Shape: ``(n_indices, 1)``; dtype: ``integer``.

    Parameters
    ----------
    split_idx_array
        The index array.

    Returns
    -------
    v
        The decoded index list.
    """
    return cast(list[int], split_idx_array[:, 0].tolist())


def decode_nyuv2_hdf5_str_unchecked(str_dataset: "h5py.Dataset") -> str:
    """
    Decode a NyuDepth v2 string from HDF5.

    NyuDepth v2 stores the strings as individual datasets. Shape: ``(n_characters, 1)``; dtype: ``<u2``.

    Parameters
    ----------
    str_dataset
        The dataset of an individual string.

    Returns
    -------
    v
        The decoded string.
    """
    str_acc = ""

    for code_point_arr in str_dataset[:, 0]:
        str_acc += chr(code_point_arr)

    return str_acc


def decode_nyuv2_hdf5_str_list_unchecked(
    h5_file: "h5py.File", ref_list_path: str
) -> list[str]:
    """
    Decode the list of strings given in the format of NyuDepth v2.

    NyuDepth v2 stores the string lists in the following order:

    - There is a reference dataset that points to the individual strings. Shape: ``(1, n_items)``, dtype: ``h5py.ref_dtype``
    - The strings themselves are separate datasets placed into a separate group, called ``#refs#``.

    Parameters
    ----------
    h5_file
        The hdf5 file.
    ref_list_path
        The path of the dataset containing the references to the individual strings.

    Returns
    -------
    v
        The decoded list of strings.
    """
    import h5py

    ref_list_dataset: h5py.Dataset = h5_file[ref_list_path]  # type: ignore

    result: list[str] = []
    for str_ref in ref_list_dataset[0]:
        ref_dataset = cast(h5py.Dataset, h5_file[str_ref])
        result.append(decode_nyuv2_hdf5_str_unchecked(ref_dataset))

    return result
