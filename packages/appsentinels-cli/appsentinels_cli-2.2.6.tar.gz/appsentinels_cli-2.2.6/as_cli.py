#!/usr/bin/env python3
"""
AppSentinels CLI - A comprehensive CLI tool for AppSentinels API security management

Usage:
    python appsentinels-cli.py [command] [options]
    python appsentinels-cli.py --interactive
"""

import argparse
import asyncio
import sys
from typing import Dict, Any, List
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.cli_processor import CLIProcessor
from core.auth_context import AuthContext
from config import Config

class AppSentinelsCLI:
    """Main CLI application class"""
    
    def __init__(self):
        self.config = Config()
        self.auth_context = AuthContext()
        self.cli_processor = CLIProcessor(self.config, self.auth_context)
        
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser"""
        parser = argparse.ArgumentParser(
            description="AppSentinels CLI - API Security Management Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
    %(prog)s auth login                    # Authenticate with AppSentinels
    %(prog)s profile list                  # List available profiles
    %(prog)s profile create prod --description "Production"  # Create new profile
    %(prog)s profile switch prod           # Switch to production profile
    %(prog)s --profile prod profile current # Use specific profile
    %(prog)s plugin list                   # List available plugins
    %(prog)s init --show-only              # Preview configuration setup
    %(prog)s --interactive                 # Start interactive mode

Plugin Examples (after installing plugins):
    %(prog)s ingest config --show          # Show database configuration (ingest plugin)
    %(prog)s ingest records --file data.parquet  # Import data (ingest plugin)
    %(prog)s hello --name World            # Hello world (hello plugin)
            """
        )
        
        # Global options
        parser.add_argument(
            "--interactive", "-i",
            action="store_true",
            help="Start interactive mode"
        )
        
        parser.add_argument(
            "--config-file",
            help="Path to configuration file"
        )
        
        parser.add_argument(
            "--profile",
            help="Configuration profile to use"
        )
        
        parser.add_argument(
            "--output-format",
            choices=["table", "json", "yaml", "raw"],
            default="table",
            help="Output format (default: table)"
        )
        
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )
        
        parser.add_argument(
            "--version",
            action="version",
            version="AppSentinels CLI v1.0.0"
        )
        
        # Add subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Register command handlers
        self.cli_processor.register_handlers(subparsers)
        
        return parser
    
    async def run_command(self, args: argparse.Namespace) -> None:
        """Run a single command"""
        if not args.command:
            # No command specified, show help
            parser = self.create_parser()
            parser.print_help()
            return
            
        # Execute command
        result = await self.cli_processor.execute_command(args)
        
        # Format and display result
        self._display_result(result, args.output_format)
    
    def _display_result(self, result: Dict[str, Any], format: str) -> None:
        """Display command result in specified format"""
        if format == "json":
            print(json.dumps(result, indent=2))
        elif format == "yaml":
            try:
                import yaml
                print(yaml.dump(result, default_flow_style=False))
            except ImportError:
                print("YAML output requires PyYAML. Install with: pip install PyYAML")
                print(json.dumps(result, indent=2))
        elif format == "raw":
            if "message" in result:
                print(result["message"])
            elif "data" in result:
                print(result["data"])
            else:
                print(result)
        else:  # table format
            self._display_table(result)
    
    def _display_table(self, result: Dict[str, Any]) -> None:
        """Display result in table format"""
        if result.get("success", True):
            if "data" in result:
                data = result["data"]
                if isinstance(data, list) and data:
                    # Display as table
                    self._print_table(data)
                elif isinstance(data, dict):
                    # Display key-value pairs
                    for key, value in data.items():
                        print(f"{key}: {value}")
                else:
                    print(data)
            elif "message" in result:
                print(result["message"])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    def _print_table(self, data: List[Dict[str, Any]]) -> None:
        """Print data as a formatted table"""
        if not data:
            print("No data to display")
            return
            
        # Get all unique keys
        keys = set()
        for item in data:
            keys.update(item.keys())
        keys = sorted(keys)
        
        # Calculate column widths
        widths = {key: len(key) for key in keys}
        for item in data:
            for key in keys:
                value = str(item.get(key, ""))
                widths[key] = max(widths[key], len(value))
        
        # Print header
        header = " | ".join(key.ljust(widths[key]) for key in keys)
        print(header)
        print("-" * len(header))
        
        # Print data rows
        for item in data:
            row = " | ".join(str(item.get(key, "")).ljust(widths[key]) for key in keys)
            print(row)
    
    async def run_interactive_mode(self) -> None:
        """Run in interactive mode"""
        print("AppSentinels CLI - Interactive Mode")
        print("Type 'help' for available commands, 'exit' to quit")
        
        while True:
            try:
                command = input("as-cli> ").strip()
                if not command:
                    continue
                    
                if command.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break
                    
                if command.lower() == "help":
                    parser = self.create_parser()
                    parser.print_help()
                    continue
                
                # Parse and execute command
                try:
                    # Create a new parser instance for the interactive command
                    parser = self.create_parser()
                    # Remove the --interactive flag if present in the command
                    cmd_args = [arg for arg in command.split() if arg != "--interactive" and arg != "-i"]
                    args = parser.parse_args(cmd_args)
                    args.output_format = "table"  # Force table format in interactive mode
                    
                    result = await self.cli_processor.execute_command(args)
                    self._display_result(result, "table")
                except SystemExit:
                    # argparse calls sys.exit on error, catch it
                    pass
                except Exception as e:
                    print(f"Error: {e}")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    asyncio.run(main())

def main():
    """Entry point for the as-cli command"""
    return asyncio.run(async_main())

async def async_main():
    """Async main function"""
    cli = AppSentinelsCLI()
    parser = cli.create_parser()
    args = parser.parse_args()
    
    # Set up configuration
    if args.config_file:
        cli.config.load_config_file(args.config_file)
    
    # Switch to specified profile if provided
    if args.profile:
        success = cli.config.switch_profile(args.profile)
        if not success:
            print(f"Error: Profile '{args.profile}' not found")
            available_profiles = list(cli.config.list_profiles().keys())
            if available_profiles:
                print(f"Available profiles: {', '.join(available_profiles)}")
            return
        
        # Recreate CLI processor with new profile configuration
        cli.cli_processor = CLIProcessor(cli.config, cli.auth_context)
    
    # Run in appropriate mode
    if args.interactive:
        await cli.run_interactive_mode()
    else:
        await cli.run_command(args)