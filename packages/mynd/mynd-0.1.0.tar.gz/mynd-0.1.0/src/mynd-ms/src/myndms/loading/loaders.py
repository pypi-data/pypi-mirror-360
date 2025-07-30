"""Module for database loaders."""

from dataclasses import dataclass, field
from itertools import groupby
from pathlib import Path

import Metashape as ms

import mynd.models.record as records

from mynd.database import Engine, Session
from mynd.models.record import ChunkRecord, ChunkGroupRecord
from mynd.models.record import CameraRecord, SensorRecord, StereoRigRecord
from mynd.utils.log import logger

from myndms.helpers import (
    StereoGroup,
    get_stereo_groups,
)

from .converters import (
    convert_sensor_to_orm,
    convert_camera_to_orm,
)


@dataclass
class DatabaseLoading:
    """Facade class for data types related to database loading."""

    @dataclass(frozen=True)
    class ChunkBuildState:
        """Class representing a state when loading chunks into a database."""

        sensors: dict[ms.Sensor, SensorRecord] = field(default_factory=dict)
        cameras: dict[ms.Camera, CameraRecord] = field(default_factory=dict)

        stereo_rigs: list[StereoRigRecord] = field(default_factory=list)
        stereo_sensor_pairs: list[StereoRigRecord.SensorPair] = field(
            default_factory=list
        )
        stereo_camera_pairs: list[StereoRigRecord.CameraPair] = field(
            default_factory=list
        )


def load_document_database(
    session: Session, document: ms.Document, group_label: str = ""
) -> ChunkGroupRecord:
    """Loads data from a document to a database using Mynds ORM."""

    assert session is not None, "invalid engine"
    assert document is not None, "invalid document"

    if not group_label:
        group_label: str = Path(document.path).stem

    chunk_group_model: ChunkGroupRecord = _build_chunk_group_model(
        session, document, group_label
    )

    session.add(chunk_group_model)
    session.commit()
    session.refresh(chunk_group_model)

    return chunk_group_model


def _build_chunk_group_model(
    session: Session, document: ms.Document, group_label: str
) -> ChunkGroupRecord:
    """Builds a chunk group model for all the chunks in a Metashape document.
    Disabled chunks are not added to the group."""

    chunk_group_model: ChunkGroupRecord = ChunkGroupRecord(label=group_label)

    for chunk in document.chunks:
        if not chunk.enabled:
            logger.warning(f"Skipping disabled chunk {chunk.key}:{chunk.label}!")
            continue

        # Create cameras and sensors
        chunk_record: ChunkRecord = _build_chunk_record(session, chunk)
        chunk_group_model.chunks.append(chunk_record)

    return chunk_group_model


def _build_chunk_record(session: Session, chunk: ms.Chunk) -> ChunkRecord:
    """Builds a chunk model from a Metashape chunk."""

    state: DatabaseLoading.ChunkBuildState = DatabaseLoading.ChunkBuildState()
    chunk_record: records.ChunkRecord = records.ChunkRecord(
        key=chunk.key, label=chunk.label
    )

    # Create sensors and cameras
    state: DatabaseLoading.ChunkBuildState = _create_sensor_models(
        session, chunk, state
    )
    state: DatabaseLoading.ChunkBuildState = _create_camera_models(
        session, chunk, state
    )

    for camera_model in state.cameras.values():
        chunk_record.cameras.append(camera_model)

    for sensor_model in state.sensors.values():
        chunk_record.sensors.append(sensor_model)

    # Create composite types
    state: DatabaseLoading.ChunkBuildState = _create_stereo_models(
        session, chunk, state
    )

    for stereo_rig in state.stereo_rigs:
        chunk_record.stereo_rigs.append(stereo_rig)

    for stereo_sensor_pair in state.stereo_sensor_pairs:
        chunk_record.stereo_sensor_pairs.append(stereo_sensor_pair)

    for stereo_camera_pair in state.stereo_camera_pairs:
        chunk_record.stereo_camera_pairs.append(stereo_camera_pair)

    # Commit the chunk record in order to obtain camera and sensor ids
    session.add(chunk_record)
    session.commit()
    session.refresh(chunk_record)

    # Create camera tracks by by sensor if and camera labels
    chunk_record.camera_tracks = _track_cameras_by_sensor(chunk_record.cameras)

    # Create stereo camera tracks by rig id and camera labels
    chunk_record.stereo_camera_tracks = _track_stereo_cameras_by_rig(
        chunk_record.stereo_camera_pairs
    )

    return chunk_record


