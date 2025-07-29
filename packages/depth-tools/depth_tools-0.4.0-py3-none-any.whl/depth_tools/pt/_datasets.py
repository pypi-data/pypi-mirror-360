from typing import Final, SupportsIndex, TypedDict

import torch
import torch.utils.data

from .._camera import CameraIntrinsics
from .._datasets import Dataset


class TorchSample(TypedDict):
    name: str
    rgb: torch.Tensor
    depth: torch.Tensor
    camera: CameraIntrinsics
    mask: torch.Tensor


def move_sample_to(sample: TorchSample, device: torch.device) -> TorchSample:
    return {
        "name": sample["name"],
        "camera": sample["camera"],
        "depth": sample["depth"].to(device),
        "mask": sample["mask"].to(device),
        "rgb": sample["rgb"].to(device),
    }


class DatasetWrapper(torch.utils.data.Dataset):
    """
    Wrap the given depth dataset to a Pytorch dataset.

    Parameters
    ----------
    wrapped
        The wrapped dataset.
    device
        The device onto which the samples are placed.
    """

    def __init__(self, wrapped: Dataset, device: torch.device = torch.device("cpu")):
        self.wrapped: Final = wrapped
        self.device: Final = device

    def __getitem__(self, index: SupportsIndex) -> TorchSample:
        item = self.wrapped[index]
        return {
            "camera": item["camera"],
            "depth": torch.from_numpy(item["depth"]).to(self.device),
            "mask": torch.from_numpy(item["mask"]).to(self.device),
            "name": item["name"],
            "rgb": torch.from_numpy(item["rgb"]).to(self.device),
        }

    def __len__(self):
        return len(self.wrapped)
