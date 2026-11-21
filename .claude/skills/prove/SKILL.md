---
name: prove
description: Use whenever you write or change behaviour, to decide how it gets proven: by a test you have seen fail, or by a recorded run of the real thing where a test would be a bad one. Never by a test that cannot fail.
---

# Prove

No behaviour ships on a test that would pass whether or not the behaviour works. That is the whole aim. How you get there is yours to judge.

## Inputs

A ticket or a single behaviour, the scenarios it serves, and the project's test command (`test_command` in `.shilaycow/config.yml`, or what the project documents).

## Done when

Every behaviour you added or changed is proven one of two ways, and your report says which:

- **A test worth keeping**, that you have seen fail: either you wrote it first and watched it fail for the missing behaviour, or you broke the behaviour, watched the test fail, and restored it. A failure from an import, a fixture or the setup is not that failure: get past it until the assertion itself fails. A scenario that says something stays as it was is proven the second way, by breaking it and seeing the existing tests fail.
- **A driven check**, where a test would be a bad one: a recorded run of the real thing through the project's `drive-<app>` skill, a script, or a command and its output.

And the full suite passes.

## Choosing

- **Test-first or test-after** is your call when the behaviour and its interface are known. Test-first means short cycles, one behaviour at a time: red, the least code that turns it green, then refactor with the suite green. Either way the test must have been seen to fail.
- **A bug** with a cheap way to reproduce it: make the bug executable and see it fail before you fix it. Otherwise you cannot know the fix is what cured it.
- **Explore first** when the requirement or the interface is still moving. A prototype answers a question; it is never the build. Keep it on a `spike/` branch or in a scratch directory, write it fast, skip tests, and when the question is answered throw it away: carry the decision into the real work and write that fresh. Prototype code is not merged.
- **Use a driven check instead of a test** when a test would need broad setup, brittle mocks, slow infrastructure or state you cannot reach, or would only be deleted afterwards. Prefer no new test to a bad one.

## A test worth keeping

Judge each test against two imagined edits. Break the behaviour: if the test still passes, it proves nothing. Change only the internals: if the test fails, it is pinned to the implementation. Keep what catches the first and survives the second.

Three ways tests go wrong:

- the expected value is computed the way the code computes it, so the two can never disagree: take it from the scenario or a worked example instead;
- it reaches inside (private helpers, call order, mocks of your own collaborators) rather than what a caller observes;
- all the tests are written first and all the code after: write one, satisfy it, let it inform the next.

## Stop when

- A test seems wrong, or passing it would mean loosening it. Stop and ask; never weaken a test to get green.
- Nothing you can run would show the behaviour, by test or by driving. Say so; do not report it as proven.

## Outputs

For each behaviour: the test and how it was seen to fail, or the driven check and its record. Note in the trail when you explored first or chose a driven check over a test.
