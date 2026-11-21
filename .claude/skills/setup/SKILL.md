---
name: setup
description: Use once per repository to make GitHub itself keep agents out of main and to write the Shilaycow config, or again at any time to check that the real settings still match. Run it in a local session where the owner's gh is available.
---

# Setup

Put the one boundary in place: `main` changes only through a pull request the owner approves, and the agent's account cannot approve its own. Then record the settings every other skill reads.

Level 1 needs none of this: with no config, every skill works in the user's own session and merges nothing.

## Inputs

A GitHub repository, and the owner at the keyboard with admin rights (`gh auth status`). Ask one question at a time: the owner's login, the bot's login, the level wanted, the test command.

## Done when

All of these hold, and you have shown the owner the check's output:

1. The bot account is a collaborator with the Write role, not Admin.
2. A ruleset on the default branch requires a pull request with one approval, dismisses stale approvals on push, and blocks force pushes and deletion. The only bypass is the repository admin role, for pull requests only: the owner can merge their own pull request without a second approver, and nobody can push to the branch directly. `ruleset.json` beside this file is the body to send.
3. `.shilaycow/config.yml` exists with `owner`, `bot`, `merge_unit`, `test_command`, `budget`, `parallel_builders`, `fix_rounds`, `report_language`.
4. `AGENTS.md` has a section pointing at `.shilaycow/`, naming the branch classes (`task/`, `work/`, `spike/`) and saying only the owner merges `main`.
5. These changes are on a branch with a pull request open, not pushed to `main`.

## How

Do with `gh api` what a script can do, and walk the owner through what only a person can: creating the bot account, accepting the invitation as the bot, and connecting GitHub on claude.ai to the bot account with the Claude GitHub App installed on this repository. Say why at each step. Never overwrite a file that exists; add a section or report the difference.

If the project has a test command, propose a workflow that runs it and making it a required check; the owner adds it, since it lives under `.github/`.

To check an existing setup, compare each item above with what GitHub reports and list actual against expected. Change nothing.

## Stop when

- The repository shows signs of production use (deploy configuration, real secrets, `.env` files). Say that this is outside what the harness guards and let the owner decide.
- Rulesets are unavailable on this repository's plan. Report it; do not substitute something weaker silently.

## Outputs

The ruleset, the collaborator invitation, a setup pull request, and the check's result. Tell the owner to finish the GitHub connection before starting any session that will work as the bot: switching it mid-session breaks that session's GitHub access.
