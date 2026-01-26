from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

try:
    import orjson  # pyright: ignore[reportMissingImports]
except ImportError:
    orjson = None
    import json


def touch(file_path: str | Path) -> None:
    """Create file, should _not_ override file if exists, but will update modified date."""
    # what _is_ a valid path, anyway?
    # screw it for now, if it works on my machine it works for now.
    fp = Path(file_path) if isinstance(file_path, str) else file_path
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.touch(exist_ok=True)


## What Do I want for this object?
# - [ ] I want to save Dicts to Json files
# - [ ] I want to have optional dependency orjson as a potential parser


class Storage(ABC):
    @abstractmethod
    def read(self) -> Optional[Any]:
        raise NotImplementedError()

    @abstractmethod
    def write(self, data: Any):
        raise NotImplementedError()


class JSONStorage(Storage):
    def __init__(self, filename: str | None = None) -> None:
        super().__init__()
        self.filename = "db.json" if not filename else filename
        self._filepath = Path(self.filename)
        touch(self._filepath)

    def read(self) -> dict:
        if orjson is not None:
            with open(self._filepath, "rb") as f:
                return orjson.loads(f.read())
        with open(self._filepath, "r", encoding="utf-8") as f:
            return json.load(f)  # type: ignore

    def write(self, data: dict) -> None:
        if orjson is not None:
            with open(self._filepath, "wb") as f:
                f.write(orjson.dumps(data))
        else:
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)  # type: ignore


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self._data = {}  # empty dict or None here?

    def read(self) -> dict:
        return self._data

    def write(self, data: dict) -> None:
        self._data = data  # overwrite data, or update existing?


__all__ = ["touch", "JSONStorage"]
