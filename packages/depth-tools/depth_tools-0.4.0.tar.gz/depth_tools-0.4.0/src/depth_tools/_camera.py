import logging
import math
from dataclasses import dataclass
from typing import TypedDict

import numpy as np

import depth_tools

from ._coord_sys import CoordSys
from ._logging_internal import LOGGER


@dataclass(frozen=True)
class CameraIntrinsics:
    """
    The intrinsic properties of a simple pinhole camera.

    The assumptions of the class:

    * All camera parameters are given in pixels.
    * The center of the bottom left pixel of the projected image is at the ``(0.5, 0.5)`` coordinate.

    The negative focal lengths are not supported.

    Parameters
    ----------
    f_x
        The focal length of the camera on the X axis.
    f_y
        The focal length of the camera on the Y axis.
    c_x
        The X coordinate of the optical center of the camera.
    c_y
        The Y coordinate of the optical center of the camera.

    Raises
    ------
    ValueError
        If any of the focal lengths is negative.
    """

    f_x: float
    """
    The focal length of the camera on the X axis in pixel.
    """

    f_y: float
    """
    The focal length of the camera on the Y axis in pixel.
    """

    c_x: float
    """
    The X coordinate of the optical center of the camera in pixel.
    """

    c_y: float
    """
    The Y coordinate of the optical center of the camera in pixel.
    """

    def __post_init__(self):
        if self.f_x < 0:
            raise ValueError(
                f"The x focal length should be positive. Current focal length: {self.f_x}"
            )
        if self.f_y < 0:
            raise ValueError(
                f"The y focal length should be positive. Current focal length: {self.f_y}"
            )

    @staticmethod
    def from_fov(
        *, width: int, height: int, fov_rad: float, fov_x: bool
    ) -> "CameraIntrinsics":
        """
        Calculate the camera intrisnics from the field of view.

        Assumptions:

        * The infinitely far points are projected to the ``(width/2, height/2)`` point on the image.
        * The focal lengths on the X and Y axis are equal.

        Parameters
        ----------
        width
            The width of the image in pixels.
        height
            The height of the image in pixels.
        fov_rad
            The field of view in radians.
        fov_x
            If true, then the field of view is given on the X axis. Otherwise it is given on the Y axis.

        Returns
        -------
        v
            The calculated camera intrinsics.
        """
        if fov_x:
            f_x = width / 2 * math.cos(fov_rad / 2)
            f_y = f_x
            c_x = width / 2
            c_y = height / 2
        else:
            f_y = height / 2 * math.cos(fov_rad / 2)
            f_x = f_y
            c_x = width / 2
            c_y = height / 2

        return CameraIntrinsics(f_x=f_x, f_y=f_y, c_x=c_x, c_y=c_y)

    def get_intrinsic_mat(self) -> np.ndarray:
        """
        Get the intrinsic matrix of the camera.

        The returned matrix: ::

            [ f_x   0     c_x ]
            [ 0     f_y   c_y ]
            [ 0     0     1   ]

        The format of the returned intrinsic matrix: ``Mat``

        The dtype of the returned intrinsic matrix: `numpy.float32`
        """
        return np.array(
            [
                [self.f_x, 0, self.c_x],
                [0, self.f_y, self.c_y],
                [0, 0, 1],
            ],
            dtype=np.float32,
        )

    def get_intrinsic_mat_inv(self):
        """
        Get the inverse of the intrinsic matrix of the camera.

        The returned matrix: ::

                                -1
            [ f_x   0     c_x ]
            [ 0     f_y   c_y ]
            [ 0     0     1   ]

        The format of the returned intrinsic matrix: ``Mat``

        The dtype of the returned intrinsic matrix: `numpy.float32`
        """
        return np.linalg.inv(self.get_intrinsic_mat())

    @staticmethod
    def from_gl_proj_mat(
        P: np.ndarray, im_width: int, im_height: int
    ) -> "CameraIntrinsics":
        """
        Extract the camera parameters from a given Open GL projection matrix.

        The function assumes that the coordinate system of the view space is **Y-up right handed** and the OpenGL camera looks at the **-Z** direction. Note that this is different from our coordinates, because we use an **Y-up left-handed** coordinate system, where the camera looks at the **+Z** direction.

        This function only supports the Open GL matrices that describe a projection matching to the camera model of this class.

        The function assumes *column* vectors.

        Parameters
        ----------
        P
            The projection matrix. It is a 4x4 matrix. Format: ``Matrix`` or ``MatrixI``
        im_width
            The width of the image.
        im_height
            The height of the image.

        Returns
        -------
        v
            The described camera.

        Raises
        ------
        ValueError
            If ``P`` is not a 4x4 matrix.

            If the width or the height is non-positive.

            If any of the focal lengths is negative.
        """

        if P.shape != (4, 4):
            raise ValueError(
                f"The argument P does not have shape (4, 4). Shape: {P.shape}"
            )

        if not (
            np.issubdtype(P.dtype, np.floating) or np.issubdtype(P.dtype, np.integer)
        ):
            raise ValueError(
                f"The dtype of argument P is neither integer nor floating. Dtype: {P.dtype}"
            )

        if im_width <= 0:
            raise ValueError(
                f"The image width is non-positive. Image width: {im_width}"
            )

        if im_height <= 0:
            raise ValueError(
                f"The image height is non-positive. Image height: {im_height}"
            )

        zero_mask = np.array(
            [
                [0, 1, 0, 1],
                [1, 0, 0, 1],
                [0, 0, 0, 0],
                [1, 1, 0, 1],
            ],
            dtype=np.bool_,
        )

        max_forbidden_abs = abs(P[zero_mask]).max()
        if max_forbidden_abs > 1e-10:
            LOGGER.warning(
                f"The given projection is probably not supported by the camera model, because it contains a non-zero value at a forbidden location. Value: {max_forbidden_abs}. Forbidden locations: {zero_mask}"
            )

        if abs(P[3, 2]) < 1e-10:
            LOGGER.warning(
                f"The given projection is probably not supported by teh camera model, because the absolute value of element at index [3, 2] is less than 1e-10. Value: {P[3, 2]}"
            )

        # flip_z transform
        #   source: Y-up right handed + the camera looks at the -Z direction
        #   target: Y-up left handed + the camera looks at the +Z direction
        flip_z = np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, -1, 0],
                [0, 0, 0, 1],
            ],
            dtype=P.dtype,
        )

        ndc_2_px = np.array(
            [
                [0.5 * (im_width - 1), 0, 0, 0.5 * (im_width - 1)],
                [0, 0.5 * (im_height - 1), 0, 0.5 * (im_height - 1)],
                [0, 0, 0.5, 0.5],
                [0, 0, 0, 1.0],
            ]
        )
        total_mat = ndc_2_px @ P @ flip_z

        total_mat = total_mat / total_mat[3, 2]

        f_x = float(total_mat[0, 0])
        f_y = float(total_mat[1, 1])

        c_x = float(total_mat[0, 2])
        c_y = float(total_mat[1, 2])

        return CameraIntrinsics(f_x=f_x, f_y=f_y, c_x=c_x, c_y=c_y)


class ProjCoordSysDir(TypedDict):
    coord_sys: CoordSys
    cam_looks_at_positive_dir: bool
