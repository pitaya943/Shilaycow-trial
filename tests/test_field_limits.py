"""Every field a new todo accepts has a declared length limit, and the service enforces it.

The guard for the pitfall "boundaries the brief did not decide": a field added to
NewTodo without an entry in INPUT_LIMITS fails here by name, and so does a declared
limit the route does not actually enforce (the way `title` was before title-limit).
"""

import pytest
from fastapi.testclient import TestClient

from todo_api.app import INPUT_LIMITS, NewTodo, create_app


@pytest.mark.parametrize("field", sorted(NewTodo.model_fields))
def test_every_new_todo_field_declares_a_limit(field):
    assert field in INPUT_LIMITS, (
        f"NewTodo.{field} has no length limit: add it to INPUT_LIMITS in todo_api/app.py "
        "and decide what happens to a longer value"
    )


@pytest.mark.parametrize("field", sorted(INPUT_LIMITS))
def test_a_value_one_past_the_limit_is_refused_and_nothing_is_added(field, tmp_path):
    client = TestClient(create_app(db_path=tmp_path / "todos.db"))
    body = {"title": "ok", field: "x" * (INPUT_LIMITS[field] + 1)}
    response = client.post("/todos", json=body)
    assert response.status_code == 422, f"{field}: {INPUT_LIMITS[field] + 1} characters were accepted"
    assert client.get("/todos").json() == []
