from abc import ABC, abstractmethod
import asyncio
from collections.abc import Sequence
import contextlib
import json
from typing import Iterable

import asyncpg
from asyncpg.exceptions import PostgresError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


async def setup_jsonb_codec(conn: asyncpg.Connection):
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


class DBInterface(ABC):
    @abstractmethod
    async def execute(self, query: str, *args):
        pass

    @abstractmethod
    async def executemany(self, command: str, args: Iterable[Sequence]):
        pass

    @abstractmethod
    async def fetch(self, query: str, *args):
        pass

    @abstractmethod
    async def fetchrow(self, query: str, *args):
        pass

    @abstractmethod
    async def fetchval(self, query: str, *args):
        pass


class LockedDB(DBInterface):
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn
        self.lock = asyncio.Lock()

    async def execute(self, query: str, *args):
        async with self.lock:
            return await self.conn.execute(query, *args)

    async def executemany(self, command: str, args_list: Sequence[Sequence]):
        async with self.lock:
            return await self.conn.executemany(command, args_list)

    async def fetch(self, query: str, *args) -> list[asyncpg.Record]:
        async with self.lock:
            return await self.conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> asyncpg.Record | None:
        async with self.lock:
            return await self.conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        async with self.lock:
            return await self.conn.fetchval(query, *args)


async def create_db(database_uri) -> LockedDB:
    conn = await asyncpg.connect(database_uri)
    await setup_jsonb_codec(conn)
    return LockedDB(conn)


async def create_pool(database_uri) -> asyncpg.pool.Pool:
    return await asyncpg.create_pool(
        database_uri,
        init=setup_jsonb_codec,
        timeout=5,
        min_size=3,
        max_inactive_connection_lifetime=100,
    )


@contextlib.asynccontextmanager
async def get_transactional_db(request: Request):
    async with request.app.state.db_pool.acquire() as connection:
        transaction = connection.transaction()
        await transaction.start()

        yield LockedDB(connection)

        try:  # Try to commit
            await transaction.commit()
        except PostgresError:
            await transaction.rollback()
            raise


class AsyncDBMiddleware(BaseHTTPMiddleware):
    """Will start a DB Session at every request and commit or rollback in the end"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        async with request.app.state.db_pool.acquire() as connection:
            transaction = connection.transaction()
            await transaction.start()
            request.state.db = LockedDB(connection)

            # Continue with request
            response = await call_next(request)

            if hasattr(request.state, "errors"):
                await transaction.rollback()
            else:
                try:  # Try to commit
                    await transaction.commit()
                except PostgresError:
                    await transaction.rollback()
                    return JSONResponse(
                        {"errors": [{"message": "Error while commiting to Database"}]},
                        status_code=500,
                    )
            return response
