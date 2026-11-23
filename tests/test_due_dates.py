from datetime import date

import pytest
from fastapi.testclient import TestClient

from todo_api.app import create_app

# The scenarios say "yesterday" and "tomorrow"; the tests pin today so those
# words mean the same dates on every run.
TODAY = date(2026, 11, 21)
YESTERDAY = "2026-11-20"
TOMORROW = "2026-11-22"


@pytest.fixture
def client():
    return TestClient(create_app(today=lambda: TODAY))


def test_create_with_due_date_returns_it(client):
    response = client.post("/todos", json={"title": "繳電費", "due_date": "2026-12-01"})

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "繳電費",
        "done": False,
        "due_date": "2026-12-01",
        "priority": "normal",
    }
    assert client.get("/todos").json() == [
        {"id": 1, "title": "繳電費", "done": False, "due_date": "2026-12-01", "priority": "normal"},
    ]


def test_create_without_due_date_has_none_and_is_otherwise_as_before(client):
    response = client.post("/todos", json={"title": "買牛奶"})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "買牛奶", "done": False, "priority": "normal"}
    assert client.get("/todos").json() == [
        {"id": 1, "title": "買牛奶", "done": False, "priority": "normal"},
    ]


def test_overdue_lists_only_unfinished_todos_due_before_today(client):
    client.post("/todos", json={"title": "A", "due_date": YESTERDAY})
    client.post("/todos", json={"title": "B", "due_date": TOMORROW})
    client.post("/todos", json={"title": "C"})
    client.post("/todos", json={"title": "D", "due_date": YESTERDAY})
    client.post("/todos/4/complete")

    response = client.get("/todos", params={"overdue": "true"})

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "title": "A", "done": False, "due_date": YESTERDAY, "priority": "normal"},
    ]
    assert len(client.get("/todos").json()) == 4


def test_a_todo_due_today_is_not_overdue(client):
    client.post("/todos", json={"title": "今天到期", "due_date": TODAY.isoformat()})

    assert client.get("/todos", params={"overdue": "true"}).json() == []


@pytest.mark.parametrize(
    "bad",
    ["下週五", "2026/12/01", "2026-12-1", "20261201", "2026-02-30", "2026-12-01T10:00:00", ""],
)
def test_malformed_due_date_is_rejected_and_list_unchanged(client, bad):
    client.post("/todos", json={"title": "買牛奶"})

    response = client.post("/todos", json={"title": "繳電費", "due_date": bad})

    assert response.status_code == 422
    assert response.json() == {"detail": "due_date must be a date like 2026-12-01"}
    assert client.get("/todos").json() == [
        {"id": 1, "title": "買牛奶", "done": False, "priority": "normal"},
    ]
