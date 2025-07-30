"""Module for common geometry transformations."""

import numpy as np

from scipy.spatial.transform import Rotation


def decompose_rigid_transform(transformation: np.ndarray) -> tuple:
    """Decomposes a 3D rigid body transformation into scale, rotation, and translation."""

    assert transformation.shape == (
        4,
        4,
    ), "transformation is not a 3D rigid-body transformation"

    scaled_rotation: np.ndarray = transformation[:3, :3]
    translation: np.ndarray = transformation[:3, 3]

    scale: float = np.linalg.norm(scaled_rotation, axis=1)[0]
    rotation: np.ndarray = scaled_rotation / scale

    return scale, rotation, translation


def rotation_matrix_to_euler(
    matrix: np.ndarray,
    degrees: bool = False,
    order: str = "ZYX",
) -> tuple[float, float, float]:
    """Converts a rotation matrix to a set of Euler angles."""

    assert matrix.shape == (
        3,
        3,
    ), "rotation is not a 3D rotation matrix"
    return Rotation.from_matrix(matrix).as_euler(order, degrees=degrees)


def rotation_matrix_to_vector(matrix: np.ndarray, degrees: bool = False) -> np.ndarray:
    """Converts a rotation matrix to a rotation vector."""

    assert matrix.shape == (
        3,
        3,
    ), "rotation is not a 3D rotation matrix"
    return Rotation.from_matrix(matrix).as_rotvec(degrees=degrees)
