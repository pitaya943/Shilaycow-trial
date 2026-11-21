import pytest
from fastapi.testclient import TestClient

from todo_api.app import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_create_returns_todo_with_id_title_not_done(client):
    first = client.post("/todos", json={"title": "買牛奶"})
    second = client.post("/todos", json={"title": "繳電費"})

    assert first.status_code == 201
    assert first.json() == {"id": 1, "title": "買牛奶", "done": False}
    assert second.status_code == 201
    assert second.json() == {"id": 2, "title": "繳電費", "done": False}


def test_list_returns_todos_in_insertion_order(client):
    client.post("/todos", json={"title": "買牛奶"})
    client.post("/todos", json={"title": "繳電費"})

    response = client.get("/todos")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "title": "買牛奶", "done": False},
        {"id": 2, "title": "繳電費", "done": False},
    ]
