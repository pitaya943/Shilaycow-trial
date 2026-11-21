---
name: status
description: Use to find out where a task stands, who it is waiting on and what to do next. Read only.
---

# Status

Say where things are, without changing anything.

## Inputs

`.shilaycow/config.yml`, the task folder on `task/<slug>` (or on `main` when there is no task branch), open pull requests with their CI and verdicts, the tracking issue, and open `needs-owner` issues.

## Done when

Your reply gives, in this order:

1. **Waiting on**: the one thing blocking progress and who holds it (a pull request for the owner to merge, a `needs-owner` issue to answer, a session at work, nothing).
2. **Where the task is**: the phase, tickets done out of total, the current milestone, budget used.
3. **Next**: one step, with the command to type.

With no config, say the project is at Level 1 and name the skills that can be used directly.

## How

Read from the repository and GitHub each time; trust nothing remembered. Keep it to a few lines.

## Stop when

- GitHub cannot be reached. Report what the repository alone shows and say what is missing.

## Outputs

A reply in the conversation. Nothing is written, pushed, commented or started.
