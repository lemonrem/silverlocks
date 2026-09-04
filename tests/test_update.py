from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "update.py"
SPEC = importlib.util.spec_from_file_location("silverlocks_update", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
UPDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UPDATE)


class UpdateTests(unittest.TestCase):
    def git(self, root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def commit(self, root: Path, message: str) -> None:
        result = self.git(root, "add", "-A")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.git(root, "commit", "-m", message)
        self.assertEqual(result.returncode, 0, result.stderr)

    def create_install(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path, Path, set[str]]:
        temporary = tempfile.TemporaryDirectory()
        base = Path(temporary.name)
        remote = base / "remote.git"
        publisher = base / "publisher"
        install = base / "install"

        result = subprocess.run(
            ["git", "init", "--bare", "--initial-branch=main", str(remote)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(
            ["git", "clone", str(remote), str(publisher)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        self.git(publisher, "config", "user.name", "Silverlocks Test")
        self.git(publisher, "config", "user.email", "silverlocks@example.invalid")
        (publisher / "agents").mkdir()
        (publisher / "scripts").mkdir()
        (publisher / "VERSION").write_text("0.2.0\n", encoding="utf-8")
        (publisher / "SKILL.md").write_text("---\nname: silverlocks\ndescription: test\n---\n", encoding="utf-8")
        (publisher / "agents" / "openai.yaml").write_text(
            "policy:\n  allow_implicit_invocation: true\n",
            encoding="utf-8",
        )
        (publisher / "scripts" / "continuity.py").write_text("# test\n", encoding="utf-8")
        shutil.copy2(SCRIPT, publisher / "scripts" / "update.py")
        self.commit(publisher, "initial")
        result = self.git(publisher, "push", "origin", "main")
        self.assertEqual(result.returncode, 0, result.stderr)

        result = subprocess.run(
            ["git", "clone", str(remote), str(install)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git(install, "config", "user.name", "Silverlocks Test")
        self.git(install, "config", "user.email", "silverlocks@example.invalid")
        trusted = {UPDATE.canonical_origin(str(remote))}
        return temporary, remote, publisher, install, trusted

    def publish_version(self, publisher: Path, version: str) -> None:
        (publisher / "VERSION").write_text(f"{version}\n", encoding="utf-8")
        self.commit(publisher, f"release {version}")
        result = self.git(publisher, "push", "origin", "main")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_clean_install_fast_forwards_to_higher_version(self) -> None:
        temporary, _remote, publisher, install, trusted = self.create_install()
        with temporary:
            self.publish_version(publisher, "0.3.0")
            payload = UPDATE.perform_update(install, force=True, trusted_origins=trusted, now=1_000)
            self.assertTrue(payload["ok"], payload)
            self.assertEqual(payload["action"], "updated")
            self.assertEqual(payload["installed_version"], "0.3.0")
            self.assertEqual((install / "VERSION").read_text(encoding="utf-8"), "0.3.0\n")

    def test_dirty_worktree_is_preserved(self) -> None:
        temporary, _remote, publisher, install, trusted = self.create_install()
        with temporary:
            self.publish_version(publisher, "0.3.0")
            (install / "local-note.txt").write_text("preserve me\n", encoding="utf-8")
            payload = UPDATE.perform_update(install, force=True, trusted_origins=trusted, now=1_000)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["action"], "dirty_worktree")
            self.assertTrue((install / "local-note.txt").is_file())
            self.assertEqual((install / "VERSION").read_text(encoding="utf-8"), "0.2.0\n")

    def test_diverged_history_is_not_merged(self) -> None:
        temporary, _remote, publisher, install, trusted = self.create_install()
        with temporary:
            (install / "local.md").write_text("local history\n", encoding="utf-8")
            self.commit(install, "local commit")
            self.publish_version(publisher, "0.3.0")
            payload = UPDATE.perform_update(install, force=True, trusted_origins=trusted, now=1_000)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["action"], "diverged")
            self.assertEqual((install / "VERSION").read_text(encoding="utf-8"), "0.2.0\n")

    def test_successful_check_is_cached_for_twenty_four_hours(self) -> None:
        temporary, _remote, publisher, install, trusted = self.create_install()
        with temporary:
            first = UPDATE.perform_update(install, force=True, check_only=True, trusted_origins=trusted, now=1_000)
            self.assertEqual(first["action"], "up_to_date")
            self.publish_version(publisher, "0.3.0")
            cached = UPDATE.perform_update(install, trusted_origins=trusted, now=2_000)
            self.assertTrue(cached["ok"])
            self.assertEqual(cached["action"], "cached")
            self.assertEqual((install / "VERSION").read_text(encoding="utf-8"), "0.2.0\n")

    def test_untrusted_origin_is_rejected(self) -> None:
        temporary, _remote, _publisher, install, _trusted = self.create_install()
        with temporary:
            payload = UPDATE.perform_update(install, force=True, now=1_000)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["action"], "untrusted_origin")

    def test_non_git_install_is_left_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            (root / "VERSION").write_text("0.2.0\n", encoding="utf-8")
            payload = UPDATE.perform_update(root, force=True, now=1_000)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["action"], "not_git_install")
            self.assertEqual((root / "VERSION").read_text(encoding="utf-8"), "0.2.0\n")


if __name__ == "__main__":
    unittest.main()
