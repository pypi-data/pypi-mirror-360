"""Module for stereo camera rectification."""

from dataclasses import dataclass
from typing import TypeAlias

import cv2
import numpy as np

import mynd.schemas as schemas

from mynd.image import Image
from mynd.utils.containers import Pair
from mynd.utils.log import logger

from .pixel_map import (
    PixelMap,
    compute_pixel_map,
    remap_image_pixels,
    invert_pixel_map,
)


PixelMapPair: TypeAlias = Pair[PixelMap]


def rectify_stereo_sensors(sensors: schemas.StereoSensorPairSchema) -> None:
    """Computes stereo rectified sensors and updates the rectified sensor
    components."""
    rectified_master: schemas.RectifiedSensorSchema
    rectified_slave: schemas.RectifiedSensorSchema
    rectified_master, rectified_slave = compute_stereo_rectified_sensors(
        sensors.master.sensor,
        sensors.slave.sensor,
    )

    # Update the rectified components of the sensors
    sensors.master.sensor.rectified = rectified_master
    sensors.slave.sensor.rectified = rectified_slave


def compute_stereo_rectified_sensors(
    master_sensor: schemas.SensorSchema,
    slave_sensor: schemas.SensorSchema,
) -> tuple[schemas.RectifiedSensorSchema, schemas.RectifiedSensorSchema]:
    """Computes the camera calibrations for a pair of rectified cameras."""

    assert isinstance(master_sensor, schemas.SensorSchema), "invalid master sensor type"
    assert isinstance(slave_sensor, schemas.SensorSchema), "invalid master sensor type"

    transforms: Transforms = _compute_stereo_rectifying_transforms(
        master_sensor, slave_sensor
    )

    resolution_master: tuple[int, int] = (
        master_sensor.calibration.width,
        master_sensor.calibration.height,
    )
    resolution_slave: tuple[int, int] = (
        slave_sensor.calibration.width,
        slave_sensor.calibration.height,
    )

    desired_resolution: tuple[int, int] = resolution_master

    affine_transform: np.ndarray = _compute_common_affine_transform(
        master_sensor.calibration.projection_matrix,  # intrinsic 1
        slave_sensor.calibration.projection_matrix,  # intrinsic 2
        transforms.homographies.first,  # homography 1
        transforms.homographies.second,  # homography 2
        resolution_master,  # resolution 1
        resolution_slave,  # resolution 2
        master_sensor.calibration.distortion_vector,  # distortion 1
        slave_sensor.calibration.distortion_vector,  # distortion 2
        desired_resolution,  # desired resolution - (width, height)
    )

    # Group all the transformations applied after rectification
    # These would be needed for 3D reconstrunction
    new_first_camera: np.ndarray = (
        affine_transform.dot(transforms.homographies.first)
        .dot(master_sensor.calibration.projection_matrix)
        .dot(master_sensor.rotation_matrix)
        .dot(transforms.rotation.T)
    )

    new_second_camera: np.ndarray = (
        affine_transform.dot(transforms.homographies.second)
        .dot(slave_sensor.calibration.projection_matrix)
        .dot(slave_sensor.rotation_matrix)
        .dot(transforms.rotation.T)
    )

    updated_camera_matrices: Pair[np.ndarray] = Pair(
        first=new_first_camera,
        second=new_second_camera,
    )

    master_calibration: schemas.CalibrationSchema = _create_camera_calibration(
        width=desired_resolution[0],
        height=desired_resolution[1],
        projection_matrix=updated_camera_matrices.first,
    )

    slave_calibration: schemas.CalibrationSchema = _create_camera_calibration(
        width=desired_resolution[0],
        height=desired_resolution[1],
        projection_matrix=updated_camera_matrices.second,
    )

    rectified_master_sensor: schemas.RectifiedSensorSchema = (
        schemas.RectifiedSensorSchema(
            label=f"{master_sensor.label}_rectified",
            width=desired_resolution[0],
            height=desired_resolution[1],
            location=np.zeros(3).tolist(),
            rotation=transforms.rotation.tolist(),
            calibration=master_calibration,
        )
    )

    baseline: float = np.linalg.norm(
        slave_sensor.location_vector - master_sensor.location_vector
    )

    rectified_slave_sensor: schemas.RectifiedSensorSchema = (
        schemas.RectifiedSensorSchema(
            label=f"{slave_sensor.label}_rectified",
            width=desired_resolution[0],
            height=desired_resolution[1],
            location=np.array([baseline, 0.0, 0.0]).tolist(),
            rotation=transforms.rotation.dot(slave_sensor.rotation_matrix.T).tolist(),
            calibration=slave_calibration,
        )
    )

    return rectified_master_sensor, rectified_slave_sensor


