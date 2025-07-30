"""Impact scoring utilities for PatchMind."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict

from .analysis import PatchAnalyzer


class PatchInsight:
    """Generate a risk score for a file."""

    @staticmethod
    def file_score(file_path: str) -> Dict[str, int | str]:
        """Return a risk score and tag for the given file."""
        path = Path(file_path)

        # Unique authors from git blame
        authors = set()
        try:
            blame = subprocess.run(
                ["git", "blame", "--line-porcelain", str(path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            ).stdout.splitlines()
            for line in blame:
                if line.startswith("author "):
                    authors.add(line[len("author ") :])
        except subprocess.CalledProcessError:
            pass
        unique_authors = len(authors)

        # Total commit count from git log
        commit_count = 0
        try:
            log = subprocess.run(
                ["git", "log", "--follow", "--oneline", "--", str(path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            ).stdout.splitlines()
            commit_count = len([l for l in log if l.strip()])
        except subprocess.CalledProcessError:
            pass

        # Number of lines in current file
        try:
            line_count = len(path.read_text().splitlines())
        except OSError:
            line_count = 0

        # Number of functions changed between HEAD~1 and current
        old_content = PatchAnalyzer._get_file_content_from_git(file_path, ref="HEAD~1")
        old_funcs = PatchAnalyzer._gather_functions(old_content) if old_content else {}
        new_funcs = PatchAnalyzer._gather_functions(path.read_text())
        func_changes = len(set(old_funcs) ^ set(new_funcs))

        # Normalize heuristics
        scores = [
            min(unique_authors / 10, 1.0),
            min(commit_count / 50, 1.0),
            min(line_count / 400, 1.0),
            min(func_changes / 20, 1.0),
        ]
        score = round(sum(scores) / len(scores) * 100)

        if score < 30:
            risk = "low"
        elif score < 70:
            risk = "medium"
        else:
            risk = "high"

        return {"score": score, "risk": risk}
