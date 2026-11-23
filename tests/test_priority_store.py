"""Each todo keeps a priority; a data file from before priorities is upgraded in place."""

import sqlite3
import threading
import time
from datetime import date

import pytest

from todo_api.store import StoreUnreadable, TodoStore

# The mark the service puts on its own data file ("todo" in ASCII).
OURS = 0x746F646F


def _old_data_file(path):
    """A data file as the service wrote it before priorities existed."""
    db = sqlite3.connect(path)
    db.execute(f"PRAGMA application_id = {OURS}")
    db.execute(
        "CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "title TEXT NOT NULL, done INTEGER NOT NULL, due_date TEXT)"
    )
    db.execute("INSERT INTO todos (title, done, due_date) VALUES ('繳電費', 0, '2026-12-01')")
    db.execute("INSERT INTO todos (title, done, due_date) VALUES ('買牛奶', 1, NULL)")
    # The highest id handed out was 3, though todo 3 is gone.
    db.execute("INSERT INTO todos (title, done, due_date) VALUES ('刪掉的', 0, NULL)")
    db.execute("DELETE FROM todos WHERE id = 3")
    db.commit()
    db.close()


def _listed(store):
    return [(t.id, t.title, t.done, t.due_date, t.priority) for t in store.list()]


def test_a_new_todo_is_normal_unless_given_a_priority(tmp_path):
    store = TodoStore(tmp_path / "todos.db")

    assert store.add("買牛奶").priority == "normal"
    assert store.add("繳房租", priority="high").priority == "high"
    assert [t.priority for t in store.list()] == ["normal", "high"]


def test_a_priority_survives_a_reopen(tmp_path):
    path = tmp_path / "todos.db"
    TodoStore(path).add("倒垃圾", priority="low")

    assert [t.priority for t in TodoStore(path).list()] == ["low"]


def test_the_table_refuses_a_priority_it_does_not_know(tmp_path):
    store = TodoStore(tmp_path / "todos.db")

    with pytest.raises(sqlite3.IntegrityError):
        store.add("x", priority="urgent")
    assert store.list() == []


def test_an_old_data_file_opens_with_its_todos_unchanged_and_normal(tmp_path):
    path = tmp_path / "todos.db"
    _old_data_file(path)

    store = TodoStore(path)

    assert _listed(store) == [
        (1, "繳電費", False, date(2026, 12, 1), "normal"),
        (2, "買牛奶", True, None, "normal"),
    ]
    # Ids go on from the old file's sequence, not from the highest id left.
    assert store.add("倒垃圾", priority="low").id == 4
    assert _listed(TodoStore(path))[-1] == (4, "倒垃圾", False, None, "low")


def test_two_stores_opening_one_old_file_at_once_both_succeed(tmp_path):
    path = tmp_path / "todos.db"
    _old_data_file(path)
    # Hold the write lock so both stores reach their upgrade before either
    # can write; then let them go together.
    blocker = sqlite3.connect(path, isolation_level=None)
    blocker.execute("BEGIN IMMEDIATE")
    errors = []

    def open_store():
        try:
            TodoStore(path)
        except StoreUnreadable as error:
            errors.append(error)

    threads = [threading.Thread(target=open_store) for _ in range(2)]
    for thread in threads:
        thread.start()
    time.sleep(0.5)
    blocker.execute("COMMIT")
    blocker.close()
    for thread in threads:
        thread.join()

    assert errors == []
    assert [t.priority for t in TodoStore(path).list()] == ["normal", "normal"]
