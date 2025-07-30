"""Tests for PatchVisualizer."""

from __future__ import annotations

import unittest

from core.patch_engine import PatchResult
from core.visualizer import PatchVisualizer


class TestPatchVisualizer(unittest.TestCase):
    """Ensure tree summaries are generated correctly."""

    def test_tree_basic(self) -> None:
        result = PatchResult(
            added=["src/bar.py"],
            modified=["src/foo.py"],
            deleted=["tests/test_foo.py"],
        )
        tree = PatchVisualizer.tree_summary(result)
        expected = (
            "├── src/\n"
            "│   ├── bar.py [added]\n"
            "│   └── foo.py [modified]\n"
            "└── tests/\n"
            "    └── test_foo.py [deleted]"
        )
        self.assertEqual(tree, expected)

    def test_tree_no_changes(self) -> None:
        result = PatchResult()
        tree = PatchVisualizer.tree_summary(result)
        self.assertEqual(tree, "No changes detected.")


if __name__ == "__main__":
    unittest.main()
