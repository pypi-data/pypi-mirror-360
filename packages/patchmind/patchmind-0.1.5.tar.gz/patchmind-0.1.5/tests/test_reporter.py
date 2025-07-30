"""Tests for PatchReporter."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from core.reporter import PatchReporter
from core.patch_engine import PatchResult


class TestPatchReporter(unittest.TestCase):
    """Ensure HTML reports are generated correctly."""

    @mock.patch("core.reporter.PatchBlamer.blame")
    @mock.patch("core.reporter.PatchHistory.file_timeline")
    @mock.patch("core.reporter.PatchInsight.file_score")
    @mock.patch("core.reporter.PatchVisualizer.tree_summary")
    @mock.patch("core.reporter.PatchSummarizer.summarize")
    @mock.patch("core.reporter.PatchEngine.detect_changes")
    def test_generate_report_html(
        self,
        mock_detect: mock.Mock,
        mock_summary: mock.Mock,
        mock_tree: mock.Mock,
        mock_score: mock.Mock,
        mock_history: mock.Mock,
        mock_blame: mock.Mock,
    ) -> None:
        mock_detect.return_value = PatchResult(added=["a.py"], modified=["b.py"], deleted=[]) 
        mock_summary.return_value = "Summary"
        mock_tree.return_value = "Tree"
        mock_score.return_value = {"score": 5, "risk": "low"}
        mock_history.return_value = [{"date": "2024-01-01", "author": "Alice", "summary": "init"}]
        mock_blame.return_value = [
            {"line_number": 1, "author": "Alice", "commit_hash": "abcd1234", "code_line": "print('a')"}
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.html")
            PatchReporter.generate_report(path)
            data = Path(path).read_text()

        self.assertIn("Summary", data)
        self.assertIn("Tree", data)
        self.assertIn("5", data)
        self.assertIn("init", data)
        self.assertIn("print('a')", data)


if __name__ == "__main__":
    unittest.main()
