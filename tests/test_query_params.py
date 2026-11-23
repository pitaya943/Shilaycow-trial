"""Every query parameter of GET /todos declares the values it allows, and the service enforces them.

The guard for the pitfall "boundaries the brief did not decide", for listing: a
parameter added to the list route without an entry in LIST_QUERY_VALUES fails here
by name, and so does a declared parameter that lets a value outside its entry through.
"""

import pytest
from fastapi.testclient import TestClient

from todo_api.app import LIST_QUERY_VALUES, create_app


def _list_query_params():
    operation = create_app().openapi()["paths"]["/todos"]["get"]
    return sorted(p["name"] for p in operation.get("parameters", []) if p["in"] == "query")


@pytest.mark.parametrize("param", _list_query_params())
def test_every_list_query_parameter_declares_its_values(param):
    assert param in LIST_QUERY_VALUES, (
        f"GET /todos?{param}= has no declared values: add it to LIST_QUERY_VALUES in "
        "todo_api/app.py and decide what happens to any other value"
    )


@pytest.mark.parametrize("param", sorted(LIST_QUERY_VALUES))
def test_each_declared_value_is_accepted(param):
    client = TestClient(create_app())
    for value in LIST_QUERY_VALUES[param]:
        response = client.get("/todos", params={param: value})
        assert response.status_code == 200, f"?{param}={value!r} is declared but gave {response.status_code}"


@pytest.mark.parametrize("param", sorted(LIST_QUERY_VALUES))
def test_a_value_outside_the_declared_ones_is_refused(param):
    client = TestClient(create_app())
    allowed = LIST_QUERY_VALUES[param]
    outside = ["not-a-declared-value", ""]
    outside += [f" {v}" for v in allowed] + [f"{v} " for v in allowed]
    for value in outside:
        assert value not in allowed
        response = client.get("/todos", params={param: value})
        assert response.status_code == 422, f"?{param}={value!r} is not declared but was accepted"
