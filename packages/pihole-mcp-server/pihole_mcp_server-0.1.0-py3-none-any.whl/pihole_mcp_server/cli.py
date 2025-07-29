"""Command line interface for Pi-hole MCP server."""

import sys
from typing import Optional, Dict, Any
from pathlib import Path
import functools

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from .pihole_client import PiHoleClient, PiHoleConfig, PiHoleError
from .credential_manager import (
    CredentialManager,
    CredentialError,
    CredentialNotFoundError,
    CredentialStorageError,
    CredentialDecryptionError,
)

console = Console()


def handle_errors(func: Any) -> Any:
    """Decorator to handle common exceptions."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user.[/yellow]")
            sys.exit(1)
        except CredentialNotFoundError:
            console.print(
                "[red]Error: No Pi-hole credentials found.[/red]\n"
                "Please run [bold]pihole-mcp-cli login[/bold] first."
            )
            sys.exit(1)
        except CredentialDecryptionError as e:
            console.print(f"[red]Error: Failed to decrypt credentials: {e}[/red]")
            sys.exit(1)
        except CredentialStorageError as e:
            console.print(f"[red]Error: Failed to store credentials: {e}[/red]")
            sys.exit(1)
        except PiHoleError as e:
            console.print(f"[red]Error: Pi-hole API error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            sys.exit(1)
    return wrapper


@click.group()
@click.version_option(version="0.1.0", prog_name="pihole-mcp-cli")
@click.option(
    "--config-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    help="Configuration directory (default: ~/.local/share/pihole-mcp-server)",
)
@click.pass_context
def cli(ctx: click.Context, config_dir: Optional[Path]) -> None:
    """Pi-hole MCP CLI - Manage Pi-hole credentials and connections.
    
    This CLI tool helps you configure and manage your Pi-hole connection
    for use with the Model Context Protocol (MCP) server.
    
    Common usage:
    
    \b
    1. First, login to your Pi-hole:
       pihole-mcp-cli login
    
    \b
    2. Check your connection status:
       pihole-mcp-cli status
    
    \b
    3. Test Pi-hole functionality:
       pihole-mcp-cli test
    
    \b
    4. Manage Pi-hole state:
       pihole-mcp-cli enable
       pihole-mcp-cli disable --minutes 30
    
    For more information on any command, use:
    pihole-mcp-cli COMMAND --help
    """
    # Store config directory in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["config_dir"] = config_dir


@cli.command()
@click.option(
    "--host",
    prompt="Pi-hole hostname or IP",
    help="Pi-hole server hostname or IP address"
)
@click.option(
    "--port",
    type=int,
    default=80,
    help="Pi-hole server port (default: 80)"
)
@click.option(
    "--api-key",
    help="Pi-hole API key (for legacy Pi-hole) or '-' to read from stdin"
)
@click.option(
    "--web-password",
    help="Pi-hole web password (for modern Pi-hole) or '-' to read from stdin"
)
@click.option(
    "--use-https",
    is_flag=True,
    help="Use HTTPS for connection"
)
@click.option(
    "--no-verify-ssl",
    is_flag=True,
    help="Disable SSL certificate verification"
)
@click.option(
    "--timeout",
    type=int,
    default=30,
    help="Request timeout in seconds (default: 30)"
)
@click.pass_context
@handle_errors
def login(
    ctx: click.Context,
    host: str,
    port: int,
    api_key: Optional[str],
    web_password: Optional[str],
    use_https: bool,
    no_verify_ssl: bool,
    timeout: int
) -> None:
    """Login to Pi-hole and store credentials."""
    
    with console.status("[bold green]Setting up Pi-hole connection...", spinner="dots"):
        try:
            # Read credentials from stdin if requested
            if api_key == "-":
                api_key = sys.stdin.read().strip()
            if web_password == "-":
                web_password = sys.stdin.read().strip()
            
            # Prompt for credentials if not provided
            if not api_key and not web_password:
                console.print("\n[yellow]No credentials provided. Please provide either an API key or web password.[/yellow]")
                auth_choice = click.prompt(
                    "Authentication method",
                    type=click.Choice(["api-key", "web-password"], case_sensitive=False),
                    default="web-password"
                )
                
                if auth_choice == "api-key":
                    api_key = click.prompt("API key", hide_input=True)
                else:
                    web_password = click.prompt("Web password", hide_input=True)
            
            # Create configuration
            config = PiHoleConfig(
                host=host,
                port=port,
                api_key=api_key,
                web_password=web_password,
                use_https=use_https,
                verify_ssl=not no_verify_ssl,
                timeout=timeout
            )
            
            # Test connection
            client = PiHoleClient(config)
            
            console.print("\n[bold blue]Testing connection...[/bold blue]")
            if not client.test_connection():
                console.print("[red]✗ Connection failed[/red]")
                console.print("Please check your host, port, and network settings.")
                return
            
            console.print("[green]✓ Connection successful[/green]")
            
            # Test authentication if credentials provided
            if api_key or web_password:
                console.print("[bold blue]Testing authentication...[/bold blue]")
                if not client.test_authentication():
                    console.print("[red]✗ Authentication failed[/red]")
                    console.print("Please check your credentials.")
                    return
                
                console.print("[green]✓ Authentication successful[/green]")
            
            # Store credentials
            cred_manager = CredentialManager(ctx.obj["config_dir"])
            cred_manager.store_pihole_config(config)
            
            console.print("\n[bold green]✓ Login successful![/bold green]")
            console.print(f"Connected to Pi-hole at {host}:{port}")
            
            # Show current status
            status = client.get_status()
            console.print(f"Status: [bold]{'🟢 Enabled' if status.status == 'enabled' else '🔴 Disabled'}[/bold]")
            
        except Exception as e:
            console.print(f"[red]✗ Login failed: {str(e)}[/red]")
            raise click.Exit(1)
        
        console.print("\n[bold green]Pi-hole connection configured successfully![/bold green]")
        console.print("You can now use other commands like 'pihole-mcp-cli status' or 'pihole-mcp-cli enable'.")


@cli.command()
@click.pass_context
@handle_errors
def status(ctx: click.Context) -> None:
    """Show Pi-hole connection status and statistics.
    
    This command displays the current Pi-hole status, including
    whether it's enabled or disabled, query statistics, and
    blocking information.
    
    Example:
    pihole-mcp-cli status
    """
    cred_manager = CredentialManager(ctx.obj["config_dir"])
    config = cred_manager.get_pihole_config()
    client = PiHoleClient(config)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Fetching Pi-hole status...", total=None)
        status = client.get_status()
    
    # Main status
    status_color = "green" if status.status == "enabled" else "red"
    status_text = Text(status.status.upper(), style=f"bold {status_color}")
    
    console.print(Panel(
        status_text,
        title="Pi-hole Status",
        border_style=status_color
    ))
    
    # Statistics table
    stats_table = Table(title="Statistics", show_header=True, header_style="bold cyan")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="white")
    
    if status.queries_today is not None:
        stats_table.add_row("Queries Today", f"{status.queries_today:,}")
    if status.ads_blocked_today is not None:
        stats_table.add_row("Ads Blocked Today", f"{status.ads_blocked_today:,}")
    if status.ads_percentage_today is not None:
        stats_table.add_row("Block Percentage", f"{status.ads_percentage_today:.1f}%")
    if status.unique_domains is not None:
        stats_table.add_row("Unique Domains", f"{status.unique_domains:,}")
    if status.unique_clients is not None:
        stats_table.add_row("Unique Clients", f"{status.unique_clients:,}")
    if status.queries_forwarded is not None:
        stats_table.add_row("Queries Forwarded", f"{status.queries_forwarded:,}")
    if status.queries_cached is not None:
        stats_table.add_row("Queries Cached", f"{status.queries_cached:,}")
    
    console.print(stats_table)
    
    # Connection info
    info_table = Table(title="Connection Information", show_header=True, header_style="bold cyan")
    info_table.add_column("Setting", style="cyan")
    info_table.add_column("Value", style="white")
    
    info_table.add_row("Host", config.host)
    info_table.add_row("Port", str(config.port))
    info_table.add_row("HTTPS", "Yes" if config.use_https else "No")
    info_table.add_row("SSL Verification", "Yes" if config.verify_ssl else "No")
    info_table.add_row("Timeout", f"{config.timeout}s")
    
    console.print(info_table)


@cli.command()
@click.pass_context
@handle_errors
def test(ctx: click.Context) -> None:
    """Test Pi-hole connection and authentication.
    
    This command performs comprehensive tests of your Pi-hole
    connection including network connectivity, authentication,
    and API functionality.
    
    Example:
    pihole-mcp-cli test
    """
    cred_manager = CredentialManager(ctx.obj["config_dir"])
    config = cred_manager.get_pihole_config()
    client = PiHoleClient(config)
    
    console.print("[bold blue]Testing Pi-hole connection...[/bold blue]\n")
    
    tests = [
        ("Connection", client.test_connection),
        ("Authentication", client.test_authentication),
    ]
    
    for test_name, test_func in tests:
        console.print(f"[yellow]Testing {test_name}...[/yellow]", end=" ")
        
        try:
            result = test_func()
            if result:
                console.print("[green]✓ PASS[/green]")
            else:
                console.print("[red]✗ FAIL[/red]")
        except Exception as e:
            console.print(f"[red]✗ ERROR: {e}[/red]")
    
    console.print("\n[bold green]All tests completed![/bold green]")


@cli.command()
@click.pass_context
@handle_errors
def enable(ctx: click.Context) -> None:
    """Enable Pi-hole blocking.
    
    This command enables Pi-hole DNS filtering, which will
    start blocking ads and other configured domains.
    
    Example:
    pihole-mcp-cli enable
    """
    cred_manager = CredentialManager(ctx.obj["config_dir"])
    config = cred_manager.get_pihole_config()
    client = PiHoleClient(config)
    
    console.print("[yellow]Enabling Pi-hole...[/yellow]")
    
    if client.enable():
        console.print("[green]✓ Pi-hole enabled successfully![/green]")
    else:
        console.print("[red]✗ Failed to enable Pi-hole[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--minutes",
    type=int,
    help="Disable for specified number of minutes (default: permanent)",
)
@click.option(
    "--seconds",
    type=int,
    help="Disable for specified number of seconds",
)
@click.pass_context
@handle_errors
def disable(ctx: click.Context, minutes: Optional[int], seconds: Optional[int]) -> None:
    """Disable Pi-hole blocking.
    
    This command disables Pi-hole DNS filtering. You can specify
    a duration for automatic re-enabling, or disable permanently.
    
    Examples:
    pihole-mcp-cli disable --minutes 30
    pihole-mcp-cli disable --seconds 300
    pihole-mcp-cli disable  # Permanent disable
    """
    if minutes is not None and seconds is not None:
        console.print("[red]Error: Cannot specify both minutes and seconds[/red]")
        sys.exit(1)
    
    cred_manager = CredentialManager(ctx.obj["config_dir"])
    config = cred_manager.get_pihole_config()
    client = PiHoleClient(config)
    
    if minutes is not None:
        console.print(f"[yellow]Disabling Pi-hole for {minutes} minutes...[/yellow]")
        success = client.disable_for_minutes(minutes)
        duration_text = f"for {minutes} minutes"
    elif seconds is not None:
        console.print(f"[yellow]Disabling Pi-hole for {seconds} seconds...[/yellow]")
        success = client.disable(seconds)
        duration_text = f"for {seconds} seconds"
    else:
        if not Confirm.ask("[yellow]Disable Pi-hole permanently?[/yellow]"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
        
        console.print("[yellow]Disabling Pi-hole permanently...[/yellow]")
        success = client.disable()
        duration_text = "permanently"
    
    if success:
        console.print(f"[green]✓ Pi-hole disabled {duration_text}![/green]")
    else:
        console.print("[red]✗ Failed to disable Pi-hole[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
@handle_errors
def logout(ctx: click.Context) -> None:
    """Remove stored Pi-hole credentials.
    
    This command will delete your stored Pi-hole credentials
    from the system. You will need to login again to use
    the MCP server.
    
    Example:
    pihole-mcp-cli logout
    """
    cred_manager = CredentialManager(ctx.obj["config_dir"])
    
    if not cred_manager.has_credentials():
        console.print("[yellow]No credentials found to remove.[/yellow]")
        return
    
    if not Confirm.ask("[yellow]Remove stored Pi-hole credentials?[/yellow]"):
        console.print("[yellow]Operation cancelled.[/yellow]")
        return
    
    # Clear any cached session before deleting credentials
    try:
        config = cred_manager.get_pihole_config()
        client = PiHoleClient(config)
        client.logout()
        console.print("[green]✓ Session cache cleared[/green]")
    except Exception:
        # Ignore errors when clearing cache
        pass
    
    cred_manager.delete_credentials()
    console.print("[green]✓ Credentials removed successfully![/green]")


@cli.command()
@click.pass_context
@handle_errors
def info(ctx: click.Context) -> None:
    """Show configuration and system information.
    
    This command displays information about your current
    configuration, including storage locations and system details.
    
    Example:
    pihole-mcp-cli info
    """
    cred_manager = CredentialManager(ctx.obj["config_dir"])
    
    info_table = Table(title="System Information", show_header=True, header_style="bold cyan")
    info_table.add_column("Setting", style="cyan")
    info_table.add_column("Value", style="white")
    
    info_table.add_row("Config Directory", str(cred_manager.config_dir))
    info_table.add_row("Credentials File", str(cred_manager.config_file))
    info_table.add_row("Has Credentials", "Yes" if cred_manager.has_credentials() else "No")
    info_table.add_row("Keyring Service", cred_manager.keyring_service)
    
    console.print(info_table)
    
    if cred_manager.has_credentials():
        try:
            config = cred_manager.get_pihole_config()
            conn_table = Table(title="Connection Settings", show_header=True, header_style="bold cyan")
            conn_table.add_column("Setting", style="cyan")
            conn_table.add_column("Value", style="white")
            
            conn_table.add_row("Host", config.host)
            conn_table.add_row("Port", str(config.port))
            conn_table.add_row("HTTPS", "Yes" if config.use_https else "No")
            conn_table.add_row("SSL Verification", "Yes" if config.verify_ssl else "No")
            conn_table.add_row("Timeout", f"{config.timeout}s")
            conn_table.add_row("API Key", "***" + config.api_key[-4:] if config.api_key else "Not set")
            
            console.print(conn_table)
        except Exception as e:
            console.print(f"[red]Error reading configuration: {e}[/red]")


def main() -> None:
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main() 