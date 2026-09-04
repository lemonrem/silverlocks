# Codex autonomous installation prompt recovery record

Date: 2026-09-04

## Objective

Add a page-level prompt that lets a Codex agent autonomously install or safely update Silverlocks in a user-level environment.

## Outcome

- The English and Simplified Chinese README pages contain equivalent copy-paste installation prompts.
- The prompt prefers the built-in `$skill-installer` and falls back to the documented user-level Git installation path.
- Existing clean installations can update with fast-forward-only Git operations.
- Local edits, unrelated directories, and existing files are protected from overwrite or deletion.
- Duplicate broad workflow Skills can be disabled without deleting their files.
- Installation validation checks the Skill entrypoint, implicit invocation policy, and continuity helper.

## Decisions and constraints

- The prompt is documentation only; it does not change Silverlocks runtime instructions.
- Installation must not modify the current business repository or create `CURRENT.md` as a side effect.
- The granted authority covers only the local Skill installation and conflict-safe Codex configuration.
- Project builds, tests, external deployment, and unrelated configuration remain out of scope.

## Components changed

- `README.md`
- `README.zh-CN.md`
- `CHANGELOG.md`

## Verification

- Both README files have balanced fenced code blocks.
- All local Markdown links resolve.
- Repository diff whitespace checks passed.
- A repository-wide scan confirmed that no teammate-specific wording remains.
- The prompt explicitly bounds writes, protects existing installations, and avoids business-repository side effects.

## Recovery

Revert the commit containing this record to remove the autonomous installation prompt while retaining all existing Silverlocks behavior and documentation.
