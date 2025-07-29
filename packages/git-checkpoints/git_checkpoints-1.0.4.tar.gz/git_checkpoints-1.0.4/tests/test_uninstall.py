"""Basic tests for uninstall module."""

import subprocess
from unittest.mock import patch


from git_checkpoints.uninstall import (
    global_cleanup,
    verify_cleanup_complete,
    has_git_checkpoints_aliases_in_current_repo,
)


def test_has_git_checkpoints_aliases_in_current_repo():
    """Test checking for git-checkpoints aliases in current repo."""
    with patch(
        "git_checkpoints.uninstall.has_git_checkpoints_aliases", return_value=True
    ):
        assert has_git_checkpoints_aliases_in_current_repo() is True

    with patch(
        "git_checkpoints.uninstall.has_git_checkpoints_aliases", return_value=False
    ):
        assert has_git_checkpoints_aliases_in_current_repo() is False


def test_verify_cleanup_complete_clean():
    """Test verification when cleanup is complete."""
    with patch(
        "git_checkpoints.uninstall.has_git_checkpoints_aliases", return_value=False
    ), patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "crontab")):

        is_clean, issues = verify_cleanup_complete()
        assert is_clean is True
        assert len(issues) == 0


def test_verify_cleanup_complete_with_issues():
    """Test verification when issues remain."""
    with patch(
        "git_checkpoints.uninstall.has_git_checkpoints_aliases", return_value=True
    ):
        is_clean, issues = verify_cleanup_complete()
        assert is_clean is False
        assert len(issues) > 0
        assert any("aliases still exist" in issue for issue in issues)


def test_global_cleanup_not_git_repo():
    """Test global_cleanup when not in a git repository."""
    with patch("git_checkpoints.uninstall.is_git_repository", return_value=False):
        # Should exit early without error
        global_cleanup()


def test_global_cleanup_no_aliases():
    """Test global_cleanup when no aliases exist."""
    with patch("git_checkpoints.uninstall.is_git_repository", return_value=True), patch(
        "git_checkpoints.uninstall.has_git_checkpoints_aliases", return_value=False
    ), patch("git_checkpoints.uninstall.cleanup_cron_job") as mock_cron, patch(
        "git_checkpoints.uninstall.verify_cleanup_complete", return_value=(True, [])
    ):

        global_cleanup()
        mock_cron.assert_called_once()


def test_global_cleanup_with_aliases():
    """Test global_cleanup when aliases exist."""
    with patch("git_checkpoints.uninstall.is_git_repository", return_value=True), patch(
        "git_checkpoints.uninstall.has_git_checkpoints_aliases", return_value=True
    ), patch("git_checkpoints.uninstall.cleanup_git_aliases") as mock_aliases, patch(
        "git_checkpoints.uninstall.cleanup_cron_job"
    ) as mock_cron, patch(
        "git_checkpoints.uninstall.verify_cleanup_complete", return_value=(True, [])
    ):

        global_cleanup()
        mock_aliases.assert_called_once()
        mock_cron.assert_called_once()


def test_global_cleanup_interactive_decline():
    """Test global_cleanup interactive mode when user declines."""
    with patch("git_checkpoints.uninstall.is_git_repository", return_value=True), patch(
        "git_checkpoints.uninstall.has_git_checkpoints_aliases", return_value=True
    ), patch("builtins.input", return_value="n"):

        global_cleanup(interactive=True)
        # Should exit early without cleaning up


def test_global_cleanup_interactive_accept():
    """Test global_cleanup interactive mode when user accepts."""
    with patch("git_checkpoints.uninstall.is_git_repository", return_value=True), patch(
        "git_checkpoints.uninstall.has_git_checkpoints_aliases", return_value=True
    ), patch("builtins.input", return_value="y"), patch(
        "git_checkpoints.uninstall.cleanup_git_aliases"
    ) as mock_aliases, patch(
        "git_checkpoints.uninstall.cleanup_cron_job"
    ) as mock_cron, patch(
        "git_checkpoints.uninstall.verify_cleanup_complete", return_value=(True, [])
    ):

        global_cleanup(interactive=True)
        mock_aliases.assert_called_once()
        mock_cron.assert_called_once()
