import os
import subprocess
import sys
from io import StringIO
from pathlib import Path

import pytest

from git_rb.main import main


@pytest.fixture
def git_repo(tmp_path: Path):
    """Create git repo with commits."""
    original_cwd = Path.cwd()
    os.chdir(tmp_path)

    subprocess.run(["git", "init", "-b", "main"], check=True, capture_output=True)

    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], check=True)

    # dummy editor that'll just exit with OK, rebase can open an interactive
    # editor, don't want that in testing.
    editor_script = tmp_path / "git_editor.sh"
    editor_script.write_text("#!/bin/bash\nexit 0")
    editor_script.chmod(0o755)

    # Set GIT_EDITOR to the path of the dummy editor script
    os.environ["GIT_EDITOR"] = str(editor_script)

    # Create some initial commits
    (tmp_path / "file1.txt").write_text("initial content")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "feat: Initial commit"], check=True)
    (tmp_path / "file2.txt").write_text("second file")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "feat: Add second file"], check=True)
    (tmp_path / "file1.txt").write_text("updated content")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "fix: Update file1"], check=True)

    # Yield the path to the temporary repository
    yield tmp_path

    os.chdir(original_cwd)
    del os.environ["GIT_EDITOR"]


@pytest.fixture
def git_repo_no_commits(tmp_path: Path):
    """Create git repo with no commits."""
    original_cwd = Path.cwd()
    os.chdir(tmp_path)  # Change to the temporary directory
    subprocess.run(["git", "init", "-b", "main"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], check=True)
    editor_script = tmp_path / "git_editor.sh"
    editor_script.write_text("#!/bin/bash\nexit 0")
    editor_script.chmod(0o755)  # Make it executable
    os.environ["GIT_EDITOR"] = str(editor_script)

    yield tmp_path

    os.chdir(original_cwd)
    del os.environ["GIT_EDITOR"]


@pytest.fixture
def run_git_rb():
    """
    Run git-rb command.

    Returns a callable that takes arguments for git-rb and optional cwd.
    """

    def _runner(*args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
        original_cwd = Path.cwd()
        if cwd:
            os.chdir(cwd)

        original_argv = sys.argv
        sys.argv = ["git-rb", *args]

        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        # Capture stdout/stderr as StringIO objects,
        # captured_stdout/captured_stderr ensure stable references to these
        # values.
        sys.stdout = captured_stdout = StringIO()
        sys.stderr = captured_stderr = StringIO()

        exit_code = 0

        try:
            main()
        except SystemExit as e:
            exit_code = e.code if e.code is not None else 1
        except Exception:
            raise
        finally:
            sys.argv = original_argv
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            if cwd:
                os.chdir(original_cwd)

        return exit_code, captured_stdout.getvalue(), captured_stderr.getvalue()

    return _runner
