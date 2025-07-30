"""HTML report generation utilities for PatchMind."""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict

from .patch_engine import PatchEngine
from .summarizer import PatchSummarizer
from .visualizer import PatchVisualizer
from .insight import PatchInsight
from .history import PatchHistory
from .blamer import PatchBlamer


class PatchReporter:
    """Generate HTML reports summarizing repository changes."""

    @staticmethod
    def generate_report(output_path: str = "report.html", repo_path: str | Path = ".") -> None:
        """Generate an HTML report and write it to ``output_path``."""

        engine = PatchEngine()
        result = engine.detect_changes(repo_path)

        summary = PatchSummarizer.summarize(result)
        tree = PatchVisualizer.tree_summary(result)

        risk_sections: List[str] = []
        for file_path in result.modified + result.added:
            info = PatchInsight.file_score(file_path)
            risk_sections.append(f"<li>{file_path}: {info['score']} ({info['risk']})</li>")
        risk_html = "\n".join(risk_sections) if risk_sections else "<li>No files scored.</li>"

        history_sections: List[str] = []
        for file_path in result.modified + result.added:
            events = PatchHistory.file_timeline(file_path)
            lines = [f"<li>[{e['date']}] [{e['author']}] {e['summary']}</li>" for e in events]
            history_sections.append(f"<h3>{file_path}</h3>\n<ul>\n" + "\n".join(lines) + "\n</ul>")
        history_html = "\n".join(history_sections) if history_sections else "<p>No history available.</p>"

        blame_sections: List[str] = []
        for file_path in result.modified + result.added:
            entries = PatchBlamer.blame(file_path)
            lines = [
                f"{e['line_number']}: {e['author']} {e['commit_hash'][:8]} | {e['code_line']}" for e in entries
            ]
            blame_sections.append(f"<h3>{file_path}</h3>\n<pre>\n" + "\n".join(lines) + "\n</pre>")
        blame_html = "\n".join(blame_sections) if blame_sections else "<p>No blame information.</p>"

        html = f"""<html>
<head><title>PatchMind Report</title></head>
<body>
<h1>Patch Report</h1>
<h2>Summary</h2>
<p>{summary}</p>
<h2>Tree View</h2>
<pre>{tree}</pre>
<h2>Risk Scores</h2>
<ul>
{risk_html}
</ul>
<h2>File History</h2>
{history_html}
<h2>Blame Information</h2>
{blame_html}
</body>
</html>
"""

        Path(output_path).write_text(html)
