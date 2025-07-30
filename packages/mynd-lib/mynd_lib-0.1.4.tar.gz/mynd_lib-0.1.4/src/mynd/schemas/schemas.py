"""Module for mynds schema models."""

from collections.abc import Callable
from typing import ClassVar, Optional, TypeAlias, Self

import numpy as np

from sqlmodel import SQLModel, Field


class ChunkGroupSchema(SQLModel):
    """Class representing a chunk group schema."""

    id: int | None = Field(default=None)
    label: str

    chunks: list["ChunkSchema"] = Field(default_factory=list)


class ChunkSchema(SQLModel):
    """Class representing a chunk schema."""

    id: int | None = Field(default=None)
    label: str
    meta: dict = Field(default_factory=dict)

    sensors: list["SensorSchema"] = Field(default_factory=list)
    cameras: list["CameraSchema"] = Field(default_factory=list)

    stereo_rigs: list["StereoRigSchema"] = Field(default_factory=list)
    stereo_sensor_pairs: list["StereoSensorPairSchema"] = Field(default_factory=list)
    stereo_camera_pairs: list["StereoCameraPairSchema"] = Field(default_factory=list)


class CalibrationSchema(SQLModel):
    """Class representing a calibration schema."""

    id: int | None = Field(default=None)
    width: int
    height: int
    fx: float
    fy: float
    cx: float
    cy: float
    k1: float
    k2: float
    k3: float
    p1: float
    p2: float

    @property
    def focal_length(self) -> float:
        """Returns the focal length of the calibration."""
        return self.fx

    @property
    def projection_matrix(self) -> np.ndarray:
        """Returns the calibration projection matrix."""
        return np.array(
            [[self.fx, 0.0, self.cx], [0.0, self.fy, self.cy], [0.0, 0.0, 1.0]]
        )

    @property
    def distortion_vector(self) -> np.ndarray:
        """Returns the calibration distortion vector."""
        return np.array([self.k1, self.k2, self.p1, self.p2, self.k3])


class SensorBaseSchema(SQLModel):
    """Class representing a sensor base schema."""

    id: int | None = Field(default=None)
    label: str
    width: int
    height: int

    location: list[float] | None = Field(default=None)
    rotation: list[list[float]] | None = Field(default=None)

    calibration: CalibrationSchema | None = Field(default=None)

    def __hash__(self) -> hash:
        """Returns a hash for the object."""
        return hash(self.id)

    @property
    def location_vector(self) -> np.ndarray | None:
        """Returns the sensor location as a numpy array."""
        if not self.location:
            return None
        return np.array(self.location)

    @property
    def rotation_matrix(self) -> np.ndarray | None:
        """Returns the sensor rotation as a numpy array."""
        if not self.rotation:
            return None
        return np.array(self.rotation)


class RectifiedSensorSchema(SensorBaseSchema):
    """Class representing a rectified sensor schema."""

    pass


class SensorSchema(SensorBaseSchema):
    """Class representing a sensor schema."""

    rectified_sensor: Optional[RectifiedSensorSchema] = Field(default=None)

    @property
    def rectified(self) -> RectifiedSensorSchema | None:
        """Gets the rectified sensor."""
        return self.rectified_sensor

    @rectified.setter
    def rectified(self, sensor: RectifiedSensorSchema) -> None:
        """Sets the rectified sensor."""
        self.rectified_sensor = sensor

    def is_rectified(self) -> bool:
        """Returns true if the sensor is rectified."""
        return self.rectified_sensor is not None


class ReferenceSchema(SQLModel):
    """Class representing a reference schema."""

    id: int | None = Field(default=None)
    epsg_code: int

    longitude: float
    latitude: float
    height: float

    yaw: float
    pitch: float
    roll: float

    @property
    def location_vector(self) -> np.ndarray:
        """Returns the reference location as a numpy array."""
        return np.array([self.longitude, self.latitude, self.height])

    @property
    def rotation_vector(self) -> np.ndarray:
        """Return the reference rotation as a numpy array."""
        return np.array([self.yaw, self.pitch, self.roll])


