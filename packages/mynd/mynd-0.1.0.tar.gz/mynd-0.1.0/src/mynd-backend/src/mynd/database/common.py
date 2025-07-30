"""Module with database functionality for Mynds ORM."""

from collections.abc import Callable
from typing import TypeAlias

import sqlalchemy as sqla
import sqlmodel as sqlm

import sqlalchemy.ext.asyncio as sqlasync


Engine: TypeAlias = sqla.Engine
Session: TypeAlias = sqlm.Session

AsyncEngine: TypeAlias = sqlasync.AsyncEngine
AsyncSession: TypeAlias = sqlasync.AsyncSession
AsyncSessionFactory: TypeAlias = Callable[[None], AsyncSession]


def create_engine(
    name: str,
    host: str,
    port: int,
    username: str,
    password: str,
    **kwargs,
) -> Engine:
    """Creates a SQL database engine."""
    # NOTE: We only support postgresql databases for now
    url: str = f"postgresql+psycopg://{username}:{password}@{host}:{port}/{name}"
    engine: sqla.Engine = sqlm.create_engine(url, **kwargs)
    return engine


def verify_engine(engine: Engine) -> None | str:
    """Verifies if a database engine is able to connect."""
    try:
        connection: sqla.Connection = engine.connect()
        connection.close()
        return None
    except sqla.exc.SQLAlchemyError as error:
        return str(error)


def create_async_engine(
    name: str,
    host: str,
    port: int,
    username: str,
    password: str,
    **kwargs,
) -> AsyncEngine:
    """Creates an asynchronous SQL database engine."""
    # NOTE: We only support postgresql databases for now
    url: str = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{name}"
    engine: AsyncEngine = sqla.ext.asyncio.create_async_engine(
        url, future=True, **kwargs
    )
    return engine


def create_async_session_factory(engine: AsyncEngine) -> AsyncSessionFactory:
    """Returns a factory for asynchronous session for the given engine."""
    factory: AsyncSessionFactory = sqla.ext.asyncio.async_sessionmaker(
        engine, expire_on_commit=False
    )
    return factory


def close_all_sessions() -> None:
    """Closes all SQLAlchemy sessions."""
    sqla.orm.session.close_all_sessions()


def create_database_tables(engine: Engine) -> None:
    """Creates database tables based on the schema of the imported SQL models."""
    sqlm.SQLModel.metadata.create_all(engine)


def clear_database_tables(engine: Engine) -> None:
    """Clears the SQLModel tables in a database."""
    close_all_sessions()
    sqlm.SQLModel.metadata.drop_all(engine)


def get_database_tables() -> dict:
    """Returns the registered SQL models."""
    tables: dict = {
        name: table for name, table in sqlm.SQLModel.metadata.tables.items()
    }
    return tables
