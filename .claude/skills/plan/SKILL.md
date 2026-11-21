---
name: plan
description: Use once a brief (and a design, when the task needs one) is approved, to cut the work into tickets and milestones before building.
---

# Plan

Cut the work into thin vertical tickets, group them into milestones a person could try, and mark what can run in parallel.

## Inputs

`docs/tasks/<slug>/brief.md`, `design.md` if it exists, and `.shilaycow/pitfalls.md` if it exists.

## Done when

`docs/tasks/<slug>/plan.md` and one `tickets/T-<nn>.md` per ticket exist, and:

- every ticket is a vertical slice: when it is done, a scenario or part of one can be driven end to end;
- every ticket names the scenarios it serves; a ticket that serves none is preparation and says which scenario it prepares for;
- every scenario in the brief is covered by some ticket;
- each ticket lists what it depends on and the areas it will touch;
- each milestone ends with a set of scenarios a person can try in full;
- `plan.md` shows the order, the milestones, and which tickets may run in parallel (no dependency between them and no shared area).

## How

Size a ticket so one builder session can finish it and one verifier can read it. Put shared groundwork first. If the project has no `drive-<app>` skill yet, the first ticket creates it with `drive`. Read the pitfalls and shape tickets to avoid them.

A ticket file has: a title, `Status: open`, `Milestone:`, `Depends on:`, and the sections 做什麼, 對應的情境, 會動到的區域.

## Stop when

- A scenario cannot be sliced without a design decision that was not made. Go back to `design`.

## Outputs

`plan.md` and `tickets/`. The plan may be re-cut during the work; each re-cut gets a `trail` row. A finished ticket is never edited.
