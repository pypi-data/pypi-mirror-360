"""Tests for PatchAnalyzer."""

from __future__ import annotations

import subprocess
import unittest
from unittest import mock

from core.analysis import PatchAnalyzer


class TestPatchAnalyzer(unittest.TestCase):
    """Ensure analyze_file_diff returns useful information."""

    @mock.patch("core.analysis.subprocess.run")
    @mock.patch("pathlib.Path.read_text")
    def test_function_rename_detected(self, mock_read: mock.Mock, mock_run: mock.Mock) -> None:
        """Detect simple function rename via AST comparison."""

        old_src = "def foo():\n    return 1\n"
        new_src = "def bar():\n    return 1\n"

        def side_effect(args, stdout=None, stderr=None, text=None, check=None):
            if args[0:2] == ["git", "show"]:
                return subprocess.CompletedProcess(args, 0, stdout=old_src, stderr="")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

        mock_run.side_effect = side_effect
        mock_read.return_value = new_src

        result = PatchAnalyzer.analyze_file_diff("dummy.py")
        self.assertEqual(result["type"], "function rename")
        self.assertIn("foo", result["summary"])
        self.assertIn("bar", result["summary"])

    @mock.patch("core.analysis.subprocess.run")
    @mock.patch("pathlib.Path.read_text")
    def test_line_change_fallback(self, mock_read: mock.Mock, mock_run: mock.Mock) -> None:
        """Fallback to line change count when no function-level changes detected."""

        old_src = "a = 1\n"
        new_src = "a = 1\nb = 2\n"

        def side_effect(args, stdout=None, stderr=None, text=None, check=None):
            if args[0:2] == ["git", "show"]:
                return subprocess.CompletedProcess(args, 0, stdout=old_src, stderr="")
            if args[0:2] == ["git", "diff"]:
                return subprocess.CompletedProcess(args, 0, stdout="+b = 2\n", stderr="")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

        mock_run.side_effect = side_effect
        mock_read.return_value = new_src

        result = PatchAnalyzer.analyze_file_diff("dummy.py")
        self.assertEqual(result["type"], "code change")
        self.assertIn("1 lines added", result["summary"])


if __name__ == "__main__":
    unittest.main()
