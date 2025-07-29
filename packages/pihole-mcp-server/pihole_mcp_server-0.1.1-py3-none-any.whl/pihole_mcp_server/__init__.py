"""Pi-hole MCP server package."""

from .cli import main as cli_main
from .credential_manager import CredentialManager
from .pihole_client import PiHoleClient, PiHoleConfig, PiHoleError
from .server import PiHoleMCPServer

__version__ = "0.1.0"
__all__ = [
    "PiHoleClient",
    "PiHoleConfig",
    "PiHoleError",
    "CredentialManager",
    "PiHoleMCPServer",
    "cli_main",
]
