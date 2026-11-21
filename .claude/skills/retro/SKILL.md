---
name: retro
description: Use when a task finishes, before its final pull request, to record the pitfalls it hit so the next task does not repeat them.
---

# Retro

Find what went wrong in this task that would go wrong again, and write it where the next builder will read it.

## Inputs

What the owner found wrong after merging earlier tasks (their comments on finished tracking issues): read these first, because each is something verification missed. Then the finished task: FAIL verdicts, the findings attached to PASS verdicts, fix rounds, CI failures, the owner's corrections and send-backs, and `docs/tasks/<slug>/trail.tsv`. Read `.shilaycow/pitfalls.md` first.

## Done when

You have worked out what `.shilaycow/pitfalls.md` should say after this task:

- each new pitfall has three lines: what happened (with a pull request or commit), how to avoid it, and how many times it has happened;
- a pitfall of a class already listed raises that entry's count instead of adding one;
- every entry kept passes three tests: it will still hold in six months, it would change what the next agent does, and it is not a one-off detail such as a version, a hash or a count;
- the file holds at most 30 entries: merge near-duplicates or drop what no longer holds before adding.

And you have said which entries now have a count of 2 or more: those are for `correct`.

Run this after the final verdict, since the verdict's findings are part of what you read. The branch is frozen by then, so post the result as a `Retro:` comment on the tracking issue; whoever starts the next task writes it into the file.

## How

Group by cause, not by symptom. If you cannot write how to avoid it, you have not found the cause yet. If the cause is an unclear instruction in a skill rather than something about this project, report that separately; it is not a project pitfall.

## Stop when

- Nothing in the task meets the three tests. Write nothing; an empty retro is a fine result.

## Outputs

Changes to `.shilaycow/pitfalls.md` on the task branch, which reach `main` with the task's pull request.
