from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

from apydb.storage import JSONStorage, MemoryStorage, Storage

_COLLECTIONS = "collections"


class Collection:
    def __init__(self, database: Database, name: str) -> None:
        self._db = database
        self._name = name

    def to_dict(self) -> dict:
        if not hasattr(self, "_last_id"):
            self._last_id = 0
        return {
            self._name: {  # ? include this level, or flat dict?
                "_last_id": self._last_id,
                "docs": {
                    # ? what goes here?
                },
            }
        }


class LogicOps(StrEnum):
    AND = "$and"
    NOR = "$nor"
    OR = "$or"


class FieldOps(StrEnum):
    EQ = "$eq"
    NE = "$ne"
    GT = "$gt"
    GTE = "$gte"
    LT = "$lt"
    LTE = "$lte"
    IN = "$in"
    NIN = "$nin"
    EXISTS = "$exists"


class UpdateOps(StrEnum):
    SET = "$set"
    UNSET = "$unset"
    INC = "$inc"
    PUSH = "$push"
    PULL = "$pull"


def matches(doc: dict, query: dict[str, Any]) -> bool:
    pass


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
        if self._data is None or not self._data or _COLLECTIONS not in self._data:
            self._data = {_COLLECTIONS: {}}

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
