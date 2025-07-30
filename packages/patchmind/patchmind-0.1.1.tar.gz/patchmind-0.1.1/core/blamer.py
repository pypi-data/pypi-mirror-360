"""Utilities for retrieving blame information."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List


class PatchBlamer:
    """Provide methods to inspect git blame for a file."""

    @staticmethod
    def blame(file_path: str | Path) -> List[Dict[str, str]]:
        """Return a list of blame entries for the given file.

        Each entry dictionary contains ``line_number``, ``author``, ``commit_hash``,
        and ``code_line``.
        """
        path = Path(file_path)
        try:
            result = subprocess.run(
                ["git", "blame", "--line-porcelain", str(path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Failed to retrieve git blame for {file_path}") from exc

        entries: List[Dict[str, str]] = []
        lines = result.stdout.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line:
                i += 1
                continue
            if line[0].isalnum():
                parts = line.split()
                if len(parts) < 3:
                    i += 1
                    continue
                commit_hash = parts[0]
                line_number = int(parts[2])
                num_lines = int(parts[3]) if len(parts) > 3 else 1
                author = "Unknown"
                i += 1
                # read metadata lines
                while i < len(lines) and not lines[i].startswith("\t"):
                    meta = lines[i]
                    if meta.startswith("author "):
                        author = meta[len("author ") :]
                    i += 1
                # now parse code lines
                for _ in range(num_lines):
                    if i >= len(lines):
                        break
                    code_line = lines[i][1:] if lines[i].startswith("\t") else ""
                    entries.append(
                        {
                            "line_number": line_number,
                            "author": author,
                            "commit_hash": commit_hash,
                            "code_line": code_line,
                        }
                    )
                    line_number += 1
                    i += 1
            else:
                i += 1
        return entries
