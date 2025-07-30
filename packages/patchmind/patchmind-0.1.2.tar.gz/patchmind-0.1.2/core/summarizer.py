"""Utility module for summarizing patch results."""

from __future__ import annotations

from core.patch_engine import PatchResult


class PatchSummarizer:
    """Generate human-readable summaries of repository changes."""

    @staticmethod
    def summarize(patch_result: PatchResult) -> str:
        """Return a short summary string for the given patch result."""
        added = len(patch_result.added)
        modified = len(patch_result.modified)
        deleted = len(patch_result.deleted)

        if added == 0 and modified == 0 and deleted == 0:
            return "No changes detected in the working directory."

        def pluralize(count: int, singular: str, plural: str) -> str:
            return f"{count} {singular if count == 1 else plural}"

        parts = [
            f"{pluralize(added, 'new file added', 'new files added')}",
            f"{pluralize(modified, 'file modified', 'files modified')}",
            f"{pluralize(deleted, 'file deleted', 'files deleted')}",
        ]
        return ", ".join(parts[:-1]) + f", and {parts[-1]}."
