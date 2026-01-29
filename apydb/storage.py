from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path
from typing import Any

try:
    import orjson
except ImportError:
    orjson = None
    import json


class Storage(ABC):
    @abstractmethod
    def read(self) -> dict | None:
        raise NotImplementedError()

    @abstractmethod
    def write(self, data: Any) -> None:
        raise NotImplementedError()


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self._data = {}

    def read(self) -> dict:
        return deepcopy(self._data)

    def write(self, data: dict) -> None:
        self._data = deepcopy(data)


class JSONStorage(Storage):
    def __init__(self, filename: str | Path) -> None:
        super().__init__()
        if not filename:
            filename = "data.json"
        self._filepath = Path(filename)

    def read(self) -> dict | None:
        self._filepath.parent.mkdir(parents=True, exist_ok=True)

        if orjson is not None:
            with open(self._filepath, "rb") as f:
                data = f.read()
                return None if not data else orjson.loads(data)

        with open(self._filepath, "r", encoding="utf-8") as f:
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
