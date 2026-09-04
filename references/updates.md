# Safe updates

Use this reference only for Silverlocks installation, update diagnosis, update policy changes, or an explicit manual update.

## Automatic check

On the first development task in a new Codex conversation, run from the installed Silverlocks directory:

```bash
python3 scripts/update.py
```

The updater stores only a small rate-limit record inside the installation's Git metadata. A successful check is cached for 24 hours. A network failure is cached for one hour. It does not use a Hook, daemon, scheduler, startup item, or project file.

Automatic application requires all of these conditions:

- the installation directory is the root of a Git checkout;
- `origin` canonically identifies `https://github.com/lemonrem/silverlocks`;
- the checked-out branch is `main`;
- tracked and untracked local state is clean;
- the remote has a strictly higher three-part `VERSION`;
- the local revision is an ancestor of `origin/main`;
- required Skill files and implicit-invocation metadata are present remotely.

The update is a fast-forward with Git Hooks disabled for that operation. If any condition fails, the updater preserves local files and returns structured JSON explaining why. Never work around a rejection by deleting changes, resetting history, changing the remote, or forcing a merge unless the user explicitly asks for installation repair.

## Manual commands

Ignore the cache and safely apply an eligible update:

```bash
python3 scripts/update.py --force
```

Check availability without updating:

```bash
python3 scripts/update.py --force --check-only
```

Important actions include `updated`, `up_to_date`, `cached`, `update_available`, `not_git_install`, `untrusted_origin`, `dirty_worktree`, `diverged`, and `network_error`.

When an update is applied, finish the current task with the already-loaded instructions. Recommend one Codex restart afterward if immediate adoption of changed Skill instructions matters. Codex normally detects local Skill changes automatically, so no restart loop or service restart is part of this mechanism.

## Installation requirement

Auto-update cannot bootstrap an installation that was copied without `.git`, including some archive or installer-based copies. Install Silverlocks as a Git clone to enable it. An existing pre-`0.2.0` installation needs one manual fast-forward or reinstall before automatic checks are available.

The trust boundary is the `lemonrem/silverlocks` repository's `main` branch. Publishing a release therefore requires incrementing the repository `VERSION`; ordinary commits without a higher version are fetched but not applied.
