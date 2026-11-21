---
name: how
description: Use for "how does X work", before changing an unfamiliar area, or to decide where new code should live. For why something is the way it is, use why.
---

# How

Explain how a part of the system works today, well enough that someone new to it could start changing it with confidence.

## Inputs

A question about behaviour, structure or placement. If its scope is unclear, state the reading you chose and proceed.

## Done when

The explanation:

- follows the data: what comes in, what transforms it, where it ends up, who owns each piece of state;
- cites a file and line for every claim about the code;
- marks anything you inferred and did not read as an inference;
- ends with what a change in this area would have to respect.

## How

Explore read-only. Where a subagent is available, give it the question and have it explore and explain in one pass, so the files stay out of your context; otherwise read directly. Present its explanation with light edits only.

## Stop when

- The answer depends on behaviour you can only learn by running the system. Say what to run; `blast-radius` or `drive` is the tool for that.

## Outputs

A reply in the conversation. When called from `sharpen` or `design`, the points they need go into their file.
