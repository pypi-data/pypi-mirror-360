"""Package for stereo vision, including stereo matching, range and normal map
estimation, and geometric image transformations."""

from .hitnet import create_hitnet_matcher

# NOTE: Consider moving to image module
from .pixel_map import (
    PixelMap,
    compute_pixel_map,
    invert_pixel_map,
    remap_image_pixels,
)

from .range_map import (
    compute_ranges_from_disparities,
    compute_points_from_ranges,
    compute_normals_from_ranges,
    fill_range_map_dilation,
)

from .stereo_geometry import (
    StereoGeometry,
    compute_stereo_geometry,
    compute_stereo_range_maps,
    distort_stereo_geometry,
)

from .stereo_matcher import StereoMatcher

from .stereo_rectification import (
    compute_sensor_rectification_map,
    compute_stereo_rectification_map,
    compute_stereo_rectified_sensors,
    rectify_stereo_sensors,
)


__all__ = [
    "create_hitnet_matcher",
    # ...
    "PixelMap",
    "compute_pixel_map",
    "invert_pixel_map",
    "remap_image_pixels",
    # ...
    "PointCloud",
    "PointCloudLoader",
    "PointCloudProcessor",
    # ...
    "downsample_point_cloud",
    "estimate_point_cloud_normals",
    "create_downsampler",
    "create_normal_estimator",
    # ...
    "compute_range_from_disparity",
    "compute_points_from_range",
    "compute_normals_from_range",
    "fill_range_map_dilation",
    # ...
    "StereoGeometry",
    "compute_stereo_geometry",
    "compute_stereo_range_maps",
    "distort_stereo_geometry",
    # ...
    "StereoMatcher",
    # ...
    "compute_sensor_rectification_map",
    "compute_stereo_rectification_map",
    "compute_stereo_rectified_sensors",
    "rectify_stereo_sensors",
]
