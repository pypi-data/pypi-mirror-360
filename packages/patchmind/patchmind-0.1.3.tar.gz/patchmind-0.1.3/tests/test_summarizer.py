"""Tests for PatchSummarizer."""

import unittest

from core.patch_engine import PatchResult
from core.summarizer import PatchSummarizer


class TestPatchSummarizer(unittest.TestCase):
    """Ensure summaries are generated correctly."""

    def test_summarize_counts(self) -> None:
        result = PatchResult(
            added=["a.py"],
            modified=["b.py", "c.py"],
            deleted=["d.py"],
        )
        summary = PatchSummarizer.summarize(result)
        self.assertEqual(
            summary,
            "1 new file added, 2 files modified, and 1 file deleted.",
        )

    def test_summarize_no_changes(self) -> None:
        result = PatchResult()
        summary = PatchSummarizer.summarize(result)
        self.assertEqual(summary, "No changes detected in the working directory.")


if __name__ == "__main__":
    unittest.main()
