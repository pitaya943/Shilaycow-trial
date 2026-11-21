---
name: verify
description: Use to judge the pull request the owner is about to merge, from a session that built none of it; also any ticket that deserves a second look before it is merged into the task branch. Posts PASS or FAIL for one commit.
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
4. **Tests that can fail**: for each scenario shown by a test, you broke the behaviour in a throwaway copy and the test failed; and its expected values come from the scenario, not from the code under test.
5. **What went unsaid**: anything the diff changes that neither the description nor the trail mentions.
6. **The code itself**: read it as the person who will maintain it, against `principles`. Is there work no scenario asked for, a smaller change that would have done, a leftover of an abandoned attempt, state with two owners? Skip this check when the brief's care level is 快.

For a whole task branch, also run `blast-radius` against `main`.

Then one comment is posted that starts `## Verification: PASS` or `## Verification: FAIL`, names the full head commit, and lists the checks with their evidence. With no pull request yet, post it on the tracking issue.

## The verdict

It is a **FAIL** when any of these is true:

- the suite fails, or a scenario this work serves is not shown;
- the "how to try it" steps do not work as written;
- a test still passes with its behaviour broken, or takes its expected value from the code it tests;
- a behaviour is reported as proven with neither a test nor a recorded driven check;
- the diff makes a significant change nobody mentioned;
- the same state has two owners that can disagree, or leftover code changes behaviour beyond the scenarios;
- for a whole branch, a `blast-radius` fact is false and something existing depends on it.

Otherwise it is a **PASS**. Anything else you found (a defect outside the scenarios, an unspecified input, a weak spot, everything else from reading the code) goes under a `### Findings` heading in the same comment, each with how to reproduce it. A finding never turns a PASS into a FAIL, and is never left out to keep a PASS clean.

## How

Evidence is a command and its output, a screenshot, a file and line: never a sentence. A FAIL says which check failed (and which scenario, when one is involved), how to reproduce it and what you saw, so the builder need not guess.

Work in a fresh worktree at the head commit, and break behaviours only in a throwaway copy. On a large change, sample: every scenario's main test, then as many others as the time allows, and say what you sampled. "How to try it" means the brief's steps for the scenarios this work serves, run through `drive-<app>`. Write in the language set by `report_language`, keeping the heading line in English.

## Stop when

- `drive-<app>` no longer works as written. Report "drive is stale"; that is not a FAIL of this work, unless this work is what created or changed it.
- You cannot run the project at all. Say what is missing.

## Outputs

One comment, never edited afterwards; a new head needs a new verdict. You push nothing to the branch you judge and you never merge.
