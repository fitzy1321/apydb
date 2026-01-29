from __future__ import annotations

from pathlib import Path
from typing import Any

from apydb.storage import JSONStorage, MemoryStorage, Storage

__COLLECTIONS = "collections"


class Collection:
    def __init__(self, database: Database, name: str) -> None:
        self._db = database
        self._name = name


class Database:
    def __init__(self, storage: Storage, lazy=True) -> None:
        self._storage = storage
        self._dirty = False

        if lazy:
            self._data: dict[str, Any] | None = None
        else:
            self._load()

        self._collections: dict[str, Collection] = {}

    def _load(self) -> None:
        if self._data is not None:
            return

        self._data = self._storage.read()
        if self._data is None or not self._data or __COLLECTIONS not in self._data:
            self._data = {__COLLECTIONS: {}}

    def __getitem__(self, name: str) -> Collection:
        # ? Error or Default String?
        if not name:
            raise ValueError("'name' string must have a value")

        if self._data is None:
            self._load()

        if name not in self._collections:
            self._collections[name] = Collection(self, name)
        return self._collections[name]


# I'm thinking MongoDB like interface
class Client:
    def __init__(self, data_dir: str | Path = "./data") -> None:
        self._base_dir = Path(data_dir)
        self._dbs: dict[str, Database] = {}

    def __getitem__(self, name: str) -> Database:
        """Get a Database. Name maps to json file name."""
        # ? Error or Default String?
        if not name:
            raise ValueError("'name' string must have a value")

        if name not in self._dbs:
            self._dbs[name] = Database(JSONStorage(self._base_dir / f"{name}.json"))
        return self._dbs[name]

    def list_dbs(self) -> list[str]:
        """List all databases."""
        return [f.stem for f in self._base_dir.glob("*.json")]


__all__ = [
    "Client",
    "Collection",
    "Database",
    "JSONStorage",
    "MemoryStorage",
    "Storage",
]
