"""
Plugin Interface for AppSentinels CLI

This module defines the base plugin interface that all CLI plugins must implement.
Plugins use this interface to register command handlers and provide metadata.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass, field

from .base_handler import BaseCommandHandler


@dataclass
class PluginMetadata:
    """Metadata information for a plugin"""
    name: str
    version: str
    description: str
    author: str = ""
    homepage: str = ""
    license: str = ""
    requires_core_version: str = ">=1.0.0"
    requires_plugins: List[str] = field(default_factory=list)
    provides_commands: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "homepage": self.homepage,
            "license": self.license,
            "requires_core_version": self.requires_core_version,
            "requires_plugins": self.requires_plugins,
            "provides_commands": self.provides_commands
        }


class BasePlugin(ABC):
    """Base class that all CLI plugins must inherit from"""
    
    def __init__(self):
        self._config = None
        self._auth_context = None
        self._loaded = False
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass
    
    @abstractmethod
    def get_command_handlers(self) -> Dict[str, BaseCommandHandler]:
        """Return command handlers provided by this plugin
        
        Returns:
            Dict mapping command names to handler classes (not instances)
        """
        pass
    
    def on_load(self, config, auth_context) -> None:
        """Called when plugin is loaded
        
        Args:
            config: CLI configuration object
            auth_context: Authentication context
        """
        self._config = config
        self._auth_context = auth_context
        self._loaded = True
    
    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        self._loaded = False
        self._config = None
        self._auth_context = None
    
    def check_compatibility(self, core_version: str) -> bool:
        """Check if plugin is compatible with core version
        
        Args:
            core_version: Version string of the core CLI
            
        Returns:
            True if compatible, False otherwise
        """
        # Basic version compatibility check
        # In a real implementation, this would use proper version parsing
        required = self.metadata.requires_core_version
        if required.startswith(">="):
            return True  # Simplified for MVP
        return True
    
    @property
    def is_loaded(self) -> bool:
        """Check if plugin is currently loaded"""
        return self._loaded
    
    @property
    def config(self):
        """Access to CLI configuration (only available after on_load)"""
        return self._config
    
    @property
    def auth_context(self):
        """Access to authentication context (only available after on_load)"""
        return self._auth_context


class PluginValidationResult:
    """Result of plugin validation"""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add validation warning"""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }


class PluginValidator:
    """Validates plugin implementations"""
    
    @staticmethod
    def validate_plugin(plugin_class) -> PluginValidationResult:
        """Validate a plugin class
        
        Args:
            plugin_class: Plugin class to validate
            
        Returns:
            PluginValidationResult with validation results
        """
        result = PluginValidationResult(True)
        
        # Check if it's a subclass of BasePlugin
        if not issubclass(plugin_class, BasePlugin):
            result.add_error("Plugin must inherit from BasePlugin")
            return result
        
        try:
            # Try to instantiate
            plugin = plugin_class()
            
            # Check metadata property
            try:
                metadata = plugin.metadata
                if not isinstance(metadata, PluginMetadata):
                    result.add_error("metadata property must return PluginMetadata instance")
            except Exception as e:
                result.add_error(f"Failed to get plugin metadata: {e}")
            
            # Check get_command_handlers method
            try:
                handlers = plugin.get_command_handlers()
                if not isinstance(handlers, dict):
                    result.add_error("get_command_handlers must return a dictionary")
                else:
                    for name, handler_class in handlers.items():
                        if not issubclass(handler_class, BaseCommandHandler):
                            result.add_error(f"Handler '{name}' must be a BaseCommandHandler subclass")
            except Exception as e:
                result.add_error(f"Failed to get command handlers: {e}")
                
        except Exception as e:
            result.add_error(f"Failed to instantiate plugin: {e}")
        
        return result