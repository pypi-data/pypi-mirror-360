import unittest

import npy_unittest
import numpy as np
import torch

import depth_tools
import depth_tools.pt


class TestNormalizeValues(npy_unittest.NpyTestCase):
    def setUp(self):
        self.original_values = np.array(
            [[1, 2, 3, 4, 10], [2, 3, -2, 5, -1], [3, 4, 5, 6, 12]], dtype=np.float32
        )
        self.original_values = np.reshape(self.original_values, (3, 1, 5))
        self.mask = np.array(
            [
                [True, True, True, True, True],
                [True, True, False, True, False],
                [True, True, True, True, True],
            ]
        )
        self.mask = np.reshape(self.mask, (3, 1, 5))
        self.expected_normalized_values = np.array(
            [
                [-2.0, -1.0, 0.0, 1.0, 7.0],
                [-3.0, 0.0, 0, 6.0, 0],
                [-2.0, -1.0, 0.0, 1.0, 7.0],
            ],
            dtype=np.float32,
        )
        self.expected_normalized_values = np.reshape(
            self.expected_normalized_values, (3, 1, 5)
        )

    def test_normalize_values__happy_path__multiple(self):
        actual_normalized_values = depth_tools.normalize_values(
            values=self.original_values,
            mask=self.mask,
            verify_args=True,
            first_dim_separates=True,
        )

        self.assertAllclose(
            self.expected_normalized_values, actual_normalized_values, atol=1e-4
        )

    def test_normalize_values__happy_path__multiple__fortran(self):
        actual_normalized_values = depth_tools.normalize_values(
            values=np.asfortranarray(self.original_values),
            mask=self.mask,
            verify_args=True,
            first_dim_separates=True,
        )

        self.assertAllclose(
            self.expected_normalized_values, actual_normalized_values, atol=1e-4
        )

    def test_normalize_values__happy_path__single(self):
        actual_normalized_values = depth_tools.normalize_values(
            values=self.original_values[0],
            mask=self.mask[0],
            verify_args=True,
            first_dim_separates=True,
        )

        self.assertAllclose(
            self.expected_normalized_values[0], actual_normalized_values, atol=1e-4
        )

    def test_normalize_values__single_value(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.normalize_values(
                values=np.array(2, dtype=np.float32),
                mask=np.array(True),
                verify_args=True,
                first_dim_separates=False,
            )

        msg = str(cm.exception)
        self.assertIn("The value array should be at least one dimensional", msg)

    def test_normalize_values__invalid_values_dtype(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.normalize_values(
                values=self.original_values.astype(np.int32),
                mask=self.mask,
                verify_args=True,
                first_dim_separates=True,
            )

        msg = str(cm.exception)
        self.assertIn("array of values to nomralize", msg)
        self.assertIn("int32", msg)

    def test_normalize_values__invalid_mask_dtype(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.normalize_values(
                values=self.original_values,
                mask=self.mask.astype(np.float32),
                verify_args=True,
                first_dim_separates=True,
            )

        msg = str(cm.exception)
        self.assertIn("mask that selects valid values", msg)
        self.assertIn("float32", msg)

    def test_normalize_values__inconsistent_shape(self):
        mask_with_new_shape = np.expand_dims(self.mask, axis=-1)
        with self.assertRaises(ValueError) as cm:
            depth_tools.normalize_values(
                values=self.original_values,
                mask=mask_with_new_shape,
                verify_args=True,
                first_dim_separates=True,
            )

        msg = str(cm.exception)
        self.assertIn("The shape of the values", msg)
        self.assertIn(str(self.original_values.shape), msg)
        self.assertIn(str(mask_with_new_shape.shape), msg)

    def test_normalize_values__not_enough_dimensions(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.normalize_values(
                values=torch.from_numpy(self.original_values.flatten()),
                mask=torch.from_numpy(self.mask.flatten()),
                verify_args=True,
                first_dim_separates=True,
            )

        msg = str(cm.exception)
        self.assertIn("The value array should be at least two", msg)
        self.assertIn(str(self.original_values.size), msg)

    def test_normalize_values__happy_path__multiple_pt(self):
        actual_normalized_values = depth_tools.pt.normalize_values(
            values=torch.from_numpy(self.original_values),
            mask=torch.from_numpy(self.mask),
            verify_args=True,
            first_dim_separates=True,
        ).numpy()

        self.assertAllclose(self.expected_normalized_values, actual_normalized_values)

    def test_normalize_values__happy_path__single_pt(self):
        actual_normalized_values = depth_tools.pt.normalize_values(
            values=torch.from_numpy(self.original_values[0]),
            mask=torch.from_numpy(self.mask[0]),
            verify_args=True,
            first_dim_separates=True,
        ).numpy()

        self.assertAllclose(
            self.expected_normalized_values[0], actual_normalized_values, atol=1e-4
        )

    def test_normalize_values__single_value_pt(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.normalize_values(
                values=np.array(2, dtype=np.float32),
                mask=np.array(True),
                verify_args=True,
                first_dim_separates=False,
            )

        msg = str(cm.exception)
        self.assertIn("The value array should be at least one dimensional", msg)

    def test_normalize_values__invalid_values_dtype_pt(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.normalize_values(
                values=torch.from_numpy(self.original_values.astype(np.int32)),
                mask=torch.from_numpy(self.mask),
                verify_args=True,
                first_dim_separates=True,
            )

        msg = str(cm.exception)
        self.assertIn("array of values to nomralize", msg)
        self.assertIn("int32", msg)

    def test_normalize_values__invalid_mask_dtype_pt(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.normalize_values(
                values=torch.from_numpy(self.original_values),
                mask=torch.from_numpy(self.mask.astype(np.float32)),
                verify_args=True,
                first_dim_separates=True,
            )

        msg = str(cm.exception)
        self.assertIn("mask that selects valid values", msg)
        self.assertIn("float32", msg)

    def test_normalize_values__inconsistent_shape_pt(self):
        mask_with_new_shape = np.expand_dims(self.mask, axis=-1)
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.normalize_values(
                values=torch.from_numpy(self.original_values),
                mask=torch.from_numpy(mask_with_new_shape),
                verify_args=True,
                first_dim_separates=True,
            )

        msg = str(cm.exception)
        self.assertIn("The shape of the values", msg)
        self.assertIn(str(self.original_values.shape), msg)
        self.assertIn(str(mask_with_new_shape.shape), msg)

    def test_normalize_values__not_enough_dimensions_pt(self):
        with self.assertRaises(ValueError) as cm:
            depth_tools.pt.normalize_values(
                values=torch.from_numpy(self.original_values.flatten()),
                mask=torch.from_numpy(self.mask.flatten()),
                verify_args=True,
                first_dim_separates=True,
            )

        msg = str(cm.exception)
        self.assertIn("The value array should be at least two", msg)
        self.assertIn(str(self.original_values.size), msg)
