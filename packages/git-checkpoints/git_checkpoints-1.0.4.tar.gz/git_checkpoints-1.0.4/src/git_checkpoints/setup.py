"""Setup and configuration for Git Checkpoints."""

import subprocess
import sys
from pathlib import Path

from .utils import (
    should_auto_setup,
    format_path_for_display,
)


def setup_git_aliases(project_dir=None):
    """Set up Git aliases for checkpoint commands."""
    if project_dir is None:
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir)

    # Use git-checkpoints CLI for all commands
    aliases = {
        "checkpoint": '!f() { git-checkpoints --create "$@"; }; f',
        "checkpoints": '!f() { \
            if [ $# -eq 0 ]; then \
                git-checkpoints --list; \
            else \
                case "$1" in \
                    create) shift; git-checkpoints --create "$@" ;; \
                    list) git-checkpoints --list ;; \
                    delete) shift; git-checkpoints --delete "$@" ;; \
                    load) git-checkpoints --load "$2" ;; \
                    *) echo "Usage: git checkpoints [create|list|delete|load]" ;; \
                esac \
            fi \
        }; f',
    }

    print("Setting up Git aliases...")

    # Change to project directory
    import os

    original_dir = os.getcwd()
    os.chdir(project_dir)

    try:
        for alias, command in aliases.items():
            try:
                subprocess.run(
                    ["git", "config", "--local", f"alias.{alias}", command],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"Warning: Could not set alias '{alias}': {e}")

        print("✅ Git aliases configured")
    finally:
        os.chdir(original_dir)


def cleanup_git_aliases(project_dir=None):
    """Remove Git aliases for checkpoint commands."""
    if project_dir is None:
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir)

    # List of aliases to remove (including legacy aliases)
    aliases = [
        "checkpoint",
        "checkpoints",
        # Legacy aliases from older versions
        "cp",
        "cpls",
        "cpd",
        "cpld"
    ]

    print("Removing Git aliases...")

    # Change to project directory
    import os

    original_dir = os.getcwd()
    os.chdir(project_dir)

    try:
        for alias in aliases:
            try:
                subprocess.run(
                    ["git", "config", "--local", "--unset", f"alias.{alias}"],
                    check=True,
                    capture_output=True,
                )
                print(f"✅ Removed alias 'git {alias}'")
            except subprocess.CalledProcessError:
                # Alias doesn't exist, which is fine
                pass

        print("✅ Git aliases cleanup completed")
    finally:
        os.chdir(original_dir)


def cleanup_cron_job(project_dir=None):
    """Remove cron job for automatic checkpoints."""
    if project_dir is None:
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir)

    project_dir = project_dir.resolve()

    try:
        # Get current crontab
        try:
            current_cron = subprocess.run(
                ["crontab", "-l"], capture_output=True, text=True, check=True
            ).stdout
        except subprocess.CalledProcessError:
            # No crontab exists
            print("✅ No cron jobs to remove")
            return

        # Filter out git-checkpoints entries for this project
        lines = current_cron.strip().split("\n") if current_cron.strip() else []
        new_lines = []
        removed_count = 0

        for line in lines:
            if line.strip() and "git-checkpoints" in line and str(project_dir) in line:
                removed_count += 1
                continue
            new_lines.append(line)

        if removed_count > 0:
            # Install new crontab
            new_cron = "\n".join(new_lines) + "\n" if new_lines else ""
            subprocess.run(["crontab", "-"], input=new_cron, text=True, check=True)
            print(f"✅ Removed {removed_count} cron job(s) for {project_dir}")
        else:
            print("✅ No cron jobs found to remove")

    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not remove cron job: {e}")


def cleanup_git_checkpoints(project_dir=None):
    """Complete cleanup of Git Checkpoints."""
    if project_dir is None:
        project_dir = Path.cwd()

    print("🔄 Cleaning up Git Checkpoints...")
    print()

    # Remove Git aliases
    cleanup_git_aliases(project_dir)
    print()

    # Remove cron job
    cleanup_cron_job(project_dir)
    print()

    print("🎉 Git Checkpoints cleanup complete!")
    print("The package can now be safely uninstalled.")
    print()


def setup_cron_job(project_dir=None):
    """Set up cron job for automatic checkpoints."""
    if project_dir is None:
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir)

    project_dir = project_dir.resolve()

    # Get the path to the git-checkpoints command
    try:
        subprocess.run(
            [sys.executable, "-c", "import git_checkpoints"],
            capture_output=True,
            text=True,
            check=True,
        )
        script_path = (
            f"{sys.executable} -m git_checkpoints.cli " f'--auto --dir "{project_dir}"'
        )
    except subprocess.CalledProcessError:
        script_path = f'git-checkpoints --auto --dir "{project_dir}"'

    # Create cron job entry with project directory
    cron_entry = (
        f'*/5 * * * * [ -n "$VIRTUAL_ENV" ] && ' f"{script_path} >/dev/null 2>&1"
    )

    try:
        # Get current crontab
        try:
            current_cron = subprocess.run(
                ["crontab", "-l"], capture_output=True, text=True, check=True
            ).stdout
        except subprocess.CalledProcessError:
            current_cron = ""

        # Check if entry already exists for this project
        # Look for the exact cron entry or any git-checkpoints entry for this project
        lines = current_cron.strip().split("\n") if current_cron.strip() else []
        for line in lines:
            if line.strip() and "git-checkpoints" in line and str(project_dir) in line:
                msg = "✅ Auto-checkpoint cron job already exists for this project"
                print(msg)
                return

        # Add new entry
        new_cron = current_cron + cron_entry + "\n"

        # Install new crontab
        subprocess.run(["crontab", "-"], input=new_cron, text=True, check=True)

        print(f"✅ Auto-checkpoint cron job installed for {project_dir}")

    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not install cron job: {e}")
        print("You can manually add this to your crontab:")
        print(f"  {cron_entry}")


def setup_git_checkpoints(project_dir=None):
    """Complete setup of Git Checkpoints."""
    if project_dir is None:
        project_dir = Path.cwd()

    print("🔄 Setting up Git Checkpoints...")
    print()

    # Check if git is available
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git is not installed or not available in PATH")
        sys.exit(1)

    # Check if we're in a git repository
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            check=True,
            cwd=project_dir,
        )
    except subprocess.CalledProcessError:
        print("❌ Not in a Git repository")
        print("Run 'git init' first to initialize a Git repository")
        sys.exit(1)

    # Set up Git aliases
    setup_git_aliases(project_dir)
    print()

    # Set up cron job
    setup_cron_job(project_dir)
    print()

    print("🎉 Git Checkpoints setup complete!")
    print()
    print("Available commands:")
    print("  git checkpoint [name]       - Create manual checkpoint")
    print("  git checkpoints             - List all checkpoints")
    print("  git checkpoints create [name] - Create checkpoint")
    print("  git checkpoints list        - List checkpoints")
    print("  git checkpoints delete <name> - Delete checkpoint")
    print("  git checkpoints load <name> - Load checkpoint")
    print()
    print("Automatic checkpoints will run every 5 minutes when:")
    print("  • You have a virtual environment activated")
    print("  • There are changes in your git repository")
    print()


def auto_setup_if_needed(project_dir=None):
    """
    Automatically setup git-checkpoints if conditions are met.

    This function is called during package installation to provide
    zero-configuration setup when appropriate.
    """
    if project_dir is None:
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir)

    # Check if auto-setup should run
    should_setup, reason = should_auto_setup()

    if not should_setup:
        # Don't print anything for silent operation
        return False

    try:
        # Run setup silently
        print(
            f"🔄 Auto-setting up git-checkpoints in {format_path_for_display(project_dir)}"
        )

        # Set up Git aliases
        setup_git_aliases(project_dir)

        # Set up cron job
        setup_cron_job(project_dir)

        print("✅ git-checkpoints auto-setup completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Auto-setup failed: {e}")
        print("Please run 'git-checkpoints-setup' manually")
        return False


if __name__ == "__main__":
    setup_git_checkpoints()
