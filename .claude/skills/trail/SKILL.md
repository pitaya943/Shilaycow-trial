---
name: trail
description: Use throughout long or unattended work to log each decision as it is made, so a reviewer who stepped away can trust the result without rebuilding the process.
---

# Trail

Keep one log, one row per decision. It is the other half of not asking on reversible work: you do not ask, and you always leave a record.

## Inputs

The decision you just made, and where its evidence is.

## Done when

`docs/tasks/<slug>/trail.tsv` has a row for every point where another reasonable person might have chosen differently: above all an assumption made in place of a question, and anything the owner would be surprised to learn only afterwards.

Each row says what was decided, why in plain words, and where the evidence is: a pointer (commit, pull request, `file:line`), never a paragraph. A timestamp and who decided help. The exact columns are yours.

## How

Write the row when you decide, not at the end. Append only: to reverse a decision, add a row. Routine steps are not decisions; do not log them.

A builder working in parallel posts its rows in its pull request's ready comment; whoever merges adds them to the file.

## Stop when

Nothing stops this skill; it runs alongside the others.

## Outputs

`trail.tsv`. `report` builds the "decisions I made myself" section from it, and `verify` treats a significant change nobody mentioned as a failure.
