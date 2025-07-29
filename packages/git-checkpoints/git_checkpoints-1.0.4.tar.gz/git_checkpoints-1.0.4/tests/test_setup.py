"""Basic tests for setup module."""

import tempfile
from pathlib import Path
from unittest.mock import patch


from git_checkpoints.setup import auto_setup_if_needed


def test_auto_setup_if_needed_conditions_not_met():
    """Test auto_setup_if_needed when conditions are not met."""
    with patch(
        "git_checkpoints.setup.should_auto_setup", return_value=(False, "Not ready")
    ):
        # Should return False and not attempt setup
        result = auto_setup_if_needed()
        assert result is False


def test_auto_setup_if_needed_success():
    """Test auto_setup_if_needed when conditions are met and setup succeeds."""
    with patch(
        "git_checkpoints.setup.should_auto_setup", return_value=(True, "Ready")
    ), patch("git_checkpoints.setup.setup_git_aliases") as mock_aliases, patch(
        "git_checkpoints.setup.setup_cron_job"
    ) as mock_cron:

        result = auto_setup_if_needed()

        assert result is True
        mock_aliases.assert_called_once()
        mock_cron.assert_called_once()


def test_auto_setup_if_needed_failure():
    """Test auto_setup_if_needed when setup fails."""
    with patch(
        "git_checkpoints.setup.should_auto_setup", return_value=(True, "Ready")
    ), patch(
        "git_checkpoints.setup.setup_git_aliases", side_effect=Exception("Setup failed")
    ):

        result = auto_setup_if_needed()

        assert result is False


def test_auto_setup_if_needed_with_project_dir():
    """Test auto_setup_if_needed with specific project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        with patch(
            "git_checkpoints.setup.should_auto_setup", return_value=(True, "Ready")
        ), patch("git_checkpoints.setup.setup_git_aliases") as mock_aliases, patch(
            "git_checkpoints.setup.setup_cron_job"
        ) as mock_cron:

            result = auto_setup_if_needed(project_dir)

            assert result is True
            mock_aliases.assert_called_once_with(project_dir)
            mock_cron.assert_called_once_with(project_dir)
