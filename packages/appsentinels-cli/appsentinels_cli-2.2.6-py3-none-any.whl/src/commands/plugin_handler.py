"""
Plugin command handler for AppSentinels CLI

This module handles plugin management commands including listing, loading,
and getting information about installed plugins.
"""

import argparse
from typing import Dict, Any, List

from core.base_handler import BaseCommandHandler, SubcommandMixin
from core.cli_processor import register_command

# Try to import tabulate, fall back to simple formatting
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False
    
    def tabulate(data, headers="keys", tablefmt="grid"):
        """Simple fallback for tabulate"""
        if not data:
            return "No data"
        
        if headers == "keys" and data:
            headers = list(data[0].keys())
        
        # Simple table formatting
        lines = []
        if headers:
            lines.append(" | ".join(str(h) for h in headers))
            lines.append("-" * len(lines[0]))
        
        for row in data:
            if isinstance(row, dict):
                line = " | ".join(str(row.get(h, "")) for h in headers)
            else:
                line = " | ".join(str(cell) for cell in row)
            lines.append(line)
        
        return "\n".join(lines)


@register_command
class PluginHandler(SubcommandMixin, BaseCommandHandler):
    """Handler for plugin management commands"""
    
    @property
    def command_name(self) -> str:
        return "plugin"
    
    @property
    def command_description(self) -> str:
        return "Manage CLI plugins"
    
    def __init__(self, config, auth_context):
        super().__init__(config, auth_context)
        self.register_subcommand("list", self._handle_list)
        self.register_subcommand("info", self._handle_info)
        self.register_subcommand("load", self._handle_load)
        self.register_subcommand("unload", self._handle_unload)
    
    async def handle_command(self, args) -> Dict[str, Any]:
        """Handle plugin commands - delegated to subcommand handlers"""
        return await self.route_subcommand(args)
    
    def add_subcommands(self, parser: argparse.ArgumentParser) -> None:
        """Add plugin subcommands"""
        subparsers = parser.add_subparsers(dest="subcommand", help="Plugin commands")
        
        # List command
        list_parser = subparsers.add_parser(
            "list",
            help="List available plugins"
        )
        list_parser.add_argument(
            "--installed-only",
            action="store_true",
            help="Show only installed plugins"
        )
        list_parser.add_argument(
            "--loaded-only",
            action="store_true",
            help="Show only loaded plugins"
        )
        
        # Info command
        info_parser = subparsers.add_parser(
            "info",
            help="Show detailed information about a plugin"
        )
        info_parser.add_argument(
            "plugin_name",
            help="Name of the plugin"
        )
        
        # Load command
        load_parser = subparsers.add_parser(
            "load",
            help="Load a specific plugin"
        )
        load_parser.add_argument(
            "plugin_name",
            help="Name of the plugin to load"
        )
        
        # Unload command
        unload_parser = subparsers.add_parser(
            "unload", 
            help="Unload a specific plugin"
        )
        unload_parser.add_argument(
            "plugin_name",
            help="Name of the plugin to unload"
        )
    
    async def _handle_list(self, args) -> Dict[str, Any]:
        """Handle plugin list command"""
        try:
            # Get CLI processor's plugin manager
            from core.cli_processor import CLIProcessor
            # Access through the main CLI processor instance
            # For now, we'll create a new plugin manager instance
            from core.plugin_manager import PluginManager
            plugin_manager = PluginManager(self.config, self.auth_context)
            plugin_manager.discover_plugins()
            
            plugins = plugin_manager.list_plugins()
            
            if not plugins:
                return self.format_success_response(
                    {"plugins": []},
                    "No plugins found"
                )
            
            # Filter plugins based on options
            if args.loaded_only:
                plugins = [p for p in plugins if p.is_loaded]
            elif args.installed_only:
                # All discovered plugins are "installed"
                pass
            
            # Format plugin data
            plugin_data = []
            for plugin in plugins:
                plugin_data.append({
                    "Name": plugin.name,
                    "Version": plugin.version,
                    "Description": plugin.description,
                    "Author": plugin.metadata.author or "Unknown",
                    "Commands": ", ".join(plugin.metadata.provides_commands),
                    "Status": "Loaded" if plugin.is_loaded else "Available"
                })
            
            # Format as table
            if plugin_data:
                table = tabulate(plugin_data, headers="keys", tablefmt="grid")
                message = f"Found {len(plugin_data)} plugin(s):\n\n{table}"
            else:
                message = "No plugins match the specified criteria"
            
            return self.format_success_response(
                {"plugins": plugin_data},
                message
            )
            
        except Exception as e:
            return self.format_error_response(
                f"Failed to list plugins: {str(e)}"
            )
    
    async def _handle_info(self, args) -> Dict[str, Any]:
        """Handle plugin info command"""
        try:
            from core.plugin_manager import PluginManager
            plugin_manager = PluginManager(self.config, self.auth_context)
            plugin_manager.discover_plugins()
            
            plugin_info = plugin_manager.get_plugin_info(args.plugin_name)
            
            if not plugin_info:
                return self.format_error_response(
                    f"Plugin '{args.plugin_name}' not found"
                )
            
            # Create detailed info
            info_data = {
                "Name": plugin_info.name,
                "Version": plugin_info.version,
                "Description": plugin_info.description,
                "Author": plugin_info.metadata.author or "Unknown",
                "Homepage": plugin_info.metadata.homepage or "Not specified",
                "License": plugin_info.metadata.license or "Not specified",
                "Module": plugin_info.module_name,
                "Core Version Required": plugin_info.metadata.requires_core_version,
                "Required Plugins": ", ".join(plugin_info.metadata.requires_plugins) or "None",
                "Provided Commands": ", ".join(plugin_info.metadata.provides_commands) or "None",
                "Status": "Loaded" if plugin_info.is_loaded else "Available"
            }
            
            # Format as table
            table_data = [[key, value] for key, value in info_data.items()]
            table = tabulate(table_data, tablefmt="grid")
            
            return self.format_success_response(
                {"plugin_info": info_data},
                f"Plugin Information:\n\n{table}"
            )
            
        except Exception as e:
            return self.format_error_response(
                f"Failed to get plugin info: {str(e)}"
            )
    
    async def _handle_load(self, args) -> Dict[str, Any]:
        """Handle plugin load command"""
        try:
            from core.plugin_manager import PluginManager
            plugin_manager = PluginManager(self.config, self.auth_context)
            plugin_manager.discover_plugins()
            
            if plugin_manager.is_plugin_loaded(args.plugin_name):
                return self.format_success_response(
                    {"plugin_name": args.plugin_name},
                    f"Plugin '{args.plugin_name}' is already loaded"
                )
            
            handlers = plugin_manager.load_plugin(args.plugin_name)
            
            if handlers:
                commands = list(handlers.keys())
                return self.format_success_response(
                    {
                        "plugin_name": args.plugin_name,
                        "loaded_commands": commands
                    },
                    f"Successfully loaded plugin '{args.plugin_name}' with commands: {', '.join(commands)}"
                )
            else:
                return self.format_error_response(
                    f"Failed to load plugin '{args.plugin_name}'"
                )
                
        except Exception as e:
            return self.format_error_response(
                f"Failed to load plugin: {str(e)}"
            )
    
    async def _handle_unload(self, args) -> Dict[str, Any]:
        """Handle plugin unload command"""
        try:
            from core.plugin_manager import PluginManager
            plugin_manager = PluginManager(self.config, self.auth_context)
            plugin_manager.discover_plugins()
            
            if not plugin_manager.is_plugin_loaded(args.plugin_name):
                return self.format_error_response(
                    f"Plugin '{args.plugin_name}' is not currently loaded"
                )
            
            success = plugin_manager.unload_plugin(args.plugin_name)
            
            if success:
                return self.format_success_response(
                    {"plugin_name": args.plugin_name},
                    f"Successfully unloaded plugin '{args.plugin_name}'"
                )
            else:
                return self.format_error_response(
                    f"Failed to unload plugin '{args.plugin_name}'"
                )
                
        except Exception as e:
            return self.format_error_response(
                f"Failed to unload plugin: {str(e)}"
            )