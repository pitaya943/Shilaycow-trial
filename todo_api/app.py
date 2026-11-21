"""HTTP layer: turns store results and errors into HTTP responses."""

from collections.abc import Callable
from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from todo_api.store import Todo, TodoStore


class NewTodo(BaseModel):
    title: str


class TodoOut(BaseModel):
    id: int
    title: str
    done: bool


def _out(todo: Todo) -> TodoOut:
    return TodoOut(id=todo.id, title=todo.title, done=todo.done)


def create_app(today: Callable[[], date] = date.today) -> FastAPI:
    """Build the app. `today` is the clock that decides what is overdue."""
    app = FastAPI(title="todo-api")
    store = TodoStore()
    app.state.store = store

    @app.post("/todos", status_code=201)
    def create_todo(body: NewTodo) -> TodoOut:
        title = body.title.strip()
        if not title:
            raise HTTPException(status_code=422, detail="title must not be blank")
        return _out(store.add(title))

    @app.get("/todos")
    def list_todos() -> list[TodoOut]:
        return [_out(todo) for todo in store.list()]

    @app.post("/todos/{todo_id}/complete")
    def complete_todo(todo_id: int) -> TodoOut:
        todo = store.complete(todo_id)
        if todo is None:
            raise HTTPException(status_code=404, detail="todo not found")
        return _out(todo)

    return app


app = create_app()
