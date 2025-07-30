"""Module for exporting Metashape data products."""

from pathlib import Path

import click
import Metashape as ms
import polars as pl

from mynd.utils.log import logger

from myndms.common import read_document
from myndms import helpers as helpers

from myndms.helpers.dense_export import export_dense_cloud
from myndms.helpers.dense_export import export_raster


@click.group()
@click.pass_context
def export_cli(context: click.Context) -> None:
    """CLI for export tasks."""
    context.ensure_object(dict)


@export_cli.command()
@click.option("--document", "document_path", type=Path, required=True)
@click.option("--output", "output_directory", type=Path, required=True)
@click.option("--select", type=str, default=None, help="export selected chunk")
@click.option(
    "--export-dense",
    "export_dense",
    is_flag=True,
    default=False,
    show_default=True,
    help="export dense products",
)
def export_batch(
    document_path: Path,
    output_directory: Path,
    select: str | None,
    export_dense: bool,
) -> None:
    """Exports a batch of data products from Metashape."""

    if not document_path.exists():
        raise ValueError(f"invalid project path: {document_path}")

    if not output_directory.exists():
        raise ValueError(f"invalid output directory: {output_directory}")

    document: ms.Document | str = read_document(document_path)
    handle_batch_export(document, output_directory, export_dense)


def handle_batch_export(
    document: ms.Document, output: Path, export_dense: bool
) -> None:
    """Handles a batch export."""

    for chunk in document.chunks:
        # TODO: Get camera calibrations
        _camera_attributes: pl.DataFrame = helpers.tabulate_camera_attributes(chunk)
        _camera_metadata: pl.DataFrame = helpers.tabulate_camera_metadata(chunk)
        reference_estimates: pl.DataFrame = helpers.tabulate_camera_references_estimate(
            chunk
        )
        reference_priors: pl.DataFrame = helpers.tabulate_camera_references_prior(chunk)

        # Save references to csv file
        reference_estimates.write_csv(
            file=output / f"{chunk.label}_reference_estimates.csv"
        )
        reference_priors.write_csv(file=output / f"{chunk.label}_reference_priors.csv")

        if export_dense:
            # Export point cloud
            _cloud_path: Path = export_dense_cloud(
                chunk, path=output / f"{chunk.label}_dense_cloud.ply"
            )

            # Export orthomosaic
            _raster_path: Path = export_raster(
                chunk,
                path=output / f"{chunk.label}_orthomosaic.tif",
            )
