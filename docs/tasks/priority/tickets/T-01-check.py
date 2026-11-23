"""T-01's check: an old data file opens with priority normal; priority survives a reopen.

Run from the repository root. Uses `main`'s store.py to write the old-format file.
"""
import importlib.util, subprocess, sys, tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, ".")
old_src = subprocess.run(["git", "show", "origin/main:todo_api/store.py"], capture_output=True, text=True, check=True).stdout
tmp = Path(tempfile.mkdtemp())
(tmp / "old_store.py").write_text(old_src)
spec = importlib.util.spec_from_file_location("old_store", tmp / "old_store.py")
old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)

db = tmp / "todos.db"
s = old.TodoStore(db)
s.add("繳電費", date(2026, 12, 1)); s.add("買牛奶"); s.complete(2)

from todo_api.store import TodoStore
new = TodoStore(db)
got = [(t.id, t.title, t.done, t.due_date, getattr(t, "priority", None)) for t in new.list()]
want = [(1, "繳電費", False, date(2026, 12, 1), "normal"), (2, "買牛奶", True, None, "normal")]
assert got == want, f"S-5: {got}"

added = new.add("倒垃圾", priority="low")
assert added.id == 3, added
again = [t.priority for t in TodoStore(db).list()]
assert again == ["normal", "normal", "low"], f"S-4: {again}"

print("T-01 check: OK")
