"""Local uninstall and cleanup functionality for git-checkpoints."""

import subprocess
from pathlib import Path
from typing import List, Tuple

from .setup import cleanup_git_aliases, cleanup_cron_job
from .utils import has_git_checkpoints_aliases, is_git_repository


def has_git_checkpoints_aliases_in_current_repo() -> bool:
    """Check if the current repository has git-checkpoints aliases configured."""
    return has_git_checkpoints_aliases(Path.cwd())


def remove_all_git_checkpoints_cron_jobs() -> Tuple[int, List[str]]:
    """Remove all git-checkpoints cron jobs from the system."""
    removed_jobs = []

    try:
        # Get current crontab
        try:
            current_cron = subprocess.run(
                ["crontab", "-l"], capture_output=True, text=True, check=True
            ).stdout
        except subprocess.CalledProcessError:
            # No crontab exists
            return 0, []

        # Split into lines and filter out git-checkpoints entries
        lines = current_cron.strip().split("\n") if current_cron.strip() else []
        new_lines = []

        for line in lines:
            if line.strip() and "git-checkpoints" in line:
                removed_jobs.append(line.strip())
            else:
                new_lines.append(line)

        # Install new crontab if we removed any jobs
        if removed_jobs:
            new_cron = "\n".join(new_lines) + "\n" if new_lines else ""
            subprocess.run(["crontab", "-"], input=new_cron, text=True, check=True)

        return len(removed_jobs), removed_jobs

    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not modify crontab: {e}")
        return 0, []


def verify_cleanup_complete(project_dir: Path = None) -> Tuple[bool, List[str]]:
    """Verify that git-checkpoints traces have been removed from the current repository."""
    if project_dir is None:
        project_dir = Path.cwd()

    issues = []

    # Check for remaining aliases in current repository
    if has_git_checkpoints_aliases(project_dir):
        issues.append(f"git-checkpoints aliases still exist in {project_dir}")

    # Check for remaining cron jobs for this project
    try:
        current_cron = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True, check=True
        ).stdout

        # Look for cron jobs that reference this specific project directory
        project_dir_str = str(project_dir.resolve())
        remaining_cron_jobs = [
            line.strip()
            for line in current_cron.split("\n")
            if line.strip() and "git-checkpoints" in line and project_dir_str in line
        ]

        if remaining_cron_jobs:
            issues.append(
                f"Found {len(remaining_cron_jobs)} remaining cron jobs for this project"
            )
            for job in remaining_cron_jobs:
                issues.append(f"  - {job}")

    except subprocess.CalledProcessError:
        # No crontab exists, which is fine
        pass

    return len(issues) == 0, issues


def global_cleanup(interactive: bool = False) -> None:
    """Perform cleanup of git-checkpoints from the current repository."""
    project_dir = Path.cwd()

    print("🔄 Cleaning up git-checkpoints...")
    print()

    # Check if current directory is a git repository
    if not is_git_repository(project_dir):
        print("❌ Current directory is not a Git repository")
        print("Please run this command from within a Git repository")
        return

    # Check if git-checkpoints is configured in current repository
    print(f"🔍 Checking current repository: {project_dir}")

    if not has_git_checkpoints_aliases(project_dir):
        print("✅ No git-checkpoints aliases found in current repository")
    else:
        print("📁 Found git-checkpoints aliases in current repository")

        if interactive:
            response = input(
                "Remove git-checkpoints aliases from current repository? (y/N): "
            )
            if response.lower() not in ["y", "yes"]:
                print("Skipping alias removal")
                return

        # Remove aliases from current repository
        print("🗑️  Removing Git aliases...")
        try:
            cleanup_git_aliases(project_dir)
            print(f"✅ Cleaned up aliases from {project_dir}")
        except Exception as e:
            print(f"❌ Failed to clean up aliases: {e}")
        print()

    # Remove cron jobs for this project
    print("🕐 Removing cron jobs for this project...")
    try:
        cleanup_cron_job(project_dir)
        print("✅ Removed cron jobs for current project")
    except Exception as e:
        print(f"❌ Failed to remove cron jobs: {e}")
    print()

    # Verify cleanup
    print("🔍 Verifying cleanup...")
    is_clean, issues = verify_cleanup_complete(project_dir)

    if is_clean:
        print(
            "✅ Cleanup verification passed - all traces removed from current project"
        )
        print()
        print("🎉 git-checkpoints has been removed from this repository!")
        print("The 'git checkpoint' commands will no longer work in this project.")
    else:
        print("⚠️  Cleanup verification found remaining items:")
        for issue in issues:
            print(f"  {issue}")
        print()
        print("You may need to manually remove the remaining items.")
        print("Run 'git-checkpoints-cleanup' again if needed.")

    print()


if __name__ == "__main__":
    # Allow running as script for testing
    global_cleanup(interactive=True)
