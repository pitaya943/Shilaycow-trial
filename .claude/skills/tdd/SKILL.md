---
name: tdd
description: Use whenever you write or change behaviour: the test comes first, fails for the right reason, then the code makes it pass. Not for spike branches or documentation-only changes.
---

# TDD

Red, then green, then refactor. The order is the point: a test you never saw fail proves nothing.

## Inputs

A ticket or a single behaviour, the scenarios it serves, and the project's test command (`test_command` in `.shilaycow/config.yml`, or what the project documents).

## Done when

For each behaviour:

- a test was written first and run, and it failed because the behaviour was missing: the failure names the missing behaviour, not a syntax, import or setup error;
- that test was committed on its own before any implementation, with a message starting `test:`;
- the smallest change that makes it pass was written and committed after it;
- the full suite passes;
- the red output and the green output are kept and posted with the work.

## How

1. **Red.** Write one test for one behaviour, in terms of what a caller observes. For a new module, add an empty shell first so the test reaches its assertion. Run it and read the failure.
2. **Green.** Write the least code that passes. Resist doing the next behaviour.
3. **Refactor.** Clean up with the suite green.

Test behaviour, not implementation: the test should survive an internal rewrite and fail when the behaviour breaks.

A purely visual scenario is tested by driving the real app with the project's `drive-<app>` skill; red is the recorded failed attempt.

A refactor adds no new red: the existing suite staying green is the evidence. Say that it is a refactor.

## Stop when

- A test seems wrong, or passing it would mean loosening it. Stop and ask; never weaken a test to get green.
- There is no way to run tests. Building that comes first, as its own ticket.

## Outputs

Two commits per behaviour (test, then code), and the red and green output. On a `spike/` branch none of this applies, and nothing on that branch is merged.
