"""Module for point cloud types."""

from collections.abc import Callable
from typing import TypeAlias

import open3d


PointCloud: TypeAlias = open3d.geometry.PointCloud
PointCloudLoader: TypeAlias = Callable[[None], PointCloud | str]
PointCloudProcessor = Callable[[PointCloud], PointCloud]
