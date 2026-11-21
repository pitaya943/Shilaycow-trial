---
name: plan
description: Use once a brief (and a design, when the task needs one) is approved, to cut the work into tickets and milestones before building.
---

# Plan

Cut the work into thin vertical tickets, group them into milestones a person could try, and mark what can run in parallel.

## Inputs

`docs/tasks/<slug>/brief.md`, `design.md` if it exists, and `.shilaycow/pitfalls.md` if it exists.

## Done when

The work is cut into pieces someone else could pick up cold, every scenario in the brief is covered by one of them, and it is clear what must come before what. Where you write that down, and in what form, is yours to judge; `docs/tasks/<slug>/plan.md` and `tickets/` is the usual place.

## How

None of this is required; it is what tends to help. Vertical slices work better than layers: when a piece is done, a scenario or part of one can be driven end to end. Say for each piece which scenarios it serves, what it depends on and which areas it touches, so pieces that share nothing can run at once. Size a piece so one session can finish it. Put shared groundwork first. If the project has no `drive-<app>` skill yet, the first ticket that leaves something runnable ends by creating it with `drive`; it cannot be written before there is an app to start.

Write each ticket's check so that it fails every time without the change, never by timing or luck, and can actually be met: run it against the code as it is and see it fail before you hand the ticket over. A check that already passes, or that nothing could satisfy, is the plan's mistake, and the builder will lose time finding that out. Mind the budget: every ticket costs a builder and a verifier. Read the pitfalls and shape tickets to avoid them.

## Stop when

- A scenario cannot be sliced without a design decision that was not made. Go back to `design`.

## Outputs

The plan, wherever you kept it. Re-cut it whenever the work shows it was wrong, and note that in the trail.
