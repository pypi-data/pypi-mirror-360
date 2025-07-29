"""
Base command handler class for AppSentinels CLI

This module provides the abstract base class that all command handlers must inherit from.
It defines the interface for command registration, argument parsing, and execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import argparse
import asyncio

class BaseCommandHandler(ABC):
    """Abstract base class for all command handlers"""
    
    def __init__(self, config, auth_context):
        """Initialize the command handler
        
        Args:
            config: Configuration object
            auth_context: Authentication context
        """
        self.config = config
        self.auth_context = auth_context
    
    @property
    @abstractmethod
    def command_name(self) -> str:
        """Return the command name (e.g., 'api', 'auth', 'ingest')"""
        pass
    
    @property
    @abstractmethod
    def command_description(self) -> str:
        """Return the command description for help text"""
        pass
    
    @abstractmethod
    def add_subcommands(self, subparsers) -> None:
        """Add subcommands to the parser
        
        Args:
            subparsers: The subparsers object to add commands to
        """
        pass
    
    @abstractmethod
    async def handle_command(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Handle the command execution
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Dict containing the command result
        """
        pass
    
    def format_success_response(self, data: Any, message: str = None) -> Dict[str, Any]:
        """Format a successful response
        
        Args:
            data: The response data
            message: Optional success message
            
        Returns:
            Formatted response dictionary
        """
        response = {
            "success": True,
            "data": data
        }
        if message:
            response["message"] = message
        return response
    
    def format_error_response(self, error: str, details: Any = None) -> Dict[str, Any]:
        """Format an error response
        
        Args:
            error: Error message
            details: Optional error details
            
        Returns:
            Formatted error response dictionary
        """
        response = {
            "success": False,
            "error": error
        }
        if details:
            response["details"] = details
        return response
    
    def require_auth(self) -> bool:
        """Check if authentication is required and available
        
        Returns:
            True if authenticated, False otherwise
        """
        if not self.auth_context.is_authenticated():
            return False
        return True
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests
        
        Returns:
            Dictionary of headers including authorization
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AppSentinels-CLI/1.0.0"
        }
        
        if self.auth_context.is_authenticated():
            token = self.auth_context.get_token()
            headers["Authorization"] = f"Bearer {token}"
        
        return headers

class SubcommandMixin:
    """Mixin class for handlers that support subcommands"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subcommand_handlers = {}
    
    def register_subcommand(self, name: str, handler_func):
        """Register a subcommand handler
        
        Args:
            name: Subcommand name
            handler_func: Function to handle the subcommand
        """
        self.subcommand_handlers[name] = handler_func
    
    async def route_subcommand(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Route to the appropriate subcommand handler
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Command result
        """
        subcommand = getattr(args, 'subcommand', None)
        if not subcommand:
            return self.format_error_response("No subcommand specified")
        
        if subcommand not in self.subcommand_handlers:
            return self.format_error_response(f"Unknown subcommand: {subcommand}")
        
        handler = self.subcommand_handlers[subcommand]
        return await handler(args)

class AsyncCommandHandler(BaseCommandHandler):
    """Base class for async command handlers"""
    
    async def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for the request
            
        Returns:
            Response data
        """
        import httpx
        
        # Prepare headers
        headers = self.get_auth_headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        # Add timeout if not specified
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30.0
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                
                # Try to parse JSON response
                try:
                    return response.json()
                except ValueError:
                    return {"content": response.text}
                    
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
            try:
                error_detail = e.response.json()
                return self.format_error_response(error_msg, error_detail)
            except ValueError:
                return self.format_error_response(error_msg, e.response.text)
                
        except httpx.RequestError as e:
            return self.format_error_response(f"Request failed: {str(e)}")
        except Exception as e:
            return self.format_error_response(f"Unexpected error: {str(e)}")

class CLIOnlyMixin:
    """Mixin for commands that only work in CLI mode"""
    
    def check_cli_mode(self, args: argparse.Namespace) -> bool:
        """Check if running in CLI mode
        
        Args:
            args: Parsed arguments
            
        Returns:
            True if in CLI mode, False otherwise
        """
        # This would be set by the main CLI processor
        return getattr(args, '_cli_mode', True)
    
    def require_cli_mode(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Require CLI mode for this command
        
        Args:
            args: Parsed arguments
            
        Returns:
            Error response if not in CLI mode, None otherwise
        """
        if not self.check_cli_mode(args):
            return self.format_error_response(
                "This command is only available in CLI mode"
            )
        return None