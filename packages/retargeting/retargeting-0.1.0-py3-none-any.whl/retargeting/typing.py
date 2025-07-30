from __future__ import annotations

from enum import Enum
from typing import TypeAlias

import numpy as np
from jaxtyping import Float

# Pose: TypeAlias = Float[np.ndarray, "7"]  # 3 translation + 4 quaternion
SO3: TypeAlias = Float[np.ndarray, "3 3"]  # 3x3 rotation matrix
SE3: TypeAlias = Float[np.ndarray, "4 4"]  # 4x4 transformation matrix
Ortho6D: TypeAlias = Float[np.ndarray, "6"]  # 6
XYZQuat: TypeAlias = Float[np.ndarray, "7"]  # 3 translation + 4 quaternion
XYZOrtho6D: TypeAlias = Float[np.ndarray, "9"]  # 3 translation + 6D rotation


class RobotType(Enum):
    GR1T1 = "gr1t1"
    GR1T2 = "gr1t2"
    GR2T2 = "gr2t2"
    GR2T2D = "gr2t2d"

    @classmethod
    def names(cls) -> list[str]:
        return [member.value for member in cls]

    @classmethod
    def from_str(cls, name: str):
        try:
            return cls[name.upper()]
        except ValueError as e:
            raise ValueError(f"Invalid robot type: {name}") from e


class HandType(Enum):
    FOURIER_6DOF = "fourier_hand_6dof"
    FOURIER_12DOF = "fourier_hand_12dof"
    INSPIRE = "inspire_hand"

    @classmethod
    def names(cls) -> list[str]:
        return [member.value for member in cls]

    @classmethod
    def from_str(cls, name: str):
        try:
            if "_hand" in name:
                name = name.replace("_hand", "")
            return cls[name.upper()]
        except ValueError as e:
            raise ValueError(f"Invalid hand type: {name}") from e
