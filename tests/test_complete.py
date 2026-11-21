import pytest
from fastapi.testclient import TestClient

from todo_api.app import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_complete_marks_only_that_todo_done(client):
    client.post("/todos", json={"title": "買牛奶"})
    client.post("/todos", json={"title": "繳電費"})

    response = client.post("/todos/1/complete")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "買牛奶", "done": True}
    assert client.get("/todos").json() == [
        {"id": 1, "title": "買牛奶", "done": True},
        {"id": 2, "title": "繳電費", "done": False},
    ]


def test_completing_an_already_done_todo_is_ok_and_keeps_it_done(client):
    client.post("/todos", json={"title": "買牛奶"})
    client.post("/todos/1/complete")

    again = client.post("/todos/1/complete")

    assert again.status_code == 200
    assert again.json() == {"id": 1, "title": "買牛奶", "done": True}
    assert client.get("/todos").json() == [
        {"id": 1, "title": "買牛奶", "done": True},
    ]


def test_complete_unknown_id_is_not_found(client):
    client.post("/todos", json={"title": "買牛奶"})

    response = client.post("/todos/999/complete")

    assert response.status_code == 404
    assert response.json() == {"detail": "todo not found"}
    assert client.get("/todos").json() == [
        {"id": 1, "title": "買牛奶", "done": False},
    ]
