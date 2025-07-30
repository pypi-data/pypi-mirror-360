"""Patch analysis utilities for understanding file changes."""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path
from typing import Dict


class PatchAnalyzer:
    """Provide methods to analyze diffs for a single file."""

    @staticmethod
    def _get_file_content_from_git(file_path: str, ref: str = "HEAD") -> str | None:
        """Return file contents from a git reference or None if not found."""
        try:
            result = subprocess.run(
                ["git", "show", f"{ref}:{file_path}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return None

    @staticmethod
    def _gather_functions(source: str) -> Dict[str, str]:
        """Return mapping of function names to body representations."""
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return {}
        funcs: Dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                body_dump = ast.dump(
                    ast.Module(body=node.body, type_ignores=[]),
                    include_attributes=False,
                )
                funcs[node.name] = body_dump
        return funcs

    @staticmethod
    def analyze_file_diff(file_path: str) -> dict:
        """Return a naive analysis of how a file changed."""
        path = Path(file_path)
        new_content = path.read_text()
        old_content = PatchAnalyzer._get_file_content_from_git(file_path)

        if old_content is None:
            return {"type": "added", "summary": "New file added"}

        old_funcs = PatchAnalyzer._gather_functions(old_content)
        new_funcs = PatchAnalyzer._gather_functions(new_content)

        added = [f for f in new_funcs if f not in old_funcs]
        removed = [f for f in old_funcs if f not in new_funcs]

        # Detect simple renames if body unchanged
        for rem in removed:
            for add in added:
                if old_funcs.get(rem) == new_funcs.get(add):
                    return {
                        "type": "function rename",
                        "summary": f"Function '{rem}' renamed to '{add}'",
                    }

        if added and not removed:
            return {
                "type": "function addition",
                "summary": "Added functions: " + ", ".join(added),
            }

        if removed and not added:
            return {
                "type": "function removal",
                "summary": "Removed functions: " + ", ".join(removed),
            }

        if added or removed:
            return {
                "type": "function change",
                "summary": "Added functions: "
                + ", ".join(added)
                + "; Removed functions: "
                + ", ".join(removed),
            }

        # Fallback: count lines added/removed in diff
        try:
            diff = subprocess.run(
                ["git", "diff", "--unified=0", "--", file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            ).stdout.splitlines()
        except subprocess.CalledProcessError:
            diff = []

        added_lines = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
        removed_lines = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))

        return {
            "type": "code change",
            "summary": f"{added_lines} lines added, {removed_lines} lines removed",
        }

