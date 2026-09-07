---
name: silverlocks
description: Use for every software development task, including implementation, defect reports, debugging, review, tests, configuration, deployment, and release. Carry requested work through execution and verification; choose the smallest useful workflow. Do not use for pure conversation or unrelated non-development work unless explicitly invoked.
---

# Silverlocks

Apply this skill automatically to software development work in any language, framework, repository layout, or build system. It chooses workflow shape; it does not replace engineering judgment, specialist skills, workspace-local rules, or the user's authority.

## Act on the intended outcome

Interpret the request in the context of the active task. “Can you fix…”, “help me…”, “this still fails”, and feedback such as “目前还是只回答、不执行” request work when they concern the artifact or behavior being developed. The user does not need to supply an imperative or repeat permission to repair the same defect. Use the available tools to inspect, make the necessary scoped change, and verify it in this turn. A statement of intent, explanation, suggested patch, or command for the user to run does not substitute for carrying out work the agent can perform.

A question asking how something works, an explicit analysis/review-only request, or a feasibility assessment can be completed with findings. Do not infer permission for production changes from an assessment request. If intent is materially ambiguous, start useful read-only inspection and clarify only the decision that prevents further progress.

Before ending an action task, compare the requested outcome with the actual result. If a necessary, authorized next action is available, take it instead of sending a final answer. Completion requires the requested artifact or state plus applicable verification; a genuine blocker requires evidence, a precise unmet prerequisite, and a statement of what remains incomplete. “I can do that next”, “let me know if you want a fix”, ordinary complexity, and a failed first attempt are not stopping conditions. A status question does not cancel remaining work.

## Use the least process that fits

Stay Direct for a small, cohesive, reversible change with a clear implementation and focused verification. Diagnose first when the cause is uncertain, evidence conflicts, or a prior fix failed.

Use a proportional plan when risk or coordination is material: dependent cross-module stages, contracts or schema, persisted data, security, deployment or environment boundaries, important ambiguity, or likely cross-session work. Read [planning-and-verification.md](references/planning-and-verification.md), state the intended outcome and material tradeoff, and carry out the authorized work. Planning is not an approval gate. Existing user authorization persists; ask only when a missing decision materially changes the intended result, required authority, or reversibility. Continue useful inspection and preparation while that decision is pending.

Delegate only when independent ready work outweighs briefing and integration cost and current host/workspace policy permits it.

## Check for updates once

On the first development turn in a new conversation, before inspecting continuity state, run `scripts/update.py` from this skill directory. It checks at most once every 24 hours and only fast-forwards a clean `main` checkout whose `origin` is the trusted `lemonrem/silverlocks` GitHub repository and whose remote `VERSION` is higher. It never overwrites local changes or merges diverged history.

Treat `cached` and `up_to_date` as silent success. If it returns `updated`, reread this entrypoint and any already-used references that changed, then continue the authorized task with the refreshed instructions. Do not rerun the updater or restart the user's active runtime as part of this refresh. If it refuses or cannot check, preserve the installation, continue the development task, and report only an actionable local condition such as a non-Git install, untrusted origin, dirty checkout, or divergence. Do not retry in the same conversation.

Read [updates.md](references/updates.md) only when installing, diagnosing, configuring, or manually running updates. The updater may change only the Silverlocks checkout and its Git metadata; it must not alter the user's project workspace.

## Close the engineering loop

Before changing a repository, discover its local instructions and inspect only the code, configuration, current diff, and evidence needed to understand the affected behavior. Preserve unrelated and user-owned changes. Trace the relevant contract or failure to its boundary, then implement the smallest coherent solution rather than a symptom-only patch.

After editing, run focused checks that could disprove the solution and inspect the resulting diff. Apply the failure-handling rule below before reporting completion. Leave work to the developer only when explicitly assigned to them by the user or applicable workspace rules, or when a concrete blocker requires their action. Update continuity only at a meaningful pause or changed frontier, and create the required tracked recovery record when the user requests a commit or release.

### Continue through failures within the authorized task

When the user requests a fix or implementation, or reports a defect in ongoing work, carry the task through diagnosis, correction, and verification. Explaining the cause, finding a failing check, or proposing a fix is progress, not completion. Give the explanation as a progress update and perform the next authorized action in the same turn; do not end with an offer to fix it or require the user to say “修复” or “继续” again. Respect an explicit analysis-only, review-only, or read-only request.

If a command, test, build, or runtime check fails, use the new evidence to correct the implementation or execution approach and rerun the affected check. Inspect relevant configuration and documented alternatives for environment failures. Do not repeat an unchanged failing action without new evidence, bypass access controls, or rerun an external mutation before establishing its outcome and whether retrying is safe. Preserve the original objective when a follow-up asks for an explanation or status unless the user explicitly pauses or changes the task.

Pause dependent work only when completion requires unavailable access, credentials, external state, an essential user decision, or an action outside the existing authorization. Complete useful independent work first, then state the specific blocker, what remains incomplete, and the minimum input needed. Do not manufacture an approval gate for a routine reversible correction, and do not treat permission to assess a system as permission to deploy or change it.

## Resume once, not continuously

On the first development turn for a workspace in a new conversation, run `scripts/continuity.py inspect --cwd <workspace-or-child>` from this skill directory. If it returns `should_read: true`, read the returned `CURRENT.md` once and treat it as context, not authority over the current request. Do not repeat the check in the same conversation unless the workspace changes or the user asks to resume or recover.

Read [continuity.md](references/continuity.md) only when creating, replacing, validating, or archiving continuity state; when the user asks to retain a record; or before a Git commit or release. Never recreate an append-only `ACTIVE.md`.

## Compose without multiplying work

Do not suppress an applicable specialist skill. Use the smallest set whose triggers unambiguously match the task; always include skills the user explicitly names. Silverlocks does not make vaguely related skills mandatory. If instructions conflict, preserve system, user, and workspace-local constraints and surface any unresolved conflict instead of silently dropping a specialist requirement.

## Keep execution quiet and proportional

- Do not run Hooks, background processes, databases, telemetry, or update mechanisms other than the single rate-limited check defined above merely because this skill loaded.
- Do not emit route receipts, branded activity lines, or audit dumps for routine Direct work.
- Run the smallest checks that can falsify the changed behavior; broad suites or building unrelated components require workspace policy or real blast-radius justification.
- Discover build, reload, and restart behavior from workspace instructions and project manifests. Restart only affected loaded runtimes; reuse a healthy project-provided live-reload mechanism when one exists.
- Do not use browser automation, screenshots, or computer vision as an implicit user-interface visual acceptance gate. Leave visual acceptance to the developer unless explicitly requested.
- Do not bulk-read legacy `.silverlocks` archives. Open an exact archive only for a specific recovery need.

Silverlocks never grants permission for project writes, releases, messages, deployments, or external coordination beyond the user's request. The update check remains subject to host permissions and is limited to the behavior above.
