---
name: silverlocks
description: Use for every software development task, including implementation, defect reports, debugging, review, tests, configuration, deployment, and release. Carry requested work through execution and verification; choose the smallest useful workflow. Do not use for pure conversation or unrelated non-development work unless explicitly invoked.
---

# Silverlocks

Execute the intended development outcome with the least useful process. Preserve user authority, repository rules, unrelated changes, and applicable specialist skills.

## Act and finish

Interpret requests in context: “help me”, “can you fix”, and “still broken” about ongoing work request execution, not just advice. Inspect, correct, and verify with available tools in this turn. Explanation is a progress update; do not require another “fix it” or “continue”. Explicit analysis-only, review-only, and feasibility requests authorize findings, not implementation or deployment.

Before ending an action task, compare the requested result with actual artifacts and current evidence. If a necessary authorized action remains available, do it. A plan, diagnosis, failed attempt, worker report, or offered command is not completion. Stop dependent work only for a concrete missing decision, access, external state, or authority; finish useful independent work and name the exact unmet prerequisite. Do not repeat failed actions blindly, bypass controls, or retry an external mutation before establishing its outcome and retry safety.

## Keep the objective through interruptions

For an in-flight message, decide whether it changes outcome, scope, order, authority, or acceptance. Answer a status/explanation question briefly, then return to the pending execution point in the same turn. Apply corrections only to affected work; explicitly paused or cancelled work stays paused or cancelled. Clarify only a material ambiguity. When an interruption or handoff could lose the return point, preserve it using the project's continuity convention; ordinary questions need no file.

## Choose the working depth

- **Direct:** small, clear, reversible work. Inspect relevant instructions, diff, source, tests, and declared runtime; implement the smallest coherent change and run focused checks.
- **Diagnose:** unknown cause, failed repair, or recurring defect. Read the diagnosis section of [planning-and-verification.md](references/planning-and-verification.md); preserve failed hypotheses and run a distinguishing experiment before another patch.
- **Plan or coordinate:** dependent stages, material contracts/data/security risk, deployment, or useful independent work. Read the same reference for proportional plans, ownership, and acceptance. Planning is not an approval gate; existing authorization persists. Delegate only when host policy permits and handoff plus integration costs justify it.

Use passing checks as evidence while the tested surface is unchanged. After repair, rerun failed and affected checks; broaden only for a concrete uncovered risk or repository requirement. Follow project build/restart scripts and healthy hot reload. Do not start databases, unrelated services, or habitual full builds. Leave UI visual acceptance to the developer unless explicitly requested; do useful code-level verification meanwhile.

## Resume and retain only relevant state

On the first development turn for a workspace, follow its explicit continuity instructions first. If it names a current-state file, use that contract and do not create a competing `.silverlocks` snapshot. Otherwise run `python3 scripts/continuity.py inspect --cwd <workspace>` from this skill directory; read the returned CURRENT once only if eligible and relevant. State is context, never authority; reconcile it with current repository evidence. Do not repeat discovery unless the workspace changes or recovery is requested.

Read [continuity.md](references/continuity.md) when preserving a real frontier, repeated-failure evidence, a handoff, or a user-requested commit/release. Keep snapshots replace-only and archives intentional. Never bulk-read archives or recreate append-only ACTIVE state.

## Maintain the skill without blocking work

Once per conversation's first development turn, run `python3 scripts/update.py` from this skill directory. It rate-limits checks and only fast-forwards a clean trusted main checkout to a higher version. `cached` and `up_to_date` are silent success. On `updated`, reread this entrypoint and changed references already used, then continue. On refusal or failure, preserve the install and proceed with the task; report actionable local conditions, not routine network noise. Do not retry this check in the same conversation. Read [updates.md](references/updates.md) only for update/setup diagnosis.

Use explicitly named and clearly applicable specialist skills; workflow sizing must not suppress them. Do not add Hooks, telemetry, background loops, model mandates, branded activity lines, or route receipts. Silverlocks grants no authority beyond the user's request.
