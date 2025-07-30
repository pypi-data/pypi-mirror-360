"""Simple script for rebase workflow."""

import argparse
import subprocess
import sys

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

LAST_N_COMMITS = 15


def run_git_command(cmd: list[str]) -> str | None:
    """Run command with git."""
    try:
        result = subprocess.run(
            ["git", *cmd],  # noqa: S607
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"[red]Error: {e.stderr.strip()}[/red]\n")
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the git-rb tool."""
    return argparse.ArgumentParser(
        description="Git rebase workflow tool.",
    )


def main() -> None:
    parser = create_parser()
    parser.parse_args()
    run_git_command(["rev-parse", "--is-inside-work-tree"])

    log_format = "%h|~|%d|~|%s|~|%ar|~|%an"
    log_output = run_git_command(["log", f"-n{LAST_N_COMMITS}", f"--pretty=format:{log_format}"])

    if not log_output:
        sys.stderr.write("[red]Error: No commits found.[/red]\n")
        sys.exit(1)

    assert isinstance(log_output, str)

    # Parse commits
    commits = []
    for line in log_output.split("\n"):
        if line.strip():
            parts = line.split("|~|")
            expected_n_parts = 5
            if len(parts) == expected_n_parts:
                commits.append(
                    {
                        "hash": parts[0],
                        "decorations": parts[1].strip(),
                        "subject": parts[2],
                        "date": parts[3],
                        "author": parts[4],
                    }
                )

    # Display commits using Rich Table
    table = Table(title="Recent Commits", show_header=True, header_style="bold magenta")
    table.add_column("Index", style="dim", width=6)
    table.add_column("Hash", style="red")
    table.add_column("Decorations", style="yellow")
    table.add_column("Subject", style="white")
    table.add_column("Date", style="green")
    table.add_column("Author", style="blue bold")

    for i, commit in enumerate(commits, 1):
        table.add_row(
            f"{i:2d}",
            commit["hash"],
            commit["decorations"] or "",
            commit["subject"],
            commit["date"],
            commit["author"],
        )

    console.print(table)

    try:
        selection = Prompt.ask("Enter the number of the commit to rebase from", default="q")
        if selection.lower() == "q":
            console.print("Aborting.")
            sys.exit(0)

        index = int(selection) - 1
        if not 0 <= index < len(commits):
            sys.stderr.write("[red]Error: Number out of range.[/red]\n")
            sys.exit(1)

        rebase_hash = commits[index]["hash"]
        console.print(f"\n[green]Running command:[/green] git rebase -i {rebase_hash}^")
        try:
            subprocess.run(
                [  # noqa: S607
                    "git",
                    "rebase",
                    "-i",
                    f"{rebase_hash}^",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"[red]Error during rebase: {e.stderr.strip()}[/red]\n")
            sys.exit(1)

    except ValueError:
        sys.stderr.write("[red]Error: Invalid input. Please enter a number.[/red]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
