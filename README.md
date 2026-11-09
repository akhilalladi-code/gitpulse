![GITPULSE — Diwali 2026](./assets/diwali-banner.svg)

<p align="center"><a href="https://akhilalladi-code.github.io/diwali-universe/"><strong>🪔 Explore Diwali Universe 2026 · Interactive celebration ↗</strong></a></p>

# GitPulse

**A truthful Git activity reporter for developers.**

GitPulse turns existing Git history into readable Markdown or JSON reports and checks whether your working tree is clean.

Unlike backdated contribution generators, GitPulse never creates empty commits, changes commit timestamps, rewrites history, or pushes to GitHub. It helps you understand and document the work you actually did.

## Features

- Summarize real commits over a configurable number of days.
- Group activity by day and list commit subjects and authors.
- Detect uncommitted working-tree changes.
- Export Markdown or JSON.
- Read-only: reporting does not modify your repository.
- Python 3.9+, standard library only.
- Automated tests and GitHub Actions CI.

## Install

```bash
git clone https://github.com/akhilalladi-code/gitpulse.git
cd gitpulse
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
```

## Usage

```bash
# Last 7 days
gitpulse report

# Last 30 days, save Markdown
gitpulse report --repo . --since 30 --output reports/activity.md

# JSON export
gitpulse report --repo ~/projects/my-app --since 14 --format json --output activity.json

# Exit with status 2 if uncommitted changes exist
gitpulse report --check-clean
```

## Example

```text
# GitPulse report — my-project
- Branch: main
- HEAD: a1b2c3d
- Window: last 7 days
- Real commits found: 4
- Days with commits: 3
- Working tree: clean
```

Values are read from your repository; GitPulse does not invent activity.

## CI

GitHub Actions runs tests on pushes, pull requests, and manual dispatch. CI results are genuine workflow records.

## Principles

1. Truthful history: never backdate or fabricate commits.
2. Read-only by default: reporting does not modify source repositories.
3. Local-first: no GitHub token or external service is required.
4. Inspectable output: Markdown for people, JSON for scripts.

## Development

```bash
python -m pip install -e . pytest
pytest -q
```

## License

MIT.
