#!/usr/bin/env python3
"""Inspect, atomically replace, or archive compact Silverlocks continuity state."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


MAX_BYTES = 8 * 1024
STATE_DIR_NAME = ".silverlocks"
SCHEMA = "silverlocks-current/v1"
ALLOWED_STATUS = {"active", "paused"}
REQUIRED_FIELDS = {"schema", "status", "workspace_root", "updated_at", "objective"}
REQUIRED_HEADINGS = (
    "# Current frontier",
    "## Verified progress",
    "## Exact next action",
    "## Constraints and decisions",
    "## Evidence",
)


def command_output(arguments: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            arguments,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return None
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value or None


def workspace_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        state_dir = candidate / STATE_DIR_NAME
        if not state_dir.is_symlink() and state_dir.is_dir():
            return candidate
    git_root = command_output(["git", "-C", str(current), "rev-parse", "--show-toplevel"])
    if git_root:
        return Path(git_root).resolve()
    return current


def ensure_safe_directory(path: Path, *, create: bool) -> None:
    if path.is_symlink():
        raise ValueError(f"unsafe directory is a symlink: {path}")
    if path.exists():
        if not path.is_dir():
            raise ValueError(f"unsafe directory path is not a directory: {path}")
        return
    if not create:
        return

    try:
        path.mkdir(mode=0o700)
    except FileExistsError:
        pass
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"unsafe directory could not be created safely: {path}")


def ensure_safe_state_tree(root: Path, *, create_state: bool, create_archive: bool = False) -> Path:
    state_dir = root / STATE_DIR_NAME
    ensure_safe_directory(state_dir, create=create_state)
    if not create_archive:
        return state_dir

    archive_dir = state_dir / "archive"
    ensure_safe_directory(archive_dir, create=True)
    work_dir = archive_dir / "work"
    ensure_safe_directory(work_dir, create=True)
    return work_dir


def decode_frontmatter_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] == '"':
        decoded = json.loads(value)
        if not isinstance(decoded, str):
            raise ValueError("quoted frontmatter value must be a string")
        return decoded
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def split_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    fields: dict[str, str] = {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body = "\n".join(lines[index + 1 :]).strip()
            return fields, body
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        try:
            fields[key.strip()] = decode_frontmatter_value(value)
        except (json.JSONDecodeError, ValueError):
            return None
    return None


def emit(root: Path, *, code: int = 0, **payload: object) -> int:
    output: dict[str, object] = {"workspace_root": str(root)}
    output.update(payload)
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return code


def version_control_revision(root: Path) -> tuple[str | None, str | None]:
    revision = command_output(["git", "-C", str(root), "rev-parse", "HEAD"])
    if revision:
        return "git", revision
    return None, None


def parse_timestamp(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.astimezone()
    return parsed


def inspect(start: Path) -> int:
    root = workspace_root(start)
    state_dir = root / STATE_DIR_NAME
    try:
        ensure_safe_state_tree(root, create_state=False)
    except (OSError, ValueError) as exc:
        return emit(root, should_read=False, reason="unsafe_state_directory", error=str(exc))
    current = state_dir / "CURRENT.md"

    if current.is_symlink():
        return emit(root, should_read=False, reason="unsafe_path", path=str(current))
    if not current.exists():
        legacy = state_dir / "ACTIVE.md"
        reason = "legacy_only" if legacy.exists() else "missing"
        return emit(root, should_read=False, reason=reason)
    if not current.is_file():
        return emit(root, should_read=False, reason="unsafe_path", path=str(current))

    try:
        size = current.stat().st_size
    except OSError as exc:
        return emit(root, should_read=False, reason="unreadable", error=type(exc).__name__)
    if size > MAX_BYTES:
        return emit(
            root,
            should_read=False,
            reason="oversize",
            path=str(current),
            size_bytes=size,
            max_bytes=MAX_BYTES,
        )

    try:
        text = current.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return emit(root, should_read=False, reason="unreadable", error=type(exc).__name__)

    parsed = split_frontmatter(text)
    if parsed is None:
        return emit(root, should_read=False, reason="invalid_frontmatter", path=str(current))
    fields, body = parsed
    missing = sorted(REQUIRED_FIELDS - fields.keys())
    if missing:
        return emit(root, should_read=False, reason="missing_fields", path=str(current), missing=missing)
    if fields["schema"] != SCHEMA:
        return emit(root, should_read=False, reason="unsupported_schema", path=str(current))
    if fields["status"] not in ALLOWED_STATUS:
        return emit(root, should_read=False, reason="inactive_status", path=str(current), status=fields["status"])
    if not fields["objective"].strip():
        return emit(root, should_read=False, reason="empty_objective", path=str(current))
    try:
        validate_body(body)
    except ValueError as exc:
        return emit(root, should_read=False, reason="invalid_body", path=str(current), error=str(exc))

    declared_root = Path(os.path.expanduser(fields["workspace_root"])).resolve()
    if declared_root != root:
        return emit(
            root,
            should_read=False,
            reason="workspace_mismatch",
            path=str(current),
            declared_workspace_root=str(declared_root),
        )

    updated_at = parse_timestamp(fields["updated_at"])
    if updated_at is None:
        return emit(root, should_read=False, reason="invalid_updated_at", path=str(current))
    age_days = max(
        0,
        int((datetime.now(timezone.utc) - updated_at.astimezone(timezone.utc)).total_seconds() // 86400),
    )
    stale_after_days = 14 if fields["status"] == "active" else 30
    base_revision = fields.get("base_revision") or None
    recorded_revision_system = fields.get("revision_system") or None
    current_revision_system, current_revision = version_control_revision(root)

    return emit(
        root,
        should_read=True,
        reason="eligible",
        path=str(current),
        status=fields["status"],
        updated_at=fields["updated_at"],
        objective=fields["objective"],
        revision_system=recorded_revision_system or current_revision_system,
        base_revision=base_revision,
        plan_path=fields.get("plan_path") or None,
        current_revision=current_revision,
        revision_changed=bool(base_revision and current_revision and base_revision != current_revision),
        age_days=age_days,
        stale_hint=age_days >= stale_after_days,
        size_bytes=size,
        body_lines=len(body.splitlines()),
    )


def normalized_slug(value: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", value.strip(), flags=re.UNICODE)
    slug = slug.replace("_", "-").strip("-")
    return slug[:80]


def archive_snapshot(root: Path, slug_value: str, *, keep_current: bool) -> Path:
    state_dir = ensure_safe_state_tree(root, create_state=False)
    current = state_dir / "CURRENT.md"
    if not current.exists() or current.is_symlink() or not current.is_file():
        raise ValueError("CURRENT.md is missing or unsafe")

    slug = normalized_slug(slug_value)
    if not slug:
        raise ValueError("archive slug is empty")

    archive_dir = ensure_safe_state_tree(root, create_state=False, create_archive=True)
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    target = archive_dir / f"{stamp}-{slug}.md"
    sequence = 2
    while target.exists():
        target = archive_dir / f"{stamp}-{slug}-{sequence}.md"
        sequence += 1

    if keep_current:
        shutil.copy2(current, target)
    else:
        os.replace(current, target)
    os.chmod(target, 0o600)
    return target


def archive_command(start: Path, slug: str, *, keep_current: bool) -> int:
    root = workspace_root(start)
    try:
        target = archive_snapshot(root, slug, keep_current=keep_current)
    except (OSError, ValueError) as exc:
        return emit(root, code=2, action="archive", ok=False, reason=str(exc))
    return emit(root, action="archive", ok=True, path=str(target), current_retained=keep_current)


def read_body(path_value: str) -> str:
    if path_value == "-":
        return sys.stdin.read()
    return Path(path_value).read_text(encoding="utf-8")


def validate_body(body: str) -> str:
    normalized = body.strip()
    if normalized.startswith("---"):
        raise ValueError("body must not contain frontmatter")
    lines = [line.strip() for line in normalized.splitlines()]
    if not lines or lines[0] != REQUIRED_HEADINGS[0]:
        raise ValueError(f"body must start with {REQUIRED_HEADINGS[0]}")
    missing = [heading for heading in REQUIRED_HEADINGS if lines.count(heading) != 1]
    if missing:
        raise ValueError("body must contain each required heading exactly once: " + ", ".join(missing))
    positions = [lines.index(heading) for heading in REQUIRED_HEADINGS]
    if positions != sorted(positions):
        raise ValueError("body headings must appear in the required order")
    unexpected = [
        line
        for line in lines
        if re.match(r"^#{1,6}\s", line) and line not in REQUIRED_HEADINGS
    ]
    if unexpected:
        raise ValueError("body contains an unexpected heading: " + unexpected[0])
    return normalized + "\n"


def quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def write_command(
    start: Path,
    *,
    status: str,
    objective: str,
    body_file: str,
    plan_path: str | None,
    archive_existing: str | None,
) -> int:
    root = workspace_root(start)
    state_dir = root / STATE_DIR_NAME
    try:
        ensure_safe_state_tree(root, create_state=False)
    except (OSError, ValueError) as exc:
        return emit(root, code=2, action="write", ok=False, reason=str(exc))
    current = state_dir / "CURRENT.md"
    objective = objective.strip()
    if not objective or len(objective) > 240:
        return emit(root, code=2, action="write", ok=False, reason="objective must be 1-240 characters")

    try:
        body = validate_body(read_body(body_file))
    except (OSError, UnicodeError, ValueError) as exc:
        return emit(root, code=2, action="write", ok=False, reason=str(exc))

    updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    revision_system, revision = version_control_revision(root)
    frontmatter = [
        "---",
        f"schema: {SCHEMA}",
        f"status: {status}",
        f"workspace_root: {quoted(str(root))}",
        f"updated_at: {updated_at}",
        f"objective: {quoted(objective)}",
    ]
    if revision:
        frontmatter.append(f"revision_system: {revision_system}")
        frontmatter.append(f"base_revision: {revision}")
    if plan_path:
        frontmatter.append(f"plan_path: {quoted(plan_path.strip())}")
    frontmatter.extend(["---", ""])
    content = "\n".join(frontmatter) + body
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_BYTES:
        return emit(
            root,
            code=2,
            action="write",
            ok=False,
            reason="oversize",
            size_bytes=len(encoded),
            max_bytes=MAX_BYTES,
        )

    archived_path: Path | None = None
    should_archive = False
    if current.is_symlink():
        return emit(root, code=2, action="write", ok=False, reason="CURRENT.md is unsafe")
    if current.exists():
        if not current.is_file():
            return emit(root, code=2, action="write", ok=False, reason="CURRENT.md is unsafe")
        try:
            existing_text = current.read_text(encoding="utf-8")
            parsed = split_frontmatter(existing_text)
            existing_objective = parsed[0].get("objective") if parsed else None
        except (OSError, UnicodeError):
            existing_objective = None
        if existing_objective != objective:
            if not archive_existing:
                return emit(
                    root,
                    code=2,
                    action="write",
                    ok=False,
                    reason="objective_changed; archive the existing snapshot first",
                )
            should_archive = True

    temp_path: Path | None = None
    try:
        ensure_safe_state_tree(root, create_state=True)
        descriptor, raw_temp = tempfile.mkstemp(prefix=".CURRENT.", suffix=".tmp", dir=state_dir)
        temp_path = Path(raw_temp)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_path, 0o600)
        if should_archive:
            archived_path = archive_snapshot(root, archive_existing or "replaced", keep_current=True)
        os.replace(temp_path, current)
    except (OSError, ValueError) as exc:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        return emit(root, code=2, action="write", ok=False, reason=str(exc) or type(exc).__name__)

    return emit(
        root,
        action="write",
        ok=True,
        path=str(current),
        archived_path=str(archived_path) if archived_path else None,
        size_bytes=len(encoded),
        revision_system=revision_system,
        base_revision=revision,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Check whether CURRENT.md should be read")
    inspect_parser.add_argument("--cwd", default=os.getcwd(), help="Workspace root or a path inside it")

    write_parser = subparsers.add_parser("write", help="Validate and atomically replace CURRENT.md")
    write_parser.add_argument("--cwd", default=os.getcwd(), help="Workspace root or a path inside it")
    write_parser.add_argument("--status", required=True, choices=sorted(ALLOWED_STATUS))
    write_parser.add_argument("--objective", required=True)
    write_parser.add_argument("--body-file", default="-", help="Markdown body file, or - for stdin")
    write_parser.add_argument("--plan-path")
    write_parser.add_argument("--archive-existing", metavar="SLUG")

    archive_parser = subparsers.add_parser("archive", help="Archive CURRENT.md")
    archive_parser.add_argument("--cwd", default=os.getcwd(), help="Workspace root or a path inside it")
    archive_parser.add_argument("--slug", required=True)
    archive_parser.add_argument("--keep-current", action="store_true")
    return parser


def main() -> int:
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("-"):
        argv = ["inspect", *argv]
    args = build_parser().parse_args(argv)
    if args.command == "inspect":
        return inspect(Path(args.cwd))
    if args.command == "write":
        return write_command(
            Path(args.cwd),
            status=args.status,
            objective=args.objective,
            body_file=args.body_file,
            plan_path=args.plan_path,
            archive_existing=args.archive_existing,
        )
    return archive_command(Path(args.cwd), args.slug, keep_current=args.keep_current)


if __name__ == "__main__":
    sys.exit(main())
