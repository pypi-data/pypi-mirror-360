"""Module for mynds backend CLI."""

import click

from .celery import celery_group
from .server import server_group

from .tools.image_processing import image_processing_group


def main() -> None:
    """Main entrypoint for the CLI."""
    cli = click.CommandCollection(
        sources=[celery_group, server_group, image_processing_group]
    )
    cli()


if __name__ == "__main__":
    main()
