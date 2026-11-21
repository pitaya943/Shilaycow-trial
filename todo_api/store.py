"""In-memory storage for todos. Knows nothing about HTTP."""

from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False


class TodoStore:
    def __init__(self) -> None:
        self._todos: list[Todo] = []
        self._next_id = 1

    def add(self, title: str) -> Todo:
        todo = Todo(id=self._next_id, title=title)
        self._next_id += 1
        self._todos.append(todo)
        return todo
