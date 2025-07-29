import asyncio
import pickle

from pathlib import Path
from typing import Any, Dict, Optional

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey


class PickleStorage(BaseStorage):
    def __init__(self, path: str = "fsm_states.pkl"):
        self._path = Path(path)
        self._lock = asyncio.Lock()

    async def _ensure_file(self):
        if not self._path.exists():
            async with self._lock:
                if not self._path.exists():
                    self._path.write_bytes(pickle.dumps({}))
    
    async def _load(self) -> Dict[str, Any]:
        await self._ensure_file()
        async with self._lock:
            return pickle.loads(self._path.read_bytes())

    async def _save(self, data: Dict[str, Any]):
        await self._ensure_file()
        async with self._lock:
            self._path.write_bytes(pickle.dumps(data))

    async def set_state(self, key: StorageKey, state: Optional[StateType] = None):
        data = await self._load()
        uid = str(key.user_id)
        saved_state = state.state if isinstance(state, State) else state
        data.setdefault(uid, {})["state"] = saved_state
        await self._save(data)

    async def get_state(self, key: StorageKey) -> Optional[str]:
        data = await self._load()
        state = data.get(str(key.user_id), {}).get("state")
        return state

    async def set_data(self, key: StorageKey, data: Dict[str, Any]):
        storage = await self._load()
        uid = str(key.user_id)
        storage[uid] = storage.get(uid, {})
        storage[uid]["data"] = data
        await self._save(storage)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        data = await self._load()
        result = data.get(str(key.user_id), {}).get("data", {})
        return result

    async def close(self):
        pass
