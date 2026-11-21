---
name: report
description: Use at the end of a milestone or a task to write what was done for the person who will decide whether to merge it. Produces the checkpoint report or the final pull request description.
---

# Report

Tell the owner what they are being asked to accept, in a form they can check without reading the diff first.

## Inputs

The task branch, `docs/tasks/<slug>/brief.md`, `design.md`, `plan.md`, `trail.tsv`, the Ready comments, the verdict comments and the CI results. Gather only from these; memory and impressions are not sources.

## Done when

A report exists under `docs/tasks/<slug>/reports/` (`m<n>.md` for a milestone, `final.md` for the task) whose first sentence says whether, by your own check, every scenario is met, followed by these sections:

1. **做了什麼**: three to five plain sentences.
2. **怎麼試**: written from zero, for someone who has never seen the project: getting the code and the right branch, installing, starting it, then each action with what they should see. Add two or three things worth trying that the tests do not cover.
3. **我自己做的決定**: from the trail: each decision made without asking, with its reason in a line.
4. **沒做到或有疑慮的**: never omitted; write 無 if there is nothing.
5. **驗證**: one line saying the independent verdict is posted as a comment on this pull request. You write the report before it exists, so claim no result.

And a table of every scenario in the brief: met or not, and a link to the evidence. Every claim links to a pull request, commit, verdict or trail row.

## How

Write in the language set by `report_language`. Lead with the conclusion. Say less, link more.

## Stop when

- A scenario is not met. Do not open a pull request into `main`: write what is missing where the owner will see it (the tracking issue, or the conversation) and leave the decision to them.

## Outputs

The report file. The final report is also the description of the one pull request into `main`. A checkpoint report waits for no reply.
