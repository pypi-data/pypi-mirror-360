"""Module for functionality related to Hitnet disparity estimation model."""

from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import cv2
import numpy as np
import onnxruntime as onnxrt
import torch

from mynd.image import Image, PixelFormat, flip_image
from mynd.utils.containers import Pair

from .stereo_matcher import StereoMatcher


class SessionArgument(NamedTuple):
    """Class representing a session argument."""

    name: str
    shape: tuple
    type: type


@dataclass
class HitnetModel:
    """Class representing a Hitnet model."""

    session: onnxrt.InferenceSession

    @property
    def inputs(self) -> list[SessionArgument]:
        """Returns the inputs of the session."""
        arguments = self.session.get_inputs()
        return [
            SessionArgument(argument.name, tuple(argument.shape), argument.type)
            for argument in arguments
        ]

    @property
    def outputs(self) -> list[SessionArgument]:
        """Returns the inputs of the session."""
        arguments = self.session.get_outputs()
        return [
            SessionArgument(argument.name, tuple(argument.shape), argument.type)
            for argument in arguments
        ]

    @property
    def input_size(self) -> tuple[int, int]:
        """Returns the expected input size for the model as (H, W)."""
        tensor_argument: SessionArgument = self.inputs[0]
        batch, channels, height, width = tensor_argument.shape
        return (height, width)


def load_hitnet(path: Path) -> HitnetModel:
    """Loads a Hitnet model from an ONNX file."""

    if not path.exists():
        raise ValueError(f"model path does not exist: {path}")
    if not path.suffix == ".onnx":
        raise ValueError(f"model path is not an ONNX file: {path}")

    providers: list = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    sess_options: onnxrt.SessionOptions = onnxrt.SessionOptions()

    session: onnxrt.InferenceSession = onnxrt.InferenceSession(
        str(path),
        sess_options=sess_options,
        providers=providers,
    )

    # TODO: Add validation based on session input and output

    return HitnetModel(session=session)


def create_hitnet_matcher(path: Path) -> StereoMatcher:
    """Creates a Hitnet stereo matcher."""

    model: HitnetModel | str = load_hitnet(path)

    def match_stereo_hitnet(left: Image, right: Image) -> Pair[Image]:
        """Matches a pair of rectified stereo images with the Hitnet model."""
        return _compute_disparity(model, left, right)

    return match_stereo_hitnet


def _preprocess_images(
    model: HitnetModel, left: Image, right: Image
) -> tuple[np.ndarray, np.ndarray]:
    """Preprocess input images for HITNET."""

    assert left.dtype in [
        np.uint8,
        np.uint16,
        np.uint32,
    ], "invalid dtype for left image"
    assert right.dtype in [
        np.uint8,
        np.uint16,
        np.uint32,
    ], "invalid dtype for right image"

    # Convert left image to grayscale
    match left.pixel_format:
        case PixelFormat.RGB:
            left_array: np.ndarray = cv2.cvtColor(left.to_array(), cv2.COLOR_RGB2GRAY)
        case PixelFormat.BGR:
            left_array: np.ndarray = cv2.cvtColor(left.to_array(), cv2.COLOR_BGR2GRAY)
        case PixelFormat.GRAY:
            left_array: np.ndarray = left.to_array()
        case _:
            raise NotImplementedError(f"invalid image format: {left.pixel_format}")

    # Convert right image to grayscale
    match right.pixel_format:
        case PixelFormat.RGB:
            right_array: np.ndarray = cv2.cvtColor(right.to_array(), cv2.COLOR_RGB2GRAY)
        case PixelFormat.BGR:
            right_array: np.ndarray = cv2.cvtColor(right.to_array(), cv2.COLOR_BGR2GRAY)
        case PixelFormat.GRAY:
            right_array: np.ndarray = right.to_array()
        case _:
            raise NotImplementedError(f"invalid image format: {right.pixel_format}")

    assert len(model.inputs) == 1, f"invalid number of inputs: {len(model.inputs)}"
    assert len(model.outputs) == 1, f"invalid number of outputs: {len(model.outputs)}"

    height: int
    width: int
    height, width = model.input_size

    left_array: np.ndarray = cv2.resize(left_array, (width, height), cv2.INTER_AREA)
    right_array: np.ndarray = cv2.resize(right_array, (width, height), cv2.INTER_AREA)

    # Grayscale needs expansion to reach H,W,C.
    # Need to do that now because resize would change the shape.
    if left_array.ndim == 2:
        left_array: np.ndarray = np.expand_dims(left_array, axis=-1)
    if right_array.ndim == 2:
        right_array: np.ndarray = np.expand_dims(right_array, axis=-1)

    left_normalized: np.ndarray = left_array / np.iinfo(left_array.dtype).max
    right_normalized: np.ndarray = right_array / np.iinfo(right_array.dtype).max

    # -> H,W,C=2 or 6 , normalized to [0,1]
    tensor: np.ndarray = np.concatenate((left_normalized, right_normalized), axis=-1)
    # -> C,H,W
    tensor: np.ndarray = tensor.transpose(2, 0, 1)
    # -> B=1,C,H,W
    tensor = np.expand_dims(tensor, 0).astype(np.float32)

    return tensor


def _postprocess_disparity(
    disparity: np.ndarray, image: Image, flip: bool = False
) -> np.ndarray:
    """Postprocess the disparity map by resizing it to match the original image,
    adjusting the disparity with the width ratio, and optionally flipping the disparity
    horizontally."""

    # Squeeze disparity to a 2D array
    disparity: np.ndarray = np.squeeze(disparity)

    # Scale disparities by the width ratios between the original images and the disparity maps
    scale: float = float(image.width) / float(disparity.shape[1])
    disparity *= scale

    # Resize disparity maps to the original image sizes
    disparity: np.ndarray = cv2.resize(
        disparity, (image.width, image.height), cv2.INTER_AREA
    )

    # If enabled, flip disparity map around y-axis (horizontally)
    if flip:
        disparity: np.ndarray = cv2.flip(disparity, 1)

    return disparity


def _compute_disparity(model: HitnetModel, left: Image, right: Image) -> Pair[Image]:
    """Computes the disparity for a pair of stereo images. The images needs to be
    rectified prior to disparity estimation. Returns the left and right disparity as
    arrays with float32 values."""

    # Create tensor from flipped images to get left disparity
    flipped_left: Image = flip_image(left)
    flipped_right: Image = flip_image(right)

    tensor: np.ndarray = _preprocess_images(model, left, right)
    flipped_tensor: np.ndarray = _preprocess_images(model, flipped_right, flipped_left)

    left_outputs: list[np.ndarray] = model.session.run(
        ["reference_output_disparity"], {"input": tensor}
    )
    right_outputs: list[np.ndarray] = model.session.run(
        ["reference_output_disparity"], {"input": flipped_tensor}
    )

    # Since we estimate the right disparity from the flipped images, we need to flip the
    # right disparity map back to the same perspective as the original rigth image
    left_disparity: np.ndarray = _postprocess_disparity(
        left_outputs[0], left, flip=False
    )
    right_disparity: np.ndarray = _postprocess_disparity(
        right_outputs[0], right, flip=True
    )

    left_disparity_image: Image = Image.from_array(left_disparity, PixelFormat.X)
    right_disparity_image: Image = Image.from_array(right_disparity, PixelFormat.X)

    return Pair(first=left_disparity_image, second=right_disparity_image)