def compute_sensor_rectification_map(sensor: schemas.SensorSchema) -> PixelMap:
    """Computes the pixel map between an unrectified and rectified sensor."""

    assert sensor.is_rectified(), "sensor is not rectified"
    assert isinstance(sensor, schemas.SensorSchema), "invalid sensor type"

    target_size: tuple[int, int] = (
        sensor.rectified.calibration.width,
        sensor.rectified.calibration.height,
    )

    pixel_map: PixelMap = compute_pixel_map(
        sensor.calibration.projection_matrix,
        sensor.calibration.distortion_vector,
        sensor.rectified.rotation_matrix,
        sensor.rectified.calibration.projection_matrix,
        target_size,
    )

    return pixel_map


def compute_stereo_rectification_map(
    sensors: schemas.StereoSensorPairSchema,
) -> PixelMapPair:
    """Computes updated camera matrices and pixel maps based on the given stereo calibration
    and rectifying transforms."""
    assert isinstance(sensors, schemas.StereoSensorPairSchema), "invalid sensors type"
    assert sensors.master.is_rectified(), "master sensor is not rectified"
    assert sensors.slave.is_rectified(), "slave sensor is not rectified"

    # Recompute final maps considering fitting transformations too
    master_pixel_map: PixelMap = compute_sensor_rectification_map(sensors.master.sensor)
    slave_pixel_map: PixelMap = compute_sensor_rectification_map(sensors.slave.sensor)

    pixel_maps: Pair[PixelMap] = Pair(
        first=master_pixel_map,
        second=slave_pixel_map,
    )

    return pixel_maps


@dataclass(frozen=True)
class Transforms:
    """Class representing rectification transforms including a common
    rotation and homographies for the two cameras."""

    rotation: np.ndarray  # common rotation for the two cameras
    homographies: Pair[np.ndarray]  # transforms for the two camera


def _compute_stereo_rectifying_transforms(
    master_sensor: schemas.SensorSchema,
    slave_sensor: schemas.SensorSchema,
) -> Transforms:
    """
    Computes the rectifying transforms for a pair of stereo sensor using the
    standard OpenCV algorithm.
    Adopted from: https://github.com/decadenza/SimpleStereo/blob/master/simplestereo/_rigs.py
    """
    assert isinstance(master_sensor, schemas.SensorSchema), "invalid master sensor type"
    assert isinstance(slave_sensor, schemas.SensorSchema), "invalid slave sensor type"

    resolution: tuple[int, int] = (
        master_sensor.calibration.width,
        master_sensor.calibration.height,
    )

    first_rotation, second_rotation, _, _, _, _, _ = cv2.stereoRectify(
        master_sensor.calibration.projection_matrix,  # 3x3 master camera matrix
        master_sensor.calibration.distortion_vector,  # 5x1 master camera distortion
        slave_sensor.calibration.projection_matrix,  # 3x3 slave camera matrix
        slave_sensor.calibration.distortion_vector,  # 5x1 slave camera distortion
        resolution,  # resolution (width, height)
        slave_sensor.rotation_matrix,  # 3x3 rotation matrix from camera 1 to camera 2
        slave_sensor.location_vector,  # 3x1 translation vector from camera 1 to camera 2
        flags=0,
    )

    # OpenCV does not compute the rectifying homography, but a rotation in the object space.
    # R1 = Rnew * Rcam^{-1}
    # To get the homography:
    first_homography: np.ndarray = first_rotation.dot(
        np.linalg.inv(master_sensor.calibration.projection_matrix)
    )
    second_homography: np.ndarray = second_rotation.dot(
        np.linalg.inv(slave_sensor.calibration.projection_matrix)
    )

    homographies: Pair[np.ndarray] = Pair(
        first=first_homography, second=second_homography
    )

    # To get the common orientation, since the first camera has orientation as origin:
    # Rcommon = R1
    # It also can be retrieved from R2, cancelling the rotation of the second camera.
    # Rcommon = R2.dot(np.linalg.inv(rig.R))

    return Transforms(rotation=first_rotation, homographies=homographies)


