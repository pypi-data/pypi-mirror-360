"""Tests for CLI module."""

import sys
from unittest.mock import Mock, patch, MagicMock

import pytest
import click
from click.testing import CliRunner

from pihole_mcp_server.cli import (
    cli,
    login,
    status,
    test,
    enable,
    disable,
    logout,
    info,
    main,
    handle_errors,
)
from pihole_mcp_server.pihole_client import PiHoleClient, PiHoleConfig, PiHoleStatus, PiHoleError
from pihole_mcp_server.credential_manager import (
    CredentialManager,
    CredentialNotFoundError,
    CredentialDecryptionError,
    CredentialStorageError,
)


class TestCLI:
    """Test cases for CLI commands."""
    
    def test_cli_group_setup(self):
        """Test CLI group is properly set up."""
        assert cli.name == "cli"
        assert cli.callback is not None
    
    def test_cli_group_version(self):
        """Test CLI version option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        
        assert result.exit_code == 0
        assert "0.1.0" in result.output
    
    def test_cli_group_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        
        assert result.exit_code == 0
        assert "Pi-hole MCP CLI" in result.output
        assert "login" in result.output
        assert "status" in result.output
        assert "enable" in result.output
        assert "disable" in result.output


class TestLoginCommand:
    """Test cases for login command."""
    
    def test_login_command_help(self):
        """Test login command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["login", "--help"])
        
        assert result.exit_code == 0
        assert "Login to Pi-hole" in result.output
        assert "--host" in result.output
        assert "--port" in result.output
        assert "--api-key" in result.output
        assert "--web-password" in result.output
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_login_success_with_api_key(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test successful login with API key."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.test_authentication.return_value = True
        mock_status = Mock()
        mock_status.status = "enabled"
        mock_client.get_status.return_value = mock_status
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            "login",
            "--host", "192.168.1.100",
            "--port", "80",
            "--api-key", "test_api_key"
        ])
        
        assert result.exit_code == 0
        mock_cred_manager.store_pihole_config.assert_called_once()
        mock_client.test_connection.assert_called_once()
        mock_client.test_authentication.assert_called_once()
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_login_success_with_web_password(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test successful login with web password."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.test_authentication.return_value = True
        mock_status = Mock()
        mock_status.status = "enabled"
        mock_client.get_status.return_value = mock_status
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            "login",
            "--host", "192.168.1.100",
            "--web-password", "test_password"
        ])
        
        assert result.exit_code == 0
        mock_cred_manager.store_pihole_config.assert_called_once()
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_login_connection_failure(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test login with connection failure."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.test_connection.return_value = False
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            "login",
            "--host", "192.168.1.100",
            "--api-key", "test_api_key"
        ])
        
        assert result.exit_code == 0  # Function doesn't exit on connection failure
        mock_client.test_connection.assert_called_once()
        mock_cred_manager.store_pihole_config.assert_not_called()
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_login_authentication_failure(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test login with authentication failure."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.test_authentication.return_value = False
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            "login",
            "--host", "192.168.1.100",
            "--api-key", "test_api_key"
        ])
        
        assert result.exit_code == 0  # Function doesn't exit on auth failure
        mock_client.test_connection.assert_called_once()
        mock_client.test_authentication.assert_called_once()
        mock_cred_manager.store_pihole_config.assert_not_called()
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.click.prompt')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_login_prompt_for_credentials(self, mock_cred_manager_class, mock_client_class, mock_prompt, mock_console):
        """Test login prompting for credentials."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.test_authentication.return_value = True
        mock_status = Mock()
        mock_status.status = "enabled"
        mock_client.get_status.return_value = mock_status
        mock_client_class.return_value = mock_client
        
        # Mock prompt responses
        mock_prompt.side_effect = ["web-password", "test_password"]
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            "login",
            "--host", "192.168.1.100"
        ])
        
        assert result.exit_code == 0
        assert mock_prompt.call_count == 2  # Authentication method and password
        mock_cred_manager.store_pihole_config.assert_called_once()
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.sys.stdin')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_login_read_from_stdin(self, mock_cred_manager_class, mock_client_class, mock_stdin, mock_console):
        """Test login reading credentials from stdin."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.test_authentication.return_value = True
        mock_status = Mock()
        mock_status.status = "enabled"
        mock_client.get_status.return_value = mock_status
        mock_client_class.return_value = mock_client
        
        mock_stdin.read.return_value = "test_api_key_from_stdin"
        mock_stdin.read.side_effect = None  # Ensure the return_value is used
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            "login",
            "--host", "192.168.1.100",
            "--api-key", "-"
        ], input="test_api_key_from_stdin")
        
        assert result.exit_code == 0
        # When using CliRunner with input, Click handles stdin differently
        # so we verify the config was stored instead of checking stdin.read directly
        mock_cred_manager.store_pihole_config.assert_called_once()


