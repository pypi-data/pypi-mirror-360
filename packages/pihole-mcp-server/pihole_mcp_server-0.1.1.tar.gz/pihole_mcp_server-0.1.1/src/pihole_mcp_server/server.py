"""MCP server for Pi-hole interactions."""

import asyncio
import logging
import sys
import traceback
from typing import Any, Dict, List, Optional, Sequence, Union

from mcp import types
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    EmbeddedResource,
    ImageContent,
    TextContent,
    Tool,
)
from pydantic import BaseModel, Field

from .credential_manager import CredentialManager, CredentialNotFoundError
from .pihole_client import PiHoleClient, PiHoleConfig, PiHoleError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PiHoleToolError(Exception):
    """Exception for Pi-hole tool errors."""

    pass


class PiHoleMCPServer:
    """MCP server for Pi-hole interactions."""

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.server: Server = Server("pihole-mcp-server")
        self.credential_manager = CredentialManager()
        self.client: Optional[PiHoleClient] = None

        # Set up server handlers
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up server request handlers."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available Pi-hole tools."""
            return [
                Tool(
                    name="pihole_status",
                    description="Get Pi-hole status and statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="pihole_enable",
                    description="Enable Pi-hole DNS blocking",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="pihole_disable",
                    description="Disable Pi-hole DNS blocking",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "duration_minutes": {
                                "type": "integer",
                                "description": "Duration in minutes to disable Pi-hole (optional, permanent if not specified)",
                                "minimum": 1,
                            },
                            "duration_seconds": {
                                "type": "integer",
                                "description": "Duration in seconds to disable Pi-hole (optional, overrides minutes)",
                                "minimum": 1,
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="pihole_version",
                    description="Get Pi-hole version information",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="pihole_test_connection",
                    description="Test Pi-hole connection and authentication",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle tool calls."""
            try:
                # Ensure we have a client
                await self._ensure_client_initialized()

                if name == "pihole_status":
                    return await self._handle_status()
                elif name == "pihole_enable":
                    return await self._handle_enable()
                elif name == "pihole_disable":
                    return await self._handle_disable(arguments)
                elif name == "pihole_version":
                    return await self._handle_version()
                elif name == "pihole_test_connection":
                    return await self._handle_test_connection()
                else:
                    raise PiHoleToolError(f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Tool call failed: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _initialize_client(self) -> None:
        """Initialize Pi-hole client from stored credentials."""
        try:
            config = self.credential_manager.get_pihole_config()
            self.client = PiHoleClient(config)
        except CredentialNotFoundError:
            # Don't raise an error immediately - let individual tools handle this
            self.client = None

    async def _ensure_client_initialized(self) -> None:
        """Ensure client is initialized, raising error if credentials not found."""
        if self.client is None:
            await self._initialize_client()

        if self.client is None:
            raise PiHoleToolError(
                "No Pi-hole credentials found. Please run 'pihole-mcp-cli login' first."
            )

    async def _handle_status(self) -> List[types.TextContent]:
        """Handle status request."""
        try:
            await self._ensure_client_initialized()
            assert self.client is not None
            status = self.client.get_status()

            # Format status information
            status_text = f"**Pi-hole Status: {status.status.upper()}**\n\n"

            if status.queries_today is not None:
                status_text += f"📊 **Queries Today:** {status.queries_today:,}\n"
            if status.ads_blocked_today is not None:
                status_text += (
                    f"🚫 **Ads Blocked Today:** {status.ads_blocked_today:,}\n"
                )
            if status.ads_percentage_today is not None:
                status_text += (
                    f"📈 **Block Percentage:** {status.ads_percentage_today:.1f}%\n"
                )
            if status.unique_domains is not None:
                status_text += f"🌐 **Unique Domains:** {status.unique_domains:,}\n"
            if status.unique_clients is not None:
                status_text += f"👥 **Unique Clients:** {status.unique_clients:,}\n"
            if status.queries_forwarded is not None:
                status_text += (
                    f"↗️ **Queries Forwarded:** {status.queries_forwarded:,}\n"
                )
            if status.queries_cached is not None:
                status_text += f"💾 **Queries Cached:** {status.queries_cached:,}\n"

            return [types.TextContent(type="text", text=status_text)]

        except PiHoleError as e:
            raise PiHoleToolError(f"Failed to get Pi-hole status: {e}")

    async def _handle_enable(self) -> List[types.TextContent]:
        """Handle enable request."""
        try:
            await self._ensure_client_initialized()
            assert self.client is not None
            success = self.client.enable()
            if success:
                return [
                    types.TextContent(
                        type="text",
                        text="✅ **Pi-hole enabled successfully!**\n\nDNS blocking is now active.",
                    )
                ]
            else:
                raise PiHoleToolError("Failed to enable Pi-hole")

        except PiHoleError as e:
            raise PiHoleToolError(f"Failed to enable Pi-hole: {e}")

    async def _handle_disable(
        self, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Handle disable request."""
        try:
            await self._ensure_client_initialized()
            assert self.client is not None
            duration_minutes = arguments.get("duration_minutes")
            duration_seconds = arguments.get("duration_seconds")

            if duration_seconds is not None:
                success = self.client.disable(duration_seconds)
                duration_text = f"for {duration_seconds} seconds"
            elif duration_minutes is not None:
                success = self.client.disable_for_minutes(duration_minutes)
                duration_text = f"for {duration_minutes} minutes"
            else:
                success = self.client.disable()
                duration_text = "permanently"

            if success:
                return [
                    types.TextContent(
                        type="text",
                        text=f"🔴 **Pi-hole disabled {duration_text}!**\n\nDNS blocking is now inactive.",
                    )
                ]
            else:
                raise PiHoleToolError("Failed to disable Pi-hole")

        except PiHoleError as e:
            raise PiHoleToolError(f"Failed to disable Pi-hole: {e}")

    async def _handle_version(self) -> List[types.TextContent]:
        """Handle version request."""
        try:
            await self._ensure_client_initialized()
            assert self.client is not None
            version_info = self.client.get_version()

            result_text = "ℹ️ **Pi-hole Version Information**\n\n"

            for key, value in version_info.items():
                result_text += f"• **{key}**: {value}\n"

            return [types.TextContent(type="text", text=result_text)]

        except PiHoleError as e:
            raise PiHoleToolError(f"Failed to get version information: {e}")

    async def _handle_test_connection(self) -> List[types.TextContent]:
        """Handle test connection request."""
        try:
            await self._ensure_client_initialized()
            assert self.client is not None
            connection_ok = self.client.test_connection()
            auth_ok = self.client.test_authentication()

            result_text = "🔧 **Pi-hole Connection Test**\n\n"

            if connection_ok:
                result_text += "✅ **Connection**: OK\n"
            else:
                result_text += "❌ **Connection**: FAILED\n"

            if auth_ok:
                result_text += "✅ **Authentication**: OK\n"
            else:
                result_text += "❌ **Authentication**: FAILED\n"

            if connection_ok and auth_ok:
                result_text += "\n🎉 **All tests passed!** Pi-hole is ready for use."
            else:
                result_text += (
                    "\n⚠️ **Some tests failed.** Please check your configuration."
                )

            return [types.TextContent(type="text", text=result_text)]

        except PiHoleError as e:
            raise PiHoleToolError(f"Failed to test connection: {e}")

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, self.server.create_initialization_options()
            )


async def async_main() -> None:
    """Async main entry point for the MCP server."""
    try:
        logger.info("Starting Pi-hole MCP server...")
        server = PiHoleMCPServer()
        logger.info("Server initialized successfully")
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


def main() -> None:
    """Sync main entry point for the MCP server."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
