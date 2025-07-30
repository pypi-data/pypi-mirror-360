"""Module to perform assimilation of camera references."""

import numpy as np
import polars as pl

from scipy.spatial.transform import Rotation

import mynd.schemas as schemas

from mynd.utils.log import logger

from .alignment import (
    RigidTransformation,
    align_points_arun,
    align_points_umeyama,
)
from .transforms import (
    convert_locations_geodetic2enu,
    convert_locations_enu2geodetic,
    convert_locations_geodetic2ned,
    convert_locations_ned2geodetic,
)


def assimilate_camera_references(
    cameras: list[schemas.CameraSchema],
) -> list[schemas.CameraSchema]:
    """Performs an assimilation between prior and aligned camera references."""

    prior_references: pl.DataFrame = _tabulate_camera_references_prior(cameras)
    aligned_references: pl.DataFrame = _tabulate_camera_references_aligned(cameras)

    # Assimilate camera references by using the
    assimilated_references: pl.DataFrame = _assimilate_camera_references_full_impl(
        prior_references,
        aligned_references,
    )

    references: dict[int, schemas.CameraSchema.ReferenceType] = (
        _parse_camera_references(assimilated_references)
    )

    assimilated_cameras: list[schemas.CameraSchema] = list()
    for camera in cameras:
        reference: schemas.CameraSchema.ReferenceType | None = references.get(camera.id)

        if reference is None:
            continue

        camera.assimilated_reference = reference
        assimilated_cameras.append(camera)

    return assimilated_cameras


def _parse_camera_references(
    table: pl.DataFrame,
) -> dict[int, schemas.CameraSchema.ReferenceType]:
    """Parse table rows as camera references."""
    references: dict[int, schemas.CameraSchema.ReferenceType] = dict()
    for row in table.iter_rows(named=True):
        camera_id: int | None = row.get("camera_id")

        if camera_id is None:
            continue

        reference: schemas.CameraSchema.ReferenceType = (
            schemas.CameraSchema.ReferenceType(
                epsg_code=4326,
                longitude=row.get("longitude"),
                latitude=row.get("latitude"),
                height=row.get("height"),
                yaw=row.get("yaw"),
                pitch=row.get("pitch"),
                roll=row.get("roll"),
            )
        )

        references[camera_id] = reference

    return references


def _tabulate_camera_references_prior(
    cameras: list[schemas.CameraSchema],
) -> pl.DataFrame:
    """Tabulates prior camera references."""
    return pl.DataFrame(
        [
            {
                "camera_id": camera.id,
                "camera_label": camera.label,
                "longitude": camera.prior_reference.longitude,
                "latitude": camera.prior_reference.latitude,
                "height": camera.prior_reference.height,
                "yaw": camera.prior_reference.yaw,
                "pitch": camera.prior_reference.pitch,
                "roll": camera.prior_reference.roll,
            }
            for camera in cameras
            if camera.prior_reference
        ]
    )


def _tabulate_camera_references_aligned(
    cameras: list[schemas.CameraSchema],
) -> pl.DataFrame:
    """Tabulates aligned camera references."""
    return pl.DataFrame(
        [
            {
                "camera_id": camera.id,
                "camera_label": camera.label,
                "longitude": camera.aligned_reference.longitude,
                "latitude": camera.aligned_reference.latitude,
                "height": camera.aligned_reference.height,
                "yaw": camera.aligned_reference.yaw,
                "pitch": camera.aligned_reference.pitch,
                "roll": camera.aligned_reference.roll,
            }
            for camera in cameras
            if camera.aligned_reference
        ]
    )