class CameraSchema(SQLModel):
    """Class representing a camera schema."""

    SensorType: ClassVar[TypeAlias] = SensorSchema
    ReferenceType: ClassVar[TypeAlias] = ReferenceSchema

    id: int | None = Field(default=None)
    label: str
    image_label: str
    meta: dict = Field(default_factory=dict)

    sensor: SensorSchema
    prior_reference: ReferenceSchema | None = Field(default=None)
    aligned_reference: ReferenceSchema | None = Field(default=None)
    assimilated_reference: ReferenceSchema | None = Field(default=None)


class PixelMapSchema(SQLModel):
    """Class representing a pixel map schema. The pixel maps is represented as
    floating point lists of shape HxWx2."""

    id: int | None = Field(default=None)
    values: list[list[list[float]]]

    @property
    def shape(self) -> tuple[int, ...]:
        """Returns the shape of the pixel map."""
        return self.to_array().shape

    @property
    def height(self) -> int:
        """Returns the height of the pixel map."""
        return self.shape[0]

    @property
    def width(self) -> int:
        """Returns the width of the pixel map."""
        return self.shape[1]

    @property
    def x(self) -> np.ndarray:
        """Returns the x component of the pixel map."""
        return self.to_array()[:, :, 0]

    @property
    def y(self) -> np.ndarray:
        """Returns the y component of the pixel map."""
        return self.to_array()[:, :, 1]

    def to_array(self) -> np.ndarray:
        """Returns the pixel map as an array."""
        return np.array(self.values).astype(np.float32)


class StereoSensorComponentSchema(SQLModel):
    """Class representing a stereo sensor component."""

    id: int | None = Field(default=None)
    sensor: SensorSchema

    @property
    def rectified_sensor(self) -> RectifiedSensorSchema | None:
        """Gets the rectified sensor record."""
        return self.sensor.rectified_sensor

    @rectified_sensor.setter
    def rectified_sensor(self, sensor: RectifiedSensorSchema) -> None:
        """Sets the rectified sensor record."""
        self.sensor.rectified_sensor = sensor

    def is_rectified(self) -> bool:
        """Returns true if the stereo sensor component is rectified."""
        return self.sensor.rectified is not None


class StereoSensorPairSchema(SQLModel):
    """Class representing a stereo sensor pair schema."""

    Component: ClassVar[TypeAlias] = StereoSensorComponentSchema

    id: int | None = Field(default=None)
    master_component: Component
    slave_component: Component

    @property
    def master(self) -> Component:
        """Gets the master component."""
        return self.master_component

    @master.setter
    def master(self, component: Component) -> None:
        """Sets the master component."""
        self.master_component = component

    @property
    def slave(self) -> Component:
        """Gets the slave component."""
        return self.slave_component

    @slave.setter
    def slave(self, component: Component) -> None:
        """Sets the slave component."""
        self.slave_component = component

    @property
    def baseline(self) -> float:
        """Returns the baseline between the master and slave sensor."""
        relative_location: np.ndarray = (
            self.slave.sensor.location_vector - self.master.sensor.location_vector
        )
        return np.linalg.norm(relative_location)


class StereoCameraPairSchema(SQLModel):
    """Class representing a stereo camera pair schema."""

    id: int | None = Field(default=None)
    master: CameraSchema
    slave: CameraSchema
    stereo_rig: Optional["StereoRigSchema"] = Field(default=None)


class StereoPixelMapSchema(SQLModel):
    """Class representing a pixel map pair schema."""

    id: int | None = Field(default=None)
    master: PixelMapSchema
    slave: PixelMapSchema


class StereoRigBase(SQLModel):
    """Class representing a stereo rig base."""

    # Define class vars with type aliases for ease of access
    SensorComponent: ClassVar[TypeAlias] = StereoSensorComponentSchema
    SensorPair: ClassVar[TypeAlias] = StereoSensorPairSchema
    CameraPair: ClassVar[TypeAlias] = StereoCameraPairSchema
    PixelMapPair: ClassVar[TypeAlias] = StereoPixelMapSchema

    id: int | None = Field(default=None)
    sensors: StereoSensorPairSchema


class StereoRigSchema(StereoRigBase):
    """Class representing a stereo rig schema without pixel maps."""

    pass


class StereoRigWithMapsSchema(StereoRigBase):
    """Class representing a stereo rig schema with pixel maps"""

    pixel_maps: StereoPixelMapSchema | None = Field(default=None)
