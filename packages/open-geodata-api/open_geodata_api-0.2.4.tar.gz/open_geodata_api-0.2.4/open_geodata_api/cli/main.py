"""
Main CLI entry point for open-geodata-api with comprehensive help
"""
import click
import json
from pathlib import Path

# Import CLI command modules
from .collections import collections_group
from .search import search_group  
from .items import items_group
from .download import download_group
from .utils import utils_group


@click.group()
@click.version_option(
    version=None,
    prog_name="open-geodata-api",
    message="%(prog)s %(version)s - Unified CLI for geospatial data access"
)
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose output for debugging')
@click.pass_context
def cli(ctx, verbose):
    """
    🛰️ Open Geodata API - Unified CLI for geospatial data access
    
    Access Microsoft Planetary Computer and AWS EarthSearch APIs from the command line.
    Supports data discovery, filtering, and intelligent downloading.
    
    \b
    Examples:
      ogapi info                                    # Show package info
      ogapi collections list --provider pc         # List PC collections
      ogapi search quick sentinel-2-l2a bbox       # Quick search
      ogapi download url https://example.com/file  # Download single file
    
    \b
    Use 'ogapi COMMAND --help' for detailed help on any command.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if verbose:
        click.echo("🚀 Open Geodata API CLI - Verbose mode enabled")


@cli.command()
def info():
    """
    Show package information and capabilities.
    
    Displays:
    - Package version and author
    - Supported APIs (Planetary Computer, EarthSearch)
    - Available capabilities and dependencies
    - Installation status
    """
    try:
        import open_geodata_api as ogapi
        ogapi.info()
    except ImportError:
        click.echo("❌ Error: open-geodata-api package not properly installed")
        click.echo("💡 Try: pip install open-geodata-api")


# Add command groups with enhanced help
cli.add_command(collections_group, name='collections')
cli.add_command(search_group, name='search')
cli.add_command(items_group, name='items') 
cli.add_command(download_group, name='download')
cli.add_command(utils_group, name='utils')


# Add global help aliases
@cli.command(name='help', hidden=True)
@click.argument('command_name', required=False)
@click.pass_context
def help_command(ctx, command_name):
    """Show help for a specific command."""
    if command_name:
        cmd = cli.get_command(ctx, command_name)
        if cmd:
            click.echo(cmd.get_help(ctx))
        else:
            click.echo(f"No such command: {command_name}")
    else:
        click.echo(cli.get_help(ctx))


if __name__ == '__main__':
    cli()
