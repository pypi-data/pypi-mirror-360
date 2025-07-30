"""Tests for PatchHistory."""

import subprocess
import unittest
from unittest import mock

from core.history import PatchHistory


class TestPatchHistory(unittest.TestCase):
    """Ensure file history is parsed correctly."""

    @mock.patch("core.history.subprocess.run")
    def test_file_timeline_parsing(self, mock_run: mock.Mock) -> None:
        log = (
            "2024-11-01|Alice|Added initial foo logic\n"
            "2025-01-03|Bob|Refactored bar into foo\n"
            "2025-06-20|Alice|Replaced API calls\n"
        )
        mock_run.return_value = subprocess.CompletedProcess(["git"], 0, stdout=log, stderr="")
        timeline = PatchHistory.file_timeline("src/foo.py")
        self.assertEqual(len(timeline), 3)
        self.assertEqual(timeline[0]["author"], "Alice")
        self.assertEqual(timeline[1]["summary"], "Refactored bar into foo")

    @mock.patch("core.history.subprocess.run", side_effect=subprocess.CalledProcessError(1, "git"))
    def test_git_failure(self, mock_run: mock.Mock) -> None:
        with self.assertRaises(RuntimeError):
            PatchHistory.file_timeline("bad.py")


if __name__ == "__main__":
    unittest.main()
