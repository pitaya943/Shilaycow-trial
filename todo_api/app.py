"""HTTP layer: turns store results and errors into HTTP responses."""

import os
import re
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from todo_api.store import Todo, TodoStore


class NewTodo(BaseModel):
    title: str
    # Kept as text so the route owns the format rule and its one message.
    due_date: str | None = None
    # Any JSON value, so the route owns the rule and its one message.
    priority: Any = None


PRIORITIES = ("low", "normal", "high")

# The longest value, in characters, each field of a new todo may hold.
# tests/test_field_limits.py fails for a NewTodo field missing here, and for a
# limit the route does not enforce: decide the limit when adding the field.
INPUT_LIMITS = {
    "title": 200,  # counted after trimming surrounding whitespace
    "due_date": len("2026-12-01"),  # bounded by the date format
    "priority": max(len(p) for p in PRIORITIES),  # bounded by the three values
}


class TodoOut(BaseModel):
    id: int
    title: str
    done: bool
    due_date: date | None = None
    priority: str


def _out(todo: Todo) -> TodoOut:
    return TodoOut(
        id=todo.id,
        title=todo.title,
        done=todo.done,
        due_date=todo.due_date,
        priority=todo.priority,
    )


def _parse_due_date(text: str) -> date:
    """Accept exactly YYYY-MM-DD; date.fromisoformat alone also takes 20261201."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise ValueError(text)
    return date.fromisoformat(text)


def create_app(
    today: Callable[[], date] = date.today, db_path: str | Path | None = None
) -> FastAPI:
    """Build the app. `today` is the clock that decides what is overdue.

    The todos live in the file at `db_path`; without it, at `$TODO_DB`;
    without that, in `todos.db` in the directory the service was started from.
    """
    app = FastAPI(title="todo-api")
    store = TodoStore(db_path or os.environ.get("TODO_DB") or "todos.db")
    app.state.store = store

    @app.post("/todos", status_code=201, response_model_exclude_none=True)
    def create_todo(body: NewTodo) -> TodoOut:
        title = body.title.strip()
        if not title:
            raise HTTPException(status_code=422, detail="title must not be blank")
        if len(title) > INPUT_LIMITS["title"]:
            raise HTTPException(
                status_code=422,
                detail=f"title must be at most {INPUT_LIMITS['title']} characters",
            )
        due_date = None
        if body.due_date is not None:
            try:
                due_date = _parse_due_date(body.due_date)
            except ValueError:
                raise HTTPException(
                    status_code=422, detail="due_date must be a date like 2026-12-01"
                )
        priority = "normal" if body.priority is None else body.priority
        # Exactly one of the three; no trimming or case folding.
        if priority not in PRIORITIES:
            raise HTTPException(
                status_code=422,
                detail="priority must be one of: " + ", ".join(PRIORITIES),
            )
        return _out(store.add(title, due_date, priority))

    @app.get("/todos", response_model_exclude_none=True)
    def list_todos(overdue: bool = False) -> list[TodoOut]:
        todos = store.overdue(today()) if overdue else store.list()
        return [_out(todo) for todo in todos]

    @app.post("/todos/{todo_id}/complete", response_model_exclude_none=True)
    def complete_todo(todo_id: int) -> TodoOut:
        todo = store.complete(todo_id)
        if todo is None:
            raise HTTPException(status_code=404, detail="todo not found")
        return _out(todo)

    return app
