import pytest
from pyddb import JSONStorage


def test_fallback_to_builtin_json(monkeypatch):
    monkeypatch.setitem("sys.modules", "orjson", None)
    parser = JSONStorage()
    assert parser.reads('{"test": 1}') == {"test": 1}


def test_with_orjson_installed():
    try:
        import orjson
    except ImportError:
        pytest.skip("orjson not available")
    parser = JSONStorage()
    assert parser.reads('{"test": 1}') == {"test": 1}
