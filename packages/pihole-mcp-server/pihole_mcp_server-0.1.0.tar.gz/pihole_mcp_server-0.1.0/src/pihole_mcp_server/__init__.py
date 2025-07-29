"""Pi-hole MCP server package."""

from .pihole_client import PiHoleClient, PiHoleConfig, PiHoleError
from .credential_manager import CredentialManager
from .server import PiHoleMCPServer
from .cli import main as cli_main

__version__ = "0.1.0"
__all__ = [
    "PiHoleClient",
    "PiHoleConfig", 
    "PiHoleError",
    "CredentialManager",
    "PiHoleMCPServer",
    "cli_main",
]
