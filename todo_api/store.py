"""Storage for todos in one SQLite file. Knows nothing about HTTP."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path

_COLUMNS = "id, title, done, due_date, priority"
# The columns of a data file written before todos had a priority.
_COLUMNS_BEFORE_PRIORITY = {"id", "title", "done", "due_date"}
# The one place the allowed priorities are written. A data file keeps the CHECK
# it was created with: changing this affects only files created afterwards.
PRIORITIES = ("low", "normal", "high")
_PRIORITY_COLUMN = (
    "priority TEXT NOT NULL DEFAULT 'normal' "
    "CHECK (priority IN (" + ", ".join(f"'{p}'" for p in PRIORITIES) + "))"
)
# Written into the header of a data file this service creates ("todo" in ASCII).
# A file is ours because it carries this, not because it looks unlike anything else.
_APPLICATION_ID = 0x746F646F


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False
    due_date: date | None = None
    priority: str = "normal"


def _todo(row: tuple) -> Todo:
    todo_id, title, done, due_date, priority = row
    return Todo(
        id=todo_id,
        title=title,
        done=bool(done),
        due_date=date.fromisoformat(due_date) if due_date is not None else None,
        priority=priority,
    )


class StoreUnreadable(Exception):
    """The data file cannot be used as this service's data. The message names it."""


class TodoStore:
    def __init__(self, path: str | Path) -> None:
        """Use the file at `path`, creating it when it does not exist.

        Raises StoreUnreadable, having written nothing, when the file cannot be
        opened or holds something other than this service's data.
        """
        self._path = Path(path)
        try:
            # Only a file that is not there yet, or holds nothing at all, is a
            # first start. Asking SQLite would not do: it calls a one-byte file
            # an empty database too.
            first_start = not self._path.exists() or self._path.stat().st_size == 0
            with self._connection() as db:
                # Checking the columns and upgrading them is one write
                # transaction, so a second service starting on the same old
                # file waits and then finds it already upgraded.
                db.execute("BEGIN IMMEDIATE")
                if first_start:
                    db.execute(f"PRAGMA application_id = {_APPLICATION_ID}")
                elif db.execute("PRAGMA application_id").fetchone() != (_APPLICATION_ID,):
                    raise self._unreadable("this service did not write it")
                # AUTOINCREMENT: an id is never handed out twice.
                db.execute(
                    "CREATE TABLE IF NOT EXISTS todos ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "title TEXT NOT NULL, "
                    "done INTEGER NOT NULL, "
                    f"due_date TEXT, {_PRIORITY_COLUMN})"
                )
                columns = {row[1] for row in db.execute("PRAGMA table_info(todos)")}
                if columns == _COLUMNS_BEFORE_PRIORITY:
                    # Every existing row takes the default, normal.
                    db.execute(f"ALTER TABLE todos ADD COLUMN {_PRIORITY_COLUMN}")
                elif columns != set(_COLUMNS.split(", ")):
                    raise self._unreadable("its todos table has other columns")
        except (sqlite3.Error, OSError) as error:
            raise self._unreadable(str(error)) from error

    def _unreadable(self, reason: str) -> StoreUnreadable:
        return StoreUnreadable(f"cannot use the data file {self._path}: {reason}")

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

    def add(
        self, title: str, due_date: date | None = None, priority: str = "normal"
    ) -> Todo:
        """Raises sqlite3.IntegrityError for a priority not in PRIORITIES."""
        with self._connection() as db:
            cursor = db.execute(
                "INSERT INTO todos (title, done, due_date, priority) VALUES (?, 0, ?, ?)",
                (title, due_date.isoformat() if due_date is not None else None, priority),
            )
            return Todo(
                id=cursor.lastrowid, title=title, due_date=due_date, priority=priority
            )

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
        # SQLite ids are 64-bit; a number outside that is no todo's id, and
        # sqlite3 would refuse to bind it.
        if not -(2**63) <= todo_id < 2**63:
            return None
        with self._connection() as db:
            db.execute("UPDATE todos SET done = 1 WHERE id = ?", (todo_id,))
            row = db.execute(
                f"SELECT {_COLUMNS} FROM todos WHERE id = ?", (todo_id,)
            ).fetchone()
        return _todo(row) if row is not None else None
