from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "continuity.py"
BODY = """# Current frontier

## Verified progress
- Focused behavior is implemented.

## Exact next action
- Resume with the next focused check.

## Constraints and decisions
- Keep the state compact.

## Evidence
- Unit test fixture.
"""


class ContinuityTests(unittest.TestCase):
    def run_script(self, *arguments: str, body: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            input=body,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_missing_state_is_not_read(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            result = self.run_script("inspect", "--cwd", raw_root)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["should_read"])
            self.assertEqual(payload["reason"], "missing")

    def test_write_and_inspect_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            write = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                "Finish the focused change",
                body=BODY,
            )
            self.assertEqual(write.returncode, 0, write.stdout + write.stderr)
            current = Path(raw_root) / ".silverlocks" / "CURRENT.md"
            self.assertTrue(current.is_file())
            self.assertLessEqual(current.stat().st_size, 8 * 1024)

            inspect = self.run_script("inspect", "--cwd", raw_root)
            self.assertEqual(inspect.returncode, 0, inspect.stderr)
            payload = json.loads(inspect.stdout)
            self.assertTrue(payload["should_read"])
            self.assertEqual(payload["objective"], "Finish the focused change")
            self.assertEqual(payload["status"], "paused")

    def test_different_objective_requires_archive(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            first = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "active",
                "--objective",
                "First task",
                body=BODY,
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            rejected = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "active",
                "--objective",
                "Second task",
                body=BODY,
            )
            self.assertEqual(rejected.returncode, 2)
            self.assertIn("objective_changed", json.loads(rejected.stdout)["reason"])

            replaced = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "active",
                "--objective",
                "Second task",
                "--archive-existing",
                "first-task",
                body=BODY,
            )
            self.assertEqual(replaced.returncode, 0, replaced.stdout + replaced.stderr)
            payload = json.loads(replaced.stdout)
            self.assertTrue(Path(payload["archived_path"]).is_file())

    def test_archive_moves_current_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            write = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                "Archive task",
                body=BODY,
            )
            self.assertEqual(write.returncode, 0, write.stderr)

            archive = self.run_script("archive", "--cwd", raw_root, "--slug", "archive-task")
            self.assertEqual(archive.returncode, 0, archive.stdout + archive.stderr)
            payload = json.loads(archive.stdout)
            self.assertTrue(Path(payload["path"]).is_file())
            self.assertFalse((Path(raw_root) / ".silverlocks" / "CURRENT.md").exists())

    def test_invalid_body_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            result = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                "Invalid body",
                body="# Current frontier\n",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("required heading", json.loads(result.stdout)["reason"])

    def test_body_with_extra_heading_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            body = BODY.replace("## Evidence", "## Untracked history\n- Old detail.\n\n## Evidence")
            result = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                "Reject extra sections",
                body=body,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("unexpected heading", json.loads(result.stdout)["reason"])

    def test_quoted_objective_round_trips_without_false_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            objective = 'Fix "quoted" path C:\\temp'
            first = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                objective,
                body=BODY,
            )
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

            second = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                objective,
                body=BODY,
            )
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)

            inspect = self.run_script("inspect", "--cwd", raw_root)
            self.assertEqual(inspect.returncode, 0, inspect.stdout + inspect.stderr)
            self.assertEqual(json.loads(inspect.stdout)["objective"], objective)

    def test_inspect_rejects_malformed_body(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            write = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                "Validate damaged state",
                body=BODY,
            )
            self.assertEqual(write.returncode, 0, write.stdout + write.stderr)
            current = Path(raw_root) / ".silverlocks" / "CURRENT.md"
            damaged = current.read_text(encoding="utf-8").replace("## Evidence", "## Broken")
            current.write_text(damaged, encoding="utf-8")

            inspect = self.run_script("inspect", "--cwd", raw_root)
            self.assertEqual(inspect.returncode, 0, inspect.stdout + inspect.stderr)
            payload = json.loads(inspect.stdout)
            self.assertFalse(payload["should_read"])
            self.assertEqual(payload["reason"], "invalid_body")

    def test_failed_replacement_preserves_current_without_archive(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            first = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                "Original task",
                body=BODY,
            )
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            state_dir = Path(raw_root) / ".silverlocks"
            original = (state_dir / "CURRENT.md").read_text(encoding="utf-8")

            rejected = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                "Replacement task",
                "--archive-existing",
                "original-task",
                body="# Current frontier\n",
            )
            self.assertEqual(rejected.returncode, 2)
            self.assertEqual((state_dir / "CURRENT.md").read_text(encoding="utf-8"), original)
            self.assertFalse((state_dir / "archive").exists())

    def test_oversized_replacement_preserves_current_without_archive(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            first = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                "Original task",
                body=BODY,
            )
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            state_dir = Path(raw_root) / ".silverlocks"
            original = (state_dir / "CURRENT.md").read_text(encoding="utf-8")
            oversized = BODY.replace("- Unit test fixture.", "- " + ("x" * (9 * 1024)))

            rejected = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                "Replacement task",
                "--archive-existing",
                "original-task",
                body=oversized,
            )
            self.assertEqual(rejected.returncode, 2)
            self.assertEqual(json.loads(rejected.stdout)["reason"], "oversize")
            self.assertEqual((state_dir / "CURRENT.md").read_text(encoding="utf-8"), original)
            self.assertFalse((state_dir / "archive").exists())

    def test_symlinked_state_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root, tempfile.TemporaryDirectory() as raw_outside:
            state_dir = Path(raw_root) / ".silverlocks"
            try:
                state_dir.symlink_to(Path(raw_outside), target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"directory symlinks unavailable: {exc}")

            write = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                "Reject escaped state",
                body=BODY,
            )
            self.assertEqual(write.returncode, 2)
            self.assertIn("symlink", json.loads(write.stdout)["reason"])
            self.assertFalse((Path(raw_outside) / "CURRENT.md").exists())

            inspect = self.run_script("inspect", "--cwd", raw_root)
            self.assertEqual(inspect.returncode, 0, inspect.stdout + inspect.stderr)
            self.assertEqual(json.loads(inspect.stdout)["reason"], "unsafe_state_directory")

    def test_symlinked_archive_directory_preserves_current(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root, tempfile.TemporaryDirectory() as raw_outside:
            write = self.run_script(
                "write",
                "--cwd",
                raw_root,
                "--status",
                "paused",
                "--objective",
                "Reject escaped archive",
                body=BODY,
            )
            self.assertEqual(write.returncode, 0, write.stdout + write.stderr)
            state_dir = Path(raw_root) / ".silverlocks"
            try:
                (state_dir / "archive").symlink_to(Path(raw_outside), target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"directory symlinks unavailable: {exc}")

            archive = self.run_script("archive", "--cwd", raw_root, "--slug", "escaped")
            self.assertEqual(archive.returncode, 2)
            self.assertIn("symlink", json.loads(archive.stdout)["reason"])
            self.assertTrue((state_dir / "CURRENT.md").is_file())
            self.assertEqual(list(Path(raw_outside).iterdir()), [])

    def test_git_child_path_uses_unrelated_repository_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Fixture"], check=True)
            subprocess.run(
                ["git", "-C", str(root), "config", "user.email", "fixture@example.invalid"],
                check=True,
            )
            (root / "README.md").write_text("# Unrelated fixture\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
            child = root / "packages" / "example"
            child.mkdir(parents=True)

            write = self.run_script(
                "write",
                "--cwd",
                str(child),
                "--status",
                "paused",
                "--objective",
                "Resume an unrelated repository task",
                body=BODY,
            )
            self.assertEqual(write.returncode, 0, write.stdout + write.stderr)
            payload = json.loads(write.stdout)
            self.assertEqual(Path(payload["workspace_root"]), root.resolve())
            self.assertEqual(payload["revision_system"], "git")
            self.assertTrue(payload["base_revision"])
            self.assertTrue((root / ".silverlocks" / "CURRENT.md").is_file())
            self.assertFalse((child / ".silverlocks").exists())

            inspect = self.run_script("inspect", "--cwd", str(child))
            self.assertEqual(inspect.returncode, 0, inspect.stdout + inspect.stderr)
            self.assertTrue(json.loads(inspect.stdout)["should_read"])

            archive = self.run_script(
                "archive",
                "--cwd",
                str(child),
                "--slug",
                "unrelated-repository",
            )
            self.assertEqual(archive.returncode, 0, archive.stdout + archive.stderr)
            self.assertTrue(Path(json.loads(archive.stdout)["path"]).is_file())


if __name__ == "__main__":
    unittest.main()
