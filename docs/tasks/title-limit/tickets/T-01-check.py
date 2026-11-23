"""T-01's check: S-1..S-4 over HTTP, S-5 by running the guard test. Run from the repository root."""
import sqlite3, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from todo_api.app import create_app

db = Path(tempfile.mkdtemp()) / "todos.db"
c = TestClient(create_app(db_path=db))
r = c.post("/todos", json={"title": "字" * 200})
assert r.status_code == 201 and r.json()["title"] == "字" * 200, ("S-1", r.status_code)
r = c.post("/todos", json={"title": "字" * 201})
assert r.status_code == 422 and "200" in r.text, ("S-2", r.status_code, r.text[:80])
r = c.post("/todos", json={"title": "  " + "字" * 200 + "  "})
assert r.status_code == 201 and r.json()["title"] == "字" * 200, ("S-3", r.status_code)
assert len(c.get("/todos").json()) == 2, "S-2 nothing added"

# S-4: a 500-character title already in the data file.
with sqlite3.connect(db) as conn:
    conn.execute("INSERT INTO todos (title, done, priority) VALUES (?, 0, 'normal')", ("長" * 500,))
c2 = TestClient(create_app(db_path=db))
long = [t for t in c2.get("/todos").json() if len(t["title"]) == 500]
assert long, "S-4 list"
assert c2.post(f"/todos/{long[0]['id']}/complete").status_code == 200, "S-4 complete"

# S-5: the guard exists and passes on the code as it is.
guard = subprocess.run([sys.executable, "-m", "pytest", "-q", "-k", "limit", "tests/test_field_limits.py"], capture_output=True, text=True)
assert guard.returncode == 0 and "passed" in guard.stdout, ("S-5", guard.stdout[-300:])
print("T-01 check: OK")
