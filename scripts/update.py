#!/usr/bin/env python3
"""Safely check for and fast-forward a Git-installed Silverlocks Skill."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlparse


REMOTE = "origin"
BRANCH = "main"
REMOTE_REF = f"refs/remotes/{REMOTE}/{BRANCH}"
CHECK_INTERVAL_SECONDS = 24 * 60 * 60
RETRY_INTERVAL_SECONDS = 60 * 60
GIT_TIMEOUT_SECONDS = 45
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
REQUIRED_REMOTE_FILES = (
    "VERSION",
    "SKILL.md",
    "agents/openai.yaml",
    "scripts/continuity.py",
    "scripts/update.py",
)


def git(root: Path, *arguments: str, timeout: int = GIT_TIMEOUT_SECONDS) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", "-C", str(root), *arguments],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return subprocess.CompletedProcess(arguments, 124, "", type(exc).__name__)


def git_text(root: Path, *arguments: str) -> str | None:
    completed = git(root, *arguments)
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value or None


def canonical_origin(value: str) -> str | None:
    candidate = value.strip().rstrip("/")
    if not candidate:
        return None

    if candidate.startswith("git@github.com:"):
        path = candidate.removeprefix("git@github.com:")
        candidate = f"ssh://git@github.com/{path}"

    parsed = urlparse(candidate)
    if parsed.scheme in {"https", "ssh"} and parsed.hostname:
        host = parsed.hostname.lower()
        if host != "github.com" or parsed.query or parsed.fragment:
            return None
        path = parsed.path.strip("/")
        if path.endswith(".git"):
            path = path[:-4]
        if not path or path.count("/") != 1:
            return None
        return f"github.com/{path.lower()}"

    if parsed.scheme:
        return None

    try:
        return f"file://{Path(candidate).expanduser().resolve()}"
    except OSError:
        return None


TRUSTED_ORIGINS = {"github.com/lemonrem/silverlocks"}


def parse_version(value: str) -> tuple[int, int, int] | None:
    match = SEMVER.fullmatch(value.strip())
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def iso_time(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat().replace("+00:00", "Z")


def cache_path(root: Path) -> Path | None:
    raw = git_text(root, "rev-parse", "--git-path", "silverlocks-update.json")
    if raw is None:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def load_cache(path: Path | None) -> dict[str, object]:
    if path is None or not path.is_file() or path.is_symlink():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def save_cache(path: Path | None, payload: dict[str, object]) -> None:
    if path is None or path.is_symlink():
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".silverlocks-update-",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
            temporary = Path(handle.name)
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    except OSError:
        try:
            temporary.unlink(missing_ok=True)
        except (OSError, UnboundLocalError):
            pass


def result(root: Path, action: str, *, ok: bool = True, **details: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "ok": ok,
        "action": action,
        "skill_root": str(root),
    }
    payload.update(details)
    return payload


def validate_remote_tree(root: Path) -> str | None:
    for relative_path in REQUIRED_REMOTE_FILES:
        if git(root, "cat-file", "-e", f"{REMOTE_REF}:{relative_path}").returncode != 0:
            return f"missing required file: {relative_path}"

    skill = git_text(root, "show", f"{REMOTE_REF}:SKILL.md")
    metadata = git_text(root, "show", f"{REMOTE_REF}:agents/openai.yaml")
    if skill is None or not re.search(r"(?m)^name:\s*silverlocks\s*$", skill):
        return "remote SKILL.md does not identify Silverlocks"
    if metadata is None or not re.search(r"(?m)^\s*allow_implicit_invocation:\s*true\s*$", metadata):
        return "remote metadata does not allow implicit invocation"
    return None


def record_cache(
    path: Path | None,
    *,
    now: float,
    action: str,
    retry: bool = False,
    local_version: str | None = None,
    remote_version: str | None = None,
) -> None:
    interval = RETRY_INTERVAL_SECONDS if retry else CHECK_INTERVAL_SECONDS
    save_cache(
        path,
        {
            "schema": "silverlocks-update/v1",
            "checked_at": now,
            "next_check_at": now + interval,
            "action": action,
            "local_version": local_version,
            "remote_version": remote_version,
        },
    )


def perform_update(
    root: Path,
    *,
    force: bool = False,
    check_only: bool = False,
    trusted_origins: set[str] | None = None,
    now: float | None = None,
) -> dict[str, object]:
    root = root.expanduser().resolve()
    trusted_origins = TRUSTED_ORIGINS if trusted_origins is None else trusted_origins
    now = time.time() if now is None else now

    top_level = git_text(root, "rev-parse", "--show-toplevel")
    if top_level is None or Path(top_level).resolve() != root:
        return result(root, "not_git_install", ok=False, reason="skill root is not a Git checkout root")

    origin = git_text(root, "remote", "get-url", REMOTE)
    canonical = canonical_origin(origin or "")
    if canonical not in trusted_origins:
        return result(root, "untrusted_origin", ok=False, reason="origin is not the trusted Silverlocks repository")

    branch = git_text(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch != BRANCH:
        return result(root, "wrong_branch", ok=False, branch=branch, required_branch=BRANCH)

    status = git(root, "status", "--porcelain", "--untracked-files=all")
    if status.returncode != 0:
        return result(root, "git_error", ok=False, reason="could not inspect the working tree")
    if status.stdout.strip():
        return result(root, "dirty_worktree", ok=False, reason="local changes were preserved; update was skipped")

    local_version_path = root / "VERSION"
    try:
        local_version = local_version_path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return result(root, "invalid_local_version", ok=False, reason="VERSION is missing or unreadable")
    local_parsed = parse_version(local_version)
    if local_parsed is None:
        return result(root, "invalid_local_version", ok=False, local_version=local_version)

    path = cache_path(root)
    cached = load_cache(path)
    next_check_at = cached.get("next_check_at")
    if not force and isinstance(next_check_at, (int, float)) and now < next_check_at:
        return result(
            root,
            "cached",
            local_version=local_version,
            previous_action=cached.get("action"),
            next_check_at=iso_time(float(next_check_at)),
        )

    fetched = git(root, "fetch", "--quiet", REMOTE, f"{BRANCH}:{REMOTE_REF}")
    if fetched.returncode != 0:
        record_cache(path, now=now, action="network_error", retry=True, local_version=local_version)
        return result(
            root,
            "network_error",
            ok=False,
            local_version=local_version,
            reason="could not fetch the trusted origin; retry is rate-limited for one hour",
        )

    remote_version = git_text(root, "show", f"{REMOTE_REF}:VERSION")
    remote_parsed = parse_version(remote_version or "")
    if remote_parsed is None:
        record_cache(
            path,
            now=now,
            action="invalid_remote_version",
            retry=True,
            local_version=local_version,
            remote_version=remote_version,
        )
        return result(root, "invalid_remote_version", ok=False, local_version=local_version)

    if remote_parsed <= local_parsed:
        action = "up_to_date" if remote_parsed == local_parsed else "remote_version_older"
        record_cache(
            path,
            now=now,
            action=action,
            local_version=local_version,
            remote_version=remote_version,
        )
        return result(root, action, local_version=local_version, remote_version=remote_version)

    invalid_reason = validate_remote_tree(root)
    if invalid_reason is not None:
        record_cache(
            path,
            now=now,
            action="invalid_remote_tree",
            retry=True,
            local_version=local_version,
            remote_version=remote_version,
        )
        return result(
            root,
            "invalid_remote_tree",
            ok=False,
            local_version=local_version,
            remote_version=remote_version,
            reason=invalid_reason,
        )

    ancestor = git(root, "merge-base", "--is-ancestor", "HEAD", REMOTE_REF)
    if ancestor.returncode != 0:
        record_cache(
            path,
            now=now,
            action="diverged",
            local_version=local_version,
            remote_version=remote_version,
        )
        return result(
            root,
            "diverged",
            ok=False,
            local_version=local_version,
            remote_version=remote_version,
            reason="local history was preserved; automatic update requires a fast-forward",
        )

    old_revision = git_text(root, "rev-parse", "HEAD")
    if check_only:
        record_cache(
            path,
            now=now,
            action="update_available",
            local_version=local_version,
            remote_version=remote_version,
        )
        return result(
            root,
            "update_available",
            local_version=local_version,
            remote_version=remote_version,
            current_revision=old_revision,
            available_revision=git_text(root, "rev-parse", REMOTE_REF),
        )

    merged = git(root, "merge", "--quiet", "--ff-only", REMOTE_REF)
    if merged.returncode != 0:
        record_cache(
            path,
            now=now,
            action="merge_failed",
            retry=True,
            local_version=local_version,
            remote_version=remote_version,
        )
        return result(
            root,
            "merge_failed",
            ok=False,
            local_version=local_version,
            remote_version=remote_version,
            reason="fast-forward failed; local files were not intentionally overwritten",
        )

    new_revision = git_text(root, "rev-parse", "HEAD")
    try:
        installed_version = local_version_path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        installed_version = ""
    if installed_version != remote_version or new_revision == old_revision:
        return result(
            root,
            "post_update_validation_failed",
            ok=False,
            local_version=installed_version or None,
            remote_version=remote_version,
            old_revision=old_revision,
            new_revision=new_revision,
        )

    record_cache(
        path,
        now=now,
        action="updated",
        local_version=installed_version,
        remote_version=remote_version,
    )
    return result(
        root,
        "updated",
        local_version=local_version,
        installed_version=installed_version,
        old_revision=old_revision,
        new_revision=new_revision,
        restart_recommended=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Silverlocks Git checkout root (defaults to this installed Skill)",
    )
    parser.add_argument("--force", action="store_true", help="ignore the rate-limit cache")
    parser.add_argument("--check-only", action="store_true", help="report an update without applying it")
    arguments = parser.parse_args()

    payload = perform_update(arguments.root, force=arguments.force, check_only=arguments.check_only)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if payload["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
