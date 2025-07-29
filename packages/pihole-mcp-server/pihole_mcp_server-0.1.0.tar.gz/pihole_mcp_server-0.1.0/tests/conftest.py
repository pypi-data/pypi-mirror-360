"""Shared fixtures and utilities for pihole-mcp-server tests."""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, MagicMock

import pytest
import responses
from cryptography.fernet import Fernet

from pihole_mcp_server.pihole_client import PiHoleConfig, PiHoleStatus
from pihole_mcp_server.credential_manager import StoredCredentials, CredentialManager


@pytest.fixture
def sample_pihole_config() -> PiHoleConfig:
    """Create a sample PiHoleConfig for testing."""
    return PiHoleConfig(
        host="192.168.1.100",
        port=80,
        api_key="test_api_key_123",
        web_password="test_password_456",
        use_https=False,
        verify_ssl=True,
        timeout=30,
        api_version="legacy"
    )


@pytest.fixture
def sample_pihole_config_modern() -> PiHoleConfig:
    """Create a sample modern PiHoleConfig for testing."""
    return PiHoleConfig(
        host="192.168.1.100",
        port=80,
        web_password="test_password_456",
        use_https=True,
        verify_ssl=False,
        timeout=15,
        api_version="modern"
    )


@pytest.fixture
def sample_pihole_status() -> PiHoleStatus:
    """Create a sample PiHoleStatus for testing."""
    return PiHoleStatus(
        status="enabled",
        version="v5.17.1",
        queries_today=1234,
        ads_blocked_today=567,
        ads_percentage_today=45.8,
        unique_domains=890,
        unique_clients=12,
        queries_forwarded=667,
        queries_cached=567,
        clients_ever_seen=25,
        dns_queries_all_types=1234,
        reply_nodata=45,
        reply_nxdomain=67,
        reply_cname=89,
        reply_ip=1033,
        privacy_level=0
    )


@pytest.fixture
def sample_stored_credentials() -> StoredCredentials:
    """Create a sample StoredCredentials for testing."""
    return StoredCredentials(
        host="192.168.1.100",
        port=80,
        api_key="test_api_key_123",
        web_password="test_password_456",
        use_https=False,
        verify_ssl=True,
        timeout=30,
        api_version="legacy"
    )


