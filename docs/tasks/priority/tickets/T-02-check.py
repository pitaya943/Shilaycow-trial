"""T-02's check: S-1, S-2, S-3, S-6 over HTTP. Run from the repository root."""
import sys, tempfile
from datetime import date
from pathlib import Path
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from todo_api.app import create_app

db = Path(tempfile.mkdtemp()) / "todos.db"
c = TestClient(create_app(today=lambda: date(2026, 12, 10), db_path=db))

r = c.post("/todos", json={"title": "繳房租", "priority": "high"})
assert r.status_code == 201 and r.json()["priority"] == "high", ("S-1", r.status_code, r.text)
assert c.get("/todos").json()[0]["priority"] == "high", "S-1 list"

r = c.post("/todos", json={"title": "買牛奶"})
assert r.json()["priority"] == "normal", ("S-2", r.text)
assert c.post("/todos", json={"title": "y", "priority": None}).json()["priority"] == "normal", "S-2 null"

before = len(c.get("/todos").json())
for bad in ["urgent", "High", " high", "", 1]:
    r = c.post("/todos", json={"title": "x", "priority": bad})
    assert r.status_code == 422, ("S-3", bad, r.status_code)
    assert all(v in r.text for v in ("low", "normal", "high")), ("S-3 message", r.text)
assert len(c.get("/todos").json()) == before, "S-3 nothing added"

r = c.post("/todos", json={"title": "報稅", "priority": "high", "due_date": "2026-12-01"})
tid = r.json()["id"]
over = [t for t in c.get("/todos?overdue=true").json() if t["id"] == tid]
assert over and over[0]["priority"] == "high", ("S-6 overdue", over)
assert c.post(f"/todos/{tid}/complete").json()["priority"] == "high", "S-6 complete"
print("T-02 check: OK")
