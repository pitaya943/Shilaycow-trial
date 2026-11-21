---
name: drive-todo-api
description: Use to start the real todo-api service and exercise it over HTTP the way a user would, capturing a transcript as evidence. For verification, "how to try it" steps and scenario checks.
---

# Drive todo-api

## Surface

One surface: an HTTP JSON API. There is no web UI and no CLI.

| Action | Request | Expect |
|---|---|---|
| Create (S-1) | `POST /todos` with `{"title": "買牛奶"}` | `201`, `{"id": 1, "title": "買牛奶", "done": false}` |
| List (S-2) | `GET /todos` | `200`, an array in insertion order |
| Blank title (S-4) | `POST /todos` with `{"title": "   "}` | `422`, `{"detail": "title must not be blank"}`, list unchanged |

The full contract is in `docs/tasks/todo-api/design.md` (Interfaces).

## Run

From the repository root:

```
pip install -r requirements.txt
python -m uvicorn todo_api.app:app --host 127.0.0.1 --port 8765
```

No environment variables, no credentials, no seed data. The list lives in memory: every start begins empty and ids restart at 1. Stop the server with Ctrl-C (or kill the process).

## Drive

Plain HTTP with curl. The helper beside this file starts the server, runs every scenario above, prints each request with its status and body, and stops the server:

```
bash .claude/skills/drive-todo-api/drive.sh docs/tasks/<slug>/evidence/<ticket>-drive.txt
```

`PORT=9000 bash ...` uses another port. To drive by hand, start the server as in Run and send, for example:

```
curl -s -w '\n-> HTTP %{http_code}\n' -X POST http://127.0.0.1:8765/todos -H 'Content-Type: application/json' -d '{"title": "買牛奶"}'
curl -s -w '\n-> HTTP %{http_code}\n' http://127.0.0.1:8765/todos
```

When a ticket adds an endpoint, add its `call` lines to `drive.sh` and its row to the table above.

## Observe

The evidence is the transcript: each request, its HTTP status and its JSON body. `drive.sh` writes it to the path given as its first argument (default `./drive-transcript.txt`) and also prints it. Commit it as `docs/tasks/<slug>/evidence/<ticket>-drive.txt` and compare each block with the scenario's Then in the task brief.

The first run is kept at `docs/tasks/todo-api/evidence/T-01-drive.txt`.

## Known limits

- Nothing here needs a person: there is no visual surface.
- The transcript shows non-ASCII titles as raw UTF-8; a terminal without UTF-8 will garble them, the bytes are still right.
- State cannot be kept across restarts (by design), so a scenario's Given must be set up in the same run.
- `drive.sh` exits 0 even when a response is not the expected one; it records, it does not judge. Read the transcript.