class TestStatusCommand:
    """Test cases for status command."""
    
    def test_status_command_help(self):
        """Test status command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["status", "--help"])
        
        assert result.exit_code == 0
        assert "Show Pi-hole connection status" in result.output
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_status_success(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test successful status command."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_config = Mock()
        mock_config.host = "192.168.1.100"
        mock_config.port = 80
        mock_config.use_https = False
        mock_config.verify_ssl = True
        mock_config.timeout = 30
        mock_cred_manager.get_pihole_config.return_value = mock_config
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_status = Mock()
        mock_status.status = "enabled"
        mock_status.queries_today = 1234
        mock_status.ads_blocked_today = 567
        mock_status.ads_percentage_today = 45.8
        mock_status.unique_domains = 890
        mock_status.unique_clients = 12
        mock_status.queries_forwarded = 667
        mock_status.queries_cached = 567
        mock_client.get_status.return_value = mock_status
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, ["status"])
        
        assert result.exit_code == 0
        mock_client.get_status.assert_called_once()
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_status_credentials_not_found(self, mock_cred_manager_class, mock_console):
        """Test status command with credentials not found."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_cred_manager.get_pihole_config.side_effect = CredentialNotFoundError("Not found")
        mock_cred_manager_class.return_value = mock_cred_manager
        
        runner = CliRunner()
        result = runner.invoke(cli, ["status"])
        
        assert result.exit_code == 1  # handle_errors decorator should exit with 1


class TestTestCommand:
    """Test cases for test command."""
    
    def test_test_command_help(self):
        """Test test command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["test", "--help"])
        
        assert result.exit_code == 0
        assert "Test Pi-hole connection" in result.output
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_test_success(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test successful test command."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_config = Mock()
        mock_cred_manager.get_pihole_config.return_value = mock_config
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.test_authentication.return_value = True
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, ["test"])
        
        assert result.exit_code == 0
        mock_client.test_connection.assert_called_once()
        mock_client.test_authentication.assert_called_once()
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_test_connection_failure(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test test command with connection failure."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_config = Mock()
        mock_cred_manager.get_pihole_config.return_value = mock_config
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.test_connection.return_value = False
        mock_client.test_authentication.return_value = True
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, ["test"])
        
        assert result.exit_code == 0
        mock_client.test_connection.assert_called_once()
        mock_client.test_authentication.assert_called_once()


class TestEnableCommand:
    """Test cases for enable command."""
    
    def test_enable_command_help(self):
        """Test enable command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["enable", "--help"])
        
        assert result.exit_code == 0
        assert "Enable Pi-hole blocking" in result.output
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_enable_success(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test successful enable command."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_config = Mock()
        mock_cred_manager.get_pihole_config.return_value = mock_config
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.enable.return_value = True
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, ["enable"])
        
        assert result.exit_code == 0
        mock_client.enable.assert_called_once()
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_enable_failure(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test enable command failure."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_config = Mock()
        mock_cred_manager.get_pihole_config.return_value = mock_config
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.enable.return_value = False
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, ["enable"])
        
        assert result.exit_code == 1  # Should exit with error code
        mock_client.enable.assert_called_once()


