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

    # Defined above `list`: below it, the name `list` in an annotation would
    # mean the method, not the builtin.
    def overdue(self, today: date) -> list[Todo]:
        """Unfinished todos whose due date is before `today`, in insertion order."""
        return [
            todo
            for todo in self._todos
            if not todo.done and todo.due_date is not None and todo.due_date < today
        ]

    def list(self) -> list[Todo]:
        return list(self._todos)

    def complete(self, todo_id: int) -> Todo | None:
        for todo in self._todos:
            if todo.id == todo_id:
                todo.done = True
                return todo
        return None
