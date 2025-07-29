"""
Git Checkpoints - Automatic Git checkpoints every 5 minutes with zero configuration.

Features:
- Automatic checkpoints every 5 minutes when virtual environment is active
- Manual checkpoint commands (git checkpoint, git cp, etc.)
- Smart detection - only creates checkpoints when there are changes
- Automatic push to remote repository
- Team collaboration - shared checkpoints
- Zero configuration needed

Usage:
    pip install git-checkpoints
    git-checkpoints-setup
"""

__version__ = "1.0.0"
__author__ = "RevSetter"
__email__ = "developers@revsetter.com"

from .core import GitCheckpoints
from .setup import setup_git_checkpoints

__all__ = ["GitCheckpoints", "setup_git_checkpoints"]
