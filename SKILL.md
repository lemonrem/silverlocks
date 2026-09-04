---
name: silverlocks
description: Use for every software development task, including codebase analysis, implementation, modification, debugging, refactoring, review, testing, build or configuration changes, deployment, and release. Silently choose the smallest useful execution structure; do not use for pure conversation or unrelated non-development work unless explicitly invoked.
---

# Silverlocks

Apply this skill automatically to software development work in any language, framework, repository layout, or build system. It chooses workflow shape; it does not replace engineering judgment, specialist skills, workspace-local rules, or the user's authority.

## Use the least process that fits

Stay Direct for a small, cohesive, reversible change with a clear implementation and focused verification. Diagnose first when the cause is uncertain, evidence conflicts, or a prior fix failed.

Use the Plan Gate when risk or coordination is material: dependent cross-module stages, contracts or schema, persisted data, security, deployment or environment boundaries, important ambiguity, or likely cross-session work. Before editing, give one concise best recommendation with scope and the material tradeoff. Obtain approval unless the user has already explicitly approved that recommendation. After approval, read [planning-and-verification.md](references/planning-and-verification.md), write the proportional execution plan, and carry it out. Do not read that reference merely to decide whether the gate applies.

Delegate only when independent ready work outweighs briefing and integration cost and current host/workspace policy permits it.

## Resume once, not continuously

On the first development turn for a workspace in a new conversation, run `scripts/continuity.py inspect --cwd <workspace-or-child>` from this skill directory. If it returns `should_read: true`, read the returned `CURRENT.md` once and treat it as context, not authority over the current request. Do not repeat the check in the same conversation unless the workspace changes or the user asks to resume or recover.

Read [continuity.md](references/continuity.md) only when creating, replacing, validating, or archiving continuity state; when the user asks to retain a record; or before a Git commit or release. Never recreate an append-only `ACTIVE.md`.

## Compose without multiplying work

Do not suppress an applicable specialist skill. Use the smallest set whose triggers unambiguously match the task; always include skills the user explicitly names. Silverlocks does not make vaguely related skills mandatory. If instructions conflict, preserve system, user, and workspace-local constraints and surface any unresolved conflict instead of silently dropping a specialist requirement.

## Keep execution quiet and proportional

- Do not run Hooks, background processes, update checks, databases, or telemetry merely because this skill loaded.
- Do not emit route receipts, branded activity lines, or audit dumps for routine Direct work.
- Run the smallest checks that can falsify the changed behavior; broad suites or building unrelated components require workspace policy or real blast-radius justification.
- Discover build, reload, and restart behavior from workspace instructions and project manifests. Restart only affected loaded runtimes; reuse a healthy project-provided live-reload mechanism when one exists.
- Do not use browser automation, screenshots, or computer vision as an implicit user-interface visual acceptance gate. Leave visual acceptance to the developer unless explicitly requested.
- Do not bulk-read legacy `.silverlocks` archives. Open an exact archive only for a specific recovery need.

Silverlocks never grants permission for extra writes, network actions, releases, or external coordination.
