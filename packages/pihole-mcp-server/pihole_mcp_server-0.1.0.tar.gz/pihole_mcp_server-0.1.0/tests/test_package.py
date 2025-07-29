"""Tests for package initialization and imports."""

import pytest


class TestPackageImports:
    """Test cases for package imports and initialization."""
    
    def test_package_imports(self):
        """Test that package can be imported and has expected attributes."""
        import pihole_mcp_server
        
        # Check version is defined
        assert hasattr(pihole_mcp_server, '__version__')
        assert pihole_mcp_server.__version__ == "0.1.0"
        
        # Check __all__ is defined
        assert hasattr(pihole_mcp_server, '__all__')
        assert isinstance(pihole_mcp_server.__all__, list)
    
    def test_all_exports(self):
        """Test that all exports are available."""
        import pihole_mcp_server
        
        expected_exports = [
            "PiHoleClient",
            "PiHoleConfig", 
            "PiHoleError",
            "CredentialManager",
            "PiHoleMCPServer",
            "cli_main",
        ]
        
        for export in expected_exports:
            assert export in pihole_mcp_server.__all__
            assert hasattr(pihole_mcp_server, export)
    
    def test_pihole_client_import(self):
        """Test PiHoleClient import."""
        from pihole_mcp_server import PiHoleClient
        from pihole_mcp_server.pihole_client import PiHoleClient as DirectPiHoleClient
        
        assert PiHoleClient is DirectPiHoleClient
    
    def test_pihole_config_import(self):
        """Test PiHoleConfig import."""
        from pihole_mcp_server import PiHoleConfig
        from pihole_mcp_server.pihole_client import PiHoleConfig as DirectPiHoleConfig
        
        assert PiHoleConfig is DirectPiHoleConfig
    
    def test_pihole_error_import(self):
        """Test PiHoleError import."""
        from pihole_mcp_server import PiHoleError
        from pihole_mcp_server.pihole_client import PiHoleError as DirectPiHoleError
        
        assert PiHoleError is DirectPiHoleError
    
    def test_credential_manager_import(self):
        """Test CredentialManager import."""
        from pihole_mcp_server import CredentialManager
        from pihole_mcp_server.credential_manager import CredentialManager as DirectCredentialManager
        
        assert CredentialManager is DirectCredentialManager
    
    def test_pihole_mcp_server_import(self):
        """Test PiHoleMCPServer import."""
        from pihole_mcp_server import PiHoleMCPServer
        from pihole_mcp_server.server import PiHoleMCPServer as DirectPiHoleMCPServer
        
        assert PiHoleMCPServer is DirectPiHoleMCPServer
    
    def test_cli_main_import(self):
        """Test cli_main import."""
        from pihole_mcp_server import cli_main
        from pihole_mcp_server.cli import main as DirectCliMain
        
        assert cli_main is DirectCliMain
    
    def test_individual_module_imports(self):
        """Test that individual modules can be imported."""
        # These should not raise ImportError
        import pihole_mcp_server.pihole_client
        import pihole_mcp_server.credential_manager
        import pihole_mcp_server.server
        import pihole_mcp_server.cli
    
    def test_class_instantiation(self):
        """Test that classes can be instantiated through package imports."""
        from pihole_mcp_server import PiHoleConfig, CredentialManager, PiHoleMCPServer
        
        # Test PiHoleConfig
        config = PiHoleConfig(host="test.com")
        assert config.host == "test.com"
        
        # Test CredentialManager
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = CredentialManager(config_dir=Path(temp_dir))
            assert cred_manager.config_dir == Path(temp_dir)
        
        # Test PiHoleMCPServer
        server = PiHoleMCPServer()
        assert server.server is not None
    
    def test_exception_inheritance(self):
        """Test that exceptions maintain proper inheritance through package imports."""
        from pihole_mcp_server import PiHoleError
        from pihole_mcp_server.pihole_client import (
            PiHoleConnectionError,
            PiHoleAPIError,
            PiHoleAuthenticationError
        )
        
        # Test exception inheritance
        connection_error = PiHoleConnectionError("test")
        api_error = PiHoleAPIError("test")
        auth_error = PiHoleAuthenticationError("test")
        
        assert isinstance(connection_error, PiHoleError)
        assert isinstance(api_error, PiHoleError)
        assert isinstance(auth_error, PiHoleError)
    
    def test_package_docstring(self):
        """Test that package has a docstring."""
        import pihole_mcp_server
        
        assert pihole_mcp_server.__doc__ is not None
        assert "Pi-hole MCP server package" in pihole_mcp_server.__doc__ 