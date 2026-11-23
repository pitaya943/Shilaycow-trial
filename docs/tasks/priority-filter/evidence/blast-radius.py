"""Blast radius of priority-filter against main: the same requests to origin/main's code and
to this checkout's, compared answer by answer. Only requests with `priority` on the list may differ.

Run from the repository root after `git fetch origin`:
    python docs/tasks/priority-filter/evidence/blast-radius.py
"""
import json, subprocess, sys, tempfile
from pathlib import Path

CALLS = [
    ("POST", "/todos", {"title": "a", "priority": "high", "due_date": "2026-11-01"}),
    ("POST", "/todos", {"title": "b"}),
    ("POST", "/todos", {"title": "c", "priority": "urgent"}),
    ("POST", "/todos", {"title": "d", "priority": "High"}),
    ("POST", "/todos", {"title": "e", "priority": None}),
    ("POST", "/todos", {"title": "f", "priority": 1}),
    ("POST", "/todos", {"title": "x" * 201}),
    ("POST", "/todos/1/complete", None),
    ("POST", "/todos/99999999999999999999/complete", None),
    ("GET", "/todos", None),
    ("GET", "/todos?overdue=true", None),
    ("GET", "/todos?overdue=TRUE", None),
    ("GET", "/todos?overdue=maybe", None),
    ("GET", "/todos?Priority=high", None),
    ("GET", "/todos?other=1", None),
    ("GET", "/todos?priority=high", None),
    ("GET", "/todos?priority=", None),
]
PROBE = """
import json
from datetime import date
from fastapi.testclient import TestClient
from todo_api.app import create_app
c = TestClient(create_app(today=lambda: date(2026, 11, 23), db_path={db!r}), raise_server_exceptions=False)
out = []
for m, u, b in {calls!r}:
    r = c.post(u, json=b) if m == "POST" else c.get(u)
    out.append([r.status_code, r.text])
print(json.dumps(out))
"""
with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp) / "main"; base.mkdir()
    tar = subprocess.run(["git", "archive", "origin/main", "todo_api"], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(base)], input=tar, check=True)
    res = {}
    for name, repo in (("main", base), ("head", Path.cwd())):
        p = subprocess.run([sys.executable, "-c", PROBE.format(db=f"{tmp}/{name}.db", calls=CALLS)], cwd=repo,
                           capture_output=True, text=True, check=True)
        res[name] = json.loads(p.stdout)
    unexpected = 0
    for (m, u, b), x, y in zip(CALLS, res["main"], res["head"]):
        same = x == y
        allowed = "priority=" in u
        mark = "same" if same else ("differs (expected: filter)" if allowed else "DIFFERS")
        unexpected += (not same and not allowed)
        print(f"{mark:28} {m} {u} {json.dumps(b, ensure_ascii=False)[:40]}\n    main {x[0]} {x[1][:90]}\n    head {y[0]} {y[1][:90]}")
    print(f"{len(CALLS)} requests, {unexpected} unexpected differences")
    sys.exit(1 if unexpected else 0)
