"""Package with visualization functionality for rendering 2D and 3D information.
The package is based on Open3D and OpenCV."""

from .geometry_renderers import (
    visualize_registration,
    visualize_registration_batch,
)


from .image_renderers import (
    WindowHandle,
    TrackbarData,
    create_window,
    render_image,
    destroy_window,
    destroy_all_windows,
    wait_key_input,
    StereoWindows,
    create_stereo_windows,
    render_stereo_geometry,
    create_stereo_geometry_color_image,
)


__all__ = [
    "visualize_registration",
    "visualize_registration_batch",
    "WindowHandle",
    "TrackbarData",
    "create_window",
    "render_image",
    "destroy_window",
    "destroy_all_windows",
    "wait_key_input",
    "StereoWindows",
    "create_stereo_windows",
    "render_stereo_geometry",
    "create_stereo_geometry_color_image",
]
