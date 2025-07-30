import operator
from typing import SupportsIndex
from unittest import mock

import depth_tools
import depth_tools.pt
import npy_unittest
import numpy as np
import torch


class TestPtSpecial(npy_unittest.NpyTestCase):
    def test_move_sample_to(self):
        start_device = torch.device("cpu")
        alt_device = torch.device("meta")

        orig_sample: depth_tools.pt.TorchSample = {
            "camera": depth_tools.CameraIntrinsics(f_x=50, f_y=50, c_x=100, c_y=100),
            "name": "sample56",
            "depth": torch.ones((1, 10, 50), dtype=torch.float32, device=start_device),
            "mask": torch.full((1, 10, 50), True, device=start_device),
            "rgb": torch.ones((3, 10, 50), dtype=torch.float32, device=start_device),
        }

        got_sample = depth_tools.pt.move_sample_to(
            device=alt_device, sample=orig_sample
        )

        self.assertEqual(got_sample["rgb"].device, alt_device)
        self.assertEqual(got_sample["rgb"].shape, orig_sample["rgb"].shape)
        self.assertEqual(got_sample["rgb"].dtype, orig_sample["rgb"].dtype)

        self.assertEqual(got_sample["depth"].device, alt_device)
        self.assertEqual(got_sample["depth"].shape, orig_sample["depth"].shape)
        self.assertEqual(got_sample["depth"].dtype, orig_sample["depth"].dtype)

        self.assertEqual(got_sample["mask"].device, alt_device)
        self.assertEqual(got_sample["mask"].shape, orig_sample["mask"].shape)
        self.assertEqual(got_sample["mask"].dtype, orig_sample["mask"].dtype)

        self.assertEqual(got_sample["name"], orig_sample["name"])
        self.assertEqual(got_sample["camera"], orig_sample["camera"])


class TestDatasetWrapper(npy_unittest.NpyTestCase):
    def test_dataset_wrapper(self):
        dataset_mock = mock.Mock(name="dataset")
        dataset_mock.__len__ = mock.Mock(name="dataset.__len__", side_effect=lambda: 1)

        npy_sample: depth_tools.Sample = {
            "camera": depth_tools.CameraIntrinsics(f_x=10, f_y=10, c_x=40, c_y=40),
            "depth": np.ones((1, 20, 30), dtype=np.float32),
            "mask": np.ones((1, 20, 30), dtype=np.bool),
            "name": "sample5",
            "rgb": np.ones((3, 20, 30), dtype=np.float32),
        }

        def dataset_getitem(idx: SupportsIndex) -> depth_tools.Sample:
            self.assertEqual(operator.index(idx), 5)
            return npy_sample

        dataset_mock.__getitem__ = mock.Mock(
            name="dataset_mock.__getitem__", side_effect=dataset_getitem
        )

        wrapper = depth_tools.pt.DatasetWrapper(dataset_mock)

        got_sample = wrapper[5]

        self.assertAllclose(got_sample["depth"].numpy(), npy_sample["depth"])
        self.assertAllclose(got_sample["rgb"].numpy(), npy_sample["rgb"])
        self.assertEqual(got_sample["name"], npy_sample["name"])
        self.assertEqual(got_sample["camera"], npy_sample["camera"])
