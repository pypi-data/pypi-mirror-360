"""Tests for PiHoleClient class."""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException

from pihole_mcp_server.pihole_client import (
    PiHoleClient,
    PiHoleConfig,
    PiHoleStatus,
    PiHoleError,
    PiHoleConnectionError,
    PiHoleAPIError,
    PiHoleAuthenticationError,
)


class TestPiHoleClient:
    """Test cases for PiHoleClient class."""
    
    def test_init_basic(self, sample_pihole_config, mock_requests_session):
        """Test basic initialization of PiHoleClient."""
        client = PiHoleClient(sample_pihole_config)
        
        assert client.config == sample_pihole_config
        assert client.session is not None
        assert client._api_version == "legacy"  # Set from config
        assert client._session_valid is False
        assert client._csrf_token is None
    
    def test_init_with_ssl_verification_disabled(self, sample_pihole_config):
        """Test initialization with SSL verification disabled."""
        sample_pihole_config.verify_ssl = False
        
        with patch('requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            client = PiHoleClient(sample_pihole_config)
            
            assert mock_session.verify is False
    
    def test_get_session_cache_file(self, sample_pihole_config):
        """Test session cache file path generation."""
        client = PiHoleClient(sample_pihole_config)
        cache_file = client._get_session_cache_file()
        
        assert isinstance(cache_file, Path)
        assert cache_file.name == f"session_{sample_pihole_config.host}_{sample_pihole_config.port}.json"
        assert "pihole-mcp-server" in str(cache_file)
    
    def test_save_session_cache(self, sample_pihole_config):
        """Test saving session cache to file."""
        client = PiHoleClient(sample_pihole_config)
        client._session_valid = True
        client._csrf_token = "test_csrf_token"
        
        # Mock session.cookies to return dict-like behavior
        mock_cookies = {'session': 'test_session_value'}
        client.session.cookies = mock_cookies
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            client._save_session_cache()
            
            mock_open.assert_called_once()
    
    def test_load_cached_session_file_not_exists(self, sample_pihole_config):
        """Test loading cached session when file doesn't exist."""
        client = PiHoleClient(sample_pihole_config)
        
        with patch('pathlib.Path.exists', return_value=False):
            client._load_cached_session()
            
            assert client._session_valid is False
            assert client._csrf_token is None
    
    def test_load_cached_session_expired(self, sample_pihole_config):
        """Test loading cached session when session is expired."""
        client = PiHoleClient(sample_pihole_config)
        
        old_time = time.time() - 2000  # 2000 seconds ago (expired)
        cached_data = {
            "csrf_token": "old_token",
            "session_valid": True,
            "timestamp": old_time,
            "cookies": {"session": "old_session"}
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = Mock()
                mock_file.read.return_value = json.dumps(cached_data)
                mock_open.return_value.__enter__.return_value = mock_file
                
                with patch.object(client, '_clear_session_cache') as mock_clear:
                    client._load_cached_session()
                    
                    mock_clear.assert_called_once()
                    assert client._session_valid is False
                    assert client._csrf_token is None
    
    def test_load_cached_session_valid(self, sample_pihole_config):
        """Test loading valid cached session."""
        client = PiHoleClient(sample_pihole_config)
        
        current_time = time.time()
        cached_data = {
            "csrf_token": "valid_token",
            "session_valid": True,
            "timestamp": current_time,
            "cookies": {"session": "valid_session"}
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = Mock()
                mock_file.read.return_value = json.dumps(cached_data)
                mock_open.return_value.__enter__.return_value = mock_file
                
                client._load_cached_session()
                
                assert client._session_valid is True
                assert client._csrf_token == "valid_token"
    
    def test_clear_session_cache(self, sample_pihole_config):
        """Test clearing session cache."""
        client = PiHoleClient(sample_pihole_config)
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('os.remove') as mock_remove:
                client._clear_session_cache()
                mock_remove.assert_called_once_with(client._session_cache_file)
    
    def test_detect_api_version_modern_success(self, sample_pihole_config, mock_requests_session):
        """Test detecting modern API version successfully."""
        sample_pihole_config.api_version = None  # Clear preset api_version
        client = PiHoleClient(sample_pihole_config)
        
        # Mock successful modern API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests_session.get.return_value = mock_response
        
        version = client._detect_api_version()
        
        assert version == "modern"
        assert client._api_version == "modern"
    
    def test_detect_api_version_modern_unauthorized(self, sample_pihole_config, mock_requests_session):
        """Test detecting modern API version with unauthorized response."""
        sample_pihole_config.api_version = None  # Clear preset api_version
        client = PiHoleClient(sample_pihole_config)
        
        # Mock unauthorized modern API response (401 but API exists)
        mock_response = Mock()
        mock_response.status_code = 401
        mock_requests_session.get.return_value = mock_response
        
        version = client._detect_api_version()
        
        assert version == "modern"
        assert client._api_version == "modern"
    
    def test_detect_api_version_legacy_fallback(self, sample_pihole_config, mock_requests_session):
        """Test falling back to legacy API version."""
        client = PiHoleClient(sample_pihole_config)
        
        # Mock modern API failing, legacy succeeding
        mock_responses = [
            Mock(side_effect=requests.exceptions.RequestException("Modern API failed")),
            Mock(status_code=200)
        ]
        mock_requests_session.get.side_effect = mock_responses
        
        version = client._detect_api_version()
        
        assert version == "legacy"
        assert client._api_version == "legacy"
    
    def test_detect_api_version_both_fail(self, sample_pihole_config, mock_requests_session):
        """Test API version detection when both APIs fail."""
        sample_pihole_config.api_version = None  # Clear preset api_version
        client = PiHoleClient(sample_pihole_config)
        
        # Mock both APIs failing
        mock_requests_session.get.side_effect = requests.exceptions.RequestException("Connection failed")
        
        version = client._detect_api_version()
        
        # Should default to modern
        assert version == "modern"
        assert client._api_version == "modern"
    
    def test_authenticate_modern_success(self, sample_pihole_config_modern, mock_requests_session):
        """Test successful modern API authentication."""
        client = PiHoleClient(sample_pihole_config_modern)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "session": {
                "valid": True,
                "csrf": "test_csrf_token"
            }
        }
        mock_requests_session.post.return_value = mock_response
        
        # Mock the session cache save method to avoid cookie issues
        with patch.object(client, '_save_session_cache') as mock_save:
            result = client._authenticate_modern()
            
            assert result is True
            assert client._session_valid is True
            assert client._csrf_token == "test_csrf_token"
            mock_save.assert_called_once()
    
    def test_authenticate_modern_failure(self, sample_pihole_config_modern, mock_requests_session):
        """Test failed modern API authentication."""
        client = PiHoleClient(sample_pihole_config_modern)
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_requests_session.post.return_value = mock_response
        
        result = client._authenticate_modern()
        
        assert result is False
        assert client._session_valid is False
        assert client._csrf_token is None
    
    def test_authenticate_modern_no_password(self, sample_pihole_config):
        """Test modern API authentication without password."""
        sample_pihole_config.web_password = None
        client = PiHoleClient(sample_pihole_config)
        
        result = client._authenticate_modern()
        
        assert result is False
    
    def test_authenticate_modern_request_exception(self, sample_pihole_config_modern, mock_requests_session):
        """Test modern API authentication with request exception."""
        client = PiHoleClient(sample_pihole_config_modern)
        
        mock_requests_session.post.side_effect = requests.exceptions.RequestException("Network error")
        
        result = client._authenticate_modern()
        
        assert result is False
        assert client._session_valid is False
        assert client._csrf_token is None
    
    def test_ensure_authentication_modern(self, sample_pihole_config_modern, mock_requests_session):
        """Test ensuring authentication for modern API."""
        client = PiHoleClient(sample_pihole_config_modern)
        client._session_valid = True
        
        result = client._ensure_authentication("modern")
        
        assert result is True
    
    def test_ensure_authentication_legacy(self, sample_pihole_config):
        """Test ensuring authentication for legacy API."""
        client = PiHoleClient(sample_pihole_config)
        
        result = client._ensure_authentication("legacy")
        
        assert result is True  # Has API key
    
    def test_ensure_authentication_legacy_no_key(self, sample_pihole_config):
        """Test ensuring authentication for legacy API without key."""
        sample_pihole_config.api_key = None
        client = PiHoleClient(sample_pihole_config)
        
        result = client._ensure_authentication("legacy")
        
        assert result is False
    
    def test_make_request_legacy_summary(self, sample_pihole_config, mock_requests_session):
        """Test making request to legacy API summary endpoint."""
        client = PiHoleClient(sample_pihole_config)
        client._api_version = "legacy"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "enabled"}
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        result = client._make_request("summary")
        
        assert result == {"status": "enabled"}
        mock_requests_session.get.assert_called_once()
    
    def test_make_request_modern_summary(self, sample_pihole_config_modern, mock_requests_session):
        """Test making request to modern API summary endpoint."""
        client = PiHoleClient(sample_pihole_config_modern)
        client._api_version = "modern"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"queries": {"total": 1000}}}
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        result = client._make_request("summary")
        
        assert result == {"data": {"queries": {"total": 1000}}}
        mock_requests_session.get.assert_called_once()
    
    def test_make_request_connection_error(self, sample_pihole_config, mock_requests_session):
        """Test making request with connection error."""
        client = PiHoleClient(sample_pihole_config)
        
        mock_requests_session.get.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(PiHoleConnectionError) as excinfo:
            client._make_request("summary")
        
        assert "Failed to connect to Pi-hole" in str(excinfo.value)
    
    def test_make_request_timeout_error(self, sample_pihole_config, mock_requests_session):
        """Test making request with timeout error."""
        client = PiHoleClient(sample_pihole_config)
        
        mock_requests_session.get.side_effect = Timeout("Request timeout")
        
        with pytest.raises(PiHoleConnectionError) as excinfo:
            client._make_request("summary")
        
        assert "Request timeout" in str(excinfo.value)
    
    def test_make_request_http_error_401(self, sample_pihole_config, mock_requests_session):
        """Test making request with 401 HTTP error."""
        client = PiHoleClient(sample_pihole_config)
        
        mock_response = Mock()
        mock_response.status_code = 401
        http_error = HTTPError("Unauthorized")
        http_error.response = mock_response
        mock_requests_session.get.side_effect = http_error
        
        with pytest.raises(PiHoleAuthenticationError) as excinfo:
            client._make_request("summary")
        
        assert "Authentication failed" in str(excinfo.value)
    
    def test_make_request_http_error_other(self, sample_pihole_config, mock_requests_session):
        """Test making request with non-401 HTTP error."""
        client = PiHoleClient(sample_pihole_config)
        
        mock_response = Mock()
        mock_response.status_code = 500
        http_error = HTTPError("Server error")
        http_error.response = mock_response
        mock_requests_session.get.side_effect = http_error
        
        with pytest.raises(PiHoleAPIError) as excinfo:
            client._make_request("summary")
        
        assert "HTTP error" in str(excinfo.value)
    
    def test_make_request_invalid_json(self, sample_pihole_config, mock_requests_session):
        """Test making request with invalid JSON response."""
        client = PiHoleClient(sample_pihole_config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        with pytest.raises(PiHoleAPIError) as excinfo:
            client._make_request("summary")
        
        assert "Invalid JSON response" in str(excinfo.value)
    
    def test_make_request_api_error_unauthorized(self, sample_pihole_config, mock_requests_session):
        """Test making request with API error (unauthorized)."""
        client = PiHoleClient(sample_pihole_config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "error": {
                "key": "unauthorized",
                "message": "Authentication failed"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        with pytest.raises(PiHoleAuthenticationError) as excinfo:
            client._make_request("summary")
        
        assert "Authentication failed" in str(excinfo.value)
    
    def test_make_request_api_error_seats_exceeded(self, sample_pihole_config, mock_requests_session):
        """Test making request with API seats exceeded error."""
        client = PiHoleClient(sample_pihole_config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "error": {
                "key": "api_seats_exceeded",
                "message": "API session limit exceeded"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        with pytest.raises(PiHoleAuthenticationError) as excinfo:
            client._make_request("summary")
        
        assert "API session limit exceeded" in str(excinfo.value)
    
    def test_make_request_legacy_auth_error(self, sample_pihole_config, mock_requests_session):
        """Test making request with legacy API auth error."""
        client = PiHoleClient(sample_pihole_config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = ["[]"]
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        with pytest.raises(PiHoleAuthenticationError) as excinfo:
            client._make_request("summary")
        
        assert "check API key" in str(excinfo.value)
    
    def test_get_status_legacy(self, sample_pihole_config, mock_requests_session, legacy_api_response):
        """Test getting status from legacy API."""
        client = PiHoleClient(sample_pihole_config)
        client._api_version = "legacy"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = legacy_api_response
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        status = client.get_status()
        
        assert isinstance(status, PiHoleStatus)
        assert status.status == "enabled"
        assert status.queries_today == 1234
        assert status.ads_blocked_today == 567
    
    def test_get_status_modern(self, sample_pihole_config_modern, mock_requests_session, modern_api_response):
        """Test getting status from modern API."""
        client = PiHoleClient(sample_pihole_config_modern)
        client._api_version = "modern"
        client._session_valid = True
        
        # Mock responses for both summary and blocking endpoints
        mock_summary_response = Mock()
        mock_summary_response.status_code = 200
        mock_summary_response.json.return_value = modern_api_response
        mock_summary_response.raise_for_status.return_value = None
        
        mock_blocking_response = Mock()
        mock_blocking_response.status_code = 200
        mock_blocking_response.json.return_value = {"blocking": "enabled"}
        mock_blocking_response.raise_for_status.return_value = None
        
        mock_requests_session.get.side_effect = [mock_summary_response, mock_blocking_response]
        
        status = client.get_status()
        
        assert isinstance(status, PiHoleStatus)
        assert status.status == "enabled"
        assert status.queries_today == 1234
        assert status.ads_blocked_today == 567
    
    def test_is_enabled_true(self, sample_pihole_config, mock_requests_session):
        """Test is_enabled returns True."""
        client = PiHoleClient(sample_pihole_config)
        
        with patch.object(client, 'get_status') as mock_get_status:
            mock_status = Mock()
            mock_status.status = "enabled"
            mock_get_status.return_value = mock_status
            
            result = client.is_enabled()
            
            assert result is True
    
    def test_is_enabled_false(self, sample_pihole_config, mock_requests_session):
        """Test is_enabled returns False."""
        client = PiHoleClient(sample_pihole_config)
        
        with patch.object(client, 'get_status') as mock_get_status:
            mock_status = Mock()
            mock_status.status = "disabled"
            mock_get_status.return_value = mock_status
            
            result = client.is_enabled()
            
            assert result is False
    
    def test_enable_legacy(self, sample_pihole_config, mock_requests_session):
        """Test enabling Pi-hole with legacy API."""
        client = PiHoleClient(sample_pihole_config)
        client._api_version = "legacy"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "enabled"}
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        result = client.enable()
        
        assert result is True
    
    def test_enable_modern(self, sample_pihole_config_modern, mock_requests_session):
        """Test enabling Pi-hole with modern API."""
        client = PiHoleClient(sample_pihole_config_modern)
        client._api_version = "modern"
        client._session_valid = True
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"blocking": "enabled"}
        mock_response.raise_for_status.return_value = None
        
        # Mock both request methods that might be used
        mock_requests_session.post.return_value = mock_response
        mock_requests_session.request.return_value = mock_response
        
        result = client.enable()
        
        assert result is True
    
    def test_disable_legacy(self, sample_pihole_config, mock_requests_session):
        """Test disabling Pi-hole with legacy API."""
        client = PiHoleClient(sample_pihole_config)
        client._api_version = "legacy"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "disabled"}
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        result = client.disable()
        
        assert result is True
    
    def test_disable_modern(self, sample_pihole_config_modern, mock_requests_session):
        """Test disabling Pi-hole with modern API."""
        client = PiHoleClient(sample_pihole_config_modern)
        client._api_version = "modern"
        client._session_valid = True
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"blocking": "disabled"}
        mock_response.raise_for_status.return_value = None
        
        # Mock both request methods that might be used
        mock_requests_session.post.return_value = mock_response
        mock_requests_session.request.return_value = mock_response
        
        result = client.disable()
        
        assert result is True
    
    def test_disable_with_duration(self, sample_pihole_config, mock_requests_session):
        """Test disabling Pi-hole with duration."""
        client = PiHoleClient(sample_pihole_config)
        client._api_version = "legacy"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "disabled"}
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        result = client.disable(duration=300)
        
        assert result is True
    
    def test_disable_for_minutes(self, sample_pihole_config, mock_requests_session):
        """Test disabling Pi-hole for minutes."""
        client = PiHoleClient(sample_pihole_config)
        
        with patch.object(client, 'disable') as mock_disable:
            mock_disable.return_value = True
            
            result = client.disable_for_minutes(5)
            
            assert result is True
            mock_disable.assert_called_once_with(300)  # 5 minutes = 300 seconds
    
    def test_disable_for_minutes_invalid(self, sample_pihole_config):
        """Test disabling Pi-hole for invalid minutes."""
        client = PiHoleClient(sample_pihole_config)
        
        with pytest.raises(ValueError) as excinfo:
            client.disable_for_minutes(0)
        
        assert "Minutes must be positive" in str(excinfo.value)
    
    def test_get_version_legacy(self, sample_pihole_config, mock_requests_session):
        """Test getting version from legacy API."""
        client = PiHoleClient(sample_pihole_config)
        client._api_version = "legacy"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "v5.17.1"}
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        result = client.get_version()
        
        assert result == {"version": "v5.17.1"}
    
    def test_get_version_modern(self, sample_pihole_config_modern, mock_requests_session):
        """Test getting version from modern API."""
        client = PiHoleClient(sample_pihole_config_modern)
        client._api_version = "modern"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"version": "v5.17.1"}}
        mock_response.raise_for_status.return_value = None
        mock_requests_session.get.return_value = mock_response
        
        result = client.get_version()
        
        assert result == {"version": "v5.17.1"}
    
    def test_test_connection_success(self, sample_pihole_config, mock_requests_session):
        """Test successful connection test."""
        client = PiHoleClient(sample_pihole_config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests_session.get.return_value = mock_response
        
        result = client.test_connection()
        
        assert result is True
    
    def test_test_connection_unauthorized(self, sample_pihole_config, mock_requests_session):
        """Test connection test with unauthorized response."""
        client = PiHoleClient(sample_pihole_config)
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_requests_session.get.return_value = mock_response
        
        result = client.test_connection()
        
        assert result is False  # Legacy API expects 200, 401 is failure
    
    def test_test_connection_failure(self, sample_pihole_config, mock_requests_session):
        """Test connection test failure."""
        client = PiHoleClient(sample_pihole_config)
        
        mock_requests_session.get.side_effect = Exception("Connection failed")
        
        result = client.test_connection()
        
        assert result is False
    
    def test_test_authentication_modern_success(self, sample_pihole_config_modern, mock_requests_session):
        """Test successful authentication test for modern API."""
        client = PiHoleClient(sample_pihole_config_modern)
        
        with patch.object(client, '_authenticate_modern') as mock_auth:
            mock_auth.return_value = True
            
            result = client.test_authentication()
            
            assert result is True
    
    def test_test_authentication_modern_no_password(self, sample_pihole_config_modern):
        """Test authentication test for modern API without password."""
        sample_pihole_config_modern.web_password = None
        client = PiHoleClient(sample_pihole_config_modern)
        
        result = client.test_authentication()
        
        assert result is False
    
    def test_test_authentication_legacy_success(self, sample_pihole_config, mock_requests_session):
        """Test successful authentication test for legacy API."""
        client = PiHoleClient(sample_pihole_config)
        
        with patch.object(client, '_ensure_authentication') as mock_ensure:
            mock_ensure.return_value = True
            
            result = client.test_authentication()
            
            assert result is True
    
    def test_test_authentication_legacy_no_key(self, sample_pihole_config):
        """Test authentication test for legacy API without key."""
        sample_pihole_config.api_key = None
        client = PiHoleClient(sample_pihole_config)
        
        result = client.test_authentication()
        
        assert result is False
    
    def test_logout(self, sample_pihole_config, mock_requests_session):
        """Test logout functionality."""
        client = PiHoleClient(sample_pihole_config)
        client._session_valid = True
        client._csrf_token = "test_token"
        
        with patch.object(client, '_clear_session_cache') as mock_clear:
            client.logout()
            
            assert client._session_valid is False
            assert client._csrf_token is None
            mock_clear.assert_called_once()
    
    def test_make_request_require_auth_missing_password(self, sample_pihole_config_modern):
        """Test making request requiring auth without password."""
        sample_pihole_config_modern.web_password = None
        client = PiHoleClient(sample_pihole_config_modern)
        client._api_version = "modern"
        
        with pytest.raises(PiHoleAuthenticationError) as excinfo:
            client._make_request("enable", require_auth=True)
        
        assert "Web password is required" in str(excinfo.value)
    
    def test_make_request_require_auth_missing_api_key(self, sample_pihole_config):
        """Test making request requiring auth without API key."""
        sample_pihole_config.api_key = None
        client = PiHoleClient(sample_pihole_config)
        client._api_version = "legacy"
        
        with pytest.raises(PiHoleAuthenticationError) as excinfo:
            client._make_request("enable", require_auth=True)
        
        assert "API key is required" in str(excinfo.value) 