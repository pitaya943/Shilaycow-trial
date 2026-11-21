"""Storage for todos in one SQLite file. Knows nothing about HTTP."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path

_COLUMNS = "id, title, done, due_date"


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False
    due_date: date | None = None


def _todo(row: tuple) -> Todo:
    todo_id, title, done, due_date = row
    return Todo(
        id=todo_id,
        title=title,
        done=bool(done),
        due_date=date.fromisoformat(due_date) if due_date is not None else None,
    )


class TodoStore:
    def __init__(self, path: str | Path) -> None:
        """Use the file at `path`, creating it when it does not exist."""
        self._path = Path(path)
        with self._connection() as db:
            # AUTOINCREMENT: an id is never handed out twice.
            db.execute(
                "CREATE TABLE IF NOT EXISTS todos ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "title TEXT NOT NULL, "
                "done INTEGER NOT NULL, "
                "due_date TEXT)"
            )

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        """One connection per operation: committed and closed when it ends.

        Requests arrive on different threads; nothing is shared between them
        and concurrent writes are left to SQLite's own lock.
        """
        db = sqlite3.connect(self._path)
        try:
            with db:
                yield db
        finally:
            db.close()

    def add(self, title: str, due_date: date | None = None) -> Todo:
        with self._connection() as db:
            cursor = db.execute(
                "INSERT INTO todos (title, done, due_date) VALUES (?, 0, ?)",
                (title, due_date.isoformat() if due_date is not None else None),
            )
            return Todo(id=cursor.lastrowid, title=title, due_date=due_date)

    # Defined above `list`: below it, the name `list` in an annotation would
    # mean the method, not the builtin.
    def overdue(self, today: date) -> list[Todo]:
        """Unfinished todos whose due date is before `today`, in insertion order."""
        with self._connection() as db:
            # Due dates are stored as YYYY-MM-DD, which sorts as text.
            rows = db.execute(
                f"SELECT {_COLUMNS} FROM todos "
                "WHERE done = 0 AND due_date < ? ORDER BY id",
                (today.isoformat(),),
            ).fetchall()
        return [_todo(row) for row in rows]

    def list(self) -> list[Todo]:
        with self._connection() as db:
            rows = db.execute(f"SELECT {_COLUMNS} FROM todos ORDER BY id").fetchall()
        return [_todo(row) for row in rows]

    def complete(self, todo_id: int) -> Todo | None:
        with self._connection() as db:
            db.execute("UPDATE todos SET done = 1 WHERE id = ?", (todo_id,))
            row = db.execute(
                f"SELECT {_COLUMNS} FROM todos WHERE id = ?", (todo_id,)
            ).fetchone()
        return _todo(row) if row is not None else None
