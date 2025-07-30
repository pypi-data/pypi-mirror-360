"""Utilities for retrieving file history information."""

from __future__ import annotations

import subprocess
from typing import List, Dict


class PatchHistory:
    """Provide methods to inspect git history for a file."""

    @staticmethod
    def file_timeline(file_path: str) -> List[Dict[str, str]]:
        """Return a list of change events for the given file.

        Each event dictionary contains ``date``, ``author``, and ``summary`` keys.
        """
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--pretty=format:%ad|%an|%s",
                    "--date=short",
                    "--",
                    file_path,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Failed to retrieve git history for {file_path}") from exc

        timeline: List[Dict[str, str]] = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            parts = line.split("|", 2)
            if len(parts) != 3:
                continue
            date, author, summary = parts
            timeline.append({"date": date, "author": author, "summary": summary})
        return timeline