@pytest.fixture
def temp_config_dir() -> Path:
    """Create a temporary directory for configuration files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def credential_manager(temp_config_dir: Path) -> CredentialManager:
    """Create a CredentialManager instance with temporary config directory."""
    return CredentialManager(config_dir=temp_config_dir)


@pytest.fixture
def mock_keyring(mocker):
    """Mock the keyring module."""
    mock_keyring = mocker.patch("pihole_mcp_server.credential_manager.keyring")
    mock_keyring.get_password.return_value = None
    mock_keyring.set_password.return_value = None
    mock_keyring.delete_password.return_value = None
    return mock_keyring


@pytest.fixture
def mock_requests_session(mocker):
    """Mock requests.Session for testing HTTP calls."""
    mock_session = mocker.patch("requests.Session")
    mock_instance = Mock()
    mock_session.return_value = mock_instance
    
    # Configure default mock responses
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "enabled"}
    mock_response.raise_for_status.return_value = None
    mock_instance.get.return_value = mock_response
    mock_instance.post.return_value = mock_response
    mock_instance.request.return_value = mock_response
    mock_instance.cookies = Mock()
    mock_instance.verify = True
    
    return mock_instance


@pytest.fixture
def legacy_api_response() -> Dict[str, Any]:
    """Sample legacy API response."""
    return {
        "status": "enabled",
        "version": "v5.17.1",
        "queries_today": 1234,
        "ads_blocked_today": 567,
        "ads_percentage_today": 45.8,
        "unique_domains": 890,
        "unique_clients": 12,
        "queries_forwarded": 667,
        "queries_cached": 567,
        "clients_ever_seen": 25,
        "dns_queries_all_types": 1234,
        "reply_NODATA": 45,
        "reply_NXDOMAIN": 67,
        "reply_CNAME": 89,
        "reply_IP": 1033,
        "privacy_level": 0
    }


@pytest.fixture
def modern_api_response() -> Dict[str, Any]:
    """Sample modern API response."""
    return {
        "data": {
            "queries": {
                "total": 1234,
                "blocked": 567,
                "percent_blocked": 45.8,
                "unique_domains": 890
            }
        }
    }


@pytest.fixture
def modern_auth_response() -> Dict[str, Any]:
    """Sample modern API authentication response."""
    return {
        "session": {
            "valid": True,
            "csrf": "test_csrf_token_123"
        }
    }


@pytest.fixture
def mock_mcp_server(mocker):
    """Mock MCP server for testing."""
    mock_server = mocker.patch("mcp.server.Server")
    mock_instance = Mock()
    mock_server.return_value = mock_instance
    
    # Mock the decorators to act like they register handlers
    def list_tools_decorator():
        def decorator(func):
            mock_instance._list_tools_handler = func
            return func
        return decorator
    
    def call_tool_decorator():
        def decorator(func):
            mock_instance._call_tool_handler = func
            return func
        return decorator
    
    mock_instance.list_tools = Mock(side_effect=list_tools_decorator)
    mock_instance.call_tool = Mock(side_effect=call_tool_decorator)
    
    return mock_instance


@pytest.fixture
def mock_click_context():
    """Mock Click context for CLI testing."""
    ctx = Mock()
    ctx.obj = {"config_dir": None}
    return ctx


@pytest.fixture
def mock_console(mocker):
    """Mock rich console for CLI testing."""
    return mocker.patch("pihole_mcp_server.cli.console")


@pytest.fixture
def mock_file_operations(mocker):
    """Mock file operations for testing."""
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mock_path = mocker.patch("pathlib.Path")
    mock_os = mocker.patch("os")
    
    # Configure path operations
    mock_path_instance = Mock()
    mock_path.return_value = mock_path_instance
    mock_path_instance.exists.return_value = True
    mock_path_instance.mkdir.return_value = None
    mock_path_instance.chmod.return_value = None
    mock_path_instance.unlink.return_value = None
    
    return {
        "open": mock_open,
        "path": mock_path,
        "os": mock_os
    }


@pytest.fixture
def sample_encrypted_data() -> Dict[str, str]:
    """Sample encrypted data for testing."""
    key = Fernet.generate_key()
    f = Fernet(key)
    
    sample_data = '{"host": "192.168.1.100", "port": 80}'
    encrypted_data = f.encrypt(sample_data.encode())
    
    return {
        "encrypted_data": encrypted_data.decode(),
        "salt": "test_salt_123"
    }


@pytest.fixture
def responses_mock():
    """Responses mock for HTTP testing."""
    with responses.RequestsMock() as rsps:
        yield rsps


class MockAsyncIterator:
    """Mock async iterator for testing."""
    
    def __init__(self, items):
        self.items = iter(items)
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        try:
            return next(self.items)
        except StopIteration:
            raise StopAsyncIteration


@pytest.fixture
def mock_stdio_server(mocker):
    """Mock stdio server for testing."""
    mock_stdio = mocker.patch("mcp.server.stdio.stdio_server")
    mock_stdio.return_value = MockAsyncIterator([])
    return mock_stdio


# Custom markers for organizing tests
pytest_plugins = []


# Utility functions for tests
def create_mock_response(status_code: int = 200, json_data: Optional[Dict[str, Any]] = None) -> Mock:
    """Create a mock HTTP response."""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    mock_response.raise_for_status.return_value = None
    return mock_response


def assert_pihole_config_equal(config1: PiHoleConfig, config2: PiHoleConfig) -> None:
    """Assert that two PiHoleConfig objects are equal."""
    assert config1.host == config2.host
    assert config1.port == config2.port
    assert config1.api_key == config2.api_key
    assert config1.web_password == config2.web_password
    assert config1.use_https == config2.use_https
    assert config1.verify_ssl == config2.verify_ssl
    assert config1.timeout == config2.timeout
    assert config1.api_version == config2.api_version


def assert_stored_credentials_equal(cred1: StoredCredentials, cred2: StoredCredentials) -> None:
    """Assert that two StoredCredentials objects are equal."""
    assert cred1.host == cred2.host
    assert cred1.port == cred2.port
    assert cred1.api_key == cred2.api_key
    assert cred1.web_password == cred2.web_password
    assert cred1.use_https == cred2.use_https
    assert cred1.verify_ssl == cred2.verify_ssl
    assert cred1.timeout == cred2.timeout
    assert cred1.api_version == cred2.api_version 