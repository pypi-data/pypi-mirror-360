"""Module for creating plotting figures."""

import plotly.graph_objects as go

from plotly.subplots import make_subplots

from mynd.geometry.transformations import decompose_rigid_transform
from mynd.geometry.transformations import rotation_matrix_to_euler
from mynd.pipelines.registration import RegistrationResult


def create_subplots(
    rows: int,
    cols: int,
    row_heights: list[int] = None,
    column_widths: list[int] = None,
) -> go.Figure:
    """Creates a figure with subplots with placeholder titles."""

    if not row_heights:
        row_heights = [1] * rows
    if not column_widths:
        column_widths = [1] * cols

    subplot_titles: tuple[str] = tuple(f"Plot {index}" for index in range(rows * cols))

    figure: go.Figure = make_subplots(
        rows=rows,
        cols=cols,
        row_heights=row_heights,
        column_widths=column_widths,
        subplot_titles=subplot_titles,
    )

    return figure


def trace_registration_result(
    result: RegistrationResult,
    name: str,
    legendgroup: int,
    color: str = "blue",
) -> dict[str, go.Trace]:
    """Creates graph objects for a registration result. The fitness, error, and correspondence count
    are plotted in addition to the transformation components."""

    scale, rotation, translation = decompose_rigid_transform(result.transformation)
    rotz, roty, rotx = rotation_matrix_to_euler(rotation, degrees=True)

    traces: dict = dict()

    traces["fitness"] = go.Bar(
        name=name,
        x=["Fitness"],
        y=[result.fitness],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=True,
    )

    traces["rmse"] = go.Bar(
        name=name,
        x=["RMSE"],
        y=[result.inlier_rmse],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=False,
    )

    traces["correspondences"] = go.Bar(
        name=name,
        x=["Correspondences"],
        y=[len(result.correspondence_set)],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=False,
    )

    traces["scale"] = go.Bar(
        name=name,
        x=["Scale"],
        y=[scale],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=False,
    )

    traces["rotation"] = go.Bar(
        name=name,
        x=["Rz", "Ry", "Rx"],
        y=[rotz, roty, rotx],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=False,
    )

    traces["translation"] = go.Bar(
        name=name,
        x=["Tx", "Ty", "Tz"],
        y=[translation[0], translation[1], translation[2]],
        marker_color=color,
        hoverinfo="x+y",
        legendgroup=legendgroup,
        showlegend=False,
    )

    return traces
