"""Main entrypoint for the command-line interface."""

import click

from myndms.cli.export import export_cli
from myndms.cli.ingest import ingestion
from myndms.cli.load import load_cli
from myndms.cli.reconstruction import reconstruction
from myndms.cli.registration import registration


# TODO: Look into alternative for command collection as it removes group-level
# functionality such as sub-commands
main_cli = click.CommandCollection(
    sources=[export_cli, ingestion, load_cli, reconstruction, registration]
)


def main():
    """Runs the command-line interface."""
    main_cli()


if __name__ == "__main__":
    main()
