from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path
from typing import Any, Type

__all__ = [
    "Client",
    "Collection",
    "Database",
    "JSONStorage",
    "MemoryStorage",
    "Storage",
]

# json library imports
try:
    import orjson

    print("using orjson")
except ImportError:
    orjson = None
    import json

    print("using builtin json")

####################################################################
#                            Types                                 #
####################################################################
type Document = dict[str, Any]
# class LogicOps(StrEnum):
#     AND = "$and"
#     NOR = "$nor"
#     OR = "$or"

# class FieldOps(StrEnum):
#     EQ = "$eq"  # equal
#     NE = "$ne"  # not equal
#     GT = "$gt"  # greater than
#     GTE = "$gte"  # greater than or equal
#     LT = "$lt"  # lesser than
#     LTE = "$lte"  # lesser than or equal
#     IN = "$in"  # in
#     NIN = "$nin"  # not in
#     EXISTS = "$exists"  # exists (shorten?)

# class UpdateOps(StrEnum):
#     SET = "$set"
#     UNSET = "$unset"
#     INC = "$inc"
#     PUSH = "$push"
#     PULL = "$pull"

####################################################################
#                            Storage                               #
####################################################################


class Storage(ABC):
    @abstractmethod
    def read(self) -> dict | None:
        raise NotImplementedError()

    @abstractmethod
    def write(self, data: Any) -> None:
        raise NotImplementedError()


class MemoryStorage(Storage):
    def __init__(self, *args, **kwargs) -> None:
        self._data = {}

    def read(self) -> dict:
        return deepcopy(self._data)

    def write(self, data: dict) -> None:
        self._data = deepcopy(data)


class JSONStorage(Storage):
    def __init__(self, dir_path: Path, name: str) -> None:
        if not name.endswith(".json"):
            name += ".json"
        self._filepath = Path(dir_path) / name

    def read(self) -> dict | None:
        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        if orjson is not None:
            print("using orjson")
            with open(self._filepath, "a+b") as f:
                data = f.read()
                return None if not data else orjson.loads(data)

        print("using builtin json")
        with open(self._filepath, "a+", encoding="utf-8") as f:
            data = f.read()
            return None if not data else json.load(data)  # type: ignore

    def write(self, data: dict) -> None:
        self._filepath.parent.mkdir(parents=True, exist_ok=True)

        if orjson is not None:
            with open(self._filepath, "wb") as f:
                f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
        else:
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)  # type: ignore


####################################################################
#                            Collection                            #
####################################################################


class InsertOneResult:
    __slots__ = "__inserted_id"

    def __init__(self, inserted_id: str | None) -> None:
        self.__inserted_id = inserted_id

    @property
    def inserted_id(self) -> str | None:
        """The inserted document's _id."""
        return self.__inserted_id


class InsertManyResult:
    __slots__ = "__inserted_ids"

    def __init__(self, inserted_ids: list | None) -> None:
        self.__inserted_ids = inserted_ids

    @property
    def inserted_ids(self) -> list | None:
        return self.__inserted_ids


class Collection:
    def __init__(
        self,
        name: str,
        db: Database,
        storage: Storage,
        lazy_loading: bool = True,
    ) -> None:
        self._name = name
        self._db = db
        self._storage = storage
        self._data: dict | None = None

        if not lazy_loading:
            self._load()

    def _load(self) -> None:
        if self._data is not None:
            return

        self._data = self._storage.read()
        if self._data is None or not self._data or "docs" not in self._data:
            self._data = self._default_dict()

    @staticmethod
    def _default_dict() -> dict:
        return {"docs": []}

    def insert_one(self, document: Document) -> InsertOneResult:
        if not document:
            raise ValueError("please provide at least one value!")

        result = None
        if "_id" not in document:
            new_id = str(uuid.uuid4())
            document["_id"] = new_id
            result = InsertOneResult(new_id)
        else:
            result = InsertOneResult(document["_id"])

        if self._data is None:
            self._load()
            assert self._data is not None

        self._data["docs"].append(document)
        self._storage.write(self._data)
        return result

    def insert_many(self, documents: list[Document]) -> InsertManyResult:
        if not documents or not documents[0]:
            raise ValueError("please provide at least one value!")

        ids = []
        for doc in documents:
            if "_id" not in doc:
                new_id = str(uuid.uuid4())
                doc["_id"] = new_id
                ids += new_id
            else:
                # ? Do I need to check if Id already exists here?
                ids += doc["_id"]

        if self._data is None:
            self._load()
            assert self._data is not None

        self._data["docs"].extend(documents)
        self._storage.write(self._data)
        return

    def find(self) -> list[Document]:
        if self._data is None:
            self._load()
            assert self._data is not None

        return self._data["docs"]

    def to_dict(self) -> dict:
        return self._data if self._data else self._default_dict()


####################################################################
#                            Database                              #
####################################################################


class Database:
    def __init__(
        self,
        name: str,
        base_dir: str | Path,
        storage_type: Type[Storage],
    ) -> None:
        self._name = name
        self._db_dir = Path(base_dir) / name
        self._storage_type = storage_type
        self._collections: dict[str, Collection] = {}

    def __getitem__(self, collection_name: str) -> Collection:
        """Get Collection using dictionay syntax: db['mycollection']"""
        return self.get_collection(collection_name)

    def get_collection(self, collection_name: str) -> Collection:
        # ? Error or Default String?
        if not collection_name:
            raise ValueError("'name' string must have a value")

        if collection_name not in self._collections:
            self._collections[collection_name] = Collection(
                collection_name,
                self,
                self._storage_type(self._db_dir, collection_name),  # type:ignore
            )

        if hasattr(self, "_collection_files"):
            self._collection_files += collection_name

        return self._collections[collection_name]

    def list_collection_names(self) -> list[str]:
        if not hasattr(self, "_collection_files"):
            self._collection_files = [p.stem for p in self._db_dir.glob("*.json")]
        return self._collection_files


####################################################################
#                            Client                                #
####################################################################
class Client:
    def __init__(
        self,
        *,
        data_dir: str | Path = "./data",
        storage_type: Type[Storage] | None = None,
    ) -> None:
        self._base_dir = Path(data_dir)
        self._storage_type = JSONStorage if storage_type is None else storage_type
        self._databases: dict[str, Database] = {}

    def __getitem__(self, database_name: str) -> Database:
        """Get a Database using dictionay syntax: client['mydb']"""
        return self.get_database(database_name)

    def get_database(self, database_name: str) -> Database:
        # ? Error or Default String?
        if not database_name:
            raise ValueError("'database_name' string must have a value")

        if database_name not in self._databases:
            self._databases[database_name] = Database(
                database_name,
                self._base_dir,
                storage_type=self._storage_type,
            )
        return self._databases[database_name]

    def list_database_names(self) -> list[str]:
        if not hasattr(self, "_db_sub_dirs"):
            self._db_sub_dirs = [p.name for p in self._base_dir.iterdir() if p.is_dir()]
        return self._db_sub_dirs
