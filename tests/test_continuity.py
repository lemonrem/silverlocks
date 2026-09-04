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


if __name__ == "__main__":
    unittest.main()
