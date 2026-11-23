"""T-01's check: the allowed priorities are written in one place.

Run from the repository root: python docs/tasks/priority-filter/tickets/T-01-check.py
Prints "T-01 check: OK" and exits 0, or names the first thing that does not hold.
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
OLD_CHECK = "priority TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high'))"
ONE_PLACE = 'PRIORITIES = ("low", "normal", "high")'


def fail(message):
    print(f"T-01 check: FAIL: {message}")
    sys.exit(1)


# 1. The three values are spelled out once in the package: as the one tuple in store.py.
sources = {p: p.read_text(encoding="utf-8") for p in sorted((ROOT / "todo_api").glob("*.py"))}
spelled = [str(p.relative_to(ROOT)) for p, text in sources.items() if re.search(r"""['"]high['"]""", text)]
if spelled != ["todo_api/store.py"]:
    fail(f"'high' is written in {spelled or 'no file'}; expected only todo_api/store.py")
if sources[ROOT / "todo_api/store.py"].count(ONE_PLACE) != 1:
    fail(f"todo_api/store.py does not define {ONE_PLACE} exactly once")

# 2. A data file created now gets the very same column as before this ticket.
sys.path.insert(0, str(ROOT))
from todo_api import store  # noqa: E402

if store._PRIORITY_COLUMN != OLD_CHECK:
    fail(f"the priority column changed:\n  was {OLD_CHECK}\n  now {store._PRIORITY_COLUMN}")

# 3. Changing that one place is enough: in a copy, add "urgent" there only, start on a
# fresh data file, and create an urgent todo.
with tempfile.TemporaryDirectory() as tmp:
    copy = Path(tmp) / "repo"
    shutil.copytree(ROOT / "todo_api", copy / "todo_api")
    path = copy / "todo_api/store.py"
    path.write_text(path.read_text(encoding="utf-8").replace(
        ONE_PLACE, 'PRIORITIES = ("low", "normal", "high", "urgent")'), encoding="utf-8")
    probe = (
        "from fastapi.testclient import TestClient\n"
        "from todo_api.app import create_app\n"
        f"c = TestClient(create_app(db_path={str(Path(tmp) / 'fresh.db')!r}), raise_server_exceptions=False)\n"
        "r = c.post('/todos', json={'title': 'x', 'priority': 'urgent'})\n"
        "print(r.status_code, r.json())\n"
    )
    out = subprocess.run([sys.executable, "-c", probe], cwd=copy, capture_output=True, text=True)
    if not out.stdout.startswith("201 "):
        fail(f"with 'urgent' added in store.py only, creating one gave: {out.stdout.strip() or out.stderr.strip()[-300:]}")

print("T-01 check: OK")
