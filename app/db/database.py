from contextlib import asynccontextmanager
from typing import AsyncIterator

import asyncpg
from asyncpg import Pool

from app.config import settings
from app.db.schema import SCHEMA_SQL


class Database:
    def __init__(self) -> None:
        self.pool: Pool | None = None

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(dsn=settings.database_url, min_size=1, max_size=10)

    async def disconnect(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def create_tables(self) -> None:
        if self.pool is None:
            raise RuntimeError("Database pool is not initialized")
        async with self.pool.acquire() as connection:
            await connection.execute(SCHEMA_SQL)

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[asyncpg.Connection]:
        if self.pool is None:
            raise RuntimeError("Database pool is not initialized")
        async with self.pool.acquire() as connection:
            yield connection


db = Database()

