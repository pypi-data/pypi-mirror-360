"""Module for invoking reconstruction tasks through the command-line interface."""

from pathlib import Path

import click
import Metashape as ms

from myndms.common import read_document, write_document
from myndms.reconstruction import handle_reconstruction_task

from mynd.config import read_config
from mynd.utils.log import logger


@click.group()
@click.pass_context
def reconstruction(context: click.Context) -> None:
    """Command-line interface to reconstruction task for the backend."""
    context.ensure_object(dict)


@reconstruction.command()
@click.option("--document", "document_path", type=Path, required=True)
@click.option("--chunk", "chunk_labels", type=str, multiple=True)
@click.option("--config", "config_path", type=Path)
def reconstruct(
    document_path: Path, chunk_labels: tuple[str], config_path: Path
) -> None:
    """Reconstruct geometry from groups of cameras."""

    assert document_path.exists(), f"file does not exist: {document_path}"
    assert config_path.exists(), f"file does not exist: {config_path}"

    document: ms.Document | str = read_document(document_path)
    config: dict = read_config(config_path).unwrap()

    handle_reconstruction_task(document, chunk_labels, config.get("reconstruction"))

    write_document(document, document_path)
