# Installation prerequisite recovery record

Date: 2026-09-04

## Objective

Make conflicting workflow removal an explicit prerequisite rather than leaving it only inside the autonomous installation prompt.

## Outcome

- Both README installation sections now show a prominent prerequisite before any installation method.
- Existing user-level Superpowers, Goldilocks, and legacy `goldlocks` installations must be disabled and then uninstalled before Silverlocks installation.
- Hooks registered by those installations must be removed from the active configuration.

## Decisions and constraints

- The prerequisite applies only to the user-level Codex environment.
- Existing protections for project files, archives, continuity state, local changes, and unrelated configuration remain unchanged in the full installation prompt.

## Components changed

- `README.md`
- `README.zh-CN.md`

## Verification

- Both README files have balanced fenced code blocks.
- All local Markdown links resolve.
- Repository diff whitespace checks passed.
- Required product names, disable-then-uninstall ordering, Hook cleanup, and the installation gate are present on both pages.

## Recovery

Revert the commit containing this record to remove the prominent prerequisite while retaining the same requirement inside the autonomous installation prompt.
