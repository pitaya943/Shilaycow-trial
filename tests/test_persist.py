"""The list survives a restart: a second app on the same file sees the same todos."""

import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from todo_api.app import create_app


def _start(db_path):
    """A new app on the same file stands in for stopping and starting the service."""
    return TestClient(create_app(db_path=db_path))


def test_todos_due_dates_and_done_survive_a_restart(tmp_path):
    db_path = tmp_path / "todos.db"
    before = _start(db_path)
    before.post("/todos", json={"title": "繳電費", "due_date": "2026-12-01"})
    before.post("/todos", json={"title": "買牛奶"})
    before.post("/todos/2/complete")

    after = _start(db_path)

    assert after.get("/todos").json() == [
        {"id": 1, "title": "繳電費", "done": False, "due_date": "2026-12-01"},
        {"id": 2, "title": "買牛奶", "done": True},
    ]


def test_ids_continue_after_a_restart(tmp_path):
    db_path = tmp_path / "todos.db"
    before = _start(db_path)
    before.post("/todos", json={"title": "繳電費"})
    before.post("/todos", json={"title": "買牛奶"})

    created = _start(db_path).post("/todos", json={"title": "倒垃圾"})

    assert created.status_code == 201
    assert created.json() == {"id": 3, "title": "倒垃圾", "done": False}


def test_first_start_creates_the_file_and_lists_nothing(tmp_path):
    db_path = tmp_path / "todos.db"
    assert not db_path.exists()

    client = _start(db_path)

    assert client.get("/todos").json() == []
    assert db_path.is_file()


def test_path_comes_from_TODO_DB_when_no_argument_is_given(tmp_path, monkeypatch):
    db_path = tmp_path / "from-env.db"
    monkeypatch.setenv("TODO_DB", str(db_path))
    TestClient(create_app()).post("/todos", json={"title": "買牛奶"})

    assert db_path.is_file()
    assert TestClient(create_app()).get("/todos").json() == [
        {"id": 1, "title": "買牛奶", "done": False}
    ]


def test_argument_wins_over_TODO_DB(tmp_path, monkeypatch):
    env_path = tmp_path / "from-env.db"
    arg_path = tmp_path / "from-arg.db"
    monkeypatch.setenv("TODO_DB", str(env_path))

    TestClient(create_app(db_path=arg_path)).post("/todos", json={"title": "買牛奶"})

    assert arg_path.is_file()
    assert not env_path.exists()


def test_default_path_is_todos_db_in_the_start_directory(tmp_path, monkeypatch):
    monkeypatch.delenv("TODO_DB", raising=False)
    monkeypatch.chdir(tmp_path)

    TestClient(create_app()).post("/todos", json={"title": "買牛奶"})

    assert (tmp_path / "todos.db").is_file()


def test_importing_the_module_touches_no_file(tmp_path, monkeypatch):
    monkeypatch.delenv("TODO_DB", raising=False)
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).parent.parent))
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")

    subprocess.run(
        [sys.executable, "-c", "import todo_api.app"], cwd=tmp_path, check=True
    )

    assert list(tmp_path.iterdir()) == []
