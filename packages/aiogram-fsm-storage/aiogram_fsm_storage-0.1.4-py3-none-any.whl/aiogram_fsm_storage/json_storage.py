import asyncio
import json

from pathlib import Path
from typing import Any, Dict, Optional

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey


class JSONStorage(BaseStorage):
    def __init__(self, path: str = "fsm_states.json"):
        self._path = Path(path)
        self._lock = asyncio.Lock()

    async def _ensure_file(self):
        if not self._path.exists():
            async with self._lock:
                if not self._path.exists():
                    self._path.write_text("{}", encoding="utf-8")

    async def _load(self) -> Dict[str, Any]:
        await self._ensure_file()
        async with self._lock:
            content = self._path.read_text(encoding="utf-8")
            return json.loads(content or "{}")

    async def _save(self, data: Dict[str, Any]):
        await self._ensure_file()
        async with self._lock:
            self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    async def set_state(self, key: StorageKey, state: Optional[StateType] = None):
        data = await self._load()
        uid = str(key.user_id)
        saved_state = state.state if isinstance(state, State) else state
        data.setdefault(uid, {})["state"] = saved_state
        await self._save(data)

    async def get_state(self, key: StorageKey) -> Optional[str]:
        data = await self._load()
        return data.get(str(key.user_id), {}).get("state")

    async def set_data(self, key: StorageKey, data: Dict[str, Any]):
        storage = await self._load()
        uid = str(key.user_id)
        storage.setdefault(uid, {})["data"] = data
        await self._save(storage)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        data = await self._load()
        return data.get(str(key.user_id), {}).get("data", {})

    async def close(self):
        pass
