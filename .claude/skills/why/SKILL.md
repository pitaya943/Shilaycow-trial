---
name: why
description: Use for "why is X this way", design rationale, a regression's history, or before undoing a decision someone made earlier. For how something behaves, use how.
---

# Why

Answer from the record, not from the code. The code shows what is; the reasons are in what people wrote when they changed it.

## Inputs

A question about a reason or a history.

## Done when

The answer has three parts, kept apart:

- **What the record says**, each point with its source: a commit, a pull request discussion, a row in a trail, a line in a design or decision file.
- **What you infer**, marked as inference.
- **What the record does not answer.**

## How

Read, in this order, whatever exists: `docs/tasks/*/trail.tsv` and `docs/tasks/*/design.md` for the area, `.shilaycow/pitfalls.md`, the commits and pull requests that introduced the thing and each later change to it, then any decision log the project keeps.

## Stop when

- The record is too thin to answer. Say so plainly and hand the question back; do not supply a plausible reason of your own as if it were the record's.

## Outputs

A reply in the conversation.
