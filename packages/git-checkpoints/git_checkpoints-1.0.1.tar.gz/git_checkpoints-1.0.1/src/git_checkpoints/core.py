"""Core Git Checkpoints functionality."""

import os
import subprocess
from datetime import datetime
from pathlib import Path


class GitCheckpoints:
    """Main Git Checkpoints class handling all checkpoint operations."""

    def __init__(self, project_dir=None):
        """Initialize Git Checkpoints.

        Args:
            project_dir: Optional project directory. Defaults to current directory.
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()

    def is_git_repo(self):
        """Check if current directory is a git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_dir,
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def has_changes(self):
        """Check if there are any changes in the working directory."""
        try:
            # Check staged changes
            staged = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=self.project_dir,
                capture_output=True,
            )

            # Check unstaged changes
            unstaged = subprocess.run(
                ["git", "diff", "--quiet"], cwd=self.project_dir, capture_output=True
            )

            # Check untracked files
            untracked = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
            )

            return (
                staged.returncode != 0
                or unstaged.returncode != 0
                or untracked.stdout.strip()
            )

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def create_checkpoint(self, name=None):
        """Create a checkpoint with optional name.

        Args:
            name: Optional checkpoint name. Defaults to timestamp.

        Returns:
            str: The checkpoint tag name if successful, None otherwise.
        """
        if not self.is_git_repo():
            print("Not in a git repository")
            return None

        if not self.has_changes():
            print("No changes detected, skipping checkpoint")
            return None

        # Generate checkpoint name
        if not name:
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            name = f"auto_{timestamp}"
        else:
            # Sanitize name for Git tag (no spaces, special chars)
            import re

            name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)

        checkpoint_tag = f"checkpoint/{name}"

        try:
            # Stage all changes
            subprocess.run(["git", "add", "-A"], cwd=self.project_dir, check=True)

            # Create savepoint commit
            subprocess.run(
                ["git", "commit", "--no-verify", "-m", f"SAVEPOINT - {name}"],
                cwd=self.project_dir,
                check=True,
            )

            # Create tag
            subprocess.run(
                ["git", "tag", checkpoint_tag], cwd=self.project_dir, check=True
            )

            # Push tag to remote
            try:
                subprocess.run(
                    ["git", "push", "origin", checkpoint_tag],
                    cwd=self.project_dir,
                    check=True,
                )
            except subprocess.CalledProcessError:
                print("Warning: Could not push checkpoint to remote")

            # Undo the commit (keep changes staged)
            subprocess.run(
                ["git", "reset", "HEAD~1", "--mixed"], cwd=self.project_dir, check=True
            )

            print(f"Automatic checkpoint created and pushed: {checkpoint_tag}")
            return checkpoint_tag

        except subprocess.CalledProcessError as e:
            print(f"Error creating checkpoint: {e}")
            return None

    def list_checkpoints(self):
        """List all checkpoint tags."""
        try:
            result = subprocess.run(
                ["git", "tag", "-l", "checkpoint/*"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            return []

    def delete_checkpoint(self, name):
        """Delete a checkpoint both locally and remotely.

        Args:
            name: Checkpoint name (without 'checkpoint/' prefix).
        """
        checkpoint_tag = f"checkpoint/{name}"

        try:
            # Delete local tag
            subprocess.run(
                ["git", "tag", "-d", checkpoint_tag], cwd=self.project_dir, check=True
            )

            # Delete remote tag
            try:
                subprocess.run(
                    ["git", "push", "origin", f":refs/tags/{checkpoint_tag}"],
                    cwd=self.project_dir,
                    check=True,
                )
            except subprocess.CalledProcessError:
                print("Warning: Could not delete checkpoint from remote")

            print(f"Deleted checkpoint: {checkpoint_tag}")

        except subprocess.CalledProcessError as e:
            print(f"Error deleting checkpoint: {e}")

    def load_checkpoint(self, name):
        """Load a checkpoint and stage the changes.

        Args:
            name: Checkpoint name (without 'checkpoint/' prefix).
        """
        checkpoint_tag = f"checkpoint/{name}"

        try:
            # Reset to checkpoint
            subprocess.run(
                ["git", "reset", "--hard", checkpoint_tag],
                cwd=self.project_dir,
                check=True,
            )

            # Undo the commit to stage changes
            subprocess.run(
                ["git", "reset", "HEAD~1", "--mixed"], cwd=self.project_dir, check=True
            )

            print(f"Loaded checkpoint: {checkpoint_tag}")

        except subprocess.CalledProcessError as e:
            print(f"Error loading checkpoint: {e}")

    def auto_checkpoint(self):
        """Run automatic checkpoint if conditions are met."""
        # Check if virtual environment is active
        if not os.getenv("VIRTUAL_ENV"):
            print("Virtual environment not activated, skipping auto-checkpoint")
            return None

        print("Changes detected, creating automatic checkpoint...")

    def delete_all_checkpoints(self):
        """Delete all checkpoints."""
        checkpoints = self.list_checkpoints()
        if not checkpoints:
            print("No checkpoints found")
            return

        for checkpoint in checkpoints:
            # Extract name from checkpoint/name format
            name = checkpoint.split("/")[-1]
            self.delete_checkpoint(name)

        print(f"Deleted {len(checkpoints)} checkpoints")
        return self.create_checkpoint()
