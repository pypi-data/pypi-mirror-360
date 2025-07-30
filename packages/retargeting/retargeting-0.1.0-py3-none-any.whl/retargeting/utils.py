from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from beartype import beartype as typechecker
from jaxtyping import Float, jaxtyped
from numba import njit
from scipy.spatial.transform import Rotation as R

from retargeting.typing import SE3, SO3, Ortho6D, XYZOrtho6D, XYZQuat

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PROJECT_ROOT / "conf"


# @jaxtyped(typechecker=typechecker)
# @dataclass
# class Pose:
#     translation: Float[np.ndarray, "3"]
#     rotation: Float[np.ndarray, "x=3 y=3"]

#     @classmethod
#     def from_xyzquat(cls, translation: Float[np.ndarray, "3"], quat: Float[np.ndarray, "4"]):
#         rot: Float[np.ndarray, "3 3"] = R.from_quat(quat).as_matrix()
#         return cls(translation=translation, rotation=rot)

#     @classmethod
#     def from_xyzeuler(cls, translation: Float[np.ndarray, "3"], euler: Float[np.ndarray, "3"]):
#         rot = R.from_euler("xyz", euler).as_matrix()
#         return cls(translation=translation, rotation=rot)

#     @classmethod
#     def from_pinocchio(cls, transform: pin.SE3):
#         return cls(translation=transform.translation, rotation=transform.rotation)

#     def to_pinocchio(self) -> pin.SE3:
#         return pin.SE3(translation=self.translation, rotation=self.rotation)

#     @property
#     def quat(self) -> Float[np.ndarray, "4"]:
#         return R.from_matrix(self.rotation).as_quat()


def get_timestamp_utc():
    return datetime.now(timezone.utc)


def datetime_to_iso(dt: datetime) -> str:
    """
    Convert a datetime object to an ISO 8601 filename with microseconds.
    Args:
        dt (datetime): The datetime object to convert.
    Returns:
        str: ISO 8601 filename-safe string with microseconds.
    """
    return dt.replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H-%M-%S_%f")


def posix_to_iso(posix: float) -> str:
    """
    Convert a POSIX timestamp to an ISO 8601 filename with microseconds.
    Args:
        posix (float): The POSIX timestamp to convert.
    Returns:
        str: ISO 8601 filename-safe string with microseconds.
    """
    dt = datetime.fromtimestamp(posix, tz=timezone.utc)
    return datetime_to_iso(dt)


def iso_to_datetime(filename: str) -> datetime:
    """
    Convert an ISO 8601 filename with microseconds back to a datetime object.
    Args:
        filename (str): The filename to parse, including or excluding the file extension.
    Returns:
        datetime: Parsed datetime object.
    """
    if "." in filename:
        base_name = filename.split(".")[0]  # Remove file extension
    else:
        base_name = filename
    return datetime.strptime(base_name, "%Y-%m-%dT%H-%M-%S_%f").replace(tzinfo=timezone.utc)


@jaxtyped(typechecker=typechecker)
@njit
def se3_to_xyzortho6d(se3: SE3) -> XYZOrtho6D:
    """
    Convert SE(3) to continuous 6D rotation representation.
    """
    so3 = se3[:3, :3]
    xyz = se3[:3, 3]
    ortho6d = so3_to_ortho6d(so3)
    return np.concatenate([xyz, ortho6d])


@jaxtyped(typechecker=typechecker)
@njit
def xyzortho6d_to_se3(xyzortho6d: XYZOrtho6D) -> SE3:
    """
    Convert continuous 6D rotation representation to SE(3).
    """
    xyz = xyzortho6d[:3]
    ortho6d = xyzortho6d[3:]
    so3 = ortho6d_to_so3(ortho6d)
    se3 = np.eye(4)
    se3[:3, :3] = so3
    se3[:3, 3] = xyz
    return se3


@jaxtyped(typechecker=typechecker)
@njit
def so3_to_ortho6d(so3: SO3) -> Ortho6D:
    """
    Convert to continuous 6D rotation representation adapted from
    On the Continuity of Rotation Representations in Neural Networks
    https://arxiv.org/pdf/1812.07035.pdf
    https://github.com/papagina/RotationContinuity/blob/master/sanity_test/code/tools.py
    """
    return so3[:, :2].transpose().reshape(-1)


@jaxtyped(typechecker=typechecker)
@njit
def ortho6d_to_so3(ortho6d: Ortho6D) -> SO3:
    """
    Convert from continuous 6D rotation representation to SO(3), adapted from
    On the Continuity of Rotation Representations in Neural Networks
    https://arxiv.org/pdf/1812.07035.pdf
    https://github.com/papagina/RotationContinuity/blob/master/sanity_test/code/tools.py
    """
    x_raw = ortho6d[:3]
    y_raw = ortho6d[3:6]

    x = x_raw / np.linalg.norm(x_raw)
    z = np.cross(x, y_raw)
    z = z / np.linalg.norm(z)
    y = np.cross(z, x)
    return np.column_stack((x, y, z))


@jaxtyped(typechecker=typechecker)
def ortho6d_to_R(ortho6d: Ortho6D) -> R:
    return R.from_matrix(ortho6d_to_so3(ortho6d))


@jaxtyped(typechecker=typechecker)
def R_to_ortho6d(rot: R) -> Ortho6D:
    return so3_to_ortho6d(rot.as_matrix())


@jaxtyped(typechecker=typechecker)
def se3_to_xyzquat(se3: SE3) -> XYZQuat:
    se3 = np.asanyarray(se3).astype(float)
    if se3.shape != (4, 4):
        raise ValueError("Input must be a 4x4 matrix")
    return _se3_to_xyzquat(se3)


@jaxtyped(typechecker=typechecker)
def xyzquat_to_se3(xyzquat: XYZQuat) -> SE3:
    xyzquat = np.asanyarray(xyzquat).astype(float)
    if xyzquat.shape != (7,):
        raise ValueError("Input must be a 7-element array")
    return _xyzquat_to_se3(xyzquat)


@jaxtyped(typechecker=typechecker)
@njit
def _se3_to_xyzquat(se3: SE3) -> XYZQuat:
    translation = se3[:3, 3]
    rotmat = se3[:3, :3]

    quat = R.from_matrix(rotmat).as_quat()

    xyzquat = np.concatenate([translation, quat])
    return xyzquat


@jaxtyped(typechecker=typechecker)
@njit
def _xyzquat_to_se3(xyzquat: XYZQuat) -> SE3:
    translation = xyzquat[:3]
    quat = xyzquat[3:]

    rotmat = R.from_quat(quat).as_matrix()

    se3 = np.eye(4)
    se3[:3, :3] = rotmat
    se3[:3, 3] = translation

    return se3


def mat_update(prev_mat, mat):
    if np.linalg.det(mat) == 0:
        return prev_mat
    else:
        return mat


@njit
def fast_mat_inv(mat: SE3) -> SE3:
    mat = np.asarray(mat)
    ret = np.eye(4)
    ret[:3, :3] = mat[:3, :3].T
    ret[:3, 3] = -mat[:3, :3].T @ mat[:3, 3]
    return ret


@jaxtyped(typechecker=typechecker)
def _remap(
    x: Float[np.ndarray, "dim"],
    old_min: Float[np.ndarray, "dim"],
    old_max: Float[np.ndarray, "dim"],
    new_min: Float[np.ndarray, "dim"],
    new_max: Float[np.ndarray, "dim"],
    clip=True,
) -> Float[np.ndarray, "dim"]:
    tmp = (x - old_min) / (old_max - old_min)
    if clip:
        tmp = np.clip(tmp, 0, 1)
    return new_min + tmp * (new_max - new_min)


def remap(
    x: list | np.ndarray,
    old_min: list | np.ndarray,
    old_max: list | np.ndarray,
    new_min: list | np.ndarray,
    new_max: list | np.ndarray,
    clip=True,
):
    """Remap array to new range.

    Args:
        x (list | np.ndarray): Array to remap.
        old_min (list | np.ndarray): Minimum value of the old range.
        old_max (list | np.ndarray): Maximum value of the old range.
        new_min (list | np.ndarray): Minimum value of the new range.
        new_max (list | np.ndarray): Maximum value of the new range.
        clip (bool, optional): Whether to clip the values to the new range. Defaults to True.

    Returns:
        np.ndarray: Remapped array.
    """
    x = np.asarray(x, dtype=float)
    old_min = np.asarray(old_min, dtype=float)
    old_max = np.asarray(old_max, dtype=float)
    new_min = np.asarray(new_min, dtype=float)
    new_max = np.asarray(new_max, dtype=float)
    return _remap(x, old_min, old_max, new_min, new_max, clip)


def wxyz_to_xyzw(wxyz: np.ndarray) -> np.ndarray:
    return np.concatenate((wxyz[1:], [wxyz[0]]))


def xyzw_to_wxyz(xyzw: np.ndarray) -> np.ndarray:
    return np.concatenate(([xyzw[3]], xyzw[:3]))
