import unittest
from typing import Callable, Iterable

import npy_unittest
import numpy as np


class TestBase(npy_unittest.NpyTestCase):
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
