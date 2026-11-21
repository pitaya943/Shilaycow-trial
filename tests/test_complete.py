import pytest
from fastapi.testclient import TestClient

from todo_api.app import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_complete_unknown_id_is_not_found(client):
    client.post("/todos", json={"title": "買牛奶"})

    response = client.post("/todos/999/complete")

    assert response.status_code == 404
    assert response.json() == {"detail": "todo not found"}
    assert client.get("/todos").json() == [
        {"id": 1, "title": "買牛奶", "done": False},
    ]
