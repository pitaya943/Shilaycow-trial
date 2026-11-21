#!/usr/bin/env bash
# Start the real todo-api, drive it over HTTP with curl, and write a transcript.
# Usage: bash .claude/skills/drive-todo-api/drive.sh [transcript-path]
# Run from the repository root. PORT (default 8765) picks the port.
set -u

PORT="${PORT:-8765}"
BASE="http://127.0.0.1:${PORT}"
OUT="${1:-drive-transcript.txt}"
LOG="$(mktemp)"
# Our own data file, so a run never reads or writes the real todos.db and
# always starts from an empty list.
DATA_DIR="$(mktemp -d)"
export TODO_DB="$DATA_DIR/todos.db"

SERVER=""
# Stop our server and wait until it has really gone, so the port is free
# (and the list is gone) before the next start or before this script returns.
stop_server() {
  if [ -n "$SERVER" ]; then
    kill "$SERVER" 2>/dev/null
    wait "$SERVER" 2>/dev/null
    SERVER=""
  fi
}
cleanup() {
  stop_server
  rm -f "$LOG"
  rm -rf "$DATA_DIR"
}
trap cleanup EXIT

# Start our own server on our own data file, or exit 1.
start_server() {
  # Never drive a server we did not start: its list would not be empty.
  # Give a server that is still shutting down up to 5 seconds to let go.
  local busy=1 up=0
  for _ in $(seq 1 50); do
    if ! curl -s -o /dev/null "$BASE/todos"; then busy=0; break; fi
    sleep 0.1
  done
  if [ "$busy" = 1 ]; then
    echo "something is already answering on $BASE; stop it or pick another PORT" >&2
    exit 1
  fi

  python -m uvicorn todo_api.app:create_app --factory --host 127.0.0.1 --port "$PORT" >"$LOG" 2>&1 &
  SERVER=$!

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
}

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

# "Overdue" is relative to the machine's date, so the overdue scenario uses
# dates computed from it rather than fixed ones.
YESTERDAY="$(date -d yesterday +%F)"
TOMORROW="$(date -d tomorrow +%F)"

# The block is redirected, not piped: a pipe would run it in a subshell, where
# the server's pid would be lost to cleanup and `exit 1` would not end the script.
{
  start_server
  echo "# todo-api drive, $(date -u +%Y-%m-%dT%H:%M:%SZ), commit $(git rev-parse --short HEAD 2>/dev/null)"
  echo
  echo "## the list starts empty"
  call GET /todos
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

  echo "## due-dates S-1 create with a due date"
  call POST /todos '{"title": "繳電費", "due_date": "2026-12-01"}'
  echo "## due-dates S-2 create without a due date: no due_date in the answer"
  call POST /todos '{"title": "買牛奶"}'
  echo "## due-dates S-4 malformed due date, then the list has nothing new"
  call GET /todos
  call POST /todos '{"title": "報稅", "due_date": "下週五"}'
  call GET /todos

  # A fresh server on an empty data file, so the list holds exactly the four
  # todos of the scenario.
  stop_server
  rm -f "$TODO_DB"
  start_server
  echo "## due-dates S-3 only the overdue (fresh server and data file; today is $(date +%F))"
  echo "## A due yesterday, B due tomorrow, C no due date, D due yesterday and done"
  call POST /todos "{\"title\": \"A\", \"due_date\": \"$YESTERDAY\"}"
  call POST /todos "{\"title\": \"B\", \"due_date\": \"$TOMORROW\"}"
  call POST /todos '{"title": "C"}'
  call POST /todos "{\"title\": \"D\", \"due_date\": \"$YESTERDAY\"}"
  call POST /todos/4/complete
  echo "## all four are there"
  call GET /todos
  echo "## only A is overdue"
  call GET '/todos?overdue=true'
} >"$OUT"
cat "$OUT"