def _create_camera_calibration(
    width: int,
    height: int,
    projection_matrix: np.ndarray,
    distortion_vector: np.ndarray = np.zeros(5, dtype=np.float32),
) -> schemas.CalibrationSchema:
    """Converts a camera matrix to a calibration."""
    assert projection_matrix.shape == (3, 3), "invalid projection matrix shape"
    assert distortion_vector.shape == (5,), "invalid distortion vector shape"

    assert projection_matrix.dtype in [
        np.float32,
        np.float64,
    ], f"invalid projection dtype: {projection_matrix.dtype}"
    assert distortion_vector.dtype in [
        np.float32,
        np.float64,
    ], f"invalid distortion dtype: {distortion_vector.dtype}"

    fx: float = projection_matrix[0, 0]
    fy: float = projection_matrix[1, 1]
    cx: float = projection_matrix[0, 2]
    cy: float = projection_matrix[1, 2]

    k1: float = distortion_vector[0]
    k2: float = distortion_vector[1]
    p1: float = distortion_vector[2]
    p2: float = distortion_vector[3]
    k3: float = distortion_vector[4]

    return schemas.CalibrationSchema(
        width=width,
        height=height,
        fx=fx,
        fy=fy,
        cx=cx,
        cy=cy,
        k1=k1,
        k2=k2,
        k3=k3,
        p1=p1,
        p2=p2,
    )


def _compute_common_affine_transform(
    first_camera_matrix: np.ndarray,
    second_camera_matrix: np.ndarray,
    first_homography: np.ndarray,
    second_homography: np.ndarray,
    first_dims: tuple[int, int],
    second_dims: tuple[int, int],
    first_distortion: np.ndarray | None = None,
    second_distortion: np.ndarray | None = None,
    desired_dims: tuple[int, int] | None = None,
) -> np.ndarray:
    """
    Compute affine tranformation to fit the rectified images into desidered dimensions.

    After rectification usually the image is no more into the original image bounds.
    One can apply any transformation that do not affect disparity to fit the image into boundaries.
    This function corrects flipped images too.
    The algorithm may fail if one epipole is too close to the image.

    Parameters
    ----------
    first_camera_matrix, second_camera_matrix : numpy.ndarray
        3x3 original camera matrices of intrinsic parameters.
    first_homography, second_homography : numpy.ndarray
        3x3 rectifying transforms.
    first_dims, second_dims : tuple
        Resolution of images as (width, height) tuple.
    first_distortion, second_distortion : numpy.ndarray, optional
        Distortion coefficients in the order followed by OpenCV. If None is passed, zero distortion is
        assumed.
    desired_dims : tuple, optional
        Resolution of destination images as (width, height) tuple (default to the first image
        resolution).

    Returns
    -------
    numpy.ndarray
        3x3 affine transformation to be used both for the first and for the second camera.
    """

    if first_distortion is not None:
        assert first_distortion.shape == (
            5,
        ), f"invalid distortion shape: {first_distortion.shape}"
    if second_distortion is not None:
        assert second_distortion.shape == (
            5,
        ), f"invalid distortion shape: {second_distortion.shape}"

    if desired_dims is None:
        desired_dims = first_dims

    desired_width: int
    desired_height: int
    desired_width, desired_height = desired_dims

    first_corners: ImageCorners = compute_image_corners(
        homography=first_homography,
        camera_matrix=first_camera_matrix,
        dimensions=first_dims,
        distortion=first_distortion,
    )

    second_corners: ImageCorners = compute_image_corners(
        homography=second_homography,
        camera_matrix=second_camera_matrix,
        dimensions=second_dims,
        distortion=second_distortion,
    )

    min_x1: float = first_corners.min[0]
    max_x1: float = first_corners.max[0]

    min_x2: float = second_corners.min[0]
    max_x2: float = second_corners.max[0]

    min_y: float = min(first_corners.min[1], second_corners.min[1])
    max_y: float = max(first_corners.max[1], second_corners.max[1])

    # Flip factor
    flip_x: int = 1
    flip_y: int = 1

    if first_corners.top_left[0] > first_corners.top_right[0]:
        flip_x: int = -1
    if first_corners.top_left[1] > first_corners.bottom_left[1]:
        flip_y: int = -1

    # Scale X (choose common scale X to best fit bigger image between left and right)
    if max_x2 - min_x2 > max_x1 - min_x1:
        scale_x: float = flip_x * desired_width / (max_x2 - min_x2)
    else:
        scale_x: float = flip_x * desired_width / (max_x1 - min_x1)

    # Scale Y (unique not to lose rectification)
    scale_y: float = flip_y * desired_height / (max_y - min_y)

    # Translation X (keep always at left border)
    if flip_x == 1:
        translation_x: float = -min(min_x1, min_x2) * scale_x
    else:
        translation_x: float = -min(max_x1, max_x2) * scale_x

    # Translation Y (keep always at top border)
    if flip_y == 1:
        translation_y: float = -min_y * scale_y
    else:
        translation_y: float = -max_y * scale_y

    # Final affine transformation
    affine: np.ndarray = np.array(
        [[scale_x, 0, translation_x], [0, scale_y, translation_y], [0, 0, 1]]
    )

    return affine


