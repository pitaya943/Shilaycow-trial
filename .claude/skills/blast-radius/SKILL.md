---
name: blast-radius
description: Use before a change to shared code ships, and before a task branch goes to main, to find what it could break elsewhere and prove the facts its safety rests on by running code.
---

# Blast radius

Find what a change breaks somewhere else, beyond the diff. Listing callers is not the job; the job is the breakage a search will not show, and proving the one or two facts the change's safety depends on.

## Inputs

A diff: a pull request, or a task branch against `main`.

## Done when

You have named the facts this change is safe because of, and for each one said how far down this ladder you got and why you stopped there:

1. You said so. Worth nothing alone.
2. You pointed at the line, or at the library's own source.
3. You walked the failure step by step and it cannot be reached.
4. You ran it: a small script or test that calls the real code and fails loudly if you are wrong.
5. You reproduced it in the running app.

Every fact reached step 3, 4 or 5, or says what made that impossible.

## How

Look where a search does not: implicit ordering, shared state, defaults, serialised formats, what other code assumes about a return shape, what runs at import or start-up. Step 4 is usually one short script that imports what the app ships and calls the exact function. When an implementation is swapped behind an interface that is meant to stay the same, the script sends ordinary and extreme inputs (very large, very small, empty, malformed) to the old code and the new and compares every answer; do it before the first ticket is verified, not only at the end.

Do not hand back an essay. Hand back the facts, the level each reached, and the output that proves it.

## Stop when

- A fact turns out false. That is the finding: report it with the reproduction and stop polishing the rest.

## Outputs

A short list in the conversation, or inside a `verify` verdict or a final report when called from there.
