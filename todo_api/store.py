"""In-memory storage for todos. Knows nothing about HTTP."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False
    due_date: date | None = None


class TodoStore:
    def __init__(self) -> None:
        self._todos: list[Todo] = []
        self._next_id = 1

    def add(self, title: str, due_date: date | None = None) -> Todo:
        todo = Todo(id=self._next_id, title=title, due_date=due_date)
        self._next_id += 1
        self._todos.append(todo)
        return todo

    def list(self) -> list[Todo]:
        return list(self._todos)

    def complete(self, todo_id: int) -> Todo | None:
        for todo in self._todos:
            if todo.id == todo_id:
                todo.done = True
                return todo
        return None
