"""Module for full registration methods."""

from typing import TypeVar

import numpy as np
import open3d

import open3d.pipelines.registration as reg

from .types import RegistrationResult


Key: TypeVar = TypeVar("Key")


def build_pose_graph(
    results: dict[Key, dict[Key, RegistrationResult]],
) -> reg.PoseGraph:
    """Builds a pose graph from registered point clouds."""

    odometry: np.ndarray = np.identity(4)

    pose_graph: reg.PoseGraph = reg.PoseGraph()
    pose_graph.nodes.append(reg.PoseGraphNode(odometry))

    for source_id, registrations in results.items():
        for target_id, result in registrations.items():
            if target_id == source_id + 1:  # odometry case
                odometry: np.ndarray = np.dot(result.transformation, odometry)

                pose_graph.nodes.append(
                    reg.PoseGraphNode(
                        np.linalg.inv(odometry),
                    )
                )
                pose_graph.edges.append(
                    reg.PoseGraphEdge(
                        source_id,
                        target_id,
                        result.transformation,
                        result.information,
                        uncertain=False,
                    )
                )
            else:  # loop closure case
                pose_graph.edges.append(
                    reg.PoseGraphEdge(
                        source_id,
                        target_id,
                        result.transformation,
                        result.information,
                        uncertain=True,
                    )
                )

    return pose_graph


def optimize_pose_graph(
    pose_graph: reg.PoseGraph,
    correspondence_distance: float,
    prune_threshold: float,
    preference_loop_closure: float,
    reference_node: int = -1,
) -> reg.PoseGraph:
    """Optimizes a pose graph by optimizing and pruning graph edges."""

    method = reg.GlobalOptimizationLevenbergMarquardt()

    criteria = reg.GlobalOptimizationConvergenceCriteria()

    option = reg.GlobalOptimizationOption(
        max_correspondence_distance=correspondence_distance,
        edge_prune_threshold=prune_threshold,
        preference_loop_closure=preference_loop_closure,
        reference_node=reference_node,
    )

    reg.global_optimization(
        pose_graph,
        method,
        criteria,
        option,
    )

    return pose_graph
