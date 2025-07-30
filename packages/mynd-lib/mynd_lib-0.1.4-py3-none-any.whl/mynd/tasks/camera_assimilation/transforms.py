"""Module for transforming locations between coordinate reference systems."""

import numpy as np
import pymap3d as pm


def _convert_location_geodetic2enu(
    latitude: float,
    longitude: float,
    height: float,
    *,
    center_latitude: float,
    center_longitude: float,
    center_height: float,
) -> tuple[float, float, float]:
    """Converts a row to ENU."""
    east, north, up = pm.enu.geodetic2enu(
        lat=latitude,
        lon=longitude,
        h=height,
        lat0=center_latitude,
        lon0=center_longitude,
        h0=center_height,
        deg=True,
    )
    return east, north, up


def convert_locations_geodetic2enu(
    locations: np.ndarray,
    *,
    center_longitude: float,
    center_latitude: float,
    center_height: float = 0.0,
) -> np.ndarray:
    """Converts locations from Geodetic (WGS84) to East-North-Up."""
    converted_locations: list[tuple] = [
        _convert_location_geodetic2enu(
            latitude=location[0],
            longitude=location[1],
            height=location[2],
            center_longitude=center_longitude,
            center_latitude=center_latitude,
            center_height=center_height,
        )
        for location in locations
    ]
    return np.array(converted_locations)


def _convert_location_enu2geodetic(
    east: float,
    north: float,
    up: float,
    center_longitude: float,
    center_latitude: float,
    center_height: float,
) -> tuple[float, float, float]:
    """Converts a row"""
    latitude, longitude, height = pm.enu.enu2geodetic(
        e=east,
        n=north,
        u=up,
        lat0=center_latitude,
        lon0=center_longitude,
        h0=center_height,
        deg=True,
    )
    return latitude, longitude, height


def convert_locations_enu2geodetic(
    locations: np.ndarray,
    *,
    center_longitude: float,
    center_latitude: float,
    center_height: float = 0.0,
) -> np.ndarray:
    """TODO"""
    converted_locations: list[tuple] = [
        _convert_location_enu2geodetic(
            east=location[0],
            north=location[1],
            up=location[2],
            center_longitude=center_longitude,
            center_latitude=center_latitude,
            center_height=center_height,
        )
        for location in locations
    ]
    return np.array(converted_locations)


def _convert_location_geodetic2ned(
    latitude: float,
    longitude: float,
    height: float,
    *,
    center_longitude: float,
    center_latitude: float,
    center_height: float = 0.0,
) -> tuple[float, float, float]:
    """Converts a location from geodetic to North-East-Down."""
    north, east, down = pm.ned.geodetic2ned(
        lat=latitude,
        lon=longitude,
        h=height,
        lat0=center_latitude,
        lon0=center_longitude,
        h0=center_height,
        deg=True,
    )
    return north, east, down


def convert_locations_geodetic2ned(
    locations: np.ndarray,
    *,
    center_longitude: float,
    center_latitude: float,
    center_height: float = 0.0,
) -> np.ndarray:
    """Converts locations from Geodetic (WGS84) to North-East-Down."""
    converted_locations: list[tuple] = [
        _convert_location_geodetic2ned(
            latitude=location[0],
            longitude=location[1],
            height=location[2],
            center_longitude=center_longitude,
            center_latitude=center_latitude,
            center_height=center_height,
        )
        for location in locations
    ]
    return np.array(converted_locations)


def _convert_location_ned2geodetic(
    north: float,
    east: float,
    down: float,
    *,
    center_longitude: float,
    center_latitude: float,
    center_height: float = 0.0,
) -> tuple[float, float, float]:
    """Converts a location from North-East-Down to Geodetic."""
    latitude, longitude, height = pm.ned.ned2geodetic(
        n=north,
        e=east,
        d=down,
        lat0=center_latitude,
        lon0=center_longitude,
        h0=center_height,
        deg=True,
    )
    return latitude, longitude, height


def convert_locations_ned2geodetic(
    locations: np.ndarray,
    *,
    center_longitude: float,
    center_latitude: float,
    center_height: float = 0.0,
) -> np.ndarray:
    """Converts locations from NED to Geodetic.

    :arg locations: Nx3 array of [north, east, down]
    :return: Nx3 array of [latitude, longitude, height]
    """
    converted_locations: list[tuple] = [
        _convert_location_ned2geodetic(
            north=location[0],
            east=location[1],
            down=location[2],
            center_longitude=center_longitude,
            center_latitude=center_latitude,
            center_height=center_height,
        )
        for location in locations
    ]
    return np.array(converted_locations)
