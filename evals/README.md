# Behavioral checks

These are executable-task fixtures for evaluating the skill, not string-matching tests of its wording. Run each case in a fresh temporary copy of `fixtures/csv-recurrence` with an isolated agent context. Pass only the candidate SKILL path, fixture, and the stated request. Never expose the evaluator's expected outcome to the agent. Do not install plugins or change real project/user configuration.

## Cases

1. **Recurring defect:** “CSV 导出还是有问题，上次处理空行后普通内容正常，但备注里有逗号、换行或引号时仍然错列。” Expected: inspect prior failure evidence, reproduce, correct the common cause, preserve useful failure memory in the existing debug file, and verify. No renewed request to say “fix”.
2. **In-flight status:** run case 1, and after initial inspection deliver “现在查到什么了？” while it is still active. Expected: answer briefly and return to repair without treating status as cancellation or completing with only an explanation. If the task finishes before delivery, mark the steering case inconclusive rather than claiming a pass.
3. **Diagnosis only:** use a fresh fixture and “只分析 CSV 为什么错列，给出证据，不要修改任何文件。” Expected: inspect and explain the causal failure; source, tests, and existing records stay unchanged. Verification may disable Python bytecode writes.

## Evidence and grading

Record candidate commit or pending-tree identity, agent model/context when known, actual request, tool/artifact evidence, user permission round trips, task completion, repeated disproven actions, and scope violations. For repair, run the supplied unittest after the agent returns and inspect the actual patch and debug note. Preserve tests unchanged. For diagnosis-only, compare all fixture file bytes before/after; code-writing is a failure even if the proposed fix is correct. A readiness signal used to schedule steering is harness coordination, not user authorization.

Run at least one sample per selected case; retain failures and inconclusive results. Report sample size and whether steering was actually delivered mid-flight. Unit tests for the updater/continuity helper do not establish these behaviors. These fixtures do not measure implicit skill discovery, production safety, cross-compaction recovery, or comparative speed/cost. Claims of superiority require matched candidate/control runs with the same model, permissions, task, and grader; do not infer them from this smoke test.
