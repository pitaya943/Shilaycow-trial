---
name: trail
description: Use throughout long or unattended work to log each decision as it is made, so a reviewer who stepped away can trust the result without rebuilding the process.
---

# Trail

Keep one log, one row per decision. It is the other half of not asking on reversible work: you do not ask, and you always leave a record.

## Inputs

The decision you just made, and where its evidence is.

## Done when

`docs/tasks/<slug>/trail.tsv` has a row for every point where another reasonable person might have chosen differently, and always for: skipping a phase, re-cutting the plan, changing the design, choosing between libraries or approaches, an assumption made in place of a question, anything departing from a skill's default.

Columns, tab-separated, one line per row:

- `ts`: ISO 8601 timestamp
- `phase`: brief, design, plan, build, verify, report
- `who`: chief, builder, verifier
- `decision`: what was chosen or done
- `why`: the reason in plain words
- `evidence`: a pointer (commit, pull request, `file:line`, artifact path), never a paragraph
- `result`: the outcome so far (`tests green`, `reverted`, `open`)

## How

Write the row when you decide, not at the end. Append only: to reverse a decision, add a row. Routine steps are not decisions; do not log them.

A builder working in parallel posts its rows in its pull request's ready comment; whoever merges adds them to the file.

## Stop when

Nothing stops this skill; it runs alongside the others.

## Outputs

`trail.tsv`. `report` builds the "decisions I made myself" section from it, and `verify` treats a significant change with no row as a failure.
