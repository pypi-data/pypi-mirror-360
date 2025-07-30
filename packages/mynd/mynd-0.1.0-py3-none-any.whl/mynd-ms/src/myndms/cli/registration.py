"""Module for invoking registration tasks through the command-line interface."""

from pathlib import Path

import click
import Metashape as ms

from mynd.config import read_config

from myndms.common import read_document, write_document
from myndms.registration import handle_chunk_registration


@click.group()
def registration() -> None:
    """Group for registration commands invoked through the command-line interface."""
    pass


@registration.command()
@click.option("--document", "document_path", type=Path, required=True)
@click.option("--config", "config_path", type=Path, required=True)
@click.option("--cache", type=Path, required=True)
@click.option(
    "--reference",
    "reference_chunk",
    type=str,
    help="reference chunk label",
    required=True,
)
@click.option(
    "--vis", "visualize", is_flag=True, default=False, help="visualize results"
)
@click.option(
    "--force-export",
    "force_export",
    is_flag=True,
    default=False,
    help="force export of point clouds",
)
def register_chunks(
    document_path: Path,
    config_path: Path,
    cache: Path,
    reference_chunk: str | None = None,
    visualize: bool = False,
    force_export: bool = False,
) -> None:
    """Register chunks in a Metashape document."""

    assert document_path.exists(), f"document does not exist: {document_path}"
    assert config_path.exists(), f"file does not exist: {config_path}"
    assert cache.exists(), f"directory does not exist: {cache}"

    assert document_path.is_file(), f"document path is not a file: {document_path}"
    assert config_path.is_file(), f"config path is not a file: {config_path}"
    assert cache.is_dir(), f"cache path is not a directory: {cache}"

    document: ms.Document | str = read_document(document_path)
    config: dict = read_config(config_path)

    assert "registration" in config, "missing configuration key 'registration'"

    handle_chunk_registration(
        document,
        config.get("registration"),
        cache,
        reference_chunk,
        visualize,
        force_export,
    )

    write_document(document)
