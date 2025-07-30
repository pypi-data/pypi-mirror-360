"""Module for Mynds router dependencies."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request

from mynd.api.settings import ApplicationSettings
from mynd.api.image_store import ImageStore
from mynd.database import Engine, Session

from mynd.database import AsyncEngine, AsyncSession, AsyncSessionFactory
from mynd.database import create_async_engine, create_async_session_factory

from mynd.utils.log import logger


@lru_cache
def get_settings() -> ApplicationSettings:
    """Returns the application settings. Caches the instance if it has already
    been created."""
    return ApplicationSettings()


ApplicationSettingsDep = Annotated[ApplicationSettings, Depends(get_settings)]


def get_engine(request: Request) -> Engine:
    """Returns the application database engine."""
    try:
        engine: Engine = request.app.state.engine
        return engine
    except AttributeError as error:
        logger.error(f"error when accessing database engine: {error}")
        raise


EngineDep = Annotated[Engine, Depends(get_engine)]


def get_session(request: Request) -> Session:
    """Returns the database session."""
    try:
        engine: Engine = request.app.state.engine
        with Session(engine) as session:
            yield session
    except AttributeError as error:
        logger.error(f"error when accessing database engine: {error}")
        raise


SessionDep = Annotated[Session, Depends(get_session)]


async def get_async_session(request: Request) -> AsyncSession:
    """Returns an async database session."""
    try:
        engine: AsyncEngine | None = request.app.state.async_engine
        assert isinstance(engine, AsyncEngine), "invalid async engine type"
        session_factory: AsyncSessionFactory = create_async_session_factory(engine)
        async with session_factory() as session:
            yield session
    except AttributeError as error:
        logger.error(f"error when accessing application async engine: {error}")
        raise


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def get_image_store(request: Request) -> ImageStore:
    """Retrieves the image store from the application state."""
    try:
        image_store: ImageStore = request.app.state.image_store
        return image_store
    except AttributeError as error:
        logger.error(f"error when accessing application image repository: {error}")
        raise


ImageStoreDep = Annotated[ImageStore, Depends(get_image_store)]
