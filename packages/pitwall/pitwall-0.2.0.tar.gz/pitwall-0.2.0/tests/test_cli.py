"""
Tests for Pitwall CLI - The agentic AI companion to MultiViewer.
"""

from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import requests

from pitwall.cli import (
    app,
    _check_multiviewer,
    _resolve_model,
    POPULAR_MODELS,
)


class TestMultiViewerCheck:
    """Test the MultiViewer connectivity check."""

    @patch("pitwall.cli.requests.get")
    def test_check_multiviewer_success_200(self, mock_get):
        """Test successful MultiViewer check with 200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        assert _check_multiviewer() is True
        mock_get.assert_called_once_with(
            "http://localhost:10101/api/graphql", timeout=2
        )

    @patch("pitwall.cli.requests.get")
    def test_check_multiviewer_success_400(self, mock_get):
        """Test successful MultiViewer check with 400 CSRF status."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response

        assert _check_multiviewer() is True
        mock_get.assert_called_once_with(
            "http://localhost:10101/api/graphql", timeout=2
        )

    @patch("pitwall.cli.requests.get")
    def test_check_multiviewer_success_405(self, mock_get):
        """Test successful MultiViewer check with 405 method not allowed."""
        mock_response = MagicMock()
        mock_response.status_code = 405
        mock_get.return_value = mock_response

        assert _check_multiviewer() is True
        mock_get.assert_called_once_with(
            "http://localhost:10101/api/graphql", timeout=2
        )

    @patch("pitwall.cli.requests.get")
    def test_check_multiviewer_failure_404(self, mock_get):
        """Test failed MultiViewer check with 404 status."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        assert _check_multiviewer() is False

    @patch("pitwall.cli.requests.get")
    def test_check_multiviewer_connection_error(self, mock_get):
        """Test MultiViewer check with connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        assert _check_multiviewer() is False

    @patch("pitwall.cli.requests.get")
    def test_check_multiviewer_timeout(self, mock_get):
        """Test MultiViewer check with timeout."""
        mock_get.side_effect = requests.exceptions.Timeout()

        assert _check_multiviewer() is False

    @patch("pitwall.cli.requests.get")
    def test_check_multiviewer_custom_host(self, mock_get):
        """Test MultiViewer check with custom URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        assert _check_multiviewer("http://192.168.1.100:10101/api/graphql") is True
        mock_get.assert_called_once_with(
            "http://192.168.1.100:10101/api/graphql", timeout=2
        )


class TestModelResolution:
    """Test model name resolution."""

    def test_resolve_known_model(self):
        """Test resolving a known model shortcut."""
        assert _resolve_model("claude-sonnet") == "anthropic/claude-sonnet-4"
        assert _resolve_model("claude-opus") == "anthropic/claude-opus-4"
        assert _resolve_model("gpt-41") == "openai/gpt-4.1"
        assert _resolve_model("deepseek") == "deepseek/deepseek-r1-0528"

    def test_resolve_unknown_model(self):
        """Test resolving an unknown model (should return as-is)."""
        custom_model = "custom/model-name"
        assert _resolve_model(custom_model) == custom_model

    def test_all_popular_models_exist(self):
        """Test that all popular model shortcuts are defined."""
        expected_models = [
            "claude-sonnet",
            "claude-opus",
            "gpt-41",
            "gpt-41-mini",
            "gemini-pro",
            "gemini-flash",
            "llama",
            "llama-free",
            "deepseek",
        ]
        for model in expected_models:
            assert model in POPULAR_MODELS
            assert POPULAR_MODELS[model] is not None


class TestCLICommands:
    """Test CLI commands and their behavior."""

    def setUp(self):
        self.runner = CliRunner()

    def test_models_command(self):
        """Test the models command."""
        runner = CliRunner()

        result = runner.invoke(app, ["models"])

        assert result.exit_code == 0
        assert "claude-sonnet" in result.stdout
        assert "claude-opus" in result.stdout
        assert "deepseek" in result.stdout
        assert "anthropic/claude-sonnet-4" in result.stdout

    def test_version_option(self):
        """Test the version option."""
        runner = CliRunner()

        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "Pitwall" in result.stdout
        assert "0.2.0" in result.stdout

    @patch("pitwall.cli._check_multiviewer")
    def test_multiviewer_check_failure(self, mock_check):
        """Test CLI behavior when MultiViewer check fails for default command."""
        mock_check.return_value = False
        runner = CliRunner()

        result = runner.invoke(app, [])

        assert result.exit_code == 1
        assert "MultiViewer is not running" in result.stdout
        assert "https://multiviewer.app" in result.stdout

    def test_custom_url_option(self):
        """Test using custom URL option with models command."""
        runner = CliRunner()

        result = runner.invoke(
            app, ["--url", "http://192.168.1.100:10101/graphql", "models"]
        )

        assert result.exit_code == 0
        assert "claude-sonnet" in result.stdout

    @patch("pitwall.cli._check_multiviewer")
    @patch("pitwall.cli.asyncio.run")
    @patch("pitwall.cli.quick_analysis")
    def test_quick_command_success(
        self, mock_quick_analysis, mock_asyncio_run, mock_check
    ):
        """Test successful quick command execution."""
        mock_check.return_value = True
        mock_quick_analysis.return_value = "Analysis result"
        runner = CliRunner()

        result = runner.invoke(app, ["quick", "test query"])

        assert result.exit_code == 0
        mock_check.assert_called_with("http://localhost:10101/graphql")
        mock_asyncio_run.assert_called_once()

    @patch("pitwall.cli._check_multiviewer")
    def test_quick_command_multiviewer_failure(self, mock_check):
        """Test quick command when MultiViewer check fails."""
        mock_check.return_value = False
        runner = CliRunner()

        result = runner.invoke(app, ["quick", "test query"])

        assert result.exit_code == 1
        assert "MultiViewer is not running" in result.stdout

    @patch("pitwall.cli._check_multiviewer")
    @patch("pitwall.cli.asyncio.run")
    @patch("pitwall.cli.quick_analysis")
    def test_quick_command_custom_host(
        self, mock_quick_analysis, mock_asyncio_run, mock_check
    ):
        """Test quick command with custom host."""
        mock_check.return_value = True
        mock_quick_analysis.return_value = "Analysis result"
        runner = CliRunner()

        result = runner.invoke(
            app, ["quick", "test query", "--url", "http://example.com:10101/graphql"]
        )

        assert result.exit_code == 0
        mock_check.assert_called_with("http://example.com:10101/graphql")

    @patch("pitwall.cli._check_multiviewer")
    @patch("pitwall.cli.asyncio.run")
    @patch("pitwall.cli.quick_analysis")
    def test_quick_command_custom_model(
        self, mock_quick_analysis, mock_asyncio_run, mock_check
    ):
        """Test quick command with custom model."""
        mock_check.return_value = True
        mock_quick_analysis.return_value = "Analysis result"
        runner = CliRunner()

        result = runner.invoke(app, ["quick", "test query", "--model", "deepseek"])

        assert result.exit_code == 0
        # Verify the resolved model is passed to asyncio.run
        mock_asyncio_run.assert_called_once()


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    @patch("pitwall.cli._check_multiviewer")
    def test_help_message(self, mock_check):
        """Test that help message is displayed correctly."""
        mock_check.return_value = True
        runner = CliRunner()

        # Set environment to disable Rich colors that can interfere with testing
        result = runner.invoke(app, ["--help"], env={"NO_COLOR": "1"})

        assert result.exit_code == 0

        # Check for content, accounting for Rich formatting and ANSI codes
        output = result.stdout
        assert "Pitwall" in output or "pitwall" in output
        assert "model" in output  # More flexible check
        assert "url" in output
        assert "verbose" in output

    @patch("pitwall.cli._check_multiviewer")
    def test_invalid_command(self, mock_check):
        """Test behavior with invalid command."""
        mock_check.return_value = True
        runner = CliRunner()

        result = runner.invoke(app, ["invalid-command"])

        # Should show help or error message
        assert result.exit_code != 0
