"""GET /todos?priority=... lists only the todos of that one priority."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from todo_api.app import create_app
from tests.test_priority_store import _old_data_file

PRIORITY_MESSAGE = "priority must be one of: low, normal, high"


@pytest.fixture
def client():
    return TestClient(create_app(today=lambda: date(2026, 11, 23)))


def _titles(response):
    return [t["title"] for t in response.json()]


@pytest.mark.parametrize(
    "priority, titles", [("low", ["t1", "t4"]), ("normal", ["t2", "t5"]), ("high", ["t3", "t6"])]
)
def test_only_that_priority_in_insertion_order(client, priority, titles):
    for i, p in enumerate(["low", "normal", "high"] * 2, 1):
        client.post("/todos", json={"title": f"t{i}", "priority": p})

    response = client.get("/todos", params={"priority": priority})

    assert response.status_code == 200
    ids = [int(t[1:]) for t in titles]
    assert response.json() == [
        {"id": i, "title": t, "done": False, "priority": priority} for i, t in zip(ids, titles)
    ]


def test_no_match_is_an_empty_list(client):
    client.post("/todos", json={"title": "a", "priority": "high"})
    client.post("/todos", json={"title": "b"})

    response = client.get("/todos", params={"priority": "low"})

    assert (response.status_code, response.json()) == (200, [])


@pytest.mark.parametrize("bad", ["urgent", "High", " high", "high ", ""])
def test_an_unknown_priority_is_refused_with_the_create_message(client, bad):
    client.post("/todos", json={"title": "a", "priority": "low"})

    response = client.get("/todos", params={"priority": bad})

    assert (response.status_code, response.json()) == (422, {"detail": PRIORITY_MESSAGE})
    assert _titles(client.get("/todos")) == ["a"]


@pytest.mark.parametrize("twice", ["priority=low&priority=high", "priority=high&priority=high"])
def test_priority_given_twice_is_refused(client, twice):
    response = client.get(f"/todos?{twice}")

    assert (response.status_code, response.json()) == (
        422,
        {"detail": "priority may be given only once"},
    )


def test_with_overdue_both_must_hold(client):
    client.post("/todos", json={"title": "late-high", "priority": "high", "due_date": "2026-11-01"})
    client.post("/todos", json={"title": "late-low", "priority": "low", "due_date": "2026-11-01"})
    client.post("/todos", json={"title": "soon-high", "priority": "high", "due_date": "2026-12-01"})

    response = client.get("/todos?overdue=true&priority=high")

    assert response.status_code == 200
    assert _titles(response) == ["late-high"]


def test_an_old_data_file_lists_every_todo_under_normal(tmp_path):
    path = tmp_path / "old.db"
    _old_data_file(path)
    client = TestClient(create_app(db_path=path))
    client.post("/todos", json={"title": "新的", "priority": "high"})

    response = client.get("/todos", params={"priority": "normal"})

    assert _titles(response) == ["繳電費", "買牛奶"]
