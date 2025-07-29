"""
Plugin Manager for AppSentinels CLI

This module handles dynamic loading and management of CLI plugins installed via pip.
Plugins are discovered through Python entry points and loaded at runtime.
"""

import importlib
import logging
import pkg_resources
from typing import Dict, List, Type, Optional, Any
from dataclasses import dataclass

from .base_handler import BaseCommandHandler
from .plugin_interface import BasePlugin, PluginMetadata, PluginValidator

@dataclass
class PluginInfo:
    """Information about a loaded plugin"""
    name: str
    version: str
    description: str
    plugin_instance: BasePlugin
    metadata: PluginMetadata
    module_name: str
    is_loaded: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "module_name": self.module_name,
            "author": self.metadata.author,
            "homepage": self.metadata.homepage,
            "license": self.metadata.license,
            "requires_core_version": self.metadata.requires_core_version,
            "provides_commands": self.metadata.provides_commands,
            "is_loaded": self.is_loaded
        }

class PluginManager:
    """Manages loading and registration of CLI plugins"""
    
    ENTRY_POINT_GROUP = "as_cli.plugins"
    
    def __init__(self, config=None, auth_context=None):
        self.config = config
        self.auth_context = auth_context
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded_handlers: Dict[str, BaseCommandHandler] = {}
        self.logger = logging.getLogger(__name__)
    
    def discover_plugins(self) -> List[PluginInfo]:
        """Discover all available plugins through entry points"""
        discovered_plugins = []
        
        try:
            for entry_point in pkg_resources.iter_entry_points(self.ENTRY_POINT_GROUP):
                try:
                    plugin_info = self._load_plugin_info(entry_point)
                    if plugin_info:
                        discovered_plugins.append(plugin_info)
                        self.plugins[plugin_info.name] = plugin_info
                        self.logger.info(f"Discovered plugin: {plugin_info.name} v{plugin_info.version}")
                except Exception as e:
                    self.logger.warning(f"Failed to load plugin '{entry_point.name}': {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error discovering plugins: {str(e)}")
        
        return discovered_plugins
    
    def _load_plugin_info(self, entry_point) -> Optional[PluginInfo]:
        """Load plugin information from an entry point"""
        try:
            # Load the plugin class
            plugin_class = entry_point.load()
            
            # Validate it's a proper plugin
            if not issubclass(plugin_class, BasePlugin):
                self.logger.warning(f"Plugin '{entry_point.name}' is not a BasePlugin subclass")
                return None
            
            # Validate plugin implementation
            validation_result = PluginValidator.validate_plugin(plugin_class)
            if not validation_result.is_valid:
                self.logger.error(f"Plugin '{entry_point.name}' validation failed: {validation_result.errors}")
                return None
            
            # Instantiate plugin
            plugin_instance = plugin_class()
            metadata = plugin_instance.metadata
            
            # Get distribution info
            dist = entry_point.dist
            
            # Create plugin info
            plugin_info = PluginInfo(
                name=entry_point.name,
                version=dist.version,
                description=metadata.description,
                plugin_instance=plugin_instance,
                metadata=metadata,
                module_name=entry_point.module_name
            )
            
            return plugin_info
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin info for '{entry_point.name}': {str(e)}")
            return None
    
    def _get_metadata(self, dist, key: str, default: str = "") -> str:
        """Safely get metadata from distribution"""
        try:
            if hasattr(dist, '_get_metadata'):
                metadata = dist._get_metadata(dist.PKG_INFO)
                if metadata:
                    for line in metadata.split('\n'):
                        if line.startswith(f"{key}:"):
                            return line.split(':', 1)[1].strip()
            return default
        except:
            return default
    
    def load_plugin(self, plugin_name: str) -> Optional[Dict[str, BaseCommandHandler]]:
        """Load and instantiate a specific plugin"""
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin '{plugin_name}' not found")
            return None
        
        plugin_info = self.plugins[plugin_name]
        if plugin_info.is_loaded:
            # Return already loaded handlers
            return self._get_plugin_handlers(plugin_info)
        
        try:
            # Call plugin lifecycle hook
            plugin_info.plugin_instance.on_load(self.config, self.auth_context)
            plugin_info.is_loaded = True
            
            # Get command handlers from plugin
            handlers = plugin_info.plugin_instance.get_command_handlers()
            
            # Instantiate handlers
            instantiated_handlers = {}
            for command_name, handler_class in handlers.items():
                handler = handler_class(self.config, self.auth_context)
                instantiated_handlers[command_name] = handler
                self.loaded_handlers[command_name] = handler
            
            self.logger.info(f"Loaded plugin: {plugin_name} with commands: {list(instantiated_handlers.keys())}")
            return instantiated_handlers
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin '{plugin_name}': {str(e)}")
            return None
    
    def _get_plugin_handlers(self, plugin_info: PluginInfo) -> Dict[str, BaseCommandHandler]:
        """Get already instantiated handlers for a plugin"""
        handlers = {}
        for command_name in plugin_info.metadata.provides_commands:
            if command_name in self.loaded_handlers:
                handlers[command_name] = self.loaded_handlers[command_name]
        return handlers
    
    def load_all_plugins(self) -> Dict[str, BaseCommandHandler]:
        """Load all discovered plugins"""
        loaded = {}
        
        for plugin_name in self.plugins.keys():
            handlers = self.load_plugin(plugin_name)
            if handlers:
                loaded.update(handlers)
        
        return loaded
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a specific plugin"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[PluginInfo]:
        """List all discovered plugins"""
        return list(self.plugins.values())
    
    def is_plugin_loaded(self, plugin_name: str) -> bool:
        """Check if a plugin is currently loaded"""
        if plugin_name not in self.plugins:
            return False
        return self.plugins[plugin_name].is_loaded
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin (remove from loaded handlers)"""
        if plugin_name not in self.plugins:
            return False
        
        plugin_info = self.plugins[plugin_name]
        if not plugin_info.is_loaded:
            return False
        
        try:
            # Remove handlers for this plugin
            for command_name in plugin_info.metadata.provides_commands:
                if command_name in self.loaded_handlers:
                    del self.loaded_handlers[command_name]
            
            # Call plugin lifecycle hook
            plugin_info.plugin_instance.on_unload()
            plugin_info.is_loaded = False
            
            self.logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin '{plugin_name}': {str(e)}")
            return False
    
    def get_plugin_commands(self) -> Dict[str, str]:
        """Get mapping of command names to plugin names"""
        commands = {}
        
        for plugin_name, plugin_info in self.plugins.items():
            for command_name in plugin_info.metadata.provides_commands:
                commands[command_name] = plugin_name
                
        return commands
    
    def get_loaded_handlers(self) -> Dict[str, BaseCommandHandler]:
        """Get all currently loaded command handlers"""
        return self.loaded_handlers.copy()