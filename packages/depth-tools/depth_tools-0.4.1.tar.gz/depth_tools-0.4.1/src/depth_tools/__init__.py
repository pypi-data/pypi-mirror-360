"""
A package to handle the depth processing-related calculations in both Pytorch and Numpy.
"""

from ._align_depth_univ import align_shift_scale
from ._camera import CameraIntrinsics
from ._coord_sys import CoordSys, get_coord_sys_conv_mat
from ._datasets import Dataset, Nyuv2Dataset, Sample, SimplifiedHypersimDataset
from ._depth_clip import DepthClip
from ._depth_map_dilation import fast_dilate_depth_map
from ._dist_maps_univ import depth_map_2_dist_map, dist_map_2_depth_map
from ._losses_univ import DepthLoss, dx_loss, mse_log_loss, mse_loss
from ._normalize_values_univ import normalize_values
from ._point_cloud import (
    PointSubsamplingConf,
    depth_2_point_cloud,
    depths_2_matplotlib_fig,
    depths_2_plotly_fig,
)

__all__ = [
    "CameraIntrinsics",
    "CoordSys",
    "get_coord_sys_conv_mat",
    "depth_2_point_cloud",
    "depths_2_plotly_fig",
    "depths_2_matplotlib_fig",
    "mse_log_loss",
    "mse_loss",
    "dx_loss",
    "DepthClip",
    "Dataset",
    "Nyuv2Dataset",
    "SimplifiedHypersimDataset",
    "Sample",
    "fast_dilate_depth_map",
    "PointSubsamplingConf",
    "align_shift_scale",
    "normalize_values",
    "DepthLoss",
    "dist_map_2_depth_map",
    "depth_map_2_dist_map",
]

__version__ = "0.4.1"
