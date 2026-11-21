---
name: drive
description: Use once per project, during its first task, to generate a project-local skill that starts the real app and exercises it the way a user would. Also use when that skill has gone stale.
---

# Drive

Give this project a scripted way to start the real thing, use it as a user does, and capture evidence. Verification, the "how to try it" steps and visual tests all stand on it.

## Inputs

The repository. Ask the user only what the repository cannot tell you.

## Done when

`.claude/skills/drive-<app>/SKILL.md` exists, written for an agent that has never seen this app, and it says:

- **Surface**: what a user touches (web UI, CLI, API, desktop app), the primary one first.
- **Run**: the exact commands to start it locally, with ports, environment and seed data.
- **Drive**: how to act on it from a script, preferring what the project already has (end-to-end specs, a debug port, plain HTTP) over a new harness.
- **Observe**: what evidence to capture (screenshots, transcripts, responses), kept under `docs/tasks/<slug>/evidence/`.

Name each action by what the user does ("create a todo"), not by a task's scenario number: the next task numbers its scenarios from one again.
- **Known limits**: what cannot be driven and must be checked by a person.

And you have used it once, start to finish, to perform one real action and captured the evidence.

## How

Find the answers in the project's own scripts, README, compose files, CI config and existing tests. Keep the generated skill short; put helper scripts beside it.

A script that starts the app must drive only the instance it started: fail if the port is already taken, confirm its own process is the one answering, wait for that process to exit when done, and exit non-zero when a step does not give the expected result.

## Stop when

- The app cannot start in this environment (a missing service, a credential, a blocked host). Say exactly what is missing; do not write a skill you could not run.
- The project is a library with no surface to drive. Say so; its tests are the driving.

## Outputs

`.claude/skills/drive-<app>/` on the task's branch. If a later check finds its steps no longer work, that is "drive is stale", to be fixed, not a failed verification.
