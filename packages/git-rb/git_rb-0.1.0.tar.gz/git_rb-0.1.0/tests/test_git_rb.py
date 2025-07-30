from pathlib import Path
from unittest.mock import patch

from git_rb import __version__
from git_rb.main import Prompt


def test_version() -> None:
    with open("pyproject.toml") as f:
        pyproject_version = [line for line in f if line.startswith("version = ")]
    assert len(pyproject_version) == 1
    assert pyproject_version[0].strip().split(" = ")[-1].replace('"', "") == __version__


def test_git_rb_help(git_repo: Path, run_git_rb):
    """Test that --help displays correctly."""
    exit_code, stdout, stderr = run_git_rb("--help", cwd=git_repo)
    assert exit_code == 0
    assert "usage: git-rb [-h]" in stdout
    assert "Git rebase workflow tool." in stdout
    assert not stderr


@patch.object(Prompt, "ask")
def test_git_rb_abort(mock_prompt_ask, git_repo: Path, run_git_rb):
    """Test user aborting the rebase."""
    mock_prompt_ask.return_value = "q"

    exit_code, stdout, stderr = run_git_rb(cwd=git_repo)

    assert exit_code == 0
    assert "Aborting." in stdout
    assert "Running command: git rebase -i" not in stdout
    assert not stderr


@patch.object(Prompt, "ask")
def test_git_rb_invalid_input(mock_prompt_ask, git_repo: Path, run_git_rb):
    """Test invalid user input for selection."""
    mock_prompt_ask.return_value = "abc"

    exit_code, stdout, stderr = run_git_rb(cwd=git_repo)

    assert exit_code == 1
    assert "Error: Invalid input. Please enter a number." in stderr
    assert "Fetching the last 15 commits..." in stdout
    assert "Recent Commits" in stdout


@patch.object(Prompt, "ask")
def test_git_rb_out_of_range_input(mock_prompt_ask, git_repo: Path, run_git_rb):
    """Test user inputting a number out of range."""
    mock_prompt_ask.return_value = "99"

    exit_code, stdout, stderr = run_git_rb(cwd=git_repo)

    assert exit_code == 1
    assert "Error: Number out of range." in stderr
    assert "Fetching the last 15 commits..." in stdout
    assert "Recent Commits" in stdout


@patch.object(Prompt, "ask")
def test_git_rb_not_in_git_repo(mock_prompt_ask, tmp_path: Path, run_git_rb):
    """Test running git-rb outside a Git repository."""
    exit_code, stdout, stderr = run_git_rb(cwd=tmp_path)

    assert exit_code == 1
    assert "Error:" in stderr
    assert not stdout


@patch.object(Prompt, "ask")
def test_git_rb_no_commits(mock_prompt_ask, git_repo_no_commits, run_git_rb):
    """Test a successful interactive rebase scenario."""
    mock_prompt_ask.return_value = "2"
    exit_code, _, stderr = run_git_rb(cwd=git_repo_no_commits)
    assert exit_code == 1
    assert "Error: fatal: your current branch 'main' does not have any commits yet" in stderr
