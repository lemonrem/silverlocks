# Continuity and archives

Keep resumable state compact and keep historical records out of normal startup context.

## Current frontier

Use `<workspace>/.silverlocks/CURRENT.md` only when work may need to resume in another conversation. Do not create it for a completed one-turn fix.

The entrypoint already performs the once-per-conversation inspection. `should_read: true` means the file is structurally eligible, not necessarily relevant. Compare its objective with the current request; ignore unrelated context without deleting it. `stale_hint`, `revision_changed`, and `age_days` are advisory and never automatically invalidate a recoverable task.

`CURRENT.md` must remain at or below 8 KiB and normally below 120 lines. Keep only:

- current objective and status (`active` or `paused`);
- verified progress rather than intended work;
- one exact next action;
- durable constraints and decisions;
- minimal evidence such as an optional version-control revision or relevant plan path.

Never include credentials, tokens, sensitive endpoints, raw private logs, conversational transcripts, or a growing history of completed steps.

## Replace deterministically

Prepare a body containing exactly these sections:

```markdown
# Current frontier

## Verified progress
- ...

## Exact next action
- ...

## Constraints and decisions
- ...

## Evidence
- ...
```

Then write it through the helper instead of appending to the live file:

```bash
scripts/continuity.py write \
  --cwd <workspace-or-child> \
  --status paused \
  --objective "Short outcome to resume" \
  --body-file <prepared-body.md>
```

Use `--body-file -` to read the body from standard input. The helper resolves the workspace, records a Git revision when available, validates required sections and size, and atomically replaces `CURRENT.md`. It refuses to replace a different objective unless `--archive-existing <slug>` is supplied. In a directory without Git metadata or an existing `.silverlocks` directory, pass the workspace root itself rather than an arbitrary child directory.

Refresh only after a meaningful milestone, before pausing, or when the exact next action changes. Re-summarize the whole state each time; do not retain obsolete bullets merely because they were previously written.

## Archive intentionally

When a task finishes, is cancelled, is replaced, or the user explicitly requests a retained checkpoint, archive it with:

```bash
scripts/continuity.py archive --cwd <workspace-or-child> --slug <short-name>
```

This moves the snapshot to `.silverlocks/archive/work/YYYYMMDD-HHMMSS-<slug>.md`. Use `--keep-current` only for an explicit checkpoint while the same task remains active. Archives are immutable; corrections get a new file. Append-only legacy files belong under `.silverlocks/archive/legacy/` and are never startup context.

## Required Git and release records

`.silverlocks` is local operational state and must not be the only recovery record for a committed or released version.

Before completing any user-requested Git commit or release, create a tracked Markdown recovery record. Reuse the repository's established changelog, release-note, ADR, or version-archive convention when one exists. Otherwise create:

- `docs/versions/<version>.md` for a named release;
- `docs/versions/YYYYMMDD-HHMMSS-<slug>.md` for a commit without a release version.

The record must include the objective, user-visible or operational outcome, important decisions and constraints, files or components changed, verification actually performed, and recovery or rollback guidance. Never claim checks that did not run and never store secrets. Stage the record with the related changes.

A commit cannot contain its own final hash. Record the base revision when useful and treat the resulting commit as the archived revision. For a release whose final operational outcome is known only after deployment, follow repository policy: either finalize the record before release with pending acceptance clearly marked, or add a separate post-release record that distinguishes the released revision from the archive-finalization revision.
