"""Read-only Git activity reporting. Never creates or rewrites Git commits."""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class GitPulseError(RuntimeError):
    """Raised when GitPulse cannot inspect a repository."""


def _git(repo: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True, capture_output=True, text=True, encoding="utf-8"
        )
    except FileNotFoundError as exc:
        raise GitPulseError("Git is not installed or not on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "Unknown Git error").strip()
        raise GitPulseError(detail) from exc
    return result.stdout.strip()


def inspect_repo(repo: str | Path, since_days: int = 7) -> dict[str, Any]:
    """Summarize actual commits and working-tree changes in a repository."""
    path = Path(repo).expanduser().resolve()
    if since_days < 1:
        raise GitPulseError("since_days must be at least 1.")
    if not path.exists() or not path.is_dir():
        raise GitPulseError(f"Repository directory does not exist: {path}")

    top = Path(_git(path, "rev-parse", "--show-toplevel"))
    branch = _git(top, "branch", "--show-current") or "(detached HEAD)"
    head = _git(top, "rev-parse", "--short", "HEAD")
    raw = _git(
        top, "log", f"--since={since_days} days ago",
        "--date=iso-strict", "--pretty=format:%H%x1f%ad%x1f%an%x1f%s"
    )
    commits = []
    day_counts: Counter[str] = Counter()
    for line in raw.splitlines() if raw else []:
        parts = line.split("\x1f", 3)
        if len(parts) != 4:
            continue
        sha, date_text, author, subject = parts
        date = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
        day = date.date().isoformat()
        day_counts[day] += 1
        commits.append({
            "sha": sha[:12], "date": date_text,
            "day": day, "author": author, "subject": subject
        })

    status = _git(top, "status", "--porcelain")
    changed = [line.split(maxsplit=1)[-1] for line in status.splitlines() if line.strip()]
    return {
        "repository": str(top),
        "branch": branch,
        "head": head,
        "window_days": since_days,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit_count": len(commits),
        "active_days": len(day_counts),
        "daily_commits": dict(sorted(day_counts.items())),
        "commits": commits,
        "working_tree_clean": not bool(status),
        "changed_paths": changed,
    }


def to_markdown(data: dict[str, Any]) -> str:
    lines = [
        f"# GitPulse report — {Path(data['repository']).name}", "",
        f"- Branch: `{data['branch']}`",
        f"- HEAD: `{data['head']}`",
        f"- Window: last {data['window_days']} days",
        f"- Real commits found: **{data['commit_count']}**",
        f"- Days with commits: **{data['active_days']}**",
        f"- Working tree: **{'clean' if data['working_tree_clean'] else 'has uncommitted changes'}**",
        "",
        "> This report reads existing Git history. It does not create, backdate, or push commits.",
        "", "## Daily activity", "",
        "| Date | Commits |", "|---|---:|",
    ]
    if data["daily_commits"]:
        lines.extend(f"| {day} | {count} |" for day, count in data["daily_commits"].items())
    else:
        lines.append("| No commits in this window | 0 |")
    lines.extend(["", "## Recent commits", ""])
    if data["commits"]:
        lines.extend(
            f"- `{c['sha']}` · {c['day']} · **{c['author']}** — {c['subject']}"
            for c in data["commits"]
        )
    else:
        lines.append("No commits found in the selected period.")
    lines.extend(["", "## Uncommitted changes", ""])
    lines.extend(f"- `{p}`" for p in data["changed_paths"])
    if not data["changed_paths"]:
        lines.append("Working tree is clean.")
    lines.append("")
    return "\n".join(lines)


def write_report(data: dict[str, Any], output: str | Path, fmt: str = "markdown") -> Path:
    destination = Path(output).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = to_markdown(data) if fmt == "markdown" else json.dumps(data, indent=2) + "\n"
    destination.write_text(payload, encoding="utf-8")
    return destination
