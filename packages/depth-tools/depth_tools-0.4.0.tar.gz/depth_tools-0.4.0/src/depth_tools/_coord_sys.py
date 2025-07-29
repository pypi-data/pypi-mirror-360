import itertools
from enum import Enum, auto

import numpy as np


def get_coord_sys_conv_mat(from_: "CoordSys", to: "CoordSys") -> np.ndarray:
    R"""
    Create a matrix that converts between different coordinate systems.

    Format  ::

                    returned_mat
        from ------------------------> to

    Parameters
    ----------
    from\_
        The initial coordinate system.
    to
        The target coordinate system.

    Returns
    -------
    v
        The conversion matrix. Format: ``Mat_3x3``
    """
    return _coord_sys_conv_lut[from_, to].copy()


class CoordSys(Enum):
    """
    The enum that specifies the different supported 3D coordinate systems.
    """

    RH_YUp = auto()
    """
    Right-handed Y-up
    """

    RH_ZUp = auto()
    """
    Right-handed Z-up
    """

    LH_YUp = auto()
    """
    Left-handed Y-up
    """

    LH_ZUp = auto()
    """
    Left-handed Z-up
    """


def _generate_coord_sys_conv_lut() -> dict[tuple[CoordSys, CoordSys], np.ndarray]:
    """
    The function to generate a look-up table that stores the coordinate system conversion matrices.

    Returns
    -------
    v
        A dictionary with the key structure ``(from, to)``, where ``from`` is the initial coordinate system and ``to`` is the target coordinate system. The format of the values: ``Mat_3x3``
    """

    to_left_handed_y_up = {
        CoordSys.LH_YUp: np.eye(3, dtype=np.float32),
        CoordSys.LH_ZUp: np.array(
            [
                [1, 0, 0],
                [0, 0, 1],
                [0, -1, 0],
            ],
            dtype=np.float32,
        ),
        CoordSys.RH_YUp: np.array(
            [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, -1],
            ],
            dtype=np.float32,
        ),
        CoordSys.RH_ZUp: np.array(
            [
                [1, 0, 0],
                [0, 0, 1],
                [0, 1, 0],
            ],
            dtype=np.float32,
        ),
    }

    from_left_handed_y_up = {k: v.T for k, v in to_left_handed_y_up.items()}

    lut: dict[tuple[CoordSys, CoordSys], np.ndarray] = dict()
    for from_, to in itertools.product(CoordSys, CoordSys):
        conv_mat = from_left_handed_y_up[to] @ to_left_handed_y_up[from_]
        lut[from_, to] = conv_mat
    return lut


_coord_sys_conv_lut = _generate_coord_sys_conv_lut()
