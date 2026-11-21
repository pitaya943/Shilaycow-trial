---
name: design
description: Use after a task brief is approved and before planning or coding anything non-trivial, to derive the system's shape from the scenarios. Also the whole deliverable of a spec-only task.
---

# Design

Work backward from the approved scenarios to the shape of the system, so the plan and the code follow from what the user asked for and nothing else.

## Inputs

`docs/tasks/<slug>/brief.md`. The repository as it is (`how`, `why`). If there is no brief, ask for the scenarios first or run `sharpen`.

## Done when

`docs/tasks/<slug>/design.md` exists, someone could build from it without asking you what you meant, and every scenario in the brief has a place in it. Its form and depth are yours to judge.

## How

None of this is required; it is what tends to help. Views worth considering, a table or a diagram each:

- **Frame**: the parts and the boundaries between them.
- **Data flow**: what enters, what transforms it, where it rests.
- **Interfaces**: types and signatures at each boundary.
- **Workflow**: one scenario traced end to end.
- **Notifications**: who must learn that something happened, and how.
- **State owners**: each piece of state has exactly one owner.

Anything that points back to no scenario is probably extra. Sketching a second, different shape before committing often shows what the first one costs; a good shape has one owner per piece of state, one supported way to do each thing, and asks the least of its callers. Saying how each scenario will be proven makes planning easier. With the user present, design in conversation and keep the file current as you go.

## Stop when

- A scenario cannot be met without changing the brief. Go back to the user; the scenarios are theirs.
- The design needs a fact only running something can settle. Settle it with a throwaway prototype on a `spike/` branch, record the result with `trail`, and bring back the decision, not the code.

## Outputs

`docs/tasks/<slug>/design.md`, in the language set by `report_language`. If implementation later proves it wrong, change it and add a `trail` row; never change the scenarios to match.
