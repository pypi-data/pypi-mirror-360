"""Automatic cleanup system for orphaned git-checkpoints installations."""

import os
import sys
from pathlib import Path


def check_and_cleanup_orphaned():
    """Check for and clean up orphaned git-checkpoints installations."""
    try:
        # Only run in virtual environments
        if not os.environ.get('VIRTUAL_ENV'):
            return
            
        # Only run in git repositories
        from .utils import is_git_repository, has_git_checkpoints_aliases
        current_dir = Path.cwd()
        
        if not is_git_repository(current_dir):
            return
            
        # Check if git-checkpoints aliases exist
        if not has_git_checkpoints_aliases(current_dir):
            return
            
        # Check if this appears to be an orphaned installation
        if _is_orphaned_installation():
            print("🔄 Detected orphaned git-checkpoints installation, auto-cleaning...")
            
            from .uninstall import global_cleanup
            global_cleanup()
            
            print("✅ Orphaned git-checkpoints installation cleaned up successfully")
            print("   Commands like 'git checkpoint' will no longer work")
            
    except Exception:
        # Silent fail to avoid breaking anything
        pass


def _is_orphaned_installation():
    """Detect if this is an orphaned installation that should be cleaned up."""
    try:
        # Strategy 1: Check if we're running from a different Python than what's in the venv
        current_python = Path(sys.executable)
        venv_python = Path(os.environ.get('VIRTUAL_ENV', '')) / 'bin' / 'python'
        
        # If they don't match, this might be an orphaned installation
        if venv_python.exists() and current_python.resolve() != venv_python.resolve():
            return True
            
        # Strategy 2: Check if git-checkpoints is NOT in the current environment's packages
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                installed_packages = result.stdout.lower()
                if 'git-checkpoints' not in installed_packages:
                    # Package not installed but aliases exist = orphaned
                    return True
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        # Strategy 3: Check for cleanup marker file
        cleanup_marker = Path.home() / '.git-checkpoints' / 'cleanup_pending.txt'
        if cleanup_marker.exists():
            current_dir = str(Path.cwd().resolve())
            
            with open(cleanup_marker, 'r') as f:
                pending_dirs = [line.strip() for line in f if line.strip()]
            
            if current_dir in pending_dirs:
                # Remove this directory from pending list
                remaining = [d for d in pending_dirs if d != current_dir]
                
                if remaining:
                    with open(cleanup_marker, 'w') as f:
                        for d in remaining:
                            f.write(f"{d}\n")
                else:
                    cleanup_marker.unlink()
                    # Remove parent directory if empty
                    try:
                        cleanup_marker.parent.rmdir()
                    except OSError:
                        pass
                        
                return True
                
        return False
        
    except Exception:
        return False


def mark_for_cleanup():
    """Mark current directory for cleanup on next import."""
    try:
        # Create marker directory
        marker_dir = Path.home() / '.git-checkpoints'
        marker_dir.mkdir(exist_ok=True)
        
        # Add current directory to cleanup pending list
        cleanup_marker = marker_dir / 'cleanup_pending.txt'
        current_dir = str(Path.cwd().resolve())
        
        # Read existing entries
        existing = set()
        if cleanup_marker.exists():
            with open(cleanup_marker, 'r') as f:
                existing = {line.strip() for line in f if line.strip()}
        
        # Add current directory
        existing.add(current_dir)
        
        # Write back
        with open(cleanup_marker, 'w') as f:
            for d in sorted(existing):
                f.write(f"{d}\n")
                
    except Exception:
        pass  # Silent fail


def register_installation():
    """Register current installation for tracking."""
    try:
        # Only register if we're in a git repository with venv
        if not os.environ.get('VIRTUAL_ENV'):
            return
            
        from .utils import is_git_repository
        if not is_git_repository(Path.cwd()):
            return
            
        # Track this installation
        track_dir = Path.home() / '.git-checkpoints'
        track_dir.mkdir(exist_ok=True)
        
        install_file = track_dir / 'installations.txt'
        current_dir = str(Path.cwd().resolve())
        
        # Read existing installations
        existing = set()
        if install_file.exists():
            with open(install_file, 'r') as f:
                existing = {line.strip() for line in f if line.strip()}
        
        # Add current installation
        existing.add(current_dir)
        
        # Write back
        with open(install_file, 'w') as f:
            for location in sorted(existing):
                f.write(f"{location}\n")
                
    except Exception:
        pass  # Silent fail