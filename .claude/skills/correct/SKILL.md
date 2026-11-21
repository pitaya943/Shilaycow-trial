---
name: correct
description: Use when the same class of mistake has happened twice in a project, to propose a change that makes it impossible instead of another note asking agents to be careful.
---

# Correct

A mistake that recurs is the repository's fault, not the agent's. Change the repository so the next agent cannot make it.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example and takes the shortest path that works. Design so that a change that looks right from one file is right for the whole.

## Inputs

Entries in `.shilaycow/pitfalls.md` with a count of 2 or more, and the commits, pull requests and review comments behind them.

## Done when

For each such class there is a proposal and a pull request that fixes it at the highest rung that works:

1. **Architecture**: one owner per piece of state, one supported way per task, internals hidden so the wrong import fails, old ways deleted so they cannot be copied.
2. **Types**: the bad state cannot be written.
3. **A lint or check** whose error names what to use instead. If the pattern is already common, fail only when a change adds more.
4. **A test** of the behaviour.
5. **Documentation**, last.

And the new guard is shown failing on every past instance the pitfall entry lists, then passing on the fix. Re-apply each past mistake in turn and run the guard; one it does not catch is not covered. Remove the pitfall entry only if all of it is covered; otherwise cut the entry down to the part that still rests on someone remembering.

## How

Write the proposal for the owner in plain words: how many times this happened (with links), what the change stops, and what it costs (build time, what it forbids).

## Stop when

- The fix needs a change under `.github/`. You cannot push workflow changes. Put the exact change in the proposal for the owner to apply, and stop there.
- No rung above documentation works. Say so; keep the pitfall entry.

## Outputs

A proposal (in the report or the tracking issue) and a pull request. Only the owner merges it.
