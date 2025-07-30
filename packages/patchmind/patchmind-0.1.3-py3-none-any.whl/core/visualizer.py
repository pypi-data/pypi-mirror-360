"""Utilities for visualizing repository changes."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from core.patch_engine import PatchResult


class PatchVisualizer:
    """Generate visual representations of :class:`PatchResult`."""

    @staticmethod
    def tree_summary(patch_result: PatchResult) -> str:
        """Return a tree-like summary string for the given patch result."""
        if (
            not patch_result.added
            and not patch_result.modified
            and not patch_result.deleted
        ):
            return "No changes detected."

        def insert(tree: Dict[str, dict], path: str, status: str) -> None:
            parts = Path(path).parts
            node = tree
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = {"__status__": status}

        tree: Dict[str, dict] = {}
        for p in patch_result.added:
            insert(tree, p, "[added]")
        for p in patch_result.modified:
            insert(tree, p, "[modified]")
        for p in patch_result.deleted:
            insert(tree, p, "[deleted]")

        def build(node: Dict[str, dict], prefix: str = "") -> list[str]:
            lines: list[str] = []
            keys = sorted(node.keys())
            for i, key in enumerate(keys):
                child = node[key]
                last = i == len(keys) - 1
                connector = "└── " if last else "├── "
                if isinstance(child, dict) and "__status__" not in child:
                    lines.append(prefix + connector + f"{key}/")
                    extension = "    " if last else "│   "
                    lines.extend(build(child, prefix + extension))
                else:
                    status = child["__status__"] if isinstance(child, dict) else ""
                    lines.append(prefix + connector + f"{key} {status}")
            return lines

        return "\n".join(build(tree))