def _create_sensor_models(
    session: Session, chunk: ms.Chunk, state: DatabaseLoading.ChunkBuildState
) -> DatabaseLoading.ChunkBuildState:
    """Creates sensor models for the sensors in a chunk."""

    # Create sensor models and submodels
    for sensor in chunk.sensors:
        if sensor in state.sensors:
            logger.warning(f"Already built model for sensor {sensor}. Skipping!")
            continue

        sensor_model: SensorRecord = convert_sensor_to_orm(sensor)

        # Store the mapping from Metashape sensor to ORM sensor
        state.sensors[sensor] = sensor_model

    return state


def _create_camera_models(
    session: Session, chunk: ms.Chunk, state: DatabaseLoading.ChunkBuildState
) -> DatabaseLoading.ChunkBuildState:
    """Creates camera models for the cameras in a chunk."""

    # Create camera models and submodels
    for camera in chunk.cameras:
        if camera in state.cameras:
            logger.warning(f"Already built model for camera {camera}. Skipping!")
            continue

        # Create a sensor model for the camera
        camera_model: CameraRecord = convert_camera_to_orm(camera)

        # Look up and assign sensor model
        sensor_model: SensorRecord | None = state.sensors.get(camera.sensor)
        if sensor_model is not None:
            camera_model.sensor = sensor_model

        # Store the mapping from Metashape camera to ORM camera
        state.cameras[camera] = camera_model

    return state


def _create_stereo_models(
    session: Session,
    chunk: ms.Chunk,
    state: DatabaseLoading.ChunkBuildState,
) -> DatabaseLoading.ChunkBuildState:
    """Creates stereo models for the sensors and cameras in a chunk."""

    stereo_groups: list[StereoGroup] = get_stereo_groups(chunk)

    for stereo_group in stereo_groups:
        master_sensor: SensorRecord | None = state.sensors.get(
            stereo_group.sensor_pair.first
        )
        slave_sensor: SensorRecord | None = state.sensors.get(
            stereo_group.sensor_pair.second
        )

        assert master_sensor is not None, "invalid master sensor"
        assert slave_sensor is not None, "invalid slave sensor"

        stereo_sensor: StereoRigRecord.SensorPair = StereoRigRecord.SensorPair(
            master=master_sensor,
            slave=slave_sensor,
        )

        stereo_rig: StereoRigRecord = StereoRigRecord(sensors=stereo_sensor)

        state.stereo_sensor_pairs.append(stereo_sensor)
        state.stereo_rigs.append(stereo_rig)

        for camera_pair in stereo_group.camera_pairs:
            master_camera: CameraRecord | None = state.cameras.get(camera_pair.first)
            slave_camera: CameraRecord | None = state.cameras.get(camera_pair.second)

            assert master_camera is not None, "invalid master camera"
            assert slave_camera is not None, "invalid slave camera"

            stereo_camera_pair: StereoRigRecord.CameraPair = StereoRigRecord.CameraPair(
                master=master_camera,
                slave=slave_camera,
                stereo_rig=stereo_rig,
            )

            state.stereo_camera_pairs.append(stereo_camera_pair)

    return state


def _track_cameras_by_sensor(
    cameras: list[records.CameraRecord],
) -> list[records.CameraTrackRecord]:
    """Creates camera tracks for camera captured by the same sensor."""

    # Sort cameras by sensor id so that we can use the groupby to partition them
    cameras: list[records.CameraRecord] = sorted(cameras, key=lambda x: x.sensor.id)

    # Group cameras by sensor id
    cameras_by_sensor: list[list[records.CameraRecord]] = [
        list(group) for _, group in groupby(cameras, lambda x: x.sensor.id)
    ]

    # Sort cameras for each group to create the tracks
    tracks: list[records.CameraTrackRecord] = list()
    for camera_group in cameras_by_sensor:
        sorted_camera_group: list[records.CameraRecord] = sorted(
            camera_group, key=lambda camera: camera.label
        )
        track: records.CameraTrackRecord = records.CameraTrackRecord(
            cameras=sorted_camera_group
        )
        tracks.append(track)

    return tracks


def _track_stereo_cameras_by_rig(
    camera_pairs: list[records.StereoRigRecord.CameraPair],
) -> list[records.StereoCameraTrackRecord]:
    """Creates stereo camera tracks for camera pairs captured by the same stereo rig."""

    camera_pairs: list[records.StereoRigRecord.CameraPair] = sorted(
        camera_pairs, key=lambda x: x.stereo_rig.id
    )

    camera_pairs_by_rig: list = [
        list(group) for _, group in groupby(camera_pairs, lambda x: x.stereo_rig.id)
    ]

    tracks: list[records.StereoCameraTrackRecord] = list()
    for camera_pair_group in camera_pairs_by_rig:
        sorted_camera_pairs: list[records.StereoRigRecord.CameraPair] = sorted(
            camera_pair_group, key=lambda pair: pair.master.label
        )
        tracks.append(records.StereoCameraTrackRecord(camera_pairs=sorted_camera_pairs))

    return tracks
