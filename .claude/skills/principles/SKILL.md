---
name: principles
description: "Use when writing code, choosing between two ways to do something, or reviewing someone's work: the handful of judgements a good engineer applies without being told."
---

# Principles

These are judgements, not rules. They are here because writing code costs you almost nothing, so nothing pushes you toward the simpler answer the way effort pushes a person. Depart from any of them when the task calls for it, and say that you did.

- **The smallest change that meets the scenario.** Before adding anything, ask whether a smaller change would do. Say what you chose to leave out.
- **Delete before you add.** Remove what is dead or in the way first, then build on the simpler base. Code nobody asked for is a cost, not a gift.
- **Fix the cause, not the symptom.** If the same workaround appears twice, the design is wrong; change the design.
- **One owner for each piece of state, one supported way to do each thing.** Two places that can disagree eventually will.
- **Prove it on the real thing.** "It compiles" and "the test I wrote passes" are not evidence. Run the feature, read the actual value.
- **Test what a caller can observe.** A test should survive a rewrite of the internals and fail when the behaviour breaks.
- **Write for the next reader.** Fewer layers, fewer one-caller wrappers, no comment that restates the code, no trace of an approach you tried and abandoned.

## When reviewing

Read the change as the person who will have to maintain it. For each principle ask whether the change honours it, and where it does not, whether that was a choice someone explained or something nobody noticed.
