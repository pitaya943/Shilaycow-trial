"""A data file this service did not write stops the start and is left alone."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from todo_api.app import create_app
from todo_api.store import StoreUnreadable, TodoStore


def _tables(path):
    db = sqlite3.connect(path)
    try:
        return [name for (name,) in db.execute("SELECT name FROM sqlite_master")]
    finally:
        db.close()


def _database(path, schema):
    db = sqlite3.connect(path)
    db.execute(schema)
    db.commit()
    db.close()


@pytest.mark.parametrize(
    "garbage",
    [b"not a database", "這不是資料庫\n".encode() * 200],
    ids=["shorter than a header", "longer than a page"],
)
def test_garbage_is_refused_and_not_touched(tmp_path, garbage):
    path = tmp_path / "todos.db"
    path.write_bytes(garbage)

    with pytest.raises(StoreUnreadable) as raised:
        TodoStore(path)

    assert str(path) in str(raised.value)
    assert path.read_bytes() == garbage
    assert [entry.name for entry in tmp_path.iterdir()] == ["todos.db"]


def test_a_database_of_something_else_is_refused_and_gets_no_todos_table(tmp_path):
    path = tmp_path / "todos.db"
    _database(path, "CREATE TABLE recipes (name TEXT)")
    before = path.read_bytes()

    with pytest.raises(StoreUnreadable) as raised:
        TodoStore(path)

    assert str(path) in str(raised.value)
    assert _tables(path) == ["recipes"]
    assert path.read_bytes() == before


def test_a_database_holding_only_a_view_is_refused_and_not_touched(tmp_path):
    # It has no table at all, yet it is still someone else's database.
    path = tmp_path / "todos.db"
    _database(path, "CREATE VIEW answers AS SELECT 42 AS answer")
    before = path.read_bytes()

    with pytest.raises(StoreUnreadable) as raised:
        TodoStore(path)

    assert str(path) in str(raised.value)
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "schema",
    [
        "CREATE TABLE todos (id INTEGER PRIMARY KEY, title TEXT NOT NULL)",
        "CREATE TABLE todos (id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
        "done INTEGER NOT NULL, due_date TEXT, owner TEXT)",
        "CREATE TABLE todos (id INTEGER PRIMARY KEY, name TEXT NOT NULL, "
        "done INTEGER NOT NULL, due_date TEXT)",
    ],
    ids=["columns missing", "a column too many", "a column renamed"],
)
def test_a_todos_table_with_other_columns_is_refused(tmp_path, schema):
    path = tmp_path / "todos.db"
    _database(path, schema)
    before = path.read_bytes()

    with pytest.raises(StoreUnreadable) as raised:
        TodoStore(path)

    assert str(path) in str(raised.value)
    assert path.read_bytes() == before


def test_a_file_in_a_directory_that_does_not_exist_is_refused(tmp_path):
    path = tmp_path / "no-such-directory" / "todos.db"

    with pytest.raises(StoreUnreadable) as raised:
        TodoStore(path)

    assert str(path) in str(raised.value)
    assert not path.parent.exists()


def test_a_directory_is_refused(tmp_path):
    with pytest.raises(StoreUnreadable) as raised:
        TodoStore(tmp_path)

    assert str(tmp_path) in str(raised.value)
    assert list(tmp_path.iterdir()) == []


def test_an_empty_file_is_a_first_start(tmp_path):
    path = tmp_path / "todos.db"
    path.write_bytes(b"")

    client = TestClient(create_app(db_path=path))

    assert client.get("/todos").json() == []
    created = client.post("/todos", json={"title": "買牛奶"})
    assert created.json() == {"id": 1, "title": "買牛奶", "done": False}


def test_the_service_does_not_start_on_garbage(tmp_path):
    path = tmp_path / "todos.db"
    path.write_bytes(b"not a database")

    with pytest.raises(StoreUnreadable):
        create_app(db_path=path)

    assert path.read_bytes() == b"not a database"
