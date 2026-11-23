---
name: try-todo-api
description: Use to start the real todo-api service and exercise it over HTTP the way a user would, capturing a transcript as evidence. For verification, "how to try it" steps and scenario checks.
---

# Try todo-api

## Surface

One surface: an HTTP JSON API. There is no web UI and no CLI.

| Action | Request | Expect |
|---|---|---|
| Create | `POST /todos` with `{"title": "買牛奶"}` | `201`, `{"id": 1, "title": "買牛奶", "done": false, "priority": "normal"}` |
| List | `GET /todos` | `200`, an array in insertion order |
| Blank title | `POST /todos` with `{"title": "   "}` | `422`, `{"detail": "title must not be blank"}`, list unchanged |
| Complete | `POST /todos/1/complete` (no body), then `GET /todos` | `200`, `{"id": 1, "title": "買牛奶", "done": true, "priority": "normal"}`; the list shows that one done, the others unchanged. Doing it again is still `200` |
| Unknown id | `POST /todos/999/complete` | `404`, `{"detail": "todo not found"}`, list unchanged |
| Create with a due date | `POST /todos` with `{"title": "繳電費", "due_date": "2026-12-01"}` | `201`, the todo with `"due_date": "2026-12-01"` |
| Create without one | `POST /todos` with `{"title": "買牛奶"}` | `201`, the todo with no `due_date` key at all |
| Malformed due date | `POST /todos` with `{"title": "報稅", "due_date": "下週五"}` | `422`, `{"detail": "due_date must be a date like 2026-12-01"}`, list unchanged |
| Create with a priority | `POST /todos` with `{"title": "繳房租", "priority": "high"}` | `201`, the todo with `"priority": "high"`; the list shows it too. Without `priority` (or with `null`) it is `"normal"`; every todo in every answer has `priority` |
| Unknown priority | `POST /todos` with `{"title": "x", "priority": "urgent"}` (also `"High"`, `" high"`, `""`, `1`) | `422`, `{"detail": "priority must be one of: low, normal, high"}`, list unchanged |
| Title too long | `POST /todos` with a title of 201 characters (a title of exactly 200, after trimming, is accepted) | `422`, `{"detail": "title must be at most 200 characters"}`, list unchanged |
| Only the overdue | `GET /todos?overdue=true` | `200`, only todos that are not done and whose `due_date` is before today (the server machine's date) |
| Stop and start again | add two, complete one, stop the server, start it on the same data file, `GET /todos`, then add one | the same two todos with the same ids, due date and done state; the new one gets id 3 |
| Garbage data file | put anything that is not this service's data in the data file, then start the server | the process exits non-zero; the last line of its output is `todo_api.store.StoreUnreadable: ...` with the file's path; the file's bytes are unchanged |

The rows are named for what the user does, not by scenario number: the first five come from `docs/tasks/todo-api/brief.md` (full contract in that task's `design.md`, Interfaces), the four about due dates from `docs/tasks/due-dates/brief.md`, the two about priority from `docs/tasks/priority/brief.md`, the last two from `docs/tasks/persist/brief.md`.

## Run

From the repository root:

```
pip install -r requirements.txt
python -m uvicorn todo_api.app:create_app --factory --host 127.0.0.1 --port 8765
```

This is the only supported way to start it. No credentials, no seed data. The list lives in one SQLite file: `todos.db` in the directory the server was started from, or the path in the `TODO_DB` environment variable. The file is created on the first start; later starts continue from it, and ids are never reused. To start from an empty list, point `TODO_DB` at a path that does not exist yet. A data file that cannot be opened, or that holds something else, is never written to: the start fails with `StoreUnreadable` and the path. Stop the server with Ctrl-C (or kill the process).

## Drive

Plain HTTP with curl. The helper beside this file starts the server, runs every action above, prints each request with its status and body, and stops the server. It keeps the list in a temporary data file of its own (never `todos.db`) and deletes it on exit. It restarts the server on an empty data file before the overdue action, so that list holds exactly its four todos, and takes "yesterday" and "tomorrow" from the machine's date (GNU `date -d`). It then really stops and starts the server process on one data file, and last overwrites its data file with garbage and runs the start command once more, recording the exit status, the last line of output and the file's SHA-256 before and after:

```
bash .claude/skills/try-todo-api/drive.sh docs/tasks/<slug>/evidence/<ticket>-drive.txt
```

`PORT=9000 bash ...` uses another port. The helper only drives a server it started itself: it waits up to 5 seconds for the port to be free, exits 1 with a message if something still answers there, and on exit waits until its own server has really stopped, so it can be run back to back and every run starts from an empty list. To drive by hand, start the server as in Run (with `TODO_DB` set to a scratch path, unless you mean to use the real list) and send, for example:

```
curl -s -w '\n-> HTTP %{http_code}\n' -X POST http://127.0.0.1:8765/todos -H 'Content-Type: application/json' -d '{"title": "買牛奶"}'
curl -s -w '\n-> HTTP %{http_code}\n' http://127.0.0.1:8765/todos
curl -s -w '\n-> HTTP %{http_code}\n' -X POST http://127.0.0.1:8765/todos/1/complete
curl -s -w '\n-> HTTP %{http_code}\n' -X POST http://127.0.0.1:8765/todos/999/complete
```

When a ticket adds an endpoint, add its `call` lines to `drive.sh` and its row to the table above.

## Observe

The evidence is the transcript: each request, its HTTP status and its JSON body. `drive.sh` writes it to the path given as its first argument (default `./drive-transcript.txt`) and also prints it. Commit it as `docs/tasks/<slug>/evidence/<ticket>-drive.txt` and compare each block with the scenario's Then in the task brief.

Earlier runs are kept at `docs/tasks/todo-api/evidence/T-01-drive.txt` (S-1, S-2, S-4) and `docs/tasks/todo-api/evidence/T-02-drive.txt` (all five scenarios), `docs/tasks/due-dates/evidence/drive.txt` (those five again, then the four due-date scenarios), `docs/tasks/persist/evidence/drive.txt` (all of the above, then the restart and the garbage data file), and `docs/tasks/priority/evidence/T-02-drive.txt` (all of the above with a priority on every todo, plus a create with `high` and an unknown priority).

## Known limits

- The overdue scenario depends on the machine's date: a run that straddles midnight could compute "yesterday" on one day and be judged by the server on the next.
- Nothing here needs a person: there is no visual surface.
- The transcript shows non-ASCII titles as raw UTF-8; a terminal without UTF-8 will garble them, the bytes are still right.
- The transcript's header names the commit that was checked out, not whether the working tree had uncommitted changes.
- `drive.sh` exits 0 even when a response is not the expected one; it records, it does not judge. Read the transcript. It exits 1 only when it could not start its own server.
