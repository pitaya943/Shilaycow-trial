"""The drive helper starts a real server; it must also be the one to stop it.

Twice a change to this script left a server behind or drove one it had not
started, and a single run looked fine both times. So the script is run the way
that shows it: twice in a row, then once more with the port already taken.
"""

import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / ".claude/skills/drive-todo-api/drive.sh"
ROOT = Path(__file__).parent.parent


def _free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _answers(port):
    with socket.socket() as probe:
        probe.settimeout(0.2)
        return probe.connect_ex(("127.0.0.1", port)) == 0


def _drive(port, transcript):
    return subprocess.run(
        ["bash", str(SCRIPT), str(transcript)],
        cwd=ROOT,
        env={**__import__("os").environ, "PORT": str(port)},
        capture_output=True,
        text=True,
        timeout=120,
    )


def _nothing_left_on(port):
    # The script has returned; whatever it started must be gone already.
    return not _answers(port)


def test_two_runs_in_a_row_each_start_empty_and_leave_nothing_behind(tmp_path):
    port = _free_port()

    for run in ("first", "second"):
        transcript = tmp_path / f"{run}.txt"
        result = _drive(port, transcript)

        assert result.returncode == 0, result.stderr
        lines = transcript.read_text().splitlines()
        start = lines.index("## the list starts empty")
        assert lines[start + 1 : start + 4] == ["$ GET /todos ", "[]", "-> HTTP 200"]
        assert _nothing_left_on(port), f"a server is still answering after the {run} run"


def test_a_port_someone_else_holds_is_refused_and_their_server_is_not_driven(tmp_path):
    port = _free_port()
    other = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 10
        while not _answers(port):
            assert time.monotonic() < deadline, "the stand-in server did not start"
            time.sleep(0.05)
        transcript = tmp_path / "taken.txt"

        result = _drive(port, transcript)

        assert result.returncode == 1
        assert "already answering" in result.stderr
        assert not transcript.exists() or transcript.read_text() == ""
        assert other.poll() is None, "the script stopped a server it did not start"
    finally:
        other.kill()
        other.wait()
