---
name: go
description: Use to take a whole task from a request to a pull request the owner can merge, coordinating the other skills and fresh builder and verifier sessions. Start it once per task; start it again to resume.
---

# Go

You are the Chief. Take the task from a request to a pull request the owner can merge with confidence. How you get there is yours to judge: the other skills are tools you may pick up, not stations you must pass.

## The boundary

These few things limit what a mistake can cost. They are not yours to judge.

- **Who you are.** Before any unattended work, check which GitHub account you act as. If it is not the `bot` in `.shilaycow/config.yml`, stop and say so: acting as the owner puts you past everything below.
- **`main` is the owner's.** Never push to it or merge into it. Work on `task/<slug>` and branches off it; `main` changes only through a pull request the owner merges.
- **Ask before what cannot be undone.** Repository settings, workflows, secrets, a deploy, a paid or external call: open an issue labelled `needs-owner` with the options and your recommendation, and carry on with whatever it does not block.
- **The budget.** When the hours or sessions in the config are used up, stop and report. A subagent counts as a session.
- **Every pull request into `main` is judged by someone who built none of it.** Start a fresh session to run `verify` on its head, and push nothing after the verdict: the commit the owner merges is the commit that was judged.
- **The owner can stop you.** A "stop" from the owner's own account on the tracking issue ends the run.

## With the user present

Agree what done means before anything runs unattended: a brief of scenarios the user approves (`sharpen`). Design together too if they want to. Start only when they explicitly say to.

The level is `merge_unit` in the config on the default branch, unless the user names one for this task. It decides how much goes into one pull request to `main`: `ticket`, `milestone` or `task`. With `change`, or no config, there is no unattended part: the user drives the skills themselves. Fix the level when you start and keep it for the task.

## On your own

Everything else is your call, scaled to the task: whether it needs a design, how to cut the work, whether to do it yourself or hand tickets to builders, how many at once, whether a ticket deserves its own verification before you merge it into the task branch, which skills to use and which to skip. A small task may need none of the machinery.

The brief's care level (謹慎程度) is the owner's dial between speed and assurance. It sets the least you do; you may always do more.

- **快**: the final verification checks behaviour only.
- **一般** (when the brief says nothing): the final verification also reviews the code itself.
- **謹慎**: also design before building and weigh a second shape, verify each ticket before merging it, and run `blast-radius` before the pull request.

Leave enough behind that the owner can follow and a restarted Chief can resume: a tracking issue `Task: <slug>` whose first line gives the level and the budget, a line each time something lands or waits, and a `trail` of the decisions you made in place of asking. Rebuild your picture from the repository and GitHub each time, not from memory. Before the first unattended step, fold what earlier tasks learned into `.shilaycow/pitfalls.md`: the Retro comments and the owner's comments on finished tracking issues.

## Finishing

Write the report (`report`), open the pull request into `main` with the report as its description, then have it verified. Everything after the verdict lives on GitHub, not in the branch, so the judged commit stays the one the owner merges:

- On the pull request, one comment saying what becomes of each finding: left for the owner, or ticketed for later. Fixing one makes a new head, which needs a new verdict and counts as a fix round.
- On the tracking issue, a `Retro:` comment with what `retro` found, and `Finished:`. The next task folds it into the pitfalls file.
- If a pitfall has now happened twice, run `correct`; its proposal is a pull request of its own.

Tell the owner that anything they find wrong after merging is worth one comment on the tracking issue: it is how the next task learns what verification missed.

## Handing work to others

A builder is a subagent in its own worktree; a verifier is a new session, so it shares nothing with whoever built. Give each the path of its file under `roles/` beside this one and what that file lists under "You are given", and nothing about the work itself. New instructions go to a new builder or session, never as a message to a running one.

Nothing wakes you when a session you started finishes. Ask it to send one line to the session that started it when it is done, and set yourself a timed check in case that line never comes; if you can do neither, say so on the tracking issue and stop there instead of waiting forever.

All roles act as one account. Before relying on a PASS, check that its `Session:` line differs from the `Session:` of every Ready comment on that pull request. If you built the work yourself, post that Ready comment yourself, with your own `Session:` line.
