#!/usr/bin/env bash
# Start the real todo-api, drive it over HTTP with curl, and write a transcript.
# Usage: bash .claude/skills/drive-todo-api/drive.sh [transcript-path]
# Run from the repository root. PORT (default 8765) picks the port.
set -u

PORT="${PORT:-8765}"
BASE="http://127.0.0.1:${PORT}"
OUT="${1:-drive-transcript.txt}"
LOG="$(mktemp)"

SERVER=""
# Stop our server and wait until it has really gone, so the port is free
# (and the list is gone) before this script returns.
cleanup() {
  if [ -n "$SERVER" ]; then
    kill "$SERVER" 2>/dev/null
    wait "$SERVER" 2>/dev/null
  fi
  rm -f "$LOG"
}
trap cleanup EXIT

# Never drive a server we did not start: its list would not be empty.
# Give a server that is still shutting down up to 5 seconds to let go.
busy=1
for _ in $(seq 1 50); do
  if ! curl -s -o /dev/null "$BASE/todos"; then busy=0; break; fi
  sleep 0.1
done
if [ "$busy" = 1 ]; then
  echo "something is already answering on $BASE; stop it or pick another PORT" >&2
  exit 1
fi

python -m uvicorn todo_api.app:app --host 127.0.0.1 --port "$PORT" >"$LOG" 2>&1 &
SERVER=$!

up=0
for _ in $(seq 1 50); do
  if ! kill -0 "$SERVER" 2>/dev/null; then break; fi
  if curl -s -o /dev/null "$BASE/todos"; then up=1; break; fi
  sleep 0.1
done
# The answer must come from our own process: if it died (for example the port
# was taken after the check above), whatever answered is not ours.
if [ "$up" != 1 ] || ! kill -0 "$SERVER" 2>/dev/null; then
  echo "server did not start on $BASE; uvicorn said:" >&2
  cat "$LOG" >&2
  exit 1
fi

# call METHOD PATH [JSON-BODY]: prints the request, the status and the body.
call() {
  echo "\$ $1 $2 ${3:-}"
  if [ -n "${3:-}" ]; then
    curl -s -w '\n-> HTTP %{http_code}\n' -X "$1" "$BASE$2" \
      -H 'Content-Type: application/json' -d "$3"
  else
    curl -s -w '\n-> HTTP %{http_code}\n' -X "$1" "$BASE$2"
  fi
  echo
}

{
  echo "# todo-api drive, $(date -u +%Y-%m-%dT%H:%M:%SZ), commit $(git rev-parse --short HEAD 2>/dev/null)"
  echo
  echo "## S-1 create"
  call POST /todos '{"title": "買牛奶"}'
  call POST /todos '{"title": "繳電費"}'
  echo "## S-2 list"
  call GET /todos
  echo "## S-4 blank title, then the list is unchanged"
  call POST /todos '{"title": "   "}'
  call GET /todos
  echo "## S-3 complete one, then the list shows it done and the other unchanged"
  call POST /todos/1/complete
  call GET /todos
  echo "## S-3 detail: completing it again is still 200"
  call POST /todos/1/complete
  echo "## S-5 unknown id, then the list is unchanged"
  call POST /todos/999/complete
  call GET /todos
} | tee "$OUT"
