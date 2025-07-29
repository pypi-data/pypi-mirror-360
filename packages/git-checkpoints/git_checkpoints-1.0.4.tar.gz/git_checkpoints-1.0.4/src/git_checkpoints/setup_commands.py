"""Custom setuptools commands for git-checkpoints."""

import os
import sys
from pathlib import Path
from setuptools import Command
from setuptools.command.install import install
from setuptools.command.develop import develop

from .setup import auto_setup_if_needed
from .uninstall import global_cleanup


class InstallCommand(install):
    """Custom install command that sets up git-checkpoints."""

    def run(self):
        # Run the normal install process
        install.run(self)
        
        # Track this installation
        self._track_installation()
        
        # Run auto-setup
        self._run_auto_setup()

    def _track_installation(self):
        """Track this installation for future cleanup."""
        try:
            # Create tracking directory
            track_dir = Path.home() / '.git-checkpoints'
            track_dir.mkdir(exist_ok=True)
            
            # Record installation location
            install_file = track_dir / 'installations.txt'
            current_dir = Path.cwd().resolve()
            
            # Read existing installations
            existing = set()
            if install_file.exists():
                with open(install_file, 'r') as f:
                    existing = {line.strip() for line in f if line.strip()}
            
            # Add current installation if it's a git repo
            try:
                import subprocess
                subprocess.run(
                    ["git", "rev-parse", "--git-dir"],
                    capture_output=True,
                    check=True,
                    cwd=current_dir
                )
                existing.add(str(current_dir))
                
                # Write back all installations
                with open(install_file, 'w') as f:
                    for location in sorted(existing):
                        f.write(f"{location}\n")
                        
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass  # Not a git repo, don't track
                
        except Exception:
            pass  # Silent fail

    def _run_auto_setup(self):
        """Run auto-setup if conditions are met."""
        try:
            from .hooks import post_install
            post_install()
        except Exception as e:
            print(f"Warning: Auto-setup failed: {e}")


class DevelopCommand(develop):
    """Custom develop command that sets up git-checkpoints."""

    def run(self):
        # Run the normal develop process
        develop.run(self)
        
        # Run auto-setup
        try:
            from .hooks import post_install
            post_install()
        except Exception as e:
            print(f"Warning: Auto-setup failed: {e}")


class UninstallCommand(Command):
    """Custom uninstall command that cleans up git-checkpoints."""
    
    description = 'Clean up git-checkpoints before uninstall'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run cleanup before uninstall."""
        print("🔄 Running git-checkpoints cleanup before uninstall...")
        
        try:
            # Import cleanup function
            from .hooks import pre_uninstall
            pre_uninstall()
        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")