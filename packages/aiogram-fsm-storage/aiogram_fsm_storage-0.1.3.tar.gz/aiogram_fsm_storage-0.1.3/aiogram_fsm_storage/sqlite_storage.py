import aiosqlite
import asyncio
import pickle

from pathlib import Path
from typing import Any, Dict, Optional

from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from aiogram.fsm.state import State


class SQLiteStorage(BaseStorage):
    def __init__(self, path: str = "fsm_states.sqlite"):
        self._path = Path(path)
        self._lock = asyncio.Lock()
        self._db: Optional[aiosqlite.Connection] = None
        self._initialized = False

    async def _init(self):
        async with self._lock:
            if not self._initialized:
                self._db = await aiosqlite.connect(self._path)
                await self._db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS fsm_storage (
                        user_id INTEGER PRIMARY KEY,
                        state TEXT,
                        data BLOB
                    )
                    """
                )
                await self._db.commit()
                self._initialized = True

    async def _get_db(self) -> aiosqlite.Connection:
        if not self._initialized:
            await self._init()
        return self._db

    async def _get_data_blob(self, db: aiosqlite.Connection, user_id: int):
        cursor = await db.execute(
            "SELECT data FROM fsm_storage WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None

    async def set_state(self, key: StorageKey, state: Optional[StateType] = None):
        saved_state = state.state if isinstance(state, State) else state

        async with self._lock:
            db = await self._get_db()
            data_blob = await self._get_data_blob(db, key.user_id)
            await db.execute(
                """
                INSERT INTO fsm_storage(user_id, state, data) VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET state=excluded.state
                """,
                (key.user_id, saved_state, data_blob),
            )
            await db.commit()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        async with self._lock:
            db = await self._get_db()
            cursor = await db.execute(
                "SELECT state FROM fsm_storage WHERE user_id = ?", (key.user_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]):
        data_blob = pickle.dumps(data)
        current_state = await self.get_state(key)

        async with self._lock:
            db = await self._get_db()
            await db.execute(
                """
                INSERT INTO fsm_storage(user_id, state, data) VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET data=excluded.data
                """,
                (key.user_id, current_state, data_blob),
            )
            await db.commit()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        async with self._lock:
            db = await self._get_db()
            cursor = await db.execute(
                "SELECT data FROM fsm_storage WHERE user_id = ?", (key.user_id,)
            )
            row = await cursor.fetchone()
            return pickle.loads(row[0]) if row and row[0] else {}

    async def close(self):
        if self._db:
            await self._db.close()
            self._db = None
            self._initialized = False
