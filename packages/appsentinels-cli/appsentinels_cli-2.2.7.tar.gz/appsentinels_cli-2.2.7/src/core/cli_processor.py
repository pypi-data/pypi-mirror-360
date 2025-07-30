"""
CLI Processor for AppSentinels CLI

This module handles command parsing, routing, and execution.
It manages the registration of command handlers and provides the main interface
for command execution.
"""

import argparse
import asyncio
import importlib
import inspect
from typing import Dict, Any, List, Optional, Type
from pathlib import Path

from .base_handler import BaseCommandHandler
from .plugin_manager import PluginManager

class CLIProcessor:
    """Main CLI processor that handles command parsing and execution"""
    
    def __init__(self, config, auth_context):
        """Initialize the CLI processor
        
        Args:
            config: Configuration object
            auth_context: Authentication context
        """
        self.config = config
        self.auth_context = auth_context
        self.handlers: Dict[str, BaseCommandHandler] = {}
        self.plugin_manager = PluginManager(config, auth_context)
        self._load_handlers()
        self._load_plugins()
    
    def _load_handlers(self) -> None:
        """Dynamically load all command handlers from the commands directory"""
        commands_dir = Path(__file__).parent.parent / "commands"
        
        if not commands_dir.exists():
            return
        
        # Import all handler modules
        for handler_file in commands_dir.glob("*_handler.py"):
            if handler_file.name.startswith("__"):
                continue
                
            module_name = f"commands.{handler_file.stem}"
            try:
                module = importlib.import_module(module_name)
                
                # Find handler classes in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseCommandHandler) and 
                        obj != BaseCommandHandler):
                        
                        # Instantiate the handler
                        handler = obj(self.config, self.auth_context)
                        self.handlers[handler.command_name] = handler
                        
            except ImportError as e:
                print(f"Warning: Could not import {module_name}: {e}")
    
    def _load_plugins(self) -> None:
        """Discover and load plugins"""
        try:
            # Discover available plugins
            self.plugin_manager.discover_plugins()
            
            # Load all discovered plugins
            plugin_handlers = self.plugin_manager.load_all_plugins()
            
            # Register plugin handlers
            for command_name, handler in plugin_handlers.items():
                if command_name not in self.handlers:  # Don't override built-in commands
                    self.handlers[command_name] = handler
                else:
                    print(f"Warning: Plugin command '{command_name}' conflicts with built-in command")
                    
        except Exception as e:
            print(f"Warning: Plugin loading failed: {e}")
    
    def register_handlers(self, subparsers) -> None:
        """Register all command handlers with the argument parser
        
        Args:
            subparsers: The subparsers object to register commands with
        """
        for handler in self.handlers.values():
            # Create a subparser for this command
            cmd_parser = subparsers.add_parser(
                handler.command_name,
                help=handler.command_description,
                description=handler.command_description
            )
            
            # Let the handler add its subcommands
            handler.add_subcommands(cmd_parser)
    
    async def execute_command(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Execute a command based on parsed arguments
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Dictionary containing command result
        """
        command = args.command
        
        if not command:
            return {
                "success": False,
                "error": "No command specified"
            }
        
        if command not in self.handlers:
            return {
                "success": False,
                "error": f"Unknown command: {command}",
                "available_commands": list(self.handlers.keys())
            }
        
        handler = self.handlers[command]
        
        try:
            # Set CLI mode flag
            args._cli_mode = True
            
            # Execute the command
            result = await handler.handle_command(args)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Command execution failed: {str(e)}",
                "command": command
            }
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands
        
        Returns:
            List of command names
        """
        return list(self.handlers.keys())
    
    def get_command_help(self, command: str) -> Optional[str]:
        """Get help text for a specific command
        
        Args:
            command: Command name
            
        Returns:
            Help text or None if command not found
        """
        if command in self.handlers:
            return self.handlers[command].command_description
        return None

class CommandRegistry:
    """Registry for managing command handlers"""
    
    def __init__(self):
        self._handlers: Dict[str, Type[BaseCommandHandler]] = {}
    
    def register(self, handler_class: Type[BaseCommandHandler]) -> None:
        """Register a command handler class
        
        Args:
            handler_class: The handler class to register
        """
        # Create a temporary instance to get the command name
        temp_instance = handler_class(None, None)
        command_name = temp_instance.command_name
        self._handlers[command_name] = handler_class
    
    def get_handler_class(self, command: str) -> Optional[Type[BaseCommandHandler]]:
        """Get a handler class by command name
        
        Args:
            command: Command name
            
        Returns:
            Handler class or None if not found
        """
        return self._handlers.get(command)
    
    def get_all_handlers(self) -> Dict[str, Type[BaseCommandHandler]]:
        """Get all registered handler classes
        
        Returns:
            Dictionary mapping command names to handler classes
        """
        return self._handlers.copy()

# Global command registry
command_registry = CommandRegistry()

def register_command(handler_class: Type[BaseCommandHandler]) -> Type[BaseCommandHandler]:
    """Decorator to register a command handler
    
    Args:
        handler_class: The handler class to register
        
    Returns:
        The same handler class (for use as decorator)
    """
    command_registry.register(handler_class)
    return handler_class