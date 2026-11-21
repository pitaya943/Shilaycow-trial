"""HTTP layer: turns store results and errors into HTTP responses."""

from fastapi import FastAPI

from todo_api.store import TodoStore


def create_app() -> FastAPI:
    app = FastAPI(title="todo-api")
    app.state.store = TodoStore()
    return app


app = create_app()
