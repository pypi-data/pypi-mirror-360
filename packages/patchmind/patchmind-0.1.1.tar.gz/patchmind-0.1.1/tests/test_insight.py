"""Tests for PatchInsight."""

import subprocess
import unittest
from unittest import mock

from core.insight import PatchInsight


class TestPatchInsight(unittest.TestCase):
    """Ensure impact scores are computed correctly."""

    @mock.patch("core.insight.PatchAnalyzer._get_file_content_from_git")
    @mock.patch("pathlib.Path.read_text")
    @mock.patch("core.insight.subprocess.run")
    def test_file_score_computation(
        self,
        mock_run: mock.Mock,
        mock_read: mock.Mock,
        mock_get: mock.Mock,
    ) -> None:
        new_src = "def foo():\n    pass\n\ndef bar():\n    pass\n"
        old_src = "def foo():\n    pass\n"
        mock_read.return_value = new_src
        mock_get.return_value = old_src

        def side_effect(args, stdout=None, stderr=None, text=None, check=None):
            if "blame" in args:
                output = (
                    "abcd 1 1 1\n"
                    "author Alice\n\tline1\n"
                    "abcd 2 2 1\n"
                    "author Bob\n\tline2\n"
                )
                return subprocess.CompletedProcess(args, 0, stdout=output, stderr="")
            if "log" in args:
                output = "\n".join([f"c{i}" for i in range(5)])
                return subprocess.CompletedProcess(args, 0, stdout=output, stderr="")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

        mock_run.side_effect = side_effect

        result = PatchInsight.file_score("dummy.py")
        self.assertEqual(result["score"], 9)
        self.assertEqual(result["risk"], "low")

    @mock.patch("core.insight.PatchAnalyzer._get_file_content_from_git", return_value=None)
    @mock.patch("pathlib.Path.read_text", return_value="")
    @mock.patch("core.insight.subprocess.run", side_effect=subprocess.CalledProcessError(1, "git"))
    def test_git_failures(
        self,
        mock_run: mock.Mock,
        mock_read: mock.Mock,
        mock_get: mock.Mock,
    ) -> None:
        result = PatchInsight.file_score("bad.py")
        self.assertEqual(result["risk"], "low")
        self.assertLessEqual(result["score"], 30)


if __name__ == "__main__":
    unittest.main()
