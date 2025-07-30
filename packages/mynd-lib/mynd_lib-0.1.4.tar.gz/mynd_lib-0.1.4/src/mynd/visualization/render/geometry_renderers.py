"""Module for various point cloud visualization methods."""

import copy

import numpy as np
import open3d.visualization as vis

from mynd.geometry.point_cloud import PointCloud, PointCloudLoader


def create_visualizer(title: str = "Visualization") -> vis.Visualizer:
    """Creates a visualizer that can be used for drawing geometries."""

    visualizer = vis.Visualizer()
    visualizer.create_window(window_name=title)

    return visualizer


def visualize_registration(
    source: PointCloud,
    target: PointCloud,
    transformation: np.ndarray,
    source_color: list | None = None,
    target_color: list | None = None,
    title: str = "",
    window_width: int = 1024,
    window_height: int = 768,
) -> None:
    """Visualizes a pairwise registration result between two point clouds."""
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)

    if source_color:
        source_temp.paint_uniform_color(source_color)
    if target_color:
        target_temp.paint_uniform_color(target_color)

    source_temp.transform(transformation)

    vis.draw_geometries(
        geometry_list=[source_temp, target_temp],
        window_name=title,
        width=window_width,
        height=window_height,
    )


def visualize_registration_batch(
    storage: dict[int, dict],
    loaders: dict[int, PointCloudLoader],
    source_color: list = [0.60, 0.20, 0.20],
    target_color: list = [0.20, 0.20, 0.60],
) -> None:
    """Visualizes a batch of pairwise point cloud registrations."""
    for source, registrations in storage.items():
        source_cloud: PointCloud = loaders[source]().unwrap()

        for target, result in registrations.items():
            target_cloud: PointCloud = loaders[target]().unwrap()

            visualize_registration(
                source=source_cloud,
                target=target_cloud,
                transformation=result.transformation,
                source_color=source_color,
                target_color=target_color,
                title=f"Source: {source}, target: {target}",
            )
