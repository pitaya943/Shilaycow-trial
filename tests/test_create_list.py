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
    assert first.json() == {"id": 1, "title": "買牛奶", "done": False, "priority": "normal"}
    assert second.status_code == 201
    assert second.json() == {"id": 2, "title": "繳電費", "done": False, "priority": "normal"}


def test_list_returns_todos_in_insertion_order(client):
    client.post("/todos", json={"title": "買牛奶"})
    client.post("/todos", json={"title": "繳電費"})

    response = client.get("/todos")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "title": "買牛奶", "done": False, "priority": "normal"},
        {"id": 2, "title": "繳電費", "done": False, "priority": "normal"},
    ]


@pytest.mark.parametrize("blank", ["", "   ", "\t\n", "　"])
def test_blank_title_is_rejected_and_list_unchanged(client, blank):
    client.post("/todos", json={"title": "買牛奶"})

    response = client.post("/todos", json={"title": blank})

    assert response.status_code == 422
    assert response.json() == {"detail": "title must not be blank"}
    assert client.get("/todos").json() == [
        {"id": 1, "title": "買牛奶", "done": False, "priority": "normal"},
    ]


def test_title_is_stored_without_surrounding_whitespace(client):
    created = client.post("/todos", json={"title": "  買牛奶 \n"})

    assert created.status_code == 201
    assert created.json() == {"id": 1, "title": "買牛奶", "done": False, "priority": "normal"}
    assert client.get("/todos").json() == [
        {"id": 1, "title": "買牛奶", "done": False, "priority": "normal"},
    ]
