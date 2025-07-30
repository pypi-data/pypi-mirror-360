"""
Profile command handler for AppSentinels CLI

This module handles profile management commands including creating, switching,
listing, and managing multiple configuration profiles.
"""

import argparse
from typing import Dict, Any, List
from pathlib import Path

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
class ProfileHandler(SubcommandMixin, BaseCommandHandler):
    """Handler for profile management commands"""
    
    @property
    def command_name(self) -> str:
        return "profile"
    
    @property
    def command_description(self) -> str:
        return "Manage configuration profiles for different environments"
    
    def __init__(self, config, auth_context):
        super().__init__(config, auth_context)
        self.register_subcommand("list", self._handle_list)
        self.register_subcommand("current", self._handle_current)
        self.register_subcommand("switch", self._handle_switch)
        self.register_subcommand("create", self._handle_create)
        self.register_subcommand("delete", self._handle_delete)
        self.register_subcommand("show", self._handle_show)
        self.register_subcommand("copy", self._handle_copy)
    
    async def handle_command(self, args) -> Dict[str, Any]:
        """Handle profile commands - delegated to subcommand handlers"""
        return await self.route_subcommand(args)
    
    def add_subcommands(self, parser: argparse.ArgumentParser) -> None:
        """Add profile subcommands"""
        subparsers = parser.add_subparsers(dest="subcommand", help="Profile commands")
        
        # List command
        list_parser = subparsers.add_parser(
            "list",
            help="List all available profiles"
        )
        list_parser.add_argument(
            "--detailed",
            action="store_true",
            help="Show detailed profile information"
        )
        
        # Current command
        current_parser = subparsers.add_parser(
            "current",
            help="Show current active profile"
        )
        
        # Switch command
        switch_parser = subparsers.add_parser(
            "switch",
            help="Switch to a different profile"
        )
        switch_parser.add_argument(
            "profile_name",
            help="Name of the profile to switch to"
        )
        switch_parser.add_argument(
            "--save",
            action="store_true",
            help="Save the profile switch to config file"
        )
        
        # Create command
        create_parser = subparsers.add_parser(
            "create",
            help="Create a new profile"
        )
        create_parser.add_argument(
            "profile_name",
            help="Name of the new profile"
        )
        create_parser.add_argument(
            "--description",
            help="Description of the profile"
        )
        create_parser.add_argument(
            "--copy-from",
            help="Copy settings from existing profile"
        )
        create_parser.add_argument(
            "--save",
            action="store_true",
            help="Save the new profile to config file"
        )
        
        # Delete command
        delete_parser = subparsers.add_parser(
            "delete",
            help="Delete a profile"
        )
        delete_parser.add_argument(
            "profile_name",
            help="Name of the profile to delete"
        )
        delete_parser.add_argument(
            "--save",
            action="store_true",
            help="Save changes to config file"
        )
        
        # Show command
        show_parser = subparsers.add_parser(
            "show",
            help="Show detailed configuration for a profile"
        )
        show_parser.add_argument(
            "profile_name",
            nargs="?",
            help="Name of the profile to show (default: current profile)"
        )
        
        # Copy command
        copy_parser = subparsers.add_parser(
            "copy",
            help="Copy a profile to a new profile"
        )
        copy_parser.add_argument(
            "source_profile",
            help="Name of the source profile to copy from"
        )
        copy_parser.add_argument(
            "target_profile",
            help="Name of the new profile to create"
        )
        copy_parser.add_argument(
            "--description",
            help="Description for the new profile"
        )
        copy_parser.add_argument(
            "--save",
            action="store_true",
            help="Save the new profile to config file"
        )
    
    async def _handle_list(self, args) -> Dict[str, Any]:
        """Handle profile list command"""
        try:
            profiles = self.config.list_profiles()
            
            if not profiles:
                return self.format_success_response(
                    {"profiles": []},
                    "No profiles found"
                )
            
            # Format profile data
            profile_data = []
            for name, profile in profiles.items():
                is_current = "✓" if name == self.config.current_profile else ""
                
                if args.detailed:
                    profile_info = {
                        "Name": name,
                        "Current": is_current,
                        "Description": profile.description or "No description",
                        "API URL": profile.api.base_url,
                        "DB Host": profile.database.host,
                        "DB Port": profile.database.port,
                        "DB Name": profile.database.database
                    }
                else:
                    profile_info = {
                        "Name": name,
                        "Current": is_current,
                        "Description": profile.description or "No description"
                    }
                
                profile_data.append(profile_info)
            
            # Format as table
            table = tabulate(profile_data, headers="keys", tablefmt="grid")
            message = f"Available profiles:\n\n{table}"
            
            return self.format_success_response(
                {"profiles": profile_data},
                message
            )
            
        except Exception as e:
            return self.format_error_response(
                f"Failed to list profiles: {str(e)}"
            )
    
    async def _handle_current(self, args) -> Dict[str, Any]:
        """Handle profile current command"""
        try:
            current_profile = self.config.get_profile(self.config.current_profile)
            
            if not current_profile:
                return self.format_error_response(
                    f"Current profile '{self.config.current_profile}' not found"
                )
            
            profile_info = {
                "name": current_profile.name,
                "description": current_profile.description or "No description",
                "api_url": current_profile.api.base_url,
                "database_host": current_profile.database.host,
                "database_port": current_profile.database.port,
                "database_name": current_profile.database.database
            }
            
            message = f"Current profile: {current_profile.name}\nDescription: {current_profile.description or 'No description'}"
            
            return self.format_success_response(profile_info, message)
            
        except Exception as e:
            return self.format_error_response(
                f"Failed to get current profile: {str(e)}"
            )
    
    async def _handle_switch(self, args) -> Dict[str, Any]:
        """Handle profile switch command"""
        try:
            success = self.config.switch_profile(args.profile_name)
            
            if not success:
                return self.format_error_response(
                    f"Profile '{args.profile_name}' not found"
                )
            
            # Save to main config file if requested
            if args.save:
                self.config._save_main_config()
            
            return self.format_success_response(
                {"profile_name": args.profile_name},
                f"Switched to profile '{args.profile_name}'"
            )
            
        except Exception as e:
            return self.format_error_response(
                f"Failed to switch profile: {str(e)}"
            )
    
    async def _handle_create(self, args) -> Dict[str, Any]:
        """Handle profile create command"""
        try:
            # Check if profile already exists
            if self.config.get_profile(args.profile_name):
                return self.format_error_response(
                    f"Profile '{args.profile_name}' already exists"
                )
            
            # Create the profile
            new_profile = self.config.create_profile(
                name=args.profile_name,
                description=args.description or "",
                copy_from=args.copy_from
            )
            
            # Profile is automatically saved to its file, save main config if requested
            if args.save:
                self.config._save_main_config()
            
            message = f"Created profile '{args.profile_name}'"
            if args.copy_from:
                message += f" (copied from '{args.copy_from}')"
            
            return self.format_success_response(
                {"profile_name": args.profile_name, "created": True},
                message
            )
            
        except Exception as e:
            return self.format_error_response(
                f"Failed to create profile: {str(e)}"
            )
    
    async def _handle_delete(self, args) -> Dict[str, Any]:
        """Handle profile delete command"""
        try:
            success = self.config.delete_profile(args.profile_name)
            
            if not success:
                if args.profile_name == self.config.current_profile:
                    return self.format_error_response(
                        f"Cannot delete current profile '{args.profile_name}'. Switch to another profile first."
                    )
                elif args.profile_name == "default":
                    return self.format_error_response(
                        "Cannot delete the default profile"
                    )
                else:
                    return self.format_error_response(
                        f"Profile '{args.profile_name}' not found"
                    )
            
            # Profile file is automatically deleted, save main config if requested
            if args.save:
                self.config._save_main_config()
            
            return self.format_success_response(
                {"profile_name": args.profile_name, "deleted": True},
                f"Deleted profile '{args.profile_name}'"
            )
            
        except Exception as e:
            return self.format_error_response(
                f"Failed to delete profile: {str(e)}"
            )
    
    async def _handle_show(self, args) -> Dict[str, Any]:
        """Handle profile show command"""
        try:
            profile_name = args.profile_name or self.config.current_profile
            profile = self.config.get_profile(profile_name)
            
            if not profile:
                return self.format_error_response(
                    f"Profile '{profile_name}' not found"
                )
            
            # Create detailed configuration display
            config_data = [
                ["Profile Name", profile.name],
                ["Description", profile.description or "No description"],
                ["", ""],  # Empty row for separation
                ["API Settings", ""],
                ["  Base URL", profile.api.base_url],
                ["  Timeout", f"{profile.api.timeout}s"],
                ["  Max Retries", str(profile.api.max_retries)],
                ["", ""],
                ["Database Settings", ""],
                ["  Type", profile.database.db_type],
                ["  Host", profile.database.host],
                ["  Port", str(profile.database.port)],
                ["  Database", profile.database.database],
                ["  User", profile.database.user],
                ["  Use Docker", "Yes" if profile.database.use_docker else "No"],
                ["", ""],
                ["Output Settings", ""],
                ["  Default Format", profile.output.default_format],
                ["  Max Width", str(profile.output.max_width)],
                ["  Color Output", "Yes" if profile.output.color_output else "No"],
                ["", ""],
                ["Ingest Settings", ""],
                ["  Batch Size", str(profile.ingest.default_batch_size)],
                ["  Log File", profile.ingest.log_file],
                ["  Telemetry", "Enabled" if profile.ingest.enable_telemetry else "Disabled"]
            ]
            
            table = tabulate(config_data, tablefmt="grid")
            message = f"Configuration for profile '{profile_name}':\n\n{table}"
            
            return self.format_success_response(
                {"profile": profile.to_dict()},
                message
            )
            
        except Exception as e:
            return self.format_error_response(
                f"Failed to show profile: {str(e)}"
            )
    
    async def _handle_copy(self, args) -> Dict[str, Any]:
        """Handle profile copy command"""
        try:
            # Check if source profile exists
            if not self.config.get_profile(args.source_profile):
                return self.format_error_response(
                    f"Source profile '{args.source_profile}' not found"
                )
            
            # Check if target profile already exists
            if self.config.get_profile(args.target_profile):
                return self.format_error_response(
                    f"Target profile '{args.target_profile}' already exists"
                )
            
            # Create the copy
            new_profile = self.config.create_profile(
                name=args.target_profile,
                description=args.description or f"Copy of {args.source_profile}",
                copy_from=args.source_profile
            )
            
            # Profile is automatically saved to its file, save main config if requested
            if args.save:
                self.config._save_main_config()
            
            return self.format_success_response(
                {
                    "source_profile": args.source_profile,
                    "target_profile": args.target_profile,
                    "copied": True
                },
                f"Copied profile '{args.source_profile}' to '{args.target_profile}'"
            )
            
        except Exception as e:
            return self.format_error_response(
                f"Failed to copy profile: {str(e)}"
            )
    
    def _save_config(self) -> None:
        """Save current configuration to file (deprecated - profiles auto-save)"""
        try:
            # Save main config file only
            self.config._save_main_config()
            
        except Exception as e:
            # Don't fail the operation if save fails, just warn
            print(f"Warning: Failed to save config file: {e}")