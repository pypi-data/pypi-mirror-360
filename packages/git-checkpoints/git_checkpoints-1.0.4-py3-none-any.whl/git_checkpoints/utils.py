"""Common utilities for git-checkpoints."""

import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def is_virtual_environment() -> bool:
    """Check if we're running in a virtual environment."""
    return bool(os.environ.get("VIRTUAL_ENV"))


def is_git_repository(path: Optional[Path] = None) -> bool:
    """Check if the given path (or current directory) is a Git repository."""
    if path is None:
        path = Path.cwd()

    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"], capture_output=True, check=True, cwd=path
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_git_available() -> bool:
    """Check if Git is available in the system."""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_git_root(path: Optional[Path] = None) -> Optional[Path]:
    """Get the root directory of the Git repository."""
    if path is None:
        path = Path.cwd()

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            cwd=path,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def has_git_checkpoints_aliases(path: Optional[Path] = None) -> bool:
    """Check if git-checkpoints aliases are already configured in the repository."""
    if path is None:
        path = Path.cwd()

    try:
        # Check for checkpoint alias
        result = subprocess.run(
            ["git", "config", "--local", "--get", "alias.checkpoint"],
            capture_output=True,
            text=True,
            cwd=path,
        )

        if result.returncode == 0 and "git-checkpoints" in result.stdout:
            return True

        # Check for checkpoints alias
        result = subprocess.run(
            ["git", "config", "--local", "--get", "alias.checkpoints"],
            capture_output=True,
            text=True,
            cwd=path,
        )

        return result.returncode == 0 and "git-checkpoints" in result.stdout

    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def has_git_checkpoints_cron_job(path: Optional[Path] = None) -> bool:
    """Check if a git-checkpoints cron job exists for the given path."""
    if path is None:
        path = Path.cwd()

    path = path.resolve()

    try:
        current_cron = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True, check=True
        ).stdout

        lines = current_cron.strip().split("\n") if current_cron.strip() else []

        for line in lines:
            if line.strip() and "git-checkpoints" in line and str(path) in line:
                return True

        return False

    except subprocess.CalledProcessError:
        return False


def should_auto_setup() -> Tuple[bool, str]:
    """
    Determine if auto-setup should run and return the reason.

    Returns:
        Tuple of (should_setup, reason)
    """
    # Check if Git is available
    if not is_git_available():
        return False, "Git is not available"

    # Check if we're in a virtual environment
    if not is_virtual_environment():
        return False, "Not in a virtual environment"

    # Check if we're in a Git repository
    if not is_git_repository():
        return False, "Not in a Git repository"

    # Check if already set up
    if has_git_checkpoints_aliases():
        return False, "Already configured"

    return True, "Ready for auto-setup"


def format_path_for_display(path: Path) -> str:
    """Format a path for user-friendly display."""
    try:
        # Try to make it relative to home directory
        home = Path.home()
        if path.is_relative_to(home):
            return f"~/{path.relative_to(home)}"
    except (ValueError, AttributeError):
        pass

    return str(path)


def safe_run_command(
    cmd: list, cwd: Optional[Path] = None, timeout: int = 30
) -> Tuple[bool, str]:
    """
    Safely run a command and return success status and output.

    Args:
        cmd: Command to run as a list
        cwd: Working directory
        timeout: Timeout in seconds

    Returns:
        Tuple of (success, output_or_error)
    """
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd
        )

        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip() or result.stdout.strip()

    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout} seconds"
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"
    except Exception as e:
        return False, f"Unexpected error: {e}"
