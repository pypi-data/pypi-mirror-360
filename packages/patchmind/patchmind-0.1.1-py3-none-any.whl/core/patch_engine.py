"""Core logic for detecting, evaluating, and suggesting patches."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict

from .analysis import PatchAnalyzer


@dataclass
class PatchResult:
    """Structured representation of repository changes."""

    added: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)
    deleted: List[str] = field(default_factory=list)


class PatchEngine:
    """Provide patch detection utilities for a Git repository."""

    def __init__(self) -> None:
        """Initialize the PatchEngine."""
        pass

    def _ensure_git_repo(self, repo_path: Path) -> None:
        """Ensure the given path is inside a Git repository."""

        try:
            subprocess.run(
                ["git", "-C", str(repo_path), "rev-parse", "--is-inside-work-tree"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"{repo_path} is not a Git repository") from exc

    def detect_changes(self, repo_path: str | Path = ".") -> PatchResult:
        """Scan the repository and return a summary of changes."""

        path = Path(repo_path)
        self._ensure_git_repo(path)

        try:
            result = subprocess.run(
                ["git", "-C", str(path), "status", "--porcelain"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError("Failed to retrieve git status") from exc

        added: List[str] = []
        modified: List[str] = []
        deleted: List[str] = []

        for line in result.stdout.splitlines():
            if not line.strip():
                continue

            status = line[:2]
            file_path = line[3:].strip()

            # Untracked files
            if status == "??":
                added.append(file_path)
                continue

            # Any addition to index or working tree
            if "A" in status:
                added.append(file_path)

            # Deletions
            if "D" in status:
                deleted.append(file_path)

            # Modifications or renames count as modifications
            if "M" in status or "R" in status:
                modified.append(file_path)

        return PatchResult(added=added, modified=modified, deleted=deleted)

    def analyze_changes(self, repo_path: str | Path = ".") -> Dict[str, dict]:
        """Analyze each modified file and return a mapping of insights."""

        changes = self.detect_changes(repo_path)
        analysis: Dict[str, dict] = {}
        for file_path in changes.modified:
            analysis[file_path] = PatchAnalyzer.analyze_file_diff(file_path)
        return analysis
