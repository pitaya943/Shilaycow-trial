"""A title is at most 200 characters, counted after trimming; older long titles still work."""

import sqlite3

from fastapi.testclient import TestClient

from todo_api.app import create_app


def _client(tmp_path):
    return TestClient(create_app(db_path=tmp_path / "todos.db"))


def test_a_title_of_exactly_200_characters_is_accepted_as_sent(tmp_path):
    client = _client(tmp_path)
    response = client.post("/todos", json={"title": "字" * 200})
    assert response.status_code == 201
    assert client.get("/todos").json()[0]["title"] == "字" * 200


def test_a_title_of_201_characters_is_refused_and_nothing_is_added(tmp_path):
    client = _client(tmp_path)
    response = client.post("/todos", json={"title": "字" * 201})
    assert response.status_code == 422
    assert response.json() == {"detail": "title must be at most 200 characters"}
    assert client.get("/todos").json() == []


def test_surrounding_whitespace_does_not_count(tmp_path):
    client = _client(tmp_path)
    response = client.post("/todos", json={"title": "   " + "字" * 200 + "   "})
    assert response.status_code == 201
    assert response.json()["title"] == "字" * 200


def test_a_longer_title_already_stored_can_be_listed_and_completed(tmp_path):
    db = tmp_path / "todos.db"
    _client(tmp_path)  # creates the data file
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO todos (title, done, priority) VALUES (?, 0, 'normal')", ("長" * 500,))
    client = TestClient(create_app(db_path=db))
    assert client.get("/todos").json()[0]["title"] == "長" * 500
    assert client.post("/todos/1/complete").status_code == 200