def _assimilate_camera_references_full_impl(
    reference_priors: pl.DataFrame,
    reference_estimates: pl.DataFrame,
) -> pl.DataFrame:
    """Assimilate reference priors and estimates. The assimilation process
    aligns prior locations to estimates, and uses the aligned priors to fill in
    missing location estimates."""

    GEODESIC_COLUMNS: list[str] = ["latitude", "longitude", "height"]
    CARTESIAN_COLUMNS: list[str] = ["north", "east", "down"]

    for column in GEODESIC_COLUMNS:
        assert column in reference_priors.columns, f"missing prior column: {column}"
        assert (
            column in reference_estimates.columns
        ), f"missing estimate column: {column}"

    # Get centre latitude and longitude
    center_latitude: float = reference_priors.select(pl.median("latitude")).item()
    center_longitude: float = reference_priors.select(pl.median("longitude")).item()
    center_height: float = 0.0

    # Remove old reference information
    reference_priors_base: pl.DataFrame = reference_priors.select(
        pl.exclude(["latitude", "longitude", "height", "yaw", "pitch", "roll"])
    )

    # Convert reference priors to NED
    reference_priors_ned: np.ndarray = convert_locations_geodetic2ned(
        reference_priors.select(GEODESIC_COLUMNS).to_numpy(),
        center_longitude=center_longitude,
        center_latitude=center_latitude,
        center_height=center_height,
    )

    # Convert reference estimates to ENU
    reference_estimates_ned: np.ndarray = convert_locations_geodetic2ned(
        reference_estimates.select(GEODESIC_COLUMNS).to_numpy(),
        center_longitude=center_longitude,
        center_latitude=center_latitude,
        center_height=center_height,
    )

    reference_priors_ned: pl.DataFrame = pl.from_numpy(
        reference_priors_ned, schema=CARTESIAN_COLUMNS
    )

    reference_estimates_ned: pl.DataFrame = pl.from_numpy(
        reference_estimates_ned, schema=CARTESIAN_COLUMNS
    )

    # Add cartesian coordinates to prior references as columns
    reference_priors: pl.DataFrame = pl.concat(
        [reference_priors, reference_priors_ned], how="horizontal"
    )
    reference_estimates: pl.DataFrame = pl.concat(
        [reference_estimates, reference_estimates_ned], how="horizontal"
    )

    matched_priors, matched_estimates = _match_references_by_column(
        reference_priors,
        reference_estimates,
        column="camera_id",
    )

    transformation: RigidTransformation = align_points_umeyama(
        matched_priors.select(CARTESIAN_COLUMNS).to_numpy(),
        matched_estimates.select(CARTESIAN_COLUMNS).to_numpy(),
    )

    # Correct prior locations
    updated_location_priors_ned: np.ndarray = _transform_locations(
        reference_priors.select(CARTESIAN_COLUMNS).to_numpy(),
        transformation,
    )

    # Correct prior attitudes
    updated_attitude_priors: np.ndarray = _transform_attitudes(
        reference_priors.select(["yaw", "pitch", "roll"]).to_numpy(),
        transformation,
    )

    # Convert updated locations priors from ENU to WGS84
    updated_location_priors_geo: np.ndarray = convert_locations_ned2geodetic(
        updated_location_priors_ned,
        center_longitude=center_longitude,
        center_latitude=center_latitude,
        center_height=center_height,
    )

    # Combine attributes, udpated locations, and update attitudes
    updated_reference_priors: pl.DataFrame = pl.concat(
        [
            reference_priors_base,
            pl.from_numpy(
                updated_location_priors_geo, schema=["latitude", "longitude", "height"]
            ),
            pl.from_numpy(updated_attitude_priors, schema=["yaw", "pitch", "roll"]),
        ],
        how="horizontal",
    )

    # Overwrite updated priors with estimates to obtain the assimilated references
    assimilated_references: pl.DataFrame = updated_reference_priors.update(
        reference_estimates, on="camera_id"
    )

    return assimilated_references


def _match_references_by_column(
    reference_priors: pl.DataFrame,
    reference_estimates: pl.DataFrame,
    column: str,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """TODO"""

    assert (
        column in reference_priors.columns
    ), f"missing column in reference priors: {column}"
    assert (
        column in reference_estimates.columns
    ), f"missing column in reference estimates: {column}"

    # Find common camera labels between prior and aligned references
    matching_labels: pl.DataFrame = (
        reference_priors.join(
            reference_estimates,
            on=column,
            how="inner",
        )
        .select(column)
        .unique()
    )

    # Select prior and estimated references from the matching labels
    matched_priors: pl.DataFrame = reference_priors.filter(
        pl.col(column).is_in(matching_labels.get_column(column))
    )
    matched_estimates: pl.DataFrame = reference_estimates.filter(
        pl.col(column).is_in(matching_labels.get_column(column))
    )

    return matched_priors, matched_estimates


def _transform_locations(
    locations: np.ndarray, transformation: RigidTransformation
) -> np.ndarray:
    """Transforms locations by applying a rigid-body transformation."""
    transformed_locations: np.ndarray = transformation.apply(locations)
    return transformed_locations


def _transform_attitudes(
    attitudes: np.ndarray, transformation: RigidTransformation
) -> np.ndarray:
    """Transforms attitudes by applying a rigid-body transformation."""
    common_rotation: Rotation = Rotation.from_matrix(transformation.rotation)
    attitudes: Rotation = Rotation.from_euler(seq="ZYX", angles=attitudes, degrees=True)

    # Apply the common rotation to the attitudes
    transformed_attitudes: np.ndarray = (common_rotation * attitudes).as_euler(
        seq="ZYX", degrees=True
    )

    # NOTE: Correct yaw angle to interval [0, 360], as Scipy uses [-180, 180]
    mask: np.ndarray = transformed_attitudes[:, 0] < 0.0
    transformed_attitudes[mask, 0] = 360.0 + transformed_attitudes[mask, 0]

    return transformed_attitudes
