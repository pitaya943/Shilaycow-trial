#!/usr/bin/env bash
# Start the real todo-api, drive it over HTTP with curl, and write a transcript.
# Usage: bash .claude/skills/try-todo-api/drive.sh [transcript-path]
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

# The one supported way to start the service.
SERVE=(python -m uvicorn todo_api.app:create_app --factory --host 127.0.0.1 --port "$PORT")

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

  "${SERVE[@]}" >"$LOG" 2>&1 &
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
  echo "## create"
  call POST /todos '{"title": "買牛奶"}'
  call POST /todos '{"title": "繳電費"}'
  echo "## list"
  call GET /todos
  echo "## blank title, then the list is unchanged"
  call POST /todos '{"title": "   "}'
  call GET /todos
  echo "## complete one, then the list shows it done and the other unchanged"
  call POST /todos/1/complete
  call GET /todos
  echo "## completing it again is still 200"
  call POST /todos/1/complete
  echo "## unknown id, then the list is unchanged"
  call POST /todos/999/complete
  call GET /todos

  echo "## create with a due date"
  call POST /todos '{"title": "繳電費", "due_date": "2026-12-01"}'
  echo "## create without a due date: no due_date in the answer"
  call POST /todos '{"title": "買牛奶"}'
  echo "## malformed due date, then the list has nothing new"
  call GET /todos
  call POST /todos '{"title": "報稅", "due_date": "下週五"}'
  call GET /todos

  echo "## create with a priority: the answer and the list say high"
  call POST /todos '{"title": "繳房租", "priority": "high"}'
  echo "## an unknown priority, then the list has nothing new"
  call POST /todos '{"title": "x", "priority": "urgent"}'
  call GET /todos
  echo "## a title of 201 characters is refused, then the list has nothing new"
  call POST /todos "{\"title\": \"$(printf 'a%.0s' $(seq 201))\"}"
  call GET /todos

  # A fresh server on an empty data file, so the list holds exactly these
  # four todos.
  stop_server
  rm -f "$TODO_DB"
  start_server
  echo "## only the overdue (fresh server and data file; today is $(date +%F))"
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

  stop_server
  rm -f "$TODO_DB"
  start_server
  echo "## filter by priority (fresh server and data file): P1 high, P2 low, P3 high, no normal"
  call POST /todos '{"title": "P1", "priority": "high"}'
  call POST /todos '{"title": "P2", "priority": "low"}'
  call POST /todos '{"title": "P3", "priority": "high"}'
  echo "## only the two high, in insertion order"
  call GET '/todos?priority=high'
  echo "## no normal todo: an empty list"
  call GET '/todos?priority=normal'
  echo "## an unknown priority (High, empty) is refused"
  call GET '/todos?priority=High'
  call GET '/todos?priority='
  echo "## priority given twice is refused"
  call GET '/todos?priority=low&priority=high'
  echo "## without a filter all three are still there"
  call GET /todos

  stop_server
  rm -f "$TODO_DB"
  start_server
  echo "## stop the service and start it again (fresh data file first)"
  echo "## add two, complete one"
  call POST /todos '{"title": "繳電費", "due_date": "2026-12-01"}'
  call POST /todos '{"title": "買牛奶"}'
  call POST /todos/2/complete
  call GET /todos
  echo "## the service is stopped"
  stop_server
  echo "\$ GET /todos"
  curl -s -o /dev/null "$BASE/todos"
  echo "-> no answer (curl exit $?)"
  echo
  echo "## the service is started again on the same data file: the same two, one still done"
  start_server
  call GET /todos
  echo "## a new one gets the next id, 3"
  call POST /todos '{"title": "倒垃圾"}'

  stop_server
  printf 'this is not a todo list\n' >"$TODO_DB"
  echo "## the data file is garbage: the service refuses to start and leaves the file alone"
  echo "data file: $TODO_DB"
  echo "sha256 before: $(sha256sum <"$TODO_DB")"
  echo "\$ ${SERVE[*]}"
  # It should exit by itself; should it start after all, timeout stops it (exit 124).
  timeout 20 "${SERVE[@]}" >"$LOG" 2>&1
  echo "-> exit $?; the last line of its output:"
  tail -n 1 "$LOG"
  echo "sha256 after:  $(sha256sum <"$TODO_DB")"
} >"$OUT"
cat "$OUT"
