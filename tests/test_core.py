import subprocess

from gitpulse.core import inspect_repo, to_markdown


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, text=True)


def test_report_reads_real_commit_and_does_not_create_one(tmp_path):
    repo = tmp_path / "sample"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.name", "Test User")
    git(repo, "config", "user.email", "test@example.com")
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", "Add README")
    before = subprocess.check_output(
        ["git", "-C", str(repo), "rev-list", "--count", "HEAD"], text=True
    ).strip()

    data = inspect_repo(repo, 7)
    after = subprocess.check_output(
        ["git", "-C", str(repo), "rev-list", "--count", "HEAD"], text=True
    ).strip()

    assert data["commit_count"] == 1
    assert data["commits"][0]["subject"] == "Add README"
    assert before == after
    assert "does not create" in to_markdown(data)


def test_reports_dirty_working_tree(tmp_path):
    repo = tmp_path / "sample"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.name", "Test User")
    git(repo, "config", "user.email", "test@example.com")
    (repo / "tracked.txt").write_text("one\n", encoding="utf-8")
    git(repo, "add", "tracked.txt")
    git(repo, "commit", "-m", "Initial")
    (repo / "tracked.txt").write_text("two\n", encoding="utf-8")
    data = inspect_repo(repo, 7)
    assert data["working_tree_clean"] is False
    assert "tracked.txt" in data["changed_paths"]
