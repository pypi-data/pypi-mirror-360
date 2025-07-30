"""Package for handling data loading to a database."""

from pathlib import Path

import Metashape as ms

from mynd.database import Engine, Session, create_database_tables
from mynd.models.record import ChunkGroupRecord
from mynd.utils.log import logger

from .loaders import load_document_database


def handle_database_loading(engine: Engine, document: ms.Document) -> None:
    """Handles loading of data from a Metashape document to a database."""

    # Create tables if they do not exist
    create_database_tables(engine)

    with Session(engine) as session:
        # TODO: Check if a chunk group corresponding to a document is already in the group?

        # Load document data into a database using the ORM
        chunk_group: ChunkGroupRecord = load_document_database(
            session=session, document=document
        )

        logger.info(f"Loaded database with document: {Path(document.path).stem}")

        log_chunk_group_stats(session, chunk_group)


def log_chunk_group_stats(session: Session, chunk_group: ChunkGroupRecord) -> None:
    """Logs chunk group statistics to the console."""
    logger.info("")
    logger.info(f"Chunk group: {chunk_group.label}")

    for chunk in chunk_group.chunks:
        logger.info("")
        logger.info(f"Chunk:                    {chunk.label}")
        logger.info(f" - Sensors:               {len(chunk.sensors)}")
        logger.info(f" - Cameras:               {len(chunk.cameras)}")
        logger.info(f" - Stereo rigs:           {len(chunk.stereo_rigs)}")
        logger.info(f" - Stereo sensor pairs:   {len(chunk.stereo_sensor_pairs)}")
        logger.info(f" - Stereo camera pairs:   {len(chunk.stereo_camera_pairs)}")

        for stereo_rig in chunk.stereo_rigs:
            logger.info("")
            logger.info("Stereo rig:")
            logger.info(f" - Sensor, master:    {stereo_rig.sensors.master.id}")
            logger.info(f" - Sensor, slave:     {stereo_rig.sensors.slave.id}")
            if stereo_rig.sensors_rectified:
                logger.info(
                    f" - Rectified sensor, master:    {stereo_rig.sensors_rectified.master.id}"
                )
                logger.info(
                    f" - Rectified sensor, slave:     {stereo_rig.sensors_rectified.slave.id}"
                )

    logger.info("")
