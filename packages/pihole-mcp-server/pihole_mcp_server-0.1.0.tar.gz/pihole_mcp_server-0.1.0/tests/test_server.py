"""Tests for PiHoleMCPServer class."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from mcp import types

from pihole_mcp_server.server import PiHoleMCPServer, PiHoleToolError
from pihole_mcp_server.pihole_client import PiHoleClient, PiHoleStatus, PiHoleError
from pihole_mcp_server.credential_manager import CredentialNotFoundError


class TestPiHoleMCPServer:
    """Test cases for PiHoleMCPServer class."""
    
    def test_init(self, mock_mcp_server):
        """Test PiHoleMCPServer initialization."""
        server = PiHoleMCPServer()
        
        assert server.server is not None
        assert server.credential_manager is not None
        assert server.client is None
    
    @pytest.mark.asyncio
    async def test_initialize_client_success(self, mock_mcp_server):
        """Test successful client initialization."""
        server = PiHoleMCPServer()
        
        with patch.object(server.credential_manager, 'get_pihole_config') as mock_get_config:
            with patch('pihole_mcp_server.server.PiHoleClient') as mock_client_class:
                mock_config = Mock()
                mock_get_config.return_value = mock_config
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                
                await server._initialize_client()
                
                assert server.client == mock_client
                mock_client_class.assert_called_once_with(mock_config)
    
    @pytest.mark.asyncio
    async def test_initialize_client_credentials_not_found(self, mock_mcp_server):
        """Test client initialization when credentials not found."""
        server = PiHoleMCPServer()
        
        with patch.object(server.credential_manager, 'get_pihole_config') as mock_get_config:
            mock_get_config.side_effect = CredentialNotFoundError("Not found")
            
            await server._initialize_client()
            
            assert server.client is None
    
    @pytest.mark.asyncio
    async def test_ensure_client_initialized_success(self, mock_mcp_server):
        """Test ensuring client is initialized successfully."""
        server = PiHoleMCPServer()
        server.client = Mock()
        
        await server._ensure_client_initialized()
        
        # Should not raise any exception
        assert server.client is not None
    
    @pytest.mark.asyncio
    async def test_ensure_client_initialized_failure(self, mock_mcp_server):
        """Test ensuring client is initialized when client is None."""
        server = PiHoleMCPServer()
        server.client = None
        
        with patch.object(server, '_initialize_client') as mock_init:
            mock_init.return_value = None
            
            with pytest.raises(PiHoleToolError) as excinfo:
                await server._ensure_client_initialized()
            
            assert "No Pi-hole credentials found" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_handle_status_success(self, mock_mcp_server, sample_pihole_status):
        """Test handling status request successfully."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.get_status.return_value = sample_pihole_status
        server.client = mock_client
        
        result = await server._handle_status()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "enabled" in result[0].text.lower()
        assert "1,234" in result[0].text  # Formatted query count
    
    @pytest.mark.asyncio
    async def test_handle_status_pihole_error(self, mock_mcp_server):
        """Test handling status request with Pi-hole error."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.get_status.side_effect = PiHoleError("Connection failed")
        server.client = mock_client
        
        with pytest.raises(PiHoleToolError) as excinfo:
            await server._handle_status()
        
        assert "Failed to get Pi-hole status" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_handle_enable_success(self, mock_mcp_server):
        """Test handling enable request successfully."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.enable.return_value = True
        server.client = mock_client
        
        result = await server._handle_enable()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "enabled successfully" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_enable_failure(self, mock_mcp_server):
        """Test handling enable request with failure."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.enable.return_value = False
        server.client = mock_client
        
        with pytest.raises(PiHoleToolError) as excinfo:
            await server._handle_enable()
        
        assert "Failed to enable Pi-hole" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_handle_enable_pihole_error(self, mock_mcp_server):
        """Test handling enable request with Pi-hole error."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.enable.side_effect = PiHoleError("API error")
        server.client = mock_client
        
        with pytest.raises(PiHoleToolError) as excinfo:
            await server._handle_enable()
        
        assert "Failed to enable Pi-hole" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_handle_disable_permanent(self, mock_mcp_server):
        """Test handling disable request permanently."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.disable.return_value = True
        server.client = mock_client
        
        result = await server._handle_disable({})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "disabled permanently" in result[0].text
        mock_client.disable.assert_called_once_with()
    
    @pytest.mark.asyncio
    async def test_handle_disable_with_minutes(self, mock_mcp_server):
        """Test handling disable request with minutes."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.disable_for_minutes.return_value = True
        server.client = mock_client
        
        result = await server._handle_disable({"duration_minutes": 30})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "disabled for 30 minutes" in result[0].text
        mock_client.disable_for_minutes.assert_called_once_with(30)
    
    @pytest.mark.asyncio
    async def test_handle_disable_with_seconds(self, mock_mcp_server):
        """Test handling disable request with seconds."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.disable.return_value = True
        server.client = mock_client
        
        result = await server._handle_disable({"duration_seconds": 120})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "disabled for 120 seconds" in result[0].text
        mock_client.disable.assert_called_once_with(120)
    
    @pytest.mark.asyncio
    async def test_handle_disable_seconds_overrides_minutes(self, mock_mcp_server):
        """Test handling disable request where seconds overrides minutes."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.disable.return_value = True
        server.client = mock_client
        
        result = await server._handle_disable({"duration_minutes": 30, "duration_seconds": 120})
        
        assert "disabled for 120 seconds" in result[0].text
        mock_client.disable.assert_called_once_with(120)
    
    @pytest.mark.asyncio
    async def test_handle_disable_failure(self, mock_mcp_server):
        """Test handling disable request with failure."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.disable.return_value = False
        server.client = mock_client
        
        with pytest.raises(PiHoleToolError) as excinfo:
            await server._handle_disable({})
        
        assert "Failed to disable Pi-hole" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_handle_query_stats_success(self, mock_mcp_server, sample_pihole_status):
        """Test handling query stats request successfully."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.get_status.return_value = sample_pihole_status
        server.client = mock_client
        
        result = await server._handle_query_stats()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Query Statistics" in result[0].text
        assert "1,234" in result[0].text  # Total queries
        assert "567" in result[0].text   # Ads blocked
    
    @pytest.mark.asyncio
    async def test_handle_query_stats_pihole_error(self, mock_mcp_server):
        """Test handling query stats request with Pi-hole error."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.get_status.side_effect = PiHoleError("API error")
        server.client = mock_client
        
        with pytest.raises(PiHoleToolError) as excinfo:
            await server._handle_query_stats()
        
        assert "Failed to get query statistics" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_handle_top_domains_success(self, mock_mcp_server):
        """Test handling top domains request successfully."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client._make_request.return_value = {
            "top_queries": {
                "google.com": 1000,
                "facebook.com": 500,
                "youtube.com": 300
            }
        }
        server.client = mock_client
        
        result = await server._handle_top_domains({"count": 10})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Top 10 Queried Domains" in result[0].text
        assert "google.com" in result[0].text
        assert "1,000" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_top_domains_no_data(self, mock_mcp_server):
        """Test handling top domains request with no data."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client._make_request.return_value = {}
        server.client = mock_client
        
        result = await server._handle_top_domains({"count": 10})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "No top domains data available" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_top_domains_default_count(self, mock_mcp_server):
        """Test handling top domains request with default count."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client._make_request.return_value = {"top_queries": {}}
        server.client = mock_client
        
        await server._handle_top_domains({})
        
        # Should use default count of 10
        mock_client._make_request.assert_called_once_with("topItems", params={"count": 10}, require_auth=True)
    
    @pytest.mark.asyncio
    async def test_handle_top_blocked_success(self, mock_mcp_server):
        """Test handling top blocked domains request successfully."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client._make_request.return_value = {
            "top_ads": {
                "ads.example.com": 500,
                "tracker.example.com": 300,
                "malware.example.com": 200
            }
        }
        server.client = mock_client
        
        result = await server._handle_top_blocked({"count": 5})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Top 5 Blocked Domains" in result[0].text
        assert "ads.example.com" in result[0].text
        assert "500" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_top_blocked_no_data(self, mock_mcp_server):
        """Test handling top blocked domains request with no data."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client._make_request.return_value = {}
        server.client = mock_client
        
        result = await server._handle_top_blocked({"count": 5})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "No top blocked domains data available" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_query_types_success(self, mock_mcp_server):
        """Test handling query types request successfully."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client._make_request.return_value = {
            "querytypes": {
                "A": 65.5,
                "AAAA": 25.3,
                "CNAME": 8.2,
                "PTR": 1.0
            }
        }
        server.client = mock_client
        
        result = await server._handle_query_types()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Query Types Breakdown" in result[0].text
        assert "A**: 65.5%" in result[0].text
        assert "AAAA**: 25.3%" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_query_types_no_data(self, mock_mcp_server):
        """Test handling query types request with no data."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client._make_request.return_value = {}
        server.client = mock_client
        
        result = await server._handle_query_types()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "No query types data available" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_version_success(self, mock_mcp_server):
        """Test handling version request successfully."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.get_version.return_value = {
            "version": "v5.17.1",
            "tag": "v5.17.1",
            "branch": "master",
            "hash": "abc123"
        }
        server.client = mock_client
        
        result = await server._handle_version()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Version Information" in result[0].text
        assert "v5.17.1" in result[0].text
        assert "master" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_version_pihole_error(self, mock_mcp_server):
        """Test handling version request with Pi-hole error."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.get_version.side_effect = PiHoleError("API error")
        server.client = mock_client
        
        with pytest.raises(PiHoleToolError) as excinfo:
            await server._handle_version()
        
        assert "Failed to get version information" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_handle_test_connection_success(self, mock_mcp_server):
        """Test handling test connection request successfully."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.test_authentication.return_value = True
        server.client = mock_client
        
        result = await server._handle_test_connection()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Connection Test" in result[0].text
        assert "Connection**: OK" in result[0].text
        assert "Authentication**: OK" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_test_connection_failure(self, mock_mcp_server):
        """Test handling test connection request with connection failure."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.test_connection.return_value = False
        mock_client.test_authentication.return_value = True
        server.client = mock_client
        
        result = await server._handle_test_connection()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Connection**: FAILED" in result[0].text
        assert "Authentication**: OK" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_test_connection_auth_failure(self, mock_mcp_server):
        """Test handling test connection request with authentication failure."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.test_authentication.return_value = False
        server.client = mock_client
        
        result = await server._handle_test_connection()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Connection**: OK" in result[0].text
        assert "Authentication**: FAILED" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_test_connection_pihole_error(self, mock_mcp_server):
        """Test handling test connection request with Pi-hole error."""
        server = PiHoleMCPServer()
        mock_client = Mock()
        mock_client.test_connection.side_effect = PiHoleError("Network error")
        mock_client.test_authentication.return_value = True
        server.client = mock_client
        
        with pytest.raises(PiHoleToolError) as excinfo:
            await server._handle_test_connection()
        
        assert "Failed to test connection" in str(excinfo.value)
    
    @pytest.mark.skip(reason="MCP server stdio integration test - requires complex async mocking")
    @pytest.mark.asyncio
    async def test_run_method(self, mock_mcp_server, mock_stdio_server):
        """Test the run method."""
        server = PiHoleMCPServer()
        
        # Mock the stdio server context manager properly
        mock_context = Mock()
        mock_context.__aenter__ = Mock(return_value=("read_stream", "write_stream"))
        mock_context.__aexit__ = Mock(return_value=None)
        mock_stdio_server.return_value = mock_context
        
        # Mock the server run method to avoid actual execution
        mock_mcp_server.return_value.run = Mock()
        
        await server.run()
        
        mock_stdio_server.assert_called_once()
    
    @pytest.mark.skip(reason="MCP server decorator registration - complex mocking needed")
    def test_setup_handlers_list_tools(self, mock_mcp_server):
        """Test that list_tools handler is set up correctly."""
        server = PiHoleMCPServer()
        
        # The handler should be registered
        mock_mcp_server.return_value.list_tools.assert_called_once()
        assert hasattr(mock_mcp_server.return_value, '_list_tools_handler')
    
    @pytest.mark.skip(reason="MCP server decorator registration - complex mocking needed")
    def test_setup_handlers_call_tool(self, mock_mcp_server):
        """Test that call_tool handler is set up correctly."""
        server = PiHoleMCPServer()
        
        # The handler should be registered
        mock_mcp_server.return_value.call_tool.assert_called_once()
        assert hasattr(mock_mcp_server.return_value, '_call_tool_handler')
    
    @pytest.mark.skip(reason="MCP server handler testing - complex async mocking needed")
    @pytest.mark.asyncio
    async def test_list_tools_handler(self, mock_mcp_server):
        """Test the list_tools handler returns correct tools."""
        server = PiHoleMCPServer()
        
        # Get the handler function
        handler = mock_mcp_server.return_value._list_tools_handler
        
        tools = await handler()
        
        assert isinstance(tools, list)
        assert len(tools) == 9  # All the tools we defined
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "pihole_status",
            "pihole_enable",
            "pihole_disable",
            "pihole_query_stats",
            "pihole_top_domains",
            "pihole_top_blocked",
            "pihole_query_types",
            "pihole_version",
            "pihole_test_connection"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.skip(reason="MCP server handler testing - complex async mocking needed")
    @pytest.mark.asyncio
    async def test_call_tool_handler_status(self, mock_mcp_server, sample_pihole_status):
        """Test the call_tool handler for status."""
        server = PiHoleMCPServer()
        server.client = Mock()
        server.client.get_status.return_value = sample_pihole_status
        
        # Get the handler function
        handler = mock_mcp_server.return_value._call_tool_handler
        
        result = await handler("pihole_status", {})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
    
    @pytest.mark.skip(reason="MCP server handler testing - complex async mocking needed")
    @pytest.mark.asyncio
    async def test_call_tool_handler_unknown_tool(self, mock_mcp_server):
        """Test the call_tool handler with unknown tool."""
        server = PiHoleMCPServer()
        server.client = Mock()
        
        # Get the handler function
        handler = mock_mcp_server.return_value._call_tool_handler
        
        result = await handler("unknown_tool", {})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Unknown tool" in result[0].text
    
    @pytest.mark.skip(reason="MCP server handler testing - complex async mocking needed")
    @pytest.mark.asyncio
    async def test_call_tool_handler_exception(self, mock_mcp_server):
        """Test the call_tool handler with exception."""
        server = PiHoleMCPServer()
        server.client = None  # This will cause an exception
        
        # Get the handler function
        handler = mock_mcp_server.return_value._call_tool_handler
        
        result = await handler("pihole_status", {})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Error:" in result[0].text


class TestPiHoleToolError:
    """Test cases for PiHoleToolError exception."""
    
    def test_pihole_tool_error_inheritance(self):
        """Test PiHoleToolError is a proper Exception subclass."""
        error = PiHoleToolError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
    
    def test_pihole_tool_error_raising(self):
        """Test PiHoleToolError can be raised and caught."""
        with pytest.raises(PiHoleToolError) as excinfo:
            raise PiHoleToolError("Test error")
        
        assert "Test error" in str(excinfo.value)


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


@pytest.mark.skip(reason="MCP server stdio integration test - requires complex async mocking")
@pytest.mark.asyncio
async def test_async_main(mock_mcp_server, mock_stdio_server):
    """Test the async_main function."""
    from pihole_mcp_server.server import async_main
    
    # Mock the stdio server context manager properly
    mock_context = Mock()
    mock_context.__aenter__ = Mock(return_value=("read_stream", "write_stream"))
    mock_context.__aexit__ = Mock(return_value=None)
    mock_stdio_server.return_value = mock_context
    
    # Mock the server run method to avoid actual execution
    mock_mcp_server.return_value.run = Mock()
    
    await async_main()
    
    mock_stdio_server.assert_called_once()


def test_main_function():
    """Test the main function."""
    from pihole_mcp_server.server import main
    
    with patch('asyncio.run') as mock_run:
        main()
        
        mock_run.assert_called_once() 