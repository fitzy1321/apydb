try:
    import osjson as json  # pyright: ignore[reportMissingImports]
except ImportError:
    import json


def main():
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    print("Hello from pyddb!")


if __name__ == "__main__":
    main()
