"""Tests for PatchEngine."""

import subprocess
import unittest
from unittest import mock

from core.patch_engine import PatchEngine, PatchResult


class TestPatchEngine(unittest.TestCase):
    """Ensure PatchEngine initializes correctly."""

    def test_initialization(self) -> None:
        engine = PatchEngine()
        self.assertIsInstance(engine, PatchEngine)

    @mock.patch("core.patch_engine.subprocess.run")
    def test_detect_changes_parse(self, mock_run: mock.Mock) -> None:
        """Ensure git output is parsed into correct categories."""

        def side_effect(args, stdout=None, stderr=None, text=None, check=None):
            if "rev-parse" in args:
                return subprocess.CompletedProcess(args, 0, stdout="true", stderr="")
            return subprocess.CompletedProcess(
                args,
                0,
                stdout="A  file1.py\n M file2.py\nD  file3.py\n?? new.txt\n",
                stderr="",
            )

        mock_run.side_effect = side_effect
        engine = PatchEngine()
        result = engine.detect_changes()
        self.assertEqual(result.added, ["file1.py", "new.txt"])
        self.assertEqual(result.modified, ["file2.py"])
        self.assertEqual(result.deleted, ["file3.py"])

    @mock.patch("core.patch_engine.subprocess.run", side_effect=subprocess.CalledProcessError(1, "git"))
    def test_detect_changes_non_git_repo(self, mock_run: mock.Mock) -> None:
        """Ensure a helpful error is raised when not in a git repo."""

        engine = PatchEngine()
        with self.assertRaises(RuntimeError):
            engine.detect_changes()


if __name__ == "__main__":
    unittest.main()
