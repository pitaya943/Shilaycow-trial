"""T-02's check: listing todos filtered by priority (S-1 to S-8).

Run from the repository root: python docs/tasks/priority-filter/tickets/T-02-check.py
Prints "T-02 check: OK" and exits 0, or names the first thing that does not hold.
S-5 compares with the code on origin/main, so fetch first.
"""

import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path.cwd()
TODAY = date(2026, 11, 23)
DETAIL = "priority must be one of: low, normal, high"
ONCE = "priority may be given only once"


def fail(message):
    print(f"T-02 check: FAIL: {message}")
    sys.exit(1)


def run(repo, script):
    """Run a probe with `repo` as the package's home; return what it printed as JSON."""
    out = subprocess.run([sys.executable, "-c", script], cwd=repo, capture_output=True, text=True)
    if out.returncode != 0:
        fail(f"probe in {repo} crashed:\n{out.stderr[-600:]}")
    return json.loads(out.stdout)


PROBE = """
import json, sqlite3
from datetime import date
from fastapi.testclient import TestClient
from todo_api.app import create_app
c = TestClient(create_app(today=lambda: date(2026, 11, 23), db_path={db!r}), raise_server_exceptions=False)
results = []
for method, url, body in {calls!r}:
    r = c.post(url, json=body) if method == "POST" else c.get(url)
    results.append([r.status_code, r.json()])
print(json.dumps(results, ensure_ascii=False))
"""


def drive(repo, db, calls):
    return run(repo, PROBE.format(db=str(db), calls=calls))


def post(title, priority=None, due=None):
    body = {"title": title}
    if priority:
        body["priority"] = priority
    if due:
        body["due_date"] = due
    return ("POST", "/todos", body)


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    # S-1, S-2: two of each, interleaved; each filter shows its own two, in insertion order.
    seed = [post(f"t{i}", p) for i, p in enumerate(["low", "normal", "high"] * 2, 1)]
    got = drive(ROOT, tmp / "s1.db", seed + [("GET", f"/todos?priority={p}", None) for p in ("low", "normal", "high")])
    for p, (status, body) in zip(("low", "normal", "high"), got[6:]):
        titles = [t["title"] for t in body] if status == 200 else body
        want = [f"t{i}" for i, q in enumerate(["low", "normal", "high"] * 2, 1) if q == p]
        if status != 200 or titles != want or any(t["priority"] != p for t in body):
            fail(f"S-1: ?priority={p} gave {status} {titles}, expected 200 {want}")
        if any(set(t) < {"id", "title", "done", "priority"} for t in body):
            fail(f"S-1: a todo in ?priority={p} lacks a field: {body}")
    status, body = drive(ROOT, tmp / "s2.db", [post("a", "high"), ("GET", "/todos?priority=low", None)])[1]
    if (status, body) != (200, []):
        fail(f"S-2: ?priority=low with no low todo gave {status} {body}")

    # S-3: wrong values and a repeated parameter are refused, and nothing changes.
    bad = ["urgent", "High", "%20high", ""]
    got = drive(ROOT, tmp / "s3.db", [post("a", "low")] + [("GET", f"/todos?priority={v}", None) for v in bad]
                + [("GET", "/todos?priority=low&priority=high", None), ("GET", "/todos", None)])
    for v, (status, body) in zip(bad, got[1:5]):
        if (status, body) != (422, {"detail": DETAIL}):
            fail(f"S-3: ?priority={v!r} gave {status} {body}")
    if tuple(got[5]) != (422, {"detail": ONCE}):
        fail(f"S-3: a repeated priority gave {got[5]}, expected 422 {{'detail': {ONCE!r}}}")
    if [t["title"] for t in got[6][1]] != ["a"]:
        fail(f"S-3: the list changed: {got[6]}")

    # S-4: both filters at once.
    got = drive(ROOT, tmp / "s4.db", [post("late-high", "high", "2026-11-01"), post("late-low", "low", "2026-11-01"),
                                      post("soon-high", "high", "2026-12-01"),
                                      ("GET", "/todos?overdue=true&priority=high", None)])
    if [t["title"] for t in got[3][1]] != ["late-high"]:
        fail(f"S-4: overdue + high gave {got[3]}")

    # S-5: without a filter, the same answers as the code on origin/main.
    base = tmp / "main"
    base.mkdir()
    archive = subprocess.run(["git", "archive", "origin/main", "todo_api"], cwd=ROOT, capture_output=True)
    if archive.returncode != 0:
        fail("S-5: cannot read todo_api from origin/main; run git fetch")
    subprocess.run(["tar", "-x", "-C", str(base)], input=archive.stdout, check=True)
    fixed = [post("a", "low", "2026-11-01"), post("b"), post("c", "high", "2026-12-01"), post("d", "high", "2026-10-01"),
             ("POST", "/todos/2/complete", None), ("GET", "/todos", None), ("GET", "/todos?overdue=true", None)]
    before = drive(base, tmp / "s5-main.db", fixed)
    after = drive(ROOT, tmp / "s5-now.db", fixed)
    if before != after:
        fail(f"S-5: without a filter the answers differ from origin/main:\n  main {before[-2:]}\n  now  {after[-2:]}")

    # S-6: an old data file, written before priorities, lists every todo under normal.
    old = tmp / "old.db"
    db = sqlite3.connect(old)
    db.execute("PRAGMA application_id = 1953457263")
    db.execute("CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER NOT NULL, due_date TEXT)")
    db.executemany("INSERT INTO todos (title, done, due_date) VALUES (?, ?, ?)", [("舊一", 0, None), ("舊二", 1, "2026-12-01")])
    db.commit()
    db.close()
    got = drive(ROOT, old, [("GET", "/todos?priority=normal", None)])
    if [t["title"] for t in got[0][1]] != ["舊一", "舊二"]:
        fail(f"S-6: an old data file under ?priority=normal gave {got[0]}")

    # S-7: a list query parameter without declared values makes the guard test fail, by name.
    guard = ROOT / "tests/test_query_params.py"
    if not guard.exists():
        fail("S-7: tests/test_query_params.py does not exist")
    copy = tmp / "s7"
    shutil.copytree(ROOT / "todo_api", copy / "todo_api")
    shutil.copytree(ROOT / "tests", copy / "tests")
    app = copy / "todo_api/app.py"
    text = app.read_text(encoding="utf-8")
    if "def list_todos(" not in text:
        fail("S-7: no list_todos( in todo_api/app.py to add a parameter to")
    app.write_text(text.replace("def list_todos(", "def list_todos(tag: str | None = None, ", 1), encoding="utf-8")
    out = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_query_params.py"], cwd=copy,
                         capture_output=True, text=True)
    if out.returncode == 0 or "tag" not in out.stdout:
        fail(f"S-7: with an undeclared `tag` parameter the guard test did not fail naming it:\n{out.stdout[-600:]}")

    # S-8: with "urgent" added in the one place only, a fresh data file creates and filters it.
    copy = tmp / "s8"
    shutil.copytree(ROOT / "todo_api", copy / "todo_api")
    store = copy / "todo_api/store.py"
    store.write_text(store.read_text(encoding="utf-8").replace(
        'PRIORITIES = ("low", "normal", "high")', 'PRIORITIES = ("low", "normal", "high", "urgent")'), encoding="utf-8")
    got = drive(copy, tmp / "s8.db", [post("x", "urgent"), ("GET", "/todos?priority=urgent", None)])
    if got[0][0] != 201 or [t["title"] for t in got[1][1]] != ["x"]:
        fail(f"S-8: with urgent added in store.py only: create {got[0]}, filter {got[1]}")

print("T-02 check: OK")
