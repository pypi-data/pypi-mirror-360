"""
Initialization command handler for AppSentinels CLI

This module provides the init command to manually initialize or re-initialize
the CLI configuration directory structure.
"""

import argparse
from typing import Dict, Any
from pathlib import Path

from core.base_handler import BaseCommandHandler
from core.cli_processor import register_command


@register_command
class InitHandler(BaseCommandHandler):
    """Handler for initialization commands"""
    
    @property
    def command_name(self) -> str:
        return "init"
    
    @property
    def command_description(self) -> str:
        return "Initialize or re-initialize AppSentinels CLI configuration"
    
    def add_subcommands(self, parser: argparse.ArgumentParser) -> None:
        """Add init command arguments"""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force re-initialization, overwriting existing files"
        )
        parser.add_argument(
            "--show-only",
            action="store_true",
            help="Show what would be created without creating files"
        )
    
    async def handle_command(self, args) -> Dict[str, Any]:
        """Handle init command"""
        try:
            config_dir = Path.home() / ".as-cli"
            profiles_dir = config_dir / "profiles"
            
            if args.show_only:
                return self._show_initialization_plan(config_dir, profiles_dir)
            
            # Check if already initialized
            if config_dir.exists() and not args.force:
                existing_files = []
                if (config_dir / "config.yaml").exists():
                    existing_files.append("config.yaml")
                if (config_dir / ".env.template").exists():
                    existing_files.append(".env.template")
                if (config_dir / "README.md").exists():
                    existing_files.append("README.md")
                if profiles_dir.exists() and list(profiles_dir.glob("*.yaml")):
                    existing_files.append("profiles/")
                
                if existing_files:
                    return self.format_error_response(
                        f"AppSentinels CLI already initialized in {config_dir}\\n"
                        f"Existing files: {', '.join(existing_files)}\\n"
                        f"Use --force to re-initialize or --show-only to see what would be created."
                    )
            
            # Perform initialization
            result = self._perform_initialization(config_dir, profiles_dir, args.force)
            
            return self.format_success_response(
                {
                    "config_directory": str(config_dir),
                    "files_created": result["files_created"],
                    "profiles_created": result["profiles_created"]
                },
                f"AppSentinels CLI initialized successfully in {config_dir}"
            )
            
        except Exception as e:
            return self.format_error_response(
                f"Failed to initialize AppSentinels CLI: {str(e)}"
            )
    
    def _show_initialization_plan(self, config_dir: Path, profiles_dir: Path) -> Dict[str, Any]:
        """Show what would be created during initialization"""
        files_to_create = []
        files_to_update = []
        
        # Check main config file
        config_file = config_dir / "config.yaml"
        if config_file.exists():
            files_to_update.append(str(config_file))
        else:
            files_to_create.append(str(config_file))
        
        # Check .env template
        env_template = config_dir / ".env.template"
        if env_template.exists():
            files_to_update.append(str(env_template))
        else:
            files_to_create.append(str(env_template))
        
        # Check README
        readme_file = config_dir / "README.md"
        if readme_file.exists():
            files_to_update.append(str(readme_file))
        else:
            files_to_create.append(str(readme_file))
        
        # Check profiles directory
        if not profiles_dir.exists():
            files_to_create.append(f"{profiles_dir}/")
        
        # Check default profile
        default_profile = profiles_dir / "default.yaml"
        if default_profile.exists():
            files_to_update.append(str(default_profile))
        else:
            files_to_create.append(str(default_profile))
        
        message_parts = []
        if files_to_create:
            message_parts.append(f"Files to create:\\n  " + "\\n  ".join(files_to_create))
        if files_to_update:
            message_parts.append(f"Files to update:\\n  " + "\\n  ".join(files_to_update))
        
        message = "\\n\\n".join(message_parts) if message_parts else "No files need to be created or updated."
        message += f"\\n\\nConfiguration directory: {config_dir}"
        
        return self.format_success_response(
            {
                "config_directory": str(config_dir),
                "files_to_create": files_to_create,
                "files_to_update": files_to_update
            },
            message
        )
    
    def _perform_initialization(self, config_dir: Path, profiles_dir: Path, force: bool) -> Dict[str, Any]:
        """Perform the actual initialization"""
        from config import Config
        
        files_created = []
        profiles_created = []
        
        # Create a temporary config instance to trigger initialization
        # This will call _initialize_as_cli_setup()
        config = Config()
        
        # Track what was created
        if (config_dir / "config.yaml").exists():
            files_created.append("config.yaml")
        if (config_dir / ".env.template").exists():
            files_created.append(".env.template")
        if (config_dir / "README.md").exists():
            files_created.append("README.md")
        
        # Check profiles
        if profiles_dir.exists():
            for profile_file in profiles_dir.glob("*.yaml"):
                profiles_created.append(profile_file.stem)
        
        return {
            "files_created": files_created,
            "profiles_created": profiles_created
        }