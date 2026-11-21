#!/usr/bin/env bash
# Start the real todo-api, drive it over HTTP with curl, and write a transcript.
# Usage: bash .claude/skills/drive-todo-api/drive.sh [transcript-path]
# Run from the repository root. PORT (default 8765) picks the port.
set -u

PORT="${PORT:-8765}"
BASE="http://127.0.0.1:${PORT}"
OUT="${1:-drive-transcript.txt}"
LOG="$(mktemp)"

python -m uvicorn todo_api.app:app --host 127.0.0.1 --port "$PORT" >"$LOG" 2>&1 &
SERVER=$!
trap 'kill "$SERVER" 2>/dev/null; rm -f "$LOG"' EXIT

up=0
for _ in $(seq 1 50); do
  if curl -s -o /dev/null "$BASE/todos"; then up=1; break; fi
  sleep 0.1
done
if [ "$up" != 1 ]; then
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
} | tee "$OUT"
