from typing import Dict, Mapping

# from enum import StrEnum, auto

# class _Style(StrEnum):
#     BUILTIN = auto()
#     ORJSON = auto()


try:
    import orjson as json  # pyright: ignore[reportMissingImports]

    print("using orjson")
    # _style = _Style.ORJSON
except ImportError:
    import json

    print("using builtin json")
    # _style = _Style.BUILTIN


class pyddb:
    def __init__(self, filename: str | None) -> None:
        if not filename:
            self.file = "db.json"
            return
        self.file = filename

        try:
            with open(self.file, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}

    def add(self, data: Dict | Mapping) -> None:
        self.data.update(data)

    def update(self, data: Dict | Mapping) -> None:
        self.data.update(data)

    def save(self) -> None:
        try:
            with open(self.file, "w") as f:
                f.write(json.dumps(self.data, ensure_ascii=False))
        except Exception as e:
            print(f"error saving data to file: {e}")


def main():
    print("Hello from pyddb!")


if __name__ == "__main__":
    main()
