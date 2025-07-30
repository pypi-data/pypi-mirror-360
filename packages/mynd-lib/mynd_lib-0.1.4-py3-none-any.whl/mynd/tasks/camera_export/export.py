"""Module for exporting camera references."""

from pathlib import Path
from typing import Any

import polars as pl

import mynd.schemas as schemas

from mynd.config import write_config
from mynd.utils.log import logger


def export_cameras(path: Path, cameras: list[schemas.CameraSchema]) -> Path:
    """Export a collection of cameras to file."""

    camera_data: list[dict] = [camera.model_dump() for camera in cameras]
    result: Path | str = write_config(path, camera_data)

    if isinstance(result, str):
        logger.error(result)
        raise IOError(result)

    return result


def export_stereo_cameras(
    path: Path, stereo_cameras: list[schemas.StereoCameraPairSchema]
) -> Path:
    """Exports a collection of stereo cameras to file."""

    stereo_camera_data: list[dict] = [
        stereo_camera.model_dump() for stereo_camera in stereo_cameras
    ]
    result: Path | str = write_config(path, stereo_camera_data)

    if isinstance(result, str):
        logger.error(result)
        raise IOError(result)

    return result


def tabularize_cameras(cameras: list[schemas.CameraSchema]) -> pl.DataFrame:
    """Tabularizes a collection of cameras."""

    rows: list[dict[str, Any]] = list()
    for camera in cameras:
        row: dict[str, Any] = {
            "camera_id": camera.id,
            "camera_label": camera.label,
            "image_label": camera.image_label,
            "readings": camera.readings,
            "sensor_id": camera.sensor.id,
        }

        if camera.interpolated_reference is not None:
            row.update(
                {
                    "latitude": camera.interpolated_reference.latitude,
                    "longitude": camera.interpolated_reference.longitude,
                    "height": camera.interpolated_reference.height,
                    "yaw": camera.interpolated_reference.yaw,
                    "pitch": camera.interpolated_reference.pitch,
                    "roll": camera.interpolated_reference.roll,
                }
            )

        rows.append(row)

    return pl.from_dicts(rows)


def tabularize_stereo_cameras(
    stereo_cameras: list[schemas.StereoCameraPairSchema],
) -> pl.DataFrame:
    """Tabularizes a collection of stereo cameras."""

    rows: list[dict] = list()
    for stereo_camera in stereo_cameras:
        assert (
            stereo_camera.master.interpolated_reference is not None
        ), "missing interpolated reference for master camera"
        common_fields: dict[str, Any] = _get_stereo_common_fields(stereo_camera)
        master_fields: dict[str, Any] = _get_camera_fields(stereo_camera.master)
        slave_fields: dict[str, Any] = _get_camera_fields(stereo_camera.slave)

        reference_fields: dict[str, Any] = _get_reference_fields(
            stereo_camera.master.interpolated_reference
        )

        master_fields: dict[str, Any] = {
            f"master.{key}": value for key, value in master_fields.items()
        }
        slave_fields: dict[str, Any] = {
            f"slave.{key}": value for key, value in slave_fields.items()
        }

        row: dict = common_fields | master_fields | slave_fields | reference_fields
        rows.append(row)

    return pl.from_dicts(rows)


def _get_stereo_common_fields(
    stereo_camera: schemas.StereoCameraPairSchema,
) -> dict[str, Any]:
    """Retrieves common fields for a stereo camera."""
    return {
        "stereo_camera_id": stereo_camera.id,
        "stereo_rig_id": stereo_camera.stereo_rig.id,
    }


def _get_camera_fields(camera: schemas.CameraSchema) -> dict[str, Any]:
    """Retrieves selected fields from a stereo camera master."""
    return {
        "camera_id": camera.id,
        "camera_label": camera.label,
        "image_label": camera.image_label,
        "readings": camera.readings,
    }


def _get_reference_fields(
    reference: schemas.CameraSchema.ReferenceType,
) -> dict[str, Any]:
    """Retrieves fields from a camera reference."""
    return {
        "latitude": reference.latitude,
        "longitude": reference.longitude,
        "height": reference.height,
        "yaw": reference.yaw,
        "pitch": reference.pitch,
        "roll": reference.roll,
    }
