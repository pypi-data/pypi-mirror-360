"""Install and uninstall hooks for git-checkpoints."""

import os
import sys
import subprocess
import atexit
import signal
from pathlib import Path
from setuptools.command.install import install
from setuptools.command.develop import develop

from .setup import auto_setup_if_needed
from .uninstall import global_cleanup


class PostInstallCommand(install):
    """Custom install command that runs auto-setup after installation."""

    def run(self):
        # Run the normal install process
        install.run(self)

        # Register installation location for cleanup tracking
        self._register_installation()

        # Run auto-setup if conditions are met
        try:
            post_install()
        except Exception as e:
            print(f"Warning: Auto-setup failed: {e}")
            print("You can manually run: git-checkpoints-setup")

    def _register_installation(self):
        """Register current installation location for cleanup tracking."""
        try:
            # Create marker directory in user's home
            marker_dir = Path.home() / '.git-checkpoints'
            marker_dir.mkdir(exist_ok=True)

            # Record installation location
            install_file = marker_dir / 'installations.txt'
            current_dir = Path.cwd().resolve()

            # Read existing installations
            existing = set()
            if install_file.exists():
                with open(install_file, 'r') as f:
                    existing = {line.strip() for line in f if line.strip()}

            # Add current installation
            existing.add(str(current_dir))

            # Write back all installations
            with open(install_file, 'w') as f:
                for location in sorted(existing):
                    f.write(f"{location}\n")

        except Exception as e:
            print(f"Warning: Could not register installation: {e}")


class PostDevelopCommand(develop):
    """Custom develop command that runs auto-setup after installation."""

    def run(self):
        # Run the normal develop process
        develop.run(self)

        # Run auto-setup if conditions are met
        try:
            post_install()
        except Exception as e:
            print(f"Warning: Auto-setup failed: {e}")
            print("You can manually run: git-checkpoints-setup")


def post_install():
    """Post-install hook that runs auto-setup if appropriate."""
    # Only run auto-setup if we're in a virtual environment
    if not os.environ.get("VIRTUAL_ENV"):
        print("ℹ️  Not in virtual environment, skipping auto-setup")
        print("Run 'git-checkpoints-setup' manually when ready")
        return

    # Check if we're in a git repository
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            check=True,
            cwd=Path.cwd(),
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ℹ️  Not in a Git repository, skipping auto-setup")
        print("Run 'git-checkpoints-setup' in your Git project when ready")
        return

    # Run auto-setup
    print("🔄 Auto-setting up git-checkpoints...")
    try:
        auto_setup_if_needed()
        print("✅ git-checkpoints is ready to use!")
        print("Available commands:")
        print("  git checkpoint [name]       - Create manual checkpoint")
        print("  git checkpoints             - List all checkpoints")
    except Exception as e:
        print(f"❌ Auto-setup failed: {e}")
        print("Please run 'git-checkpoints-setup' manually")


def pre_uninstall():
    """Pre-uninstall hook that cleans up all git-checkpoints installations."""
    print("🔄 Auto-cleanup: Removing git-checkpoints from all configured projects...")

    try:
        # Mark current directory for cleanup (for orphaned detection)
        from .auto_cleanup import mark_for_cleanup
        mark_for_cleanup()
        
        # Read installation locations
        marker_dir = Path.home() / '.git-checkpoints'
        install_file = marker_dir / 'installations.txt'

        if install_file.exists():
            with open(install_file, 'r') as f:
                locations = [Path(line.strip()) for line in f if line.strip()]

            cleaned_count = 0
            for location in locations:
                if location.exists() and location.is_dir():
                    try:
                        # Change to that directory and run cleanup
                        original_cwd = Path.cwd()
                        os.chdir(location)
                        global_cleanup()
                        os.chdir(original_cwd)
                        cleaned_count += 1
                        print(f"✅ Cleaned up {location}")
                    except Exception as e:
                        print(f"⚠️  Could not clean up {location}: {e}")
                        # Mark for cleanup on next import if direct cleanup failed
                        from .auto_cleanup import mark_for_cleanup
                        original_cwd = Path.cwd()
                        os.chdir(location)
                        mark_for_cleanup()
                        os.chdir(original_cwd)

            # Remove marker files
            install_file.unlink()

            # Remove marker directory if empty
            try:
                marker_dir.rmdir()
            except OSError:
                pass  # Directory not empty, that's fine

            print(f"✅ Auto-cleanup completed for {cleaned_count} project(s)")

        else:
            # Fallback: clean up current directory only
            print("🔄 Running fallback cleanup for current directory...")
            global_cleanup()
            print("✅ Fallback cleanup completed")

    except Exception as e:
        print(f"⚠️  Auto-cleanup failed: {e}")
        print("Git aliases and cron jobs may need manual removal")
        # Mark for cleanup on next import if immediate cleanup failed
        from .auto_cleanup import mark_for_cleanup
        mark_for_cleanup()


def check_for_uninstall_and_cleanup():
    """Check if we're being uninstalled and run cleanup if needed."""
    try:
        # Check if this is an uninstall context
        cmd_line = ' '.join(sys.argv).lower()
        uninstall_indicators = [
            'uninstall git-checkpoints',
            'remove git-checkpoints',
            'pip uninstall',
            'uv remove'
        ]

        if any(indicator in cmd_line for indicator in uninstall_indicators):
            # Wait a moment for pip/uv to finish, then cleanup
            import time
            time.sleep(0.1)
            pre_uninstall()

    except Exception:
        pass  # Silent fail to avoid breaking anything


# Register cleanup hooks
def register_cleanup_hooks():
    """Register various cleanup hooks."""
    try:
        # Register atexit handler
        atexit.register(check_for_uninstall_and_cleanup)

        # Register signal handlers for common termination signals
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, lambda s, f: check_for_uninstall_and_cleanup())

        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, lambda s, f: check_for_uninstall_and_cleanup())

    except Exception:
        pass  # Silent fail


# Auto-register hooks when module is imported
try:
    register_cleanup_hooks()
except Exception:
    pass  # Silent fail
