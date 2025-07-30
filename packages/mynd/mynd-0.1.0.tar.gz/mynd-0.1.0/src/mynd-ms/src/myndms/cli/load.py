"""Module for loading data from a CLI."""

from pathlib import Path

import click
import dotenv
import Metashape as ms

from mynd.database import Engine, create_engine
from mynd.database import verify_engine
from mynd.database import clear_database_tables
from mynd.utils.log import logger

from myndms.common import read_document
from myndms.loading import handle_database_loading


@click.group("load")
def load_cli() -> None:
    """Group for load commands."""
    pass


@load_cli.command("load-database")
@click.option("--document", "document_path", type=Path, required=True)
@click.option("--database", "database_name", type=str, required=True)
@click.option("--host", type=str, required=True)
@click.option("--port", type=int, required=True)
@click.option("--verbose", is_flag=True, default=False)
def load_database_command(
    document_path: Path,
    database_name: str,
    host: str,
    port: int,
    verbose: bool,
) -> None:
    """Loads data from a Metashape document into a database using Mynds storage
    models."""

    assert document_path.exists(), f"document path does not exist: {document_path}"

    document: ms.Document | str = read_document(document_path)
    engine: Engine | None = prepare_database_engine(database_name, host, port, verbose)

    handle_database_loading(engine, document)


@load_cli.command("clear-database")
@click.option("--database", "database_name", type=str, required=True)
@click.option("--host", type=str, required=True)
@click.option("--port", type=int, required=True)
def clear_database_command(database_name: str, host: str, port: int) -> None:
    """Clears the tables in the database."""

    engine: Engine | None = prepare_database_engine(database_name, host, port)
    clear_database_tables(engine)
    logger.info(f"Cleared database: {database_name}")


def prepare_database_engine(
    database_name: str, host: str, port: int, verbose: bool = False
) -> Engine | None:
    """Prepares a database engine by creating the engine and verifying that it
    can connect to the database."""

    engine: Engine = create_engine(
        name=database_name,
        host=host,
        port=port,
        username=dotenv.dotenv_values(".env").get("PG_USERNAME"),
        password=dotenv.dotenv_values(".env").get("PG_PASSWORD"),
        echo=verbose,
    )

    error: None | str = verify_engine(engine)
    if error is not None:
        logger.warning(f"error when check database connection: {error}")
        return None

    return engine
