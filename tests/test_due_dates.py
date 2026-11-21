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
    }
    assert client.get("/todos").json() == [
        {"id": 1, "title": "繳電費", "done": False, "due_date": "2026-12-01"},
    ]


def test_create_without_due_date_has_none_and_is_otherwise_as_before(client):
    response = client.post("/todos", json={"title": "買牛奶"})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "買牛奶", "done": False}
    assert client.get("/todos").json() == [
        {"id": 1, "title": "買牛奶", "done": False},
    ]
