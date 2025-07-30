"""Module for camera aligners."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RigidTransformation:
    """Class representing a rigid transformation (SO(3), SE(3), Sim(3)."""

    scale: float
    rotation: np.ndarray
    translation: np.ndarray

    def apply(self, points: np.ndarray) -> np.ndarray:
        """
        Applies the rigid transformation to the points.
        :arg points: shape NxM - M = point dim, N = point count
        """
        # transformed: np.ndarray = self.scale * self.points @ self.rotation + self.translation
        transformed: np.ndarray = (
            self.scale * self.rotation.dot(points.T).T + self.translation
        )
        return transformed


def align_points_arun(A: np.ndarray, B: np.ndarray) -> RigidTransformation:
    """
    Estimates SE(3) transformation between two point sets using Arun's method.
    Estimates R and t such that B ~ RA + t

    Matching points should correspond with array indices, such that:
    A[:, i] ~ B[:, i]

    :arg A: source point set - shape (3, N)
    :arg B: target point set - shape (3, N)
    """
    assert A.shape == B.shape, "point sets A and B must be of equal size"

    N: int = A.shape[1]

    # Calculate centroids as (M, 1) vectors
    A_centroid: np.ndarray = np.mean(A, axis=0)
    B_centroid: np.ndarray = np.mean(B, axis=0)

    # Calculate the points relative to the centroid
    A_prime: np.ndarray = A - A_centroid
    B_prime: np.ndarray = B - B_centroid

    # Estimate rotation
    H: np.ndarray = np.zeros([3, 3])
    for i in range(N):
        ai: np.ndarray = A_prime[i, :]
        bi: np.ndarray = B_prime[i, :]
        H: np.ndarray = H + np.outer(ai, bi)

    U: np.ndarray
    S: np.ndarray
    V_transpose: np.ndarray
    U, S, V_transpose = np.linalg.svd(H)

    V: np.ndarray = np.transpose(V_transpose)
    U_transpose: np.ndarray = np.transpose(U)
    R: np.ndarray = (
        V @ np.diag([1, 1, np.linalg.det(V) * np.linalg.det(U_transpose)]) @ U_transpose
    )

    # Estimate translation by rotating around the centroid
    t: np.ndarray = B_centroid - R @ A_centroid

    return RigidTransformation(scale=1.0, rotation=R, translation=t)


def align_points_umeyama(
    source_points: np.ndarray, target_points: np.ndarray
) -> RigidTransformation:
    """
    Estimates the Sim(3) transformation between two point sets using Umeyamas method.
    Estimates c, R and t such as B ~ c * R @ A.T + t.

    :arg A: source point set - shape (N, M)
    :arg B: target point set - shape (N, M)

    :return c: float
    :return R: numpy.array - shape (M, M)
    :return t: numpy.array - shape (M, 1)
    """
    assert (
        source_points.shape == target_points.shape
    ), "source and target point sets must be of equal size"

    A: np.ndarray = source_points
    B: np.ndarray = target_points

    point_count: int = A.shape[0]
    point_dim: int = A.shape[1]

    # Calculate the mean point of the two point sets
    mu_a: np.ndarray = A.mean(axis=0)
    mu_b: np.ndarray = B.mean(axis=0)

    # Shape var_a = ()
    var_a: np.ndarray = np.square(A - mu_a).sum(axis=1).mean()

    # Shape cov_ab = (3, 3)
    cov_ab: np.ndarray = ((B - mu_b).T @ (A - mu_a)) / point_count

    # Expected shapes:   U = (3, 3), D = (3, 1), VT = (3, 3)
    U, D, VT = np.linalg.svd(cov_ab)
    S = np.eye(point_dim)

    if np.linalg.det(U) * np.linalg.det(VT) < 0:
        S[-1, -1] = -1

    scale: float = np.trace(np.diag(D) @ S) / var_a
    rotation: np.ndarray = U @ S @ VT
    translation: np.ndarray = mu_b - scale * rotation @ mu_a

    return RigidTransformation(scale, rotation, translation)
