import pytest


@pytest.fixture(autouse=True)
def own_data_file(tmp_path, monkeypatch):
    """Every test gets its own data file, never the real `todos.db`."""
    monkeypatch.setenv("TODO_DB", str(tmp_path / "todos.db"))
