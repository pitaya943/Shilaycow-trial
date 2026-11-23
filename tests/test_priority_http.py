from datetime import date

import pytest
from fastapi.testclient import TestClient

from todo_api.app import create_app

PRIORITY_MESSAGE = "priority must be one of: low, normal, high"


@pytest.fixture
def client():
    return TestClient(create_app(today=lambda: date(2026, 12, 10)))


def test_create_with_a_priority_keeps_it_in_the_answer_and_the_list(client):
    created = client.post("/todos", json={"title": "繳房租", "priority": "high"})

    assert created.status_code == 201
    assert created.json() == {"id": 1, "title": "繳房租", "done": False, "priority": "high"}
    assert client.get("/todos").json() == [
        {"id": 1, "title": "繳房租", "done": False, "priority": "high"}
    ]


@pytest.mark.parametrize("body", [{"title": "買牛奶"}, {"title": "買牛奶", "priority": None}])
def test_without_a_priority_it_is_normal(client, body):
    created = client.post("/todos", json=body)

    assert created.status_code == 201
    assert created.json()["priority"] == "normal"
    assert client.get("/todos").json()[0]["priority"] == "normal"


@pytest.mark.parametrize("bad", ["urgent", "High", " high", "high ", "", 1, True, ["high"]])
def test_an_unknown_priority_is_rejected_and_nothing_is_added(client, bad):
    client.post("/todos", json={"title": "買牛奶"})

    response = client.post("/todos", json={"title": "x", "priority": bad})

    assert response.status_code == 422
    assert response.json() == {"detail": PRIORITY_MESSAGE}
    assert [t["title"] for t in client.get("/todos").json()] == ["買牛奶"]


def test_overdue_list_and_complete_keep_the_priority(client):
    tid = client.post(
        "/todos", json={"title": "報稅", "priority": "high", "due_date": "2026-12-01"}
    ).json()["id"]

    overdue = client.get("/todos", params={"overdue": "true"}).json()
    completed = client.post(f"/todos/{tid}/complete")

    assert [(t["id"], t["priority"]) for t in overdue] == [(tid, "high")]
    assert completed.status_code == 200
    assert completed.json()["priority"] == "high"
