import unittest
from typing import Callable, Iterable

import numpy as np


class TestBase(unittest.TestCase):
    def assertAllclose(
        self, array1: np.ndarray, array2: np.ndarray, atol: float = 1e-4
    ):
        if not np.allclose(array1, array2, atol=atol):
            raise self.failureException(
                f"The arrays {array1} and {array2} are not close within range ({atol})."
            )

    def assertIssubdtype(self, dtype1, dtype2):
        if not np.issubdtype(dtype1, dtype2):
            raise self.failureException(
                f"The dtype {dtype1} is not a subdtype of {dtype2}"
            )

    def probe_invalid_inputs(
        self,
        arrays: Iterable[np.ndarray],
        fn: Callable,
    ) -> None:
        array_list = list(arrays)
        for array_idx in range(len(array_list)):
            # test shape
            out_list = array_list.copy()
            out_list[array_idx] = out_list[array_idx].flatten()

            with self.assertRaises(ValueError) as cm:
                fn(*out_list)

            msg = str(cm.exception).lower()
            self.assertIn("shape", msg)
            for shape_part in out_list[array_idx].shape:
                self.assertIn(str(shape_part), msg)

            # test data type
            out_list = array_list.copy()
            out_list[array_idx] = out_list[array_idx].astype(np.complex64)
            with self.assertRaises(ValueError) as cm:
                fn(*out_list)

            msg = str(cm.exception).lower()
            self.assertIn("dtype", msg)
            self.assertIn(str(out_list[array_idx].dtype), msg)
