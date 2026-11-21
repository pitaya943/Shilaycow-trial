---
name: sharpen
description: Use at the start of any task, and whenever a goal is vague, large or new, to say back what the user wants and turn it into a task brief of plain-language scenarios they approve.
---

# Sharpen

Turn an idea into a brief that someone could check the finished work against. The brief is what the user approves, what `design` starts from and what `verify` accepts against.

## Inputs

The user's idea. The repository as it is. `.shilaycow/config.yml` for the default budget, if it exists.

## Done when

Before any question, you said back in your own words what the user wants: the goal, the problem behind it, the smallest change that would meet it, and one thing you are assuming that they did not say. They confirmed or corrected it.

Then `docs/tasks/<slug>/brief.md` exists with these headings filled in:

- **目標**: what will be true for the user.
- **不做什麼**: what is deliberately left out. Never empty.
- **情境**: scenarios `S-1`, `S-2`, ... as Given / When / Then, in the user's own vocabulary, with no class, table or file names.
- **怎麼試**: how a person would try the result by hand.
- **預算**: hours and sessions.
- **謹慎程度**: 快, 一般 or 謹慎. How much checking this task is worth; the user's call, 一般 unless they say otherwise.

And for every scenario you can name either a test that would fail today or a manual step that would show it.

## How

- Restate first. Use your own words, not the user's phrasing rearranged, and prefer the narrow reading of the request: say what you would leave out. A misunderstanding caught here costs nothing.
- Write a first draft of the brief from what you already know, then ask about the gaps. Keep the file current as answers arrive.
- Ask the user about outcomes only: how they will use it, what counts as failure, what they would be upset to find missing. Offering your recommended answer with each question lets them accept in a word.
- Answer technical questions yourself by reading the repository (`how`, `why`). Do not ask the user what the code can tell you.
- Write the brief in the language set by `report_language`, Traditional Chinese by default.

## Stop when

- The user says it is enough. Write what is still unknown under the scenario it affects, as an assumption.
- The idea is several tasks. Say so, propose the split, and sharpen only the first; for a large system the first task's deliverable is the design itself.

## Outputs

`docs/tasks/<slug>/brief.md`. The task does not proceed to unattended work until the user explicitly approves it.
