---
name: design
description: Use after a task brief is approved and before planning or coding anything non-trivial, to derive the system's shape from the scenarios. Also the whole deliverable of a spec-only task.
---

# Design

Work backward from the approved scenarios to the shape of the system, so the plan and the code follow from what the user asked for and nothing else.

## Inputs

`docs/tasks/<slug>/brief.md`. The repository as it is (`how`, `why`). If there is no brief, ask for the scenarios first or run `sharpen`.

## Done when

`docs/tasks/<slug>/design.md` exists and:

- opens by saying which of the six views below it uses, which it skips and why;
- every element in it points back to at least one scenario, and anything that points to none is removed;
- two different shapes were sketched, one chosen, and the other kept with the reason it lost and what it did better;
- it ends with a table mapping each scenario to the test or driven check that will prove it.

## How

Take the views the task needs, a table or a diagram each, prose only where those fall short:

- **Frame**: the parts and the boundaries between them.
- **Data flow**: what enters, what transforms it, where it rests.
- **Interfaces**: types and signatures at each boundary.
- **Workflow**: one scenario traced end to end.
- **Notifications**: who must learn that something happened, and how.
- **State owners**: each piece of state has exactly one owner.

Choose between shapes by: one owner per piece of state, one supported way to do each thing, and the least a caller has to know. Scale the depth to the task. With the user present, design in conversation and keep the file current as you go.

## Stop when

- A scenario cannot be met without changing the brief. Go back to the user; the scenarios are theirs.
- The design needs a fact only running something can settle. Settle it on a `spike/` branch, record the result with `trail`, and bring back the conclusion, not the code.

## Outputs

`docs/tasks/<slug>/design.md`, in the language set by `report_language`. If implementation later proves it wrong, change it and add a `trail` row; never change the scenarios to match.
