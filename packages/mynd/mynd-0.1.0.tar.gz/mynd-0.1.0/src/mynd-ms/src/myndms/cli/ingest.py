"""CLI for ingesting cameras and metadata."""

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

import click
import Metashape as ms
import polars as pl

from mynd.config import read_config
from mynd.utils.filesystem import list_directory
from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result

from myndms.common import create_document, read_document, write_document
from myndms.ingestion.handler import handle_camera_ingestion
from myndms.ingestion.metadata import ingest_camera_metadata


@click.group(chain=True)
@click.pass_context
def ingestion(context: click.Context) -> None:
    """CLI group for ingesting data into Metashape."""
    context.ensure_object(dict)


def prepare_document(path: Path, create_if_not_exists: bool) -> ms.Document:
    """Command-line interface for ingesting data into the backend."""

    if not create_if_not_exists:
        assert path.exists(), f"document does not exist: {path}"
    else:
        assert path.parent.exists(), f"directory does not exist: {path.parent}"

    if path.exists():
        document: ms.Document | str = read_document(path)
    elif create_if_not_exists:
        document: ms.Document = create_document()
    else:
        raise ValueError("document does not exist")

    return document


@dataclass(frozen=True)
class CameraIngestionBundle:
    """Class representing a camera ingestion bundle."""

    label: str
    camera_file: Path
    image_directory: Path
    config_file: Path


# TODO: Investigate approaches of loading the project in one command
@ingestion.command()
@click.option("--document", "document_path", type=Path, required=True)
@click.option(
    "--create-if-not-exists",
    "create_new_document",
    is_flag=True,
    type=bool,
    default=False,
)
@click.option("--label", type=str, required=True)
@click.option("--cameras", "camera_file", type=Path, required=True)
@click.option("--imagedir", "image_directory", type=Path, required=True)
@click.option("--config", "config_file", type=Path, required=True)
@click.option("--metadata", "metadata_file", type=Path, default=None)
def ingest_cameras(
    document_path: Path,
    create_new_document: bool,
    label: str,
    camera_file: Path,
    image_directory: Path,
    config_file: Path,
    metadata_file: Path | None,
) -> None:
    """Ingests a group of cameras into Metashape as a chunk."""

    document: ms.Document = prepare_document(document_path, create_new_document)
    assert document is not None, "invalid document"

    assert camera_file.exists(), f"camera file does not exist: {camera_file}"
    assert (
        image_directory.exists()
    ), f"image directory does not exist: {image_directory}"
    assert config_file.exists(), f"configuration file does not exits: {config_file}"

    assert camera_file.is_file(), f"path is not a file: {camera_file}"
    assert config_file.is_file(), f"path is not a file: {config_file}"

    bundle: CameraIngestionBundle = CameraIngestionBundle(
        label,
        camera_file,
        image_directory,
        config_file,
    )

    assert (
        bundle.camera_file.exists()
    ), f"camera file does not exist: {bundle.camera_file}"
    assert (
        bundle.image_directory.exists()
    ), f"image directory does not exist: {bundle.image_directory}"
    assert (
        bundle.config_file.exists()
    ), f"config file does not exist: {bundle.config_file}"

    cameras: pl.DataFrame = pl.read_csv(bundle.camera_file)
    images: list[Path] = list_directory(bundle.image_directory)
    config: dict = read_config(bundle.config_file).unwrap()

    if metadata_file is not None:
        metadata: pl.DataFrame = pl.read_csv(metadata_file)
    else:
        metadata = None

    chunk: ms.Chunk = document.addChunk()
    chunk.label = bundle.label

    handle_camera_ingestion(chunk, cameras, images, config.get("ingestion"))

    if metadata_file is not None:
        ingest_camera_metadata(chunk, metadata, config.get("ingestion"))

    write_document(document, document_path)
