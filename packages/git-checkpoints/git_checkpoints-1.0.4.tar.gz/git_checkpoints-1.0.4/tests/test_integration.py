"""Integration tests for git-checkpoints."""

import tempfile
from pathlib import Path
from unittest.mock import patch


def test_package_import():
    """Test that the package imports correctly."""
    import git_checkpoints

    assert hasattr(git_checkpoints, "__version__")
    assert hasattr(git_checkpoints, "GitCheckpoints")


def test_console_scripts_available():
    """Test that console scripts are properly installed."""
    # Just test that the functions exist (they would be commands after install)
    from git_checkpoints.cli import main
    from git_checkpoints.setup import setup_git_checkpoints
    from git_checkpoints.uninstall import global_cleanup

    assert callable(main)
    assert callable(setup_git_checkpoints)
    assert callable(global_cleanup)


def test_auto_setup_workflow():
    """Test the complete auto-setup workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Mock all external dependencies
        with patch("git_checkpoints.utils.is_git_available", return_value=True), patch(
            "git_checkpoints.utils.is_virtual_environment", return_value=True
        ), patch("git_checkpoints.utils.is_git_repository", return_value=True), patch(
            "git_checkpoints.utils.has_git_checkpoints_aliases", return_value=False
        ), patch(
            "git_checkpoints.setup.setup_git_aliases"
        ) as mock_aliases, patch(
            "git_checkpoints.setup.setup_cron_job"
        ) as mock_cron:

            from git_checkpoints.setup import auto_setup_if_needed

            result = auto_setup_if_needed(project_dir)

            assert result is True
            mock_aliases.assert_called_once_with(project_dir)
            mock_cron.assert_called_once_with(project_dir)


def test_cleanup_workflow():
    """Test the complete cleanup workflow."""
    with tempfile.TemporaryDirectory():
        # Mock all external dependencies
        with patch(
            "git_checkpoints.uninstall.is_git_repository", return_value=True
        ), patch(
            "git_checkpoints.uninstall.has_git_checkpoints_aliases", return_value=True
        ), patch(
            "git_checkpoints.uninstall.cleanup_git_aliases"
        ) as mock_aliases, patch(
            "git_checkpoints.uninstall.cleanup_cron_job"
        ) as mock_cron, patch(
            "git_checkpoints.uninstall.verify_cleanup_complete", return_value=(True, [])
        ):

            from git_checkpoints.uninstall import global_cleanup

            # Should complete without errors
            global_cleanup()

            mock_aliases.assert_called_once()
            mock_cron.assert_called_once()
