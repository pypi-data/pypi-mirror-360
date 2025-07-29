"""Basic tests for utils module."""

import os
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock


from git_checkpoints.utils import (
    is_virtual_environment,
    is_git_repository,
    is_git_available,
    should_auto_setup,
)


def test_is_virtual_environment():
    """Test virtual environment detection."""
    # Test without VIRTUAL_ENV
    with patch.dict(os.environ, {}, clear=True):
        if "VIRTUAL_ENV" in os.environ:
            del os.environ["VIRTUAL_ENV"]
        assert not is_virtual_environment()

    # Test with VIRTUAL_ENV
    with patch.dict(os.environ, {"VIRTUAL_ENV": "/some/venv/path"}):
        assert is_virtual_environment()


def test_is_git_available():
    """Test Git availability check."""
    # Test when git is available (assuming it is in our test environment)
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert is_git_available()

    # Test when git is not available
    with patch("subprocess.run", side_effect=FileNotFoundError):
        assert not is_git_available()


def test_is_git_repository():
    """Test Git repository detection."""
    # Test with a temporary directory (not a git repo)
    with tempfile.TemporaryDirectory() as tmpdir:
        assert not is_git_repository(Path(tmpdir))

    # Test with a mock git repository
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with tempfile.TemporaryDirectory() as tmpdir:
            assert is_git_repository(Path(tmpdir))

    # Test when git command fails
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "git")):
        with tempfile.TemporaryDirectory() as tmpdir:
            assert not is_git_repository(Path(tmpdir))


def test_should_auto_setup():
    """Test auto-setup decision logic."""
    # Test when all conditions are not met
    with patch("git_checkpoints.utils.is_git_available", return_value=False):
        should_setup, reason = should_auto_setup()
        assert not should_setup
        assert "Git is not available" in reason

    # Test when Git available but not in venv
    with patch("git_checkpoints.utils.is_git_available", return_value=True), patch(
        "git_checkpoints.utils.is_virtual_environment", return_value=False
    ):
        should_setup, reason = should_auto_setup()
        assert not should_setup
        assert "Not in a virtual environment" in reason

    # Test when in venv but not in git repo
    with patch("git_checkpoints.utils.is_git_available", return_value=True), patch(
        "git_checkpoints.utils.is_virtual_environment", return_value=True
    ), patch("git_checkpoints.utils.is_git_repository", return_value=False):
        should_setup, reason = should_auto_setup()
        assert not should_setup
        assert "Not in a Git repository" in reason

    # Test when already configured
    with patch("git_checkpoints.utils.is_git_available", return_value=True), patch(
        "git_checkpoints.utils.is_virtual_environment", return_value=True
    ), patch("git_checkpoints.utils.is_git_repository", return_value=True), patch(
        "git_checkpoints.utils.has_git_checkpoints_aliases", return_value=True
    ):
        should_setup, reason = should_auto_setup()
        assert not should_setup
        assert "Already configured" in reason

    # Test when all conditions are met
    with patch("git_checkpoints.utils.is_git_available", return_value=True), patch(
        "git_checkpoints.utils.is_virtual_environment", return_value=True
    ), patch("git_checkpoints.utils.is_git_repository", return_value=True), patch(
        "git_checkpoints.utils.has_git_checkpoints_aliases", return_value=False
    ):
        should_setup, reason = should_auto_setup()
        assert should_setup
        assert "Ready for auto-setup" in reason