class TestDisableCommand:
    """Test cases for disable command."""
    
    def test_disable_command_help(self):
        """Test disable command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["disable", "--help"])
        
        assert result.exit_code == 0
        assert "Disable Pi-hole blocking" in result.output
        assert "--minutes" in result.output
        assert "--seconds" in result.output
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_disable_permanent(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test permanent disable command."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_config = Mock()
        mock_cred_manager.get_pihole_config.return_value = mock_config
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.disable.return_value = True
        mock_client_class.return_value = mock_client
        
        with patch('pihole_mcp_server.cli.Confirm.ask', return_value=True):
            runner = CliRunner()
            result = runner.invoke(cli, ["disable"])
            
            assert result.exit_code == 0
            mock_client.disable.assert_called_once()
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_disable_with_minutes(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test disable command with minutes."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_config = Mock()
        mock_cred_manager.get_pihole_config.return_value = mock_config
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.disable_for_minutes.return_value = True
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, ["disable", "--minutes", "30"])
        
        assert result.exit_code == 0
        mock_client.disable_for_minutes.assert_called_once_with(30)
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_disable_with_seconds(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test disable command with seconds."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_config = Mock()
        mock_cred_manager.get_pihole_config.return_value = mock_config
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client.disable.return_value = True
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, ["disable", "--seconds", "120"])
        
        assert result.exit_code == 0
        mock_client.disable.assert_called_once_with(120)
    
    @patch('pihole_mcp_server.cli.console')
    def test_disable_both_minutes_and_seconds(self, mock_console):
        """Test disable command with both minutes and seconds (should error)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["disable", "--minutes", "30", "--seconds", "120"])
        
        assert result.exit_code == 1  # Should exit with error
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_disable_permanent_cancelled(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test permanent disable command cancelled by user."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_config = Mock()
        mock_cred_manager.get_pihole_config.return_value = mock_config
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        with patch('pihole_mcp_server.cli.Confirm.ask', return_value=False):
            runner = CliRunner()
            result = runner.invoke(cli, ["disable"])
            
            assert result.exit_code == 0
            mock_client.disable.assert_not_called()


class TestLogoutCommand:
    """Test cases for logout command."""
    
    def test_logout_command_help(self):
        """Test logout command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["logout", "--help"])
        
        assert result.exit_code == 0
        assert "Remove stored Pi-hole credentials" in result.output
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_logout_success(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test successful logout command."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_cred_manager.has_credentials.return_value = True
        mock_config = Mock()
        mock_cred_manager.get_pihole_config.return_value = mock_config
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        with patch('pihole_mcp_server.cli.Confirm.ask', return_value=True):
            runner = CliRunner()
            result = runner.invoke(cli, ["logout"])
            
            assert result.exit_code == 0
            mock_client.logout.assert_called_once()
            mock_cred_manager.delete_credentials.assert_called_once()
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_logout_no_credentials(self, mock_cred_manager_class, mock_console):
        """Test logout command with no credentials."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_cred_manager.has_credentials.return_value = False
        mock_cred_manager_class.return_value = mock_cred_manager
        
        runner = CliRunner()
        result = runner.invoke(cli, ["logout"])
        
        assert result.exit_code == 0
        mock_cred_manager.delete_credentials.assert_not_called()
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_logout_cancelled(self, mock_cred_manager_class, mock_console):
        """Test logout command cancelled by user."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_cred_manager.has_credentials.return_value = True
        mock_cred_manager_class.return_value = mock_cred_manager
        
        with patch('pihole_mcp_server.cli.Confirm.ask', return_value=False):
            runner = CliRunner()
            result = runner.invoke(cli, ["logout"])
            
            assert result.exit_code == 0
            mock_cred_manager.delete_credentials.assert_not_called()


class TestInfoCommand:
    """Test cases for info command."""
    
    @patch('pihole_mcp_server.cli.console')
    @patch('pihole_mcp_server.cli.PiHoleClient')
    @patch('pihole_mcp_server.cli.CredentialManager')
    def test_info_success(self, mock_cred_manager_class, mock_client_class, mock_console):
        """Test successful info command."""
        # Setup mocks
        mock_cred_manager = Mock()
        mock_cred_manager.has_credentials.return_value = True
        mock_cred_manager.config_dir = "/tmp/test_config"
        mock_cred_manager.config_file = "/tmp/test_config/credentials.json"
        mock_cred_manager.keyring_service = "test_service"
        
        mock_config = Mock()
        mock_config.host = "192.168.1.100"
        mock_config.port = 80
        mock_config.use_https = False
        mock_config.verify_ssl = True
        mock_config.timeout = 30
        mock_config.api_key = "test_api_key_1234"
        mock_cred_manager.get_pihole_config.return_value = mock_config
        mock_cred_manager_class.return_value = mock_cred_manager
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, ["info"])
        
        assert result.exit_code == 0
        # Info command doesn't call get_version, it just displays config info


class TestHandleErrorsDecorator:
    """Test cases for handle_errors decorator."""
    
    def test_handle_errors_keyboard_interrupt(self):
        """Test handle_errors decorator with KeyboardInterrupt."""
        @handle_errors
        def test_func():
            raise KeyboardInterrupt()
        
        with patch('pihole_mcp_server.cli.console') as mock_console:
            with patch('sys.exit') as mock_exit:
                test_func()
                
                mock_exit.assert_called_once_with(1)
    
    def test_handle_errors_credential_not_found(self):
        """Test handle_errors decorator with CredentialNotFoundError."""
        @handle_errors
        def test_func():
            raise CredentialNotFoundError("Not found")
        
        with patch('pihole_mcp_server.cli.console') as mock_console:
            with patch('sys.exit') as mock_exit:
                test_func()
                
                mock_exit.assert_called_once_with(1)
    
    def test_handle_errors_credential_decryption_error(self):
        """Test handle_errors decorator with CredentialDecryptionError."""
        @handle_errors
        def test_func():
            raise CredentialDecryptionError("Decryption failed")
        
        with patch('pihole_mcp_server.cli.console') as mock_console:
            with patch('sys.exit') as mock_exit:
                test_func()
                
                mock_exit.assert_called_once_with(1)
    
    def test_handle_errors_credential_storage_error(self):
        """Test handle_errors decorator with CredentialStorageError."""
        @handle_errors
        def test_func():
            raise CredentialStorageError("Storage failed")
        
        with patch('pihole_mcp_server.cli.console') as mock_console:
            with patch('sys.exit') as mock_exit:
                test_func()
                
                mock_exit.assert_called_once_with(1)
    
    def test_handle_errors_pihole_error(self):
        """Test handle_errors decorator with PiHoleError."""
        @handle_errors
        def test_func():
            raise PiHoleError("API error")
        
        with patch('pihole_mcp_server.cli.console') as mock_console:
            with patch('sys.exit') as mock_exit:
                test_func()
                
                mock_exit.assert_called_once_with(1)
    
    def test_handle_errors_generic_exception(self):
        """Test handle_errors decorator with generic exception."""
        @handle_errors
        def test_func():
            raise Exception("Generic error")
        
        with patch('pihole_mcp_server.cli.console') as mock_console:
            with patch('sys.exit') as mock_exit:
                test_func()
                
                mock_exit.assert_called_once_with(1)
    
    def test_handle_errors_no_exception(self):
        """Test handle_errors decorator with no exception."""
        @handle_errors
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"


class TestMainFunction:
    """Test cases for main function."""
    
    def test_main_function(self):
        """Test main function calls CLI."""
        with patch('pihole_mcp_server.cli.cli') as mock_cli:
            main()
            
            mock_cli.assert_called_once() 