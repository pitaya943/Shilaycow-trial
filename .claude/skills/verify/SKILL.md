---
name: verify
description: Use to judge a pull request, or a whole task branch before it goes to main, from a session that built none of it. Posts PASS or FAIL for one commit.
---

# Verify

Judge the work cold. You did not build it, you do not fix it, and nothing the builder claims counts until you have seen it yourself.

## Inputs

The pull request or task branch, its ticket, the scenarios in `docs/tasks/<slug>/brief.md`, and the project's `drive-<app>` skill. Not the builder's conversation, and not a summary written for you. If you built any of this work, stop: someone else verifies it.

## Done when

You have checked, on a clean checkout of the head commit, and recorded evidence for each:

1. **Tests**: the full suite passes.
2. **Scenarios**: each scenario the work serves is shown by a test or by a driven action.
3. **The real thing**: you followed the "how to try it" steps with `drive-<app>` and they work as written.
4. **TDD order**: each behaviour's test commit precedes its implementation, and on the test-only commit that test fails for the right reason.
5. **What went unsaid**: anything the diff changes that neither the description nor the trail mentions.

Plus one spot check: break one behaviour on purpose and confirm its test fails, then restore it.

For a whole task branch, also run `blast-radius` against `main`.

Then one comment is posted that starts `## Verification: PASS` or `## Verification: FAIL`, names the full head commit, and lists the five checks with their evidence.

## How

Evidence is a command and its output, a screenshot, a file and line: never a sentence. A FAIL says which scenario, how to reproduce it and what you saw, so the builder need not guess.

## Stop when

- `drive-<app>` no longer works as written. Report "drive is stale"; that is not a FAIL of this work.
- You cannot run the project at all. Say what is missing.

## Outputs

One comment, never edited afterwards; a new head needs a new verdict. You push nothing to the branch you judge and you never merge.
