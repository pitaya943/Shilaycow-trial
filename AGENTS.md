# Agents

## shilaycow

This repository runs shilaycow in auto mode. Its settings are in `.shilaycow/config.yml`, and the pitfalls earlier tasks hit are in `.shilaycow/pitfalls.md`: read it before building.

- Agents act as the bot named in the config, never as the owner.
- Work lives on branches: `task/<slug>` (one per task, one pull request into `main`), `work/<slug>/<ticket>` (a ticket, merged into its task branch), `spike/<name>` (throwaway experiments).
- Only the owner merges into `main`. A ruleset on `main` enforces this; never push to `main`.
- Builders work in worktrees under `.shilaycow/worktrees/`, which git ignores.
