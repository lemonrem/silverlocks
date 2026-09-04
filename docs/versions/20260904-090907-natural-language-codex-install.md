# Natural-language Codex installation recovery record

Date: 2026-09-04

## Objective

Make the primary Codex installation method a natural-language request rather than an explicit installer invocation or procedural command list.

## Outcome

- The recommended installation path on both README pages is now one natural-language prompt addressed directly to Codex.
- Users do not need to know the name or syntax of the built-in Skill installer.
- The prompt authorizes autonomous safe installation or update while preserving local changes and unrelated configuration.
- User-level Superpowers and Goldilocks installations, including legacy `goldlocks` entries and their Hooks, are disabled and uninstalled before Silverlocks is installed.
- The manual Git method remains available only as a fallback.

## Decisions and constraints

- The prompt keeps installation verification, conflict reporting, and restart guidance.
- Removal is limited to user-level Codex installations and enablement entries; repository files, archives, and continuity state are preserved.
- Matching content found only in the current business repository is reported rather than deleted.
- It does not authorize changes to the current business repository or creation of `CURRENT.md` as an installation side effect.
- Detailed installer implementation choices are left to Codex and its currently available capabilities.

## Components changed

- `README.md`
- `README.zh-CN.md`
- `CHANGELOG.md`

## Verification

- Both README files have balanced fenced code blocks.
- All local Markdown links resolve.
- Repository diff whitespace checks passed.
- No explicit `$skill-installer` invocation remains on either README page.
- Both natural-language prompts explicitly require prior handling of Superpowers, Goldilocks, legacy `goldlocks` entries, and their Hook configuration.

## Recovery

Revert the commit containing this record to restore the prior explicit installer-oriented documentation.
