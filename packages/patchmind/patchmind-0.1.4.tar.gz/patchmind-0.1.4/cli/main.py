"""CLI entry point for PatchMind."""

from __future__ import annotations

import argparse

from core.patch_engine import PatchEngine
from core.summarizer import PatchSummarizer
from core.visualizer import PatchVisualizer
from core.history import PatchHistory
from core.blamer import PatchBlamer
from core.insight import PatchInsight
from core.reporter import PatchReporter


def main() -> None:
    """Main entry point for the PatchMind CLI."""

    parser = argparse.ArgumentParser(description="PatchMind CLI")
    parser.add_argument(
        "--changes",
        action="store_true",
        help="Display a summary of repository changes",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a short summary of repository changes",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Print intelligent analysis of modified files",
    )
    parser.add_argument(
        "--tree",
        action="store_true",
        help="Display repository changes in a tree view",
    )
    parser.add_argument(
        "--history",
        metavar="FILE",
        help="Display history timeline for the given file",
    )
    parser.add_argument(
        "--blame",
        metavar="FILE",
        help="Show blame information for the given file",
    )
    parser.add_argument(
        "--insight",
        metavar="FILE",
        help="Show risk insight score for the given file",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate an HTML report of repository changes",
    )
    args = parser.parse_args()

    if args.history:
        timeline = PatchHistory.file_timeline(args.history)
        if not timeline:
            print(f"No history found for {args.history}")
            return

        print(f"\u250c\u2500 File History: {args.history}")
        print("\u2502")
        for i, event in enumerate(timeline):
            connector = "\u2514\u2500" if i == len(timeline) - 1 else "\u251c\u2500"
            print(f"{connector} [{event['date']}] [{event['author']}] {event['summary']}")
        return

    if args.blame:
        try:
            blame = PatchBlamer.blame(args.blame)
        except RuntimeError as exc:
            print(f"Error: {exc}")
            return

        for entry in blame:
            line_no = str(entry["line_number"]).rjust(4)
            commit = entry["commit_hash"][:8]
            print(f"{line_no} {commit} {entry['author']} | {entry['code_line']}")
        return

    if args.insight:
        result = PatchInsight.file_score(args.insight)
        print(f"Impact score: {result['score']} ({result['risk']})")
        return

    if args.report:
        PatchReporter.generate_report("report.html")
        print("Report written to report.html")
        return

    if args.changes or args.summary or args.analyze or args.tree:
        engine = PatchEngine()
        try:
            result = engine.detect_changes()
        except RuntimeError as exc:
            print(f"Error: {exc}")
            return

        if args.changes:
            print("Added:")
            for p in result.added:
                print(f"  {p}")

            print("Modified:")
            for p in result.modified:
                print(f"  {p}")

            print("Deleted:")
            for p in result.deleted:
                print(f"  {p}")

        if args.summary:
            summary = PatchSummarizer.summarize(result)
            print(summary)

        if args.tree:
            tree = PatchVisualizer.tree_summary(result)
            print(tree)

        if args.analyze:
            analysis = engine.analyze_changes()
            for path, info in analysis.items():
                print(f"{path}: {info['summary']}")


if __name__ == "__main__":
    main()
