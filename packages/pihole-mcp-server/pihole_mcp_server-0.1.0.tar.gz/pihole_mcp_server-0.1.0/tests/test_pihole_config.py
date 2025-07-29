"""Tests for PiHoleConfig class and related models."""

import pytest
from pydantic import ValidationError

from pihole_mcp_server.pihole_client import PiHoleConfig, PiHoleStatus
from pihole_mcp_server.pihole_client import (
    PiHoleError,
    PiHoleConnectionError,
    PiHoleAPIError,
    PiHoleAuthenticationError,
)


class TestPiHoleConfig:
    """Test cases for PiHoleConfig class."""
    
    def test_init_minimal(self):
        """Test PiHoleConfig initialization with minimal parameters."""
        config = PiHoleConfig(host="192.168.1.100")
        
        assert config.host == "192.168.1.100"
        assert config.port == 80
        assert config.api_key is None
        assert config.web_password is None
        assert config.use_https is False
        assert config.verify_ssl is True
        assert config.timeout == 30
        assert config.api_version is None
    
    def test_init_full(self):
        """Test PiHoleConfig initialization with all parameters."""
        config = PiHoleConfig(
            host="pi.hole.local",
            port=8080,
            api_key="test_api_key",
            web_password="test_password",
            use_https=True,
            verify_ssl=False,
            timeout=60,
            api_version="modern"
        )
        
        assert config.host == "pi.hole.local"
        assert config.port == 8080
        assert config.api_key == "test_api_key"
        assert config.web_password == "test_password"
        assert config.use_https is True
        assert config.verify_ssl is False
        assert config.timeout == 60
        assert config.api_version == "modern"
    
    def test_validate_host_empty(self):
        """Test host validation with empty string."""
        with pytest.raises(ValidationError) as excinfo:
            PiHoleConfig(host="")
        
        assert "Host cannot be empty" in str(excinfo.value)
    
    def test_validate_host_whitespace(self):
        """Test host validation with whitespace."""
        with pytest.raises(ValidationError) as excinfo:
            PiHoleConfig(host="   ")
        
        assert "Host cannot be empty" in str(excinfo.value)
    
    def test_validate_host_strips_whitespace(self):
        """Test host validation strips whitespace."""
        config = PiHoleConfig(host="  192.168.1.100  ")
        assert config.host == "192.168.1.100"
    
    def test_validate_port_valid_range(self):
        """Test port validation with valid ports."""
        config1 = PiHoleConfig(host="test.com", port=1)
        assert config1.port == 1
        
        config2 = PiHoleConfig(host="test.com", port=65535)
        assert config2.port == 65535
        
        config3 = PiHoleConfig(host="test.com", port=80)
        assert config3.port == 80
    
    def test_validate_port_invalid_low(self):
        """Test port validation with port too low."""
        with pytest.raises(ValidationError) as excinfo:
            PiHoleConfig(host="test.com", port=0)
        
        assert "Port must be between 1 and 65535" in str(excinfo.value)
    
    def test_validate_port_invalid_high(self):
        """Test port validation with port too high."""
        with pytest.raises(ValidationError) as excinfo:
            PiHoleConfig(host="test.com", port=65536)
        
        assert "Port must be between 1 and 65535" in str(excinfo.value)
    
    def test_base_url_http(self):
        """Test base_url property with HTTP."""
        config = PiHoleConfig(host="192.168.1.100", port=80, use_https=False)
        assert config.base_url == "http://192.168.1.100:80"
    
    def test_base_url_https(self):
        """Test base_url property with HTTPS."""
        config = PiHoleConfig(host="192.168.1.100", port=443, use_https=True)
        assert config.base_url == "https://192.168.1.100:443"
    
    def test_base_url_custom_port(self):
        """Test base_url property with custom port."""
        config = PiHoleConfig(host="pi.hole.local", port=8080, use_https=True)
        assert config.base_url == "https://pi.hole.local:8080"
    
    def test_get_api_url_legacy_default(self):
        """Test get_api_url with legacy API (default)."""
        config = PiHoleConfig(host="192.168.1.100", port=80)
        url = config.get_api_url()
        assert url == "http://192.168.1.100:80/admin/api.php"
    
    def test_get_api_url_legacy_explicit(self):
        """Test get_api_url with legacy API explicitly."""
        config = PiHoleConfig(host="192.168.1.100", port=80)
        url = config.get_api_url("legacy")
        assert url == "http://192.168.1.100:80/admin/api.php"
    
    def test_get_api_url_modern(self):
        """Test get_api_url with modern API."""
        config = PiHoleConfig(host="192.168.1.100", port=80)
        url = config.get_api_url("modern")
        assert url == "http://192.168.1.100:80/api"
    
    def test_get_api_url_modern_https(self):
        """Test get_api_url with modern API and HTTPS."""
        config = PiHoleConfig(host="pi.hole.local", port=443, use_https=True)
        url = config.get_api_url("modern")
        assert url == "https://pi.hole.local:443/api"
    
    def test_config_serialization(self):
        """Test PiHoleConfig can be serialized and deserialized."""
        original = PiHoleConfig(
            host="192.168.1.100",
            port=8080,
            api_key="test_key",
            web_password="test_pass",
            use_https=True,
            verify_ssl=False,
            timeout=45,
            api_version="modern"
        )
        
        # Serialize to dict
        config_dict = original.model_dump()
        
        # Deserialize from dict
        restored = PiHoleConfig(**config_dict)
        
        assert restored.host == original.host
        assert restored.port == original.port
        assert restored.api_key == original.api_key
        assert restored.web_password == original.web_password
        assert restored.use_https == original.use_https
        assert restored.verify_ssl == original.verify_ssl
        assert restored.timeout == original.timeout
        assert restored.api_version == original.api_version
    
    def test_config_equality(self):
        """Test PiHoleConfig equality comparison."""
        config1 = PiHoleConfig(
            host="192.168.1.100",
            port=80,
            api_key="test_key"
        )
        config2 = PiHoleConfig(
            host="192.168.1.100",
            port=80,
            api_key="test_key"
        )
        config3 = PiHoleConfig(
            host="192.168.1.100",
            port=80,
            api_key="different_key"
        )
        
        assert config1 == config2
        assert config1 != config3


