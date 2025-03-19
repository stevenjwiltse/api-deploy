import contextlib
from typing import Any, AsyncIterator, Iterator


from core.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session, sessionmaker


class AsyncDatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async_session_manager = AsyncDatabaseSessionManager(
    settings.get_database_url(), {"echo": settings.get_config()["mysql_echo"]}
)


async def get_async_db_session():
    async with async_session_manager.session() as session:
        yield session


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_engine(host, **engine_kwargs)
        self._sessionmaker = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.contextmanager
    def connect(self) -> Iterator[Connection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        connection = self._engine.connect()
        try:
            yield connection
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @contextlib.contextmanager
    def session(self) -> Iterator[Session]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

session_manager = DatabaseSessionManager(settings.get_database_url(), {"echo": settings.get_config()["mysql_echo"]})

def get_db_session():
    with session_manager.session() as session:
        yield session

