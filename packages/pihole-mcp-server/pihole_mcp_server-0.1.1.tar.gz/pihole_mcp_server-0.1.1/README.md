# Pi-hole MCP Server

A Model Context Protocol (MCP) server for interacting with Pi-hole DNS servers from AI assistants like Cursor. This allows you to manage your Pi-hole directly through natural language commands in your IDE.

**Universal Compatibility**: Works with both legacy and modern Pi-hole installations, automatically detecting the API version and using the appropriate authentication method.

## Features

- 🔐 **Secure Credential Management**: Encrypted storage of Pi-hole credentials using system keyring
- 🎯 **Easy Setup**: Simple CLI-based configuration and authentication
- 🚀 **Rich MCP Integration**: Full support for Pi-hole operations through the MCP protocol
- 📊 **Comprehensive Statistics**: Access to detailed Pi-hole analytics and metrics
- 🛠️ **Robust CLI**: Complete command-line interface for Pi-hole management
- 🔒 **Security First**: Secure API key handling and SSL verification
- 🔄 **Universal Compatibility**: Supports both legacy and modern Pi-hole API versions
- 🤖 **Automatic Detection**: Automatically detects and adapts to your Pi-hole's API version

## Installation

### Prerequisites

- Python 3.10 or higher
- Access to a Pi-hole instance with either:
  - **Legacy Pi-hole**: API key (found in Admin → Settings → API/Web interface → Show API token)
  - **Modern Pi-hole**: Web interface password (your admin login password)
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Install from PyPI (Recommended)

```bash
# Install globally to ~/.local/
pip install --user pihole-mcp-server

# Or using uv
uv tool install pihole-mcp-server
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/brettbergin/pihole-mcp-server.git
cd pihole-mcp-server

# Install with uv (recommended)
uv sync
uv pip install -e .

# Or with pip
pip install -e .
```

## Quick Start

### 1. Configure Pi-hole Credentials

First, you need to authenticate with your Pi-hole instance:

```bash
pihole-mcp-cli login
```

The tool will automatically detect your Pi-hole's API version and prompt for appropriate credentials. If you don't provide specific authentication options, it will guide you through an interactive setup process.

**For Legacy Pi-hole:**
- **Pi-hole hostname or IP**: Your Pi-hole server address
- **Port**: Usually 80 (HTTP) or 443 (HTTPS)
- **API key**: Found in Pi-hole Admin → Settings → API/Web interface → Show API token
- **HTTPS**: Whether to use secure connection
- **SSL verification**: Whether to verify SSL certificates

**For Modern Pi-hole:**
- **Pi-hole hostname or IP**: Your Pi-hole server address
- **Port**: Usually 8080 (HTTP) or 8443 (HTTPS)
- **Web password**: Your Pi-hole admin interface password
- **HTTPS**: Whether to use secure connection
- **SSL verification**: Whether to verify SSL certificates

#### Manual Authentication Method Selection

If you prefer to specify the authentication method manually:

```bash
# For legacy Pi-hole with API key
pihole-mcp-cli login --host 192.168.1.100 --api-key YOUR_API_KEY

# For modern Pi-hole with web password
pihole-mcp-cli login --host 192.168.1.100 --port 8080 --web-password YOUR_PASSWORD

# Read credentials from stdin (useful for automation)
echo "YOUR_API_KEY" | pihole-mcp-cli login --host 192.168.1.100 --api-key -
echo "YOUR_PASSWORD" | pihole-mcp-cli login --host 192.168.1.100 --port 8080 --web-password -
```

### 2. Test Your Connection

```bash
pihole-mcp-cli test
```

### 3. Use with Cursor or Other MCP Clients

Add the following to your Cursor MCP configuration:

```json
{
  "mcpServers": {
    "pihole": {
      "command": "pihole-mcp-server",
      "args": []
    }
  }
}
```

### 4. Start Managing Pi-hole with AI

Once configured, you can use natural language commands in Cursor:

- "Disable Pi-hole for 30 minutes"
- "Show me Pi-hole statistics"
- "Enable Pi-hole blocking"
- "What are the top blocked domains?"

## CLI Usage

### Available Commands

| Command | Description |
|---------|-------------|
| `login` | Configure and store Pi-hole credentials |
| `status` | Show Pi-hole status and statistics |
| `enable` | Enable Pi-hole DNS blocking |
| `disable` | Disable Pi-hole DNS blocking |
| `test` | Test connection and authentication |
| `info` | Show configuration information |
| `logout` | Remove stored credentials |

### Login Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--host` | Pi-hole hostname or IP | `--host 192.168.1.100` |
| `--port` | Pi-hole port number | `--port 8080` |
| `--api-key` | API key for legacy Pi-hole | `--api-key YOUR_API_KEY` |
| `--web-password` | Web password for modern Pi-hole | `--web-password YOUR_PASSWORD` |
| `--use-https` | Use HTTPS connection | `--use-https` |
| `--no-verify-ssl` | Disable SSL verification | `--no-verify-ssl` |
| `--timeout` | Request timeout in seconds | `--timeout 30` |

### Examples

```bash
# Configure Pi-hole connection (interactive mode - auto-detects API version)
pihole-mcp-cli login --host 192.168.1.100

# Configure legacy Pi-hole with API key
pihole-mcp-cli login --host 192.168.1.100 --api-key YOUR_API_KEY --use-https

# Configure modern Pi-hole with web password
pihole-mcp-cli login --host 192.168.1.100 --port 8080 --web-password YOUR_PASSWORD

# Check current status
pihole-mcp-cli status

# Disable Pi-hole for 1 hour
pihole-mcp-cli disable --minutes 60

# Disable Pi-hole for 30 seconds
pihole-mcp-cli disable --seconds 30

# Enable Pi-hole
pihole-mcp-cli enable

# Show detailed help for a command
pihole-mcp-cli disable --help
```

## MCP Tools

The MCP server provides the following tools for AI assistants:

### Core Operations
- `pihole_status` - Get current Pi-hole status and basic statistics
- `pihole_enable` - Enable Pi-hole DNS blocking
- `pihole_disable` - Disable Pi-hole DNS blocking (with optional duration)

### Statistics and Analytics
### System Information
- `pihole_version` - Get Pi-hole version information
- `pihole_test_connection` - Test connection and authentication

## Configuration

### API Version Detection

The tool automatically detects your Pi-hole's API version:

- **Legacy Pi-hole**: Uses `/admin/api.php` endpoint with API key authentication
- **Modern Pi-hole**: Uses `/api/*` endpoints with web password authentication

The detection process:
1. Attempts to connect to modern API endpoints
2. Falls back to legacy API if modern endpoints are not available
3. Stores the detected version for future use

### Credential Storage

Credentials are stored securely using:
1. **System Keyring** (preferred): Uses your OS's secure credential storage
2. **Encrypted File** (fallback): AES-encrypted file in `~/.local/share/pihole-mcp-server/`

### Configuration Directory

By default, configuration is stored in:
- **Linux/macOS**: `~/.local/share/pihole-mcp-server/`
- **Windows**: `%LOCALAPPDATA%\pihole-mcp-server\`

You can override this with the `--config-dir` option.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PIHOLE_MCP_CONFIG_DIR` | Configuration directory | `~/.local/share/pihole-mcp-server` |

## Security

### Credential Protection
- API keys and web passwords are never logged or displayed in plain text
- Stored using system keyring when available
- Fallback to AES-encrypted file storage
- Machine-specific encryption keys
- Automatic detection prevents credential type mismatches

### SSL/TLS Support
- Full HTTPS support with certificate verification
- Option to disable SSL verification for self-signed certificates
- Secure connection handling with proper timeout management

### Permissions
- Configuration files use restrictive permissions (600/700)
- No sensitive data in command line arguments
- Secure credential prompting

## Troubleshooting

### Common Issues

**Connection Failed**
```bash
# Test your connection
pihole-mcp-cli test

# Check your Pi-hole is accessible
ping your-pihole-ip

# Test legacy Pi-hole API
curl http://your-pihole-ip/admin/api.php

# Test modern Pi-hole API
curl http://your-pihole-ip:8080/api/stats/summary
```

**Authentication Failed**

For **Legacy Pi-hole**:
```bash
# Verify API key in Pi-hole admin interface
# Settings → API / Web interface → Show API token

# Re-login with correct API key
pihole-mcp-cli logout
pihole-mcp-cli login --host your-pihole-ip --api-key YOUR_API_KEY
```

For **Modern Pi-hole**:
```bash
# Use your web interface password (not API key)
pihole-mcp-cli logout
pihole-mcp-cli login --host your-pihole-ip --port 8080 --web-password YOUR_PASSWORD
```

**Wrong Authentication Method**
```bash
# If you get "unauthorized" errors, try the other authentication method
# Modern Pi-hole (usually port 8080) uses web password
# Legacy Pi-hole (usually port 80) uses API key

# Check which API version your Pi-hole uses
curl -I http://your-pihole-ip:8080/api/stats/summary  # Modern
curl -I http://your-pihole-ip/admin/api.php          # Legacy
```

**MCP Server Not Responding**
```bash
# Test MCP server directly
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | pihole-mcp-server

# Check if credentials are configured
pihole-mcp-cli info
```

### Debug Mode

For debugging, you can run the MCP server with logging:

```bash
# Enable debug logging
export PYTHONPATH=src
python -m pihole_mcp_server.server
```

### Reset Configuration

```bash
# Remove all stored credentials and configuration
pihole-mcp-cli logout
rm -rf ~/.local/share/pihole-mcp-server/
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/brettbergin/pihole-mcp-server.git
cd pihole-mcp-server

# Install development dependencies
uv sync --dev

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Type checking
mypy src/

# Code formatting
black src/
isort src/
```

### Project Structure

```
pihole-mcp-server/
├── src/pihole_mcp_server/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── credential_manager.py  # Secure credential storage
│   ├── pihole_client.py    # Pi-hole API client
│   └── server.py           # MCP server implementation
├── tests/                  # Test suite
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Pi-hole](https://pi-hole.net/) - Network-wide ad blocking
- [Model Context Protocol](https://modelcontextprotocol.io/) - AI assistant integration
- [Cursor](https://cursor.sh/) - AI-powered code editor

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/brettbergin/pihole-mcp-server/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/brettbergin/pihole-mcp-server/discussions)
- 📚 **Documentation**: [GitHub Wiki](https://github.com/brettbergin/pihole-mcp-server/wiki)

---

**Made with ❤️ for the Pi-hole and AI assistant communities**