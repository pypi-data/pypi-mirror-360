"""Module for ingesting camera metadata into Metashape."""

from typing import Any, TypeAlias

import Metashape as ms
import polars as pl


Metadata: TypeAlias = dict[str, Any]


def ingest_camera_metadata(
    chunk: ms.Chunk,
    metadata: pl.DataFrame,
    config: dict,
) -> None:
    """Ingests metadata to cameras in a chunk."""

    METADATA_CONFIG_KEY: str = "metadata"
    TABLE_MAP_CONFIG_KEY: str = "table_maps"

    if METADATA_CONFIG_KEY not in config:
        raise ValueError(f"missing config entry: {METADATA_CONFIG_KEY}")

    metadata_config: dict = config.get("metadata")

    if TABLE_MAP_CONFIG_KEY not in metadata_config:
        raise ValueError(f"missing metadata config entry: {TABLE_MAP_CONFIG_KEY}")

    table_maps: dict = metadata_config.get("table_maps")

    camera_metadata: dict[str, dict] = map_metadata_to_cameras(
        metadata,
        table_maps.get("label_field"),
        table_maps.get("data_fields"),
    )

    update_camera_metadata(chunk, camera_metadata)


def map_metadata_to_cameras(
    metadata: pl.DataFrame,
    label_column: str,
    data_columns: list[str],
) -> dict[str, Metadata]:
    """Creates a mapping from camera label to metadata fields from a table."""

    assert label_column in metadata, f"missing camera label column: {label_column}"

    found_data_columns: list[str] = [
        column for column in data_columns if column in metadata
    ]

    camera_metadata: dict[str, Metadata] = {
        row.get(label_column): {
            column: row.get(column) for column in found_data_columns
        }
        for row in metadata.iter_rows(named=True)
    }

    return camera_metadata


def update_camera_metadata(chunk: ms.Chunk, metadata: dict[str, Metadata]) -> None:
    """Update the metadata for a collection of chunk cameras."""

    updated_cameras: dict[str, dict] = dict()
    for camera in chunk.cameras:
        if camera.label not in metadata:
            continue

        fields: dict = metadata.get(camera.label)

        for field, value in fields.items():
            # NOTE: Metashape only allows string values in camera metadata
            camera.meta[str(field)] = str(value)
        updated_cameras[camera.label] = fields
