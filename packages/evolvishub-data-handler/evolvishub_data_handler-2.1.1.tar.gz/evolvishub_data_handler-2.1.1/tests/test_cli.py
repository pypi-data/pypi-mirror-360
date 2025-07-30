"""Tests for the CLI module."""
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from evolvishub_data_handler.cli import cli, sync, continuous_sync


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


def test_cli_help(runner):
    """Test CLI help command."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage: cli" in result.output


def test_sync_command(runner):
    """Test sync command."""
    with patch("evolvishub_data_handler.cdc_handler.CDCHandler") as mock_handler:
        mock_instance = MagicMock()
        mock_handler.return_value = mock_instance

        result = runner.invoke(sync, [
            "--config", "tests/fixtures/test_config.yaml"
        ])

        assert result.exit_code == 0
        mock_instance.sync.assert_called_once()


def test_continuous_sync_command(runner):
    """Test continuous sync command."""
    with patch("evolvishub_data_handler.cdc_handler.CDCHandler") as mock_handler:
        mock_instance = MagicMock()
        mock_handler.return_value = mock_instance

        result = runner.invoke(continuous_sync, [
            "--config", "tests/fixtures/test_config.yaml"
        ])

        assert result.exit_code == 0
        mock_instance.run_continuous.assert_called_once()


def test_sync_command_invalid_config(runner):
    """Test sync command with invalid config."""
    result = runner.invoke(sync, [
        "--config", "nonexistent_config.yaml"
    ])

    assert result.exit_code != 0
    assert "Error" in result.output


def test_continuous_sync_command_invalid_config(runner):
    """Test continuous sync command with invalid config."""
    result = runner.invoke(continuous_sync, [
        "--config", "nonexistent_config.yaml"
    ])

    assert result.exit_code != 0
    assert "Error" in result.output 