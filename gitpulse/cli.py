"""Command-line interface for GitPulse."""
import argparse
import json
import sys

from .core import GitPulseError, inspect_repo, to_markdown, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitpulse",
        description="Report genuine Git activity without fabricating commits."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    report = sub.add_parser("report", help="Create a report from real Git history.")
    report.add_argument("--repo", default=".", help="Path to a Git repository.")
    report.add_argument("--since", type=int, default=7, help="Look-back window in days.")
    report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    report.add_argument("--output", help="Output path. Defaults to stdout.")
    report.add_argument("--check-clean", action="store_true",
                        help="Exit with status 2 if the working tree has uncommitted changes.")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = inspect_repo(args.repo, args.since)
        if args.output:
            destination = write_report(data, args.output, args.format)
            print(f"GitPulse report written to {destination}")
        else:
            print(json.dumps(data, indent=2) if args.format == "json" else to_markdown(data))
        if args.check_clean and not data["working_tree_clean"]:
            print("GitPulse: working tree is not clean.", file=sys.stderr)
            return 2
        return 0
    except GitPulseError as exc:
        print(f"GitPulse error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
