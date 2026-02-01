from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

from apydb.storage import JSONStorage, MemoryStorage, Storage

_COLLECTIONS = "collections"


class Document:
    pass


class InsertOneResult:
    __slots__ = "_inserted_id"

    def __init__(self, inserted_id: int | None) -> None:
        self._inserted_id = inserted_id


class Collection:
    def __init__(self, database: Database, name: str) -> None:
        self._db = database
        self._name = name

    def insert_one(self, doc: Document | Any) -> InsertOneResult:
        pass

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
    EQ = "$eq"  # equal
    NE = "$ne"  # not equal
    GT = "$gt"  # greater than
    GTE = "$gte"  # greater than or equal
    LT = "$lt"  # lesser than
    LTE = "$lte"  # lesser than or equal
    IN = "$in"  # in
    NIN = "$nin"  # not in
    EXISTS = "$exists"  # exists (shorten?)


class UpdateOps(StrEnum):
    SET = "$set"
    UNSET = "$unset"
    INC = "$inc"
    PUSH = "$push"
    PULL = "$pull"


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

    def __getitem__(self, collection_name: str) -> Collection:
        return self.get_collection(collection_name)

    def __getattr__(self, collection_name: str) -> Collection:
        if collection_name.startswith("_"):
            raise AttributeError(
                "Let's not access 'private' members please, Thank you!"
            )
        return self.get_collection(collection_name)

    def get_collection(self, collection_name: str) -> Collection:
        # ? Error or Default String?
        if not collection_name:
            raise ValueError("'name' string must have a value")

        if self._data is None:
            self._load()

        if collection_name not in self._collections:
            self._collections[collection_name] = Collection(self, collection_name)
        return self._collections[collection_name]


# I'm thinking MongoDB like interface
class Client:
    def __init__(self, data_dir: str | Path = "./data") -> None:
        self._base_dir = Path(data_dir)
        self._databases: dict[str, Database] = {}

    def __getitem__(self, db_name: str) -> Database:
        """Get a Database using dictionay syntax: client['mydb']"""
        return self.get_database(db_name)

    def __getattr__(self, db_name: str) -> Database:
        """Get a Database using attribute syntax: client.mydb"""
        if db_name.startswith("_"):
            raise AttributeError("let's not access 'private' members, thank you!")
        return self.get_database(db_name)

    def get_database(self, db_name: str) -> Database:
        # ? Error or Default String?
        if not db_name:
            raise ValueError("'name' string must have a value")

        if db_name not in self._databases:
            self._databases[db_name] = Database(
                JSONStorage(self._base_dir / f"{db_name}.json")
            )
        return self._databases[db_name]

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
