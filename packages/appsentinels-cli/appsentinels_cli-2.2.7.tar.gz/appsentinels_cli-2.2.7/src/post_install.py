#!/usr/bin/env python3
"""
Post-installation script for AppSentinels CLI

This script is run after pip install to initialize the user's configuration
directory and set up the default profile structure.
"""

import sys
import os
from pathlib import Path

def post_install():
    """Initialize AppSentinels CLI configuration after installation"""
    try:
        # Add the src directory to the path so we can import config
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        from config import Config
        
        print("Setting up AppSentinels CLI...")
        
        # Initialize configuration (this will create the directory structure)
        config = Config()
        
        print("AppSentinels CLI setup complete!")
        print(f"Configuration directory: {config.config_dir}")
        print("\nNext steps:")
        print("1. Run 'as-cli profile list' to see available profiles")
        print("2. Configure your settings in ~/.as-cli/.env (copy from .env.template)")
        print("3. Run 'as-cli auth login' to authenticate")
        print("4. Use 'as-cli --help' to explore available commands")
        
    except Exception as e:
        print(f"Warning: Failed to initialize AppSentinels CLI configuration: {e}")
        print("You can manually initialize by running any as-cli command.")

if __name__ == "__main__":
    post_install()