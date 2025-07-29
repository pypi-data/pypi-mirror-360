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
    pip install git-checkpoints  # Auto-setup when in venv + git repo
    # OR manually: git-checkpoints-setup
"""

__version__ = "1.0.3"
__author__ = "Moussa Mokhtari"
__email__ = "me@moussamokhtari.com"

from .core import GitCheckpoints
from .setup import setup_git_checkpoints, auto_setup_if_needed

# Auto-setup and auto-cleanup on import if appropriate conditions are met
import os
import sys

# Only run auto-setup/cleanup if:
# 1. We're not in a setup.py installation context
# 2. We're in a virtual environment
# 3. We're in a Git repository
# 4. We haven't already been set up
if (
    "setuptools" not in sys.modules  # Not during package build
    and "pip" not in sys.modules  # Not during pip install
    and "__file__" in globals()  # Running as a module, not in REPL
    and os.environ.get("VIRTUAL_ENV")  # In virtual environment
    and not os.environ.get("GIT_CHECKPOINTS_NO_AUTO_SETUP")  # Not explicitly disabled
):
    try:
        # First check for orphaned installations and clean them up
        from .auto_cleanup import check_and_cleanup_orphaned
        check_and_cleanup_orphaned()
        
        # Then run regular auto-setup if needed
        from .utils import should_auto_setup
        should_setup, reason = should_auto_setup()

        if should_setup:
            # Run auto-setup on first import
            auto_setup_if_needed()
            
            # Register this installation for tracking
            from .auto_cleanup import register_installation
            register_installation()
            
    except Exception:
        # Silently fail auto-setup - user can run manually
        pass

__all__ = ["GitCheckpoints", "setup_git_checkpoints", "auto_setup_if_needed"]
