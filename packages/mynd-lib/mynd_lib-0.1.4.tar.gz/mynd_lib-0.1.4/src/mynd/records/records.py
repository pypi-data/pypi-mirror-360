"""Module for Mynds record models."""

import textwrap
import typing

from enum import StrEnum, auto
from typing import ClassVar, Optional, TypeAlias

import numpy as np

from sqlmodel import SQLModel, Column, Field, Relationship
from sqlmodel import Integer, Float, ARRAY, JSON, Enum


class ChunkGroupRecord(SQLModel, table=True):
    """Class representing chunk group record."""

    id: Optional[int] = Field(default=None, primary_key=True)
    label: str
    chunks: list["ChunkRecord"] = Relationship(back_populates="group")


class ChunkRecord(SQLModel, table=True):
    """Class representing a chunk record."""

    id: Optional[int] = Field(default=None, primary_key=True)
    label: str
    meta: dict = Field(default_factory=dict, sa_type=JSON)

    # Create a one-to-many mapping from a chunk group to multiple chunks
    group_id: Optional[int] = Field(default=None, foreign_key="chunkgrouprecord.id")
    group: Optional["ChunkGroupRecord"] = Relationship(back_populates="chunks")

    sensors: list["SensorRecord"] = Relationship(
        back_populates="chunk",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    cameras: list["CameraRecord"] = Relationship(
        back_populates="chunk",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    stereo_rigs: list["StereoRigRecord"] = Relationship(
        back_populates="chunk",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    stereo_sensor_pairs: list["StereoSensorRecord"] = Relationship(
        back_populates="chunk",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    stereo_camera_pairs: list["StereoCameraPairRecord"] = Relationship(
        back_populates="chunk",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class CalibrationBaseRecord(SQLModel):
    """Class representing a calibration base record.

    For reference:
    https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
    """

    width: int
    height: int
    fx: float
    fy: float
    cx: float  # optical center as per OpenCV
    cy: float  # optical center as per OpenCV
    k1: float  # radial distortion as per OpenCV
    k2: float  # radial distortion as per OpenCV
    k3: float  # radial distortion as per OpenCV
    p1: float  # tangential distortion as per OpenCV
    p2: float  # tangential distortion as per OpenCV


class CalibrationRecord(CalibrationBaseRecord, table=True):
    """Class representing a calibration record."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # Create a one-to-one mapping between a sensor and a calibration
    sensor: "SensorRecord" = Relationship(
        back_populates="calibration",
        sa_relationship_kwargs={"uselist": False, "lazy": "selectin"},
    )


class RectifiedCalibrationRecord(CalibrationBaseRecord, table=True):
    """Class representing a rectified calibration record."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # Create a one-to-one mapping between a rectified sensor and calibration
    sensor: "RectifiedSensorRecord" = Relationship(
        back_populates="calibration",
        sa_relationship_kwargs={"uselist": False, "lazy": "selectin"},
    )


"""
Sensor records:
 - SensorBaseRecord
 - SensorRecord
 - RectifiedSensorRecord
"""


class SensorBaseRecord(SQLModel):
    """Class representing a sensor base record."""

    label: str
    width: int
    height: int

    location: Optional[list[float]] = Field(
        default=None,
        sa_type=ARRAY(Float, dimensions=1),
    )
    rotation: Optional[list[list[float]]] = Field(
        default=None,
        sa_type=ARRAY(Float, dimensions=2),
    )


class SensorRecord(SensorBaseRecord, table=True):
    """Class representing a sensor record."""

    id: Optional[int] = Field(default=None, primary_key=True)

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="sensors")

    calibration_id: Optional[int] = Field(
        default=None, foreign_key="calibrationrecord.id"
    )
    calibration: Optional["CalibrationRecord"] = Relationship(
        back_populates="sensor",
        sa_relationship_kwargs={"uselist": False},
    )

    rectified_sensor_id: Optional[int] = Field(
        default=None, foreign_key="sensorrecord.id"
    )
    rectified_sensor: Optional["RectifiedSensorRecord"] = Relationship(
        back_populates="source_sensor",
        sa_relationship_kwargs={"uselist": False},
    )


class RectifiedSensorRecord(SensorBaseRecord, table=True):
    """Class representing a rectified sensor record."""

    id: Optional[int] = Field(default=None, primary_key=True)

    calibration_id: Optional[int] = Field(
        default=None, foreign_key="rectifiedcalibrationrecord.id"
    )
    calibration: Optional["RectifiedCalibrationRecord"] = Relationship(
        back_populates="sensor",
        sa_relationship_kwargs={"uselist": False},
    )

    source_sensor_id: Optional[int] = Field(default=None, foreign_key="sensorrecord.id")
    source_sensor: Optional["SensorRecord"] = Relationship(
        back_populates="rectified_sensor",
        sa_relationship_kwargs={"uselist": False},
    )


"""
Reference models:
 - BaseReferenceRecord
 - PriorReferenceRecord
 - AlignedReferenceRecord
 - AssimilatedReferenceRecord
"""


class BaseReferenceRecord(SQLModel):
    """Class representing a base reference record."""

    epsg_code: int
    longitude: float
    latitude: float
    height: float
    yaw: float
    pitch: float
    roll: float


class PriorReferenceRecord(BaseReferenceRecord, table=True):
    """Class representing a prior camera reference record."""

    id: Optional[int] = Field(default=None, primary_key=True)

    camera_id: Optional[int] = Field(
        default=None, foreign_key="camerarecord.id", unique=True
    )
    camera: Optional["CameraRecord"] = Relationship(
        back_populates="prior_reference",
        sa_relationship_kwargs={"lazy": "select"},
    )


class AlignedReferenceRecord(BaseReferenceRecord, table=True):
    """Class representing an aligned camera reference record."""

    id: Optional[int] = Field(default=None, primary_key=True)

    camera_id: Optional[int] = Field(
        default=None, foreign_key="camerarecord.id", unique=True
    )
    camera: Optional["CameraRecord"] = Relationship(
        back_populates="aligned_reference",
        sa_relationship_kwargs={"lazy": "select"},
    )


class AssimilatedReferenceRecord(BaseReferenceRecord, table=True):
    """Class representing an assimilated camera reference record."""

    id: Optional[int] = Field(default=None, primary_key=True)

    camera_id: Optional[int] = Field(
        default=None, foreign_key="camerarecord.id", unique=True
    )
    camera: Optional["CameraRecord"] = Relationship(
        back_populates="assimilated_reference",
        sa_relationship_kwargs={"lazy": "select"},
    )


class CameraRecord(SQLModel, table=True):
    """Class representing a camera record."""

    id: Optional[int] = Field(default=None, primary_key=True)
    label: str
    image_label: str
    meta: dict[str, typing.Any] = Field(
        default_factory=dict,
        sa_type=JSON,
    )

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="cameras")

    # Every camera has a sensor
    sensor_id: Optional[int] = Field(default=None, foreign_key="sensorrecord.id")
    sensor: Optional["SensorRecord"] = Relationship(
        sa_relationship_kwargs={
            "uselist": False,
            "primaryjoin": lambda: CameraRecord.sensor_id == SensorRecord.id,
        }
    )

    prior_reference: Optional["PriorReferenceRecord"] = Relationship(
        back_populates="camera",
        sa_relationship_kwargs={"lazy": "select"},
    )
    aligned_reference: Optional["AlignedReferenceRecord"] = Relationship(
        back_populates="camera",
        sa_relationship_kwargs={"lazy": "select"},
    )
    assimilated_reference: Optional["AssimilatedReferenceRecord"] = Relationship(
        back_populates="camera",
        sa_relationship_kwargs={"lazy": "select"},
    )


class PixelMapRecord(SQLModel, table=True):
    """Class representing a pixel map record. The pixel map value is stored as
    a HxWx2 array with the X- and Y-coordinate mapping, respectively."""

    id: Optional[int] = Field(default=None, primary_key=True)
    values: list[list[list[float]]] = Field(sa_type=ARRAY(Float, dimensions=3))

    @property
    def height(self) -> int:
        """Returns the height of the pixel map."""
        return len(self.values)

    @property
    def width(self) -> int:
        """Returns the width of the pixel map."""
        return len(self.values[0])

    def to_array(self) -> np.ndarray:
        """Returns the pixel map as a numpy array."""
        return np.array(self.values).astype(np.float32)


"""
Stereo record models:
 - StereoSensorRecord
 - StereoCameraPairRecord
 - StereoPixelMapRecord
 - StereoRigRecord
"""


class StereoSensorComponentRecord(SQLModel, table=True):
    """Class representing a stereo sensor component."""

    id: Optional[int] = Field(default=None, primary_key=True)

    sensor_id: Optional[int] = Field(
        default=None, foreign_key="sensorrecord.id", unique=True
    )
    sensor: SensorRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": textwrap.dedent("""
                StereoSensorComponentRecord.sensor_id == SensorRecord.id
            """)
        }
    )

    pixel_map_id: Optional[int] = Field(
        default=None, foreign_key="pixelmaprecord.id", unique=True
    )
    pixel_map: PixelMapRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": textwrap.dedent("""
                StereoSensorComponentRecord.pixel_map_id == PixelMapRecord.id
            """)
        }
    )

    @property
    def rectified_sensor(self) -> RectifiedSensorRecord | None:
        """Gets the rectified sensor record."""
        return self.sensor.rectified_sensor

    @rectified_sensor.setter
    def rectified_sensor(self, sensor: RectifiedSensorRecord) -> None:
        """Sets the rectified sensor record."""
        self.sensor.rectified_sensor = sensor

    def is_rectified(self) -> bool:
        """Returns true if the sensor component is rectified."""
        return self.rectified_sensor is not None

    def has_pixel_map(self) -> bool:
        """Returns true if the sensor component has a pixel map."""
        return self.pixel_map is not None


class StereoSensorRecord(SQLModel, table=True):
    """Class representing a stereo sensor record. The stereo sensor combines
    two stereo sensor components, one master and one slave."""

    Component: ClassVar[TypeAlias] = StereoSensorComponentRecord

    id: Optional[int] = Field(default=None, primary_key=True)

    # A stereo sensor is uniquely identified by the two sensor ids
    master_component_id: Optional[int] = Field(
        default=None, foreign_key="stereosensorcomponentrecord.id", unique=True
    )
    master_component: StereoSensorComponentRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": textwrap.dedent("""
                StereoSensorRecord.master_component_id == StereoSensorComponentRecord.id
            """)
        }
    )

    slave_component_id: Optional[int] = Field(
        default=None, foreign_key="stereosensorcomponentrecord.id", unique=True
    )
    slave_component: StereoSensorComponentRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": textwrap.dedent("""
                StereoSensorRecord.slave_component_id == StereoSensorComponentRecord.id
            """)
        }
    )

    stereo_rig_id: Optional[int] = Field(
        default=None, foreign_key="stereorigrecord.id", unique=True
    )
    stereo_rig: Optional["StereoRigRecord"] = Relationship(
        sa_relationship_kwargs={
            "uselist": False,
        }
    )

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="stereo_sensor_pairs")

    @property
    def master(self) -> StereoSensorComponentRecord | None:
        """Gets the master stereo sensor component."""
        return self.master_component

    @master.setter
    def master(self, component: StereoSensorComponentRecord) -> None:
        """Sets the master stereo sensor component."""
        self.master_component = component

    @property
    def slave(self) -> StereoSensorComponentRecord | None:
        """Gets the slave stereo sensor component."""
        return self.slave_component

    @slave.setter
    def slave(self, component: StereoSensorComponentRecord) -> None:
        """Sets the slave stereo sensor component."""
        self.slave_component = component

    def is_rectified(self) -> bool:
        """Returns true if the stereo sensor components are rectified."""
        if self.master is None or self.slave is None:
            return False
        else:
            return self.master.is_rectified() and self.slave.is_rectified()

    def has_pixel_maps(self) -> bool:
        """Returns true if the stereo sensor has pixel maps."""
        return self.master.has_pixel_map() and self.slave.has_pixel_map()


class StereoCameraPairRecord(SQLModel, table=True):
    """Class representing a stereo camera pair record. A stereo camera links two
    camera records. The stereo camera is identified by the ids of the two
    cameras, and is owned by a chunk."""

    id: Optional[int] = Field(default=None, primary_key=True)

    master_camera_id: int = Field(foreign_key="camerarecord.id", unique=True)
    master_camera: CameraRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": lambda: StereoCameraPairRecord.master_camera_id
            == CameraRecord.id
        }
    )

    slave_camera_id: int = Field(foreign_key="camerarecord.id", unique=True)
    slave_camera: CameraRecord = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": lambda: StereoCameraPairRecord.slave_camera_id
            == CameraRecord.id
        }
    )

    # TODO: Add validation that the two camera sensors are part of the sensor
    stereo_rig_id: Optional[int] = Field(default=None, foreign_key="stereorigrecord.id")
    stereo_rig: Optional["StereoRigRecord"] = Relationship(
        sa_relationship_kwargs={
            "uselist": False,
        }
    )

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="stereo_camera_pairs")

    @property
    def master(self) -> CameraRecord | None:
        """Gets the master camera."""
        return self.master_camera

    @master.setter
    def master(self, camera: CameraRecord) -> None:
        """Sets the master camera."""
        self.master_camera = camera

    @property
    def slave(self) -> CameraRecord | None:
        """Gets the slave camera."""
        return self.slave_camera

    @slave.setter
    def slave(self, camera: CameraRecord) -> None:
        """Sets the slave camera."""
        self.slave_camera = camera


class StereoRigRecord(SQLModel, table=True):
    """Class representing a stereo rig record. A stereo rig contains the sensor
    records for the physical sensor system, and the sensor records for the
    virtual/rectified sensor system, including the pixel map between the two
    sensor."""

    SensorComponent: ClassVar[TypeAlias] = StereoSensorComponentRecord
    SensorPair: ClassVar[TypeAlias] = StereoSensorRecord
    CameraPair: ClassVar[TypeAlias] = StereoCameraPairRecord
    PixelMap: ClassVar[TypeAlias] = PixelMapRecord

    id: Optional[int] = Field(default=None, primary_key=True)

    sensors: StereoSensorRecord = Relationship(
        back_populates="stereo_rig",
        sa_relationship_kwargs={
            "uselist": False,
        },
    )

    camera_pairs: list["StereoCameraPairRecord"] = Relationship(
        back_populates="stereo_rig"
    )

    chunk_id: Optional[int] = Field(default=None, foreign_key="chunkrecord.id")
    chunk: Optional["ChunkRecord"] = Relationship(back_populates="stereo_rigs")

    def is_rectified(self) -> bool:
        """Returns true if the stereo rig sensors are rectified."""
        return self.sensors.is_rectified()

    def has_pixel_maps(self) -> bool:
        """Returns true if the stereo rig has pixel maps."""
        return self.sensors.has_pixel_maps()