class TestPiHoleStatus:
    """Test cases for PiHoleStatus class."""
    
    def test_init_minimal(self):
        """Test PiHoleStatus initialization with minimal parameters."""
        status = PiHoleStatus(status="enabled")
        
        assert status.status == "enabled"
        assert status.version is None
        assert status.queries_today is None
        assert status.ads_blocked_today is None
        assert status.ads_percentage_today is None
        assert status.gravity_last_updated is None
    
    def test_init_full(self):
        """Test PiHoleStatus initialization with all parameters."""
        status = PiHoleStatus(
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
        
        assert status.status == "enabled"
        assert status.version == "v5.17.1"
        assert status.queries_today == 1234
        assert status.ads_blocked_today == 567
        assert status.ads_percentage_today == 45.8
        assert status.unique_domains == 890
        assert status.unique_clients == 12
        assert status.queries_forwarded == 667
        assert status.queries_cached == 567
        assert status.clients_ever_seen == 25
        assert status.dns_queries_all_types == 1234
        assert status.reply_nodata == 45
        assert status.reply_nxdomain == 67
        assert status.reply_cname == 89
        assert status.reply_ip == 1033
        assert status.privacy_level == 0
    
    def test_status_serialization(self):
        """Test PiHoleStatus can be serialized and deserialized."""
        original = PiHoleStatus(
            status="disabled",
            version="v5.17.1",
            queries_today=5678,
            ads_blocked_today=1234,
            ads_percentage_today=21.7
        )
        
        # Serialize to dict
        status_dict = original.model_dump()
        
        # Deserialize from dict
        restored = PiHoleStatus(**status_dict)
        
        assert restored.status == original.status
        assert restored.version == original.version
        assert restored.queries_today == original.queries_today
        assert restored.ads_blocked_today == original.ads_blocked_today
        assert restored.ads_percentage_today == original.ads_percentage_today
    
    def test_status_from_dict_extra_fields(self):
        """Test PiHoleStatus creation from dict with extra fields."""
        data = {
            "status": "enabled",
            "version": "v5.17.1",
            "queries_today": 1000,
            "unknown_field": "should_be_ignored"
        }
        
        status = PiHoleStatus(**{k: v for k, v in data.items() if k in PiHoleStatus.model_fields})
        
        assert status.status == "enabled"
        assert status.version == "v5.17.1"
        assert status.queries_today == 1000
        assert not hasattr(status, "unknown_field")


class TestPiHoleExceptions:
    """Test cases for Pi-hole exception classes."""
    
    def test_pihole_error_inheritance(self):
        """Test PiHoleError is a proper Exception subclass."""
        error = PiHoleError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
    
    def test_pihole_connection_error_inheritance(self):
        """Test PiHoleConnectionError inherits from PiHoleError."""
        error = PiHoleConnectionError("Connection failed")
        assert isinstance(error, PiHoleError)
        assert isinstance(error, Exception)
        assert str(error) == "Connection failed"
    
    def test_pihole_api_error_inheritance(self):
        """Test PiHoleAPIError inherits from PiHoleError."""
        error = PiHoleAPIError("API error")
        assert isinstance(error, PiHoleError)
        assert isinstance(error, Exception)
        assert str(error) == "API error"
    
    def test_pihole_authentication_error_inheritance(self):
        """Test PiHoleAuthenticationError inherits from PiHoleError."""
        error = PiHoleAuthenticationError("Auth failed")
        assert isinstance(error, PiHoleError)
        assert isinstance(error, Exception)
        assert str(error) == "Auth failed"
    
    def test_exception_raising(self):
        """Test exceptions can be raised and caught properly."""
        with pytest.raises(PiHoleError):
            raise PiHoleError("Test")
        
        with pytest.raises(PiHoleConnectionError):
            raise PiHoleConnectionError("Test")
        
        with pytest.raises(PiHoleAPIError):
            raise PiHoleAPIError("Test")
        
        with pytest.raises(PiHoleAuthenticationError):
            raise PiHoleAuthenticationError("Test")
    
    def test_exception_catching_base_class(self):
        """Test specific exceptions can be caught with base class."""
        with pytest.raises(PiHoleError):
            raise PiHoleConnectionError("Test")
        
        with pytest.raises(PiHoleError):
            raise PiHoleAPIError("Test")
        
        with pytest.raises(PiHoleError):
            raise PiHoleAuthenticationError("Test") 