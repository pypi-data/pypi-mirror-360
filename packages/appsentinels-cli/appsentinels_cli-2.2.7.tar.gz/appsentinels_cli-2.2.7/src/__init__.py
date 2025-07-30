"""
AppSentinels CLI - API Security Management Tool

This package provides a comprehensive CLI for managing AppSentinels API security.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List
import json

__version__ = "2.2.0"
__author__ = "AppSentinels"
__email__ = "support@appsentinels.com"

__all__ = ["__version__", "__author__", "__email__", "main"]


def main():
    """Main entry point for the AppSentinels CLI"""
    # Import here to avoid circular imports
    from .core.cli_processor import CLIProcessor
    
    async def async_main():
        parser = argparse.ArgumentParser(
            description="AppSentinels CLI - A modular API security management tool with plugin architecture",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  as-cli auth login                    # OAuth authentication
  as-cli profile list                  # List available profiles
  as-cli profile create prod          # Create production profile
  as-cli plugin list                  # List available plugins
  as-cli --interactive                # Interactive mode

For more information, visit: https://docs.appsentinels.com/cli
            """
        )
        
        # Global options
        parser.add_argument("--profile", help="Use specific profile")
        parser.add_argument("--output-format", choices=["table", "json", "yaml"], 
                          default="table", help="Output format")
        parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
        parser.add_argument("--debug", action="store_true", help="Debug mode")
        parser.add_argument("--version", action="version", version=f"AppSentinels CLI {__version__}")
        parser.add_argument("--interactive", "-i", action="store_true", 
                          help="Start interactive mode")

        # Initialize configuration and auth context
        from .config import Config
        from .core.auth_context import AuthContext
        
        config = Config()
        auth_context = AuthContext()
        
        # Initialize CLI processor
        cli = CLIProcessor(config, auth_context)
        
        # Add subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        cli.add_subcommands(subparsers)
        
        # Parse arguments
        args = parser.parse_args()
        
        # If no command provided, show help
        if not args.command and not args.interactive:
            parser.print_help()
            return
        
        # Run command
        if args.interactive:
            await cli.run_interactive_mode()
        else:
            await cli.run_command(args)
    
    # Run the async main function
    asyncio.run(async_main())