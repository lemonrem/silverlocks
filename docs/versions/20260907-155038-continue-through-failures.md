# Continue through failures within authorized work

- Base revision: `dc7bf2b`.
- Objective: prevent Silverlocks from ending a repair task after explaining the cause and waiting for the user to request the same repair again.
- Outcome: diagnosis is a progress update; authorized work continues through correction and verification. Failed checks lead to evidence-driven corrections and targeted reruns.
- Scope: `SKILL.md` and `references/planning-and-verification.md`; no version bump or runtime changes.
- Boundaries: preserve explicit analysis-only requests, access controls, external mutation retry safety, and existing authorization. Pause dependent work for concrete missing inputs or authority while completing useful independent work. Checks remain with the developer only when assigned by the user/workspace or blocked.
- Verification: skill-creator `quick_validate.py` passed using `uv run --no-project --with pyyaml` after the system Python lacked PyYAML; `git diff --check` passed. Instruction changes were reviewed for consistency. No independent behavioral evaluation was run.
- Recovery: revert the commit containing this record to restore the previous workflow instructions; no application or data rollback is required.
