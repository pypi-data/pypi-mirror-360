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

    sensors: list["SensorSchema"] = Field(default_factory=list)
    cameras: list["CameraSchema"] = Field(default_factory=list)

    stereo_rigs: list["StereoRigSchema"] = Field(default_factory=list)
    stereo_sensor_pairs: list["StereoSensorPairSchema"] = Field(default_factory=list)
    stereo_camera_pairs: list["StereoCameraPairSchema"] = Field(default_factory=list)

    camera_tracks: list["CameraTrackSchema"] = Field(default_factory=list)
    stereo_camera_tracks: list["StereoCameraTrackSchema"] = Field(default_factory=list)


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


class SensorSchema(SQLModel):
    """Class representing a sensor schema."""

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

    id: int | None = Field(default=None)
    label: str
    image_label: str
    readings: dict = Field(default_factory=dict)

    sensor: SensorSchema
    prior_reference: ReferenceSchema | None = Field(default=None)
    aligned_reference: ReferenceSchema | None = Field(default=None)
    interpolated_reference: ReferenceSchema | None = Field(default=None)


class CameraTrackSchema(SQLModel):
    """Class representing a camera track schema."""

    id: Optional[int] = Field(default=None)
    cameras: list[CameraSchema] = Field(default=list)


class PixelMapSchema(SQLModel):
    """Class representing a pixel map schema. The pixel maps is represented as
    floating point lists of shape HxWx2."""

    values: list[list[list[float]]]

    @property
    def height(self) -> int:
        """Returns the height of the pixel map."""
        return len(self.values)

    @property
    def width(self) -> int:
        """Returns the width of the pixel map."""
        return len(self.values[0])

    def to_array(self) -> np.ndarray:
        """Returns the pixel map as an array."""
        return np.array(self.values).astype(np.float32)


class StereoSensorPairSchema(SQLModel):
    """Class representing a stereo sensor pair schema."""

    id: int | None = Field(default=None)
    master: SensorSchema
    slave: SensorSchema

    @property
    def baseline(self) -> float:
        """Returns the baseline between the master and slave sensor."""
        relative_location: np.ndarray = (
            self.slave.location_vector - self.master.location_vector
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
    SensorPair: ClassVar[TypeAlias] = StereoSensorPairSchema
    CameraPair: ClassVar[TypeAlias] = StereoCameraPairSchema
    PixelMapPair: ClassVar[TypeAlias] = StereoPixelMapSchema

    id: int | None = Field(default=None)
    sensors: StereoSensorPairSchema
    sensors_rectified: StereoSensorPairSchema | None = Field(default=None)


class StereoRigSchema(StereoRigBase):
    """Class representing a stereo rig schema without pixel maps."""

    pass


class StereoRigWithMapsSchema(StereoRigBase):
    """Class representing a stereo rig schema with pixel maps"""

    pixel_maps: StereoPixelMapSchema | None = Field(default=None)


class StereoCameraTrackSchema(SQLModel):
    """Class representing a stereo camera track."""

    id: Optional[int] = Field(default=None)
    camera_pairs: list[StereoCameraPairSchema] = Field(default_factory=list)

    def sort_by(self: Self, key: Callable) -> list[StereoCameraPairSchema]:
        """Sorts the cameras in the track."""
        self.camera_pairs = sorted(self.camera_pairs, key=key)
        return self.camera_pairs