@dataclass(frozen=True)
class ImageCorners:
    """Class representing image corners."""

    top_left: tuple[float, float]  # corners[0,0] = [0,0]
    top_right: tuple[float, float]  # corners[1,0] = [dims[0]-1,0]
    bottom_right: tuple[float, float]  # corners[2,0] = [dims[0]-1,dims[1]-1]
    bottom_left: tuple[float, float]  # corners[3,0] = [0, dims[1]-1]

    @property
    def min(self) -> tuple[float, float]:
        """Returns the minimum x- and y-coordinate of the image corners."""
        minx: float = min(
            self.top_left[0],
            self.top_right[0],
            self.bottom_right[0],
            self.bottom_left[0],
        )
        miny: float = min(
            self.top_left[1],
            self.top_right[1],
            self.bottom_right[1],
            self.bottom_left[1],
        )
        return (minx, miny)

    @property
    def max(self) -> tuple[float, float]:
        """Returns the maximum x- and y-coordinate of the image corners."""
        maxx: float = max(
            self.top_left[0],
            self.top_right[0],
            self.bottom_right[0],
            self.bottom_left[0],
        )
        maxy: float = max(
            self.top_left[1],
            self.top_right[1],
            self.bottom_right[1],
            self.bottom_left[1],
        )
        return (maxx, maxy)


def compute_image_corners(
    homography: np.ndarray,
    camera_matrix: np.ndarray,
    dimensions: tuple[int, int],
    distortion: np.ndarray | None = None,
) -> ImageCorners:
    """Computes updated image corners locations based on a combined homography
    and undistortion transformation."""

    width: int
    height: int
    width, height = dimensions

    if distortion is None:
        distortion: np.ndarray = np.zeros(5)

    # Set image corners in the form requested by cv2.undistortPoints
    corners: np.ndarray = np.zeros((4, 1, 2), dtype=np.float32)

    # Initialize corners in order: top left, top right, bottom right, bottom left
    corners[0, 0] = [0, 0]
    corners[1, 0] = [width - 1, 0]
    corners[2, 0] = [width - 1, height - 1]
    corners[3, 0] = [0, height - 1]

    undistorted_corners: np.ndarray = cv2.undistortPoints(
        corners, camera_matrix, distortion, R=homography.dot(camera_matrix)
    )

    undistorted_corners: list[tuple] = [
        (x, y) for x, y in np.squeeze(undistorted_corners)
    ]

    return ImageCorners(*undistorted_corners)
