"""
Configuration management for AppSentinels CLI

This module handles configuration loading from environment variables,
configuration files, and provides default values.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv
import urllib.parse

@dataclass
class APIConfig:
    """API configuration settings"""
    base_url: str = "https://api.appsentinels.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1

@dataclass
class AuthConfig:
    """Authentication configuration"""
    client_id: str = ""
    client_secret: str = ""
    auth_url: str = "https://auth.appsentinels.com"
    token_url: str = "https://auth.appsentinels.com/oauth/token"
    redirect_uri: str = "http://localhost:8080/callback"
    scope: str = "api:read api:write"

@dataclass
class OutputConfig:
    """Output formatting configuration"""
    default_format: str = "table"
    max_width: int = 120
    truncate_long_values: bool = True
    show_headers: bool = True
    color_output: bool = True

@dataclass
class DatabaseConfig:
    """Database configuration for ingest operations"""
    db_type: str = "clickhouse"
    host: str = "localhost"
    port: int = 9000
    database: str = "default"
    user: str = "default"
    password: str = ""
    docker_container: str = "clickhouse-server"
    use_docker: bool = True
    connection_timeout: int = 30
    
    def get_connection_url(self) -> str:
        """Get database connection URL"""
        if self.password:
            return f"{self.db_type}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            return f"{self.db_type}://{self.user}@{self.host}:{self.port}/{self.database}"
    
    @classmethod
    def from_url(cls, url: str) -> 'DatabaseConfig':
        """Create DatabaseConfig from connection URL"""
        parsed = urllib.parse.urlparse(url)
        
        return cls(
            db_type=parsed.scheme,
            host=parsed.hostname or "localhost",
            port=parsed.port or 9000,
            database=parsed.path.lstrip('/') or "default",
            user=parsed.username or "default",
            password=parsed.password or ""
        )

@dataclass
class IngestConfig:
    """Ingest operation configuration"""
    schema_file: str = "schema.json"
    default_batch_size: int = 1000
    log_file: str = "ingestion.log"
    overwrite_log: bool = True
    enable_ip_extraction: bool = True
    enable_telemetry: bool = True
    continue_on_error: bool = False
    supported_formats: List[str] = field(default_factory=lambda: ["parquet", "json", "csv"])

@dataclass
class ProfileConfig:
    """Configuration for a single profile"""
    name: str = "default"
    description: str = ""
    api: APIConfig = field(default_factory=APIConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ingest: IngestConfig = field(default_factory=IngestConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile configuration to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "api": {
                "base_url": self.api.base_url,
                "timeout": self.api.timeout,
                "max_retries": self.api.max_retries,
                "retry_delay": self.api.retry_delay
            },
            "auth": {
                "client_id": self.auth.client_id,
                "auth_url": self.auth.auth_url,
                "token_url": self.auth.token_url,
                "redirect_uri": self.auth.redirect_uri,
                "scope": self.auth.scope
            },
            "output": {
                "default_format": self.output.default_format,
                "max_width": self.output.max_width,
                "truncate_long_values": self.output.truncate_long_values,
                "show_headers": self.output.show_headers,
                "color_output": self.output.color_output
            },
            "database": {
                "db_type": self.database.db_type,
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "user": self.database.user,
                "docker_container": self.database.docker_container,
                "use_docker": self.database.use_docker,
                "connection_timeout": self.database.connection_timeout
            },
            "ingest": {
                "schema_file": self.ingest.schema_file,
                "default_batch_size": self.ingest.default_batch_size,
                "log_file": self.ingest.log_file,
                "overwrite_log": self.ingest.overwrite_log,
                "enable_ip_extraction": self.ingest.enable_ip_extraction,
                "enable_telemetry": self.ingest.enable_telemetry,
                "continue_on_error": self.ingest.continue_on_error,
                "supported_formats": self.ingest.supported_formats
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfileConfig':
        """Create ProfileConfig from dictionary"""
        profile = cls()
        profile.name = data.get("name", "default")
        profile.description = data.get("description", "")
        
        # Load API config
        if "api" in data:
            api_data = data["api"]
            profile.api = APIConfig(
                base_url=api_data.get("base_url", profile.api.base_url),
                timeout=api_data.get("timeout", profile.api.timeout),
                max_retries=api_data.get("max_retries", profile.api.max_retries),
                retry_delay=api_data.get("retry_delay", profile.api.retry_delay)
            )
        
        # Load Auth config
        if "auth" in data:
            auth_data = data["auth"]
            profile.auth = AuthConfig(
                client_id=auth_data.get("client_id", profile.auth.client_id),
                client_secret=auth_data.get("client_secret", profile.auth.client_secret),
                auth_url=auth_data.get("auth_url", profile.auth.auth_url),
                token_url=auth_data.get("token_url", profile.auth.token_url),
                redirect_uri=auth_data.get("redirect_uri", profile.auth.redirect_uri),
                scope=auth_data.get("scope", profile.auth.scope)
            )
        
        # Load Output config
        if "output" in data:
            output_data = data["output"]
            profile.output = OutputConfig(
                default_format=output_data.get("default_format", profile.output.default_format),
                max_width=output_data.get("max_width", profile.output.max_width),
                truncate_long_values=output_data.get("truncate_long_values", profile.output.truncate_long_values),
                show_headers=output_data.get("show_headers", profile.output.show_headers),
                color_output=output_data.get("color_output", profile.output.color_output)
            )
        
        # Load Database config
        if "database" in data:
            db_data = data["database"]
            profile.database = DatabaseConfig(
                db_type=db_data.get("db_type", profile.database.db_type),
                host=db_data.get("host", profile.database.host),
                port=db_data.get("port", profile.database.port),
                database=db_data.get("database", profile.database.database),
                user=db_data.get("user", profile.database.user),
                password=db_data.get("password", profile.database.password),
                docker_container=db_data.get("docker_container", profile.database.docker_container),
                use_docker=db_data.get("use_docker", profile.database.use_docker),
                connection_timeout=db_data.get("connection_timeout", profile.database.connection_timeout)
            )
        
        # Load Ingest config
        if "ingest" in data:
            ingest_data = data["ingest"]
            profile.ingest = IngestConfig(
                schema_file=ingest_data.get("schema_file", profile.ingest.schema_file),
                default_batch_size=ingest_data.get("default_batch_size", profile.ingest.default_batch_size),
                log_file=ingest_data.get("log_file", profile.ingest.log_file),
                overwrite_log=ingest_data.get("overwrite_log", profile.ingest.overwrite_log),
                enable_ip_extraction=ingest_data.get("enable_ip_extraction", profile.ingest.enable_ip_extraction),
                enable_telemetry=ingest_data.get("enable_telemetry", profile.ingest.enable_telemetry),
                continue_on_error=ingest_data.get("continue_on_error", profile.ingest.continue_on_error),
                supported_formats=ingest_data.get("supported_formats", profile.ingest.supported_formats)
            )
        
        return profile

@dataclass
class Config:
    """Main configuration class with profile support"""
    # Profile management
    current_profile: str = "default"
    profiles_dir: str = ""  # Will be set to ~/.as-cli/profiles
    
    # Runtime settings
    verbose: bool = False
    debug: bool = False
    config_file: Optional[str] = None
    
    # Profile cache (loaded profiles)
    _profile_cache: Dict[str, ProfileConfig] = field(default_factory=dict)
    
    # Current active configuration (delegated to current profile)
    api: APIConfig = field(default_factory=APIConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ingest: IngestConfig = field(default_factory=IngestConfig)
    
    def __post_init__(self):
        """Post-initialization to load configuration"""
        self._load_dotenv()
        self._load_environment()
        
        # Set up paths
        self.config_dir = Path.home() / ".as-cli"
        self.profiles_dir = str(self.config_dir / "profiles")
        
        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        Path(self.profiles_dir).mkdir(exist_ok=True)
        
        # Load main config file if it exists
        default_config_file = self.config_dir / "config.yaml"
        if default_config_file.exists() and not self.config_file:
            self.config_file = str(default_config_file)
        
        if self.config_file:
            self.load_config_file(self.config_file)
        
        # Check for legacy single-file config and migrate if needed
        self._migrate_legacy_config()
        
        # Initialize as-cli directory structure
        self._initialize_as_cli_setup()
        
        # Set active profile configuration
        self._activate_profile(self.current_profile)
    
    def _load_dotenv(self) -> None:
        """Load environment variables from .env file"""
        # Look for .env file in current directory or home directory
        env_paths = [
            Path.cwd() / ".env",
            Path.home() / ".as-cli" / ".env"
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                break
    
    def _load_environment(self) -> None:
        """Load configuration from environment variables"""
        # API configuration
        self.api.base_url = os.getenv("AS_API_BASE_URL", self.api.base_url)
        self.api.timeout = int(os.getenv("AS_API_TIMEOUT", str(self.api.timeout)))
        self.api.max_retries = int(os.getenv("AS_API_MAX_RETRIES", str(self.api.max_retries)))
        self.api.retry_delay = int(os.getenv("AS_API_RETRY_DELAY", str(self.api.retry_delay)))
        
        # Auth configuration
        self.auth.client_id = os.getenv("AS_CLIENT_ID", self.auth.client_id)
        self.auth.client_secret = os.getenv("AS_CLIENT_SECRET", self.auth.client_secret)
        self.auth.auth_url = os.getenv("AS_AUTH_URL", self.auth.auth_url)
        self.auth.token_url = os.getenv("AS_TOKEN_URL", self.auth.token_url)
        self.auth.redirect_uri = os.getenv("AS_REDIRECT_URI", self.auth.redirect_uri)
        self.auth.scope = os.getenv("AS_SCOPE", self.auth.scope)
        
        # Output configuration
        self.output.default_format = os.getenv("AS_OUTPUT_FORMAT", self.output.default_format)
        self.output.max_width = int(os.getenv("AS_OUTPUT_MAX_WIDTH", str(self.output.max_width)))
        self.output.truncate_long_values = os.getenv("AS_OUTPUT_TRUNCATE", "true").lower() == "true"
        self.output.show_headers = os.getenv("AS_OUTPUT_SHOW_HEADERS", "true").lower() == "true"
        self.output.color_output = os.getenv("AS_OUTPUT_COLOR", "true").lower() == "true"
        
        # Database configuration
        db_url = os.getenv("AS_DB_URL")
        if db_url:
            try:
                self.database = DatabaseConfig.from_url(db_url)
            except Exception:
                pass  # Keep defaults if URL parsing fails
        
        self.database.user = os.getenv("AS_DB_USER", self.database.user)
        self.database.password = os.getenv("AS_DB_PASSWORD", self.database.password)
        self.database.host = os.getenv("AS_DB_HOST", self.database.host)
        self.database.port = int(os.getenv("AS_DB_PORT", str(self.database.port)))
        self.database.database = os.getenv("AS_DB_DATABASE", self.database.database)
        self.database.docker_container = os.getenv("AS_DB_CONTAINER", self.database.docker_container)
        self.database.use_docker = os.getenv("AS_DB_USE_DOCKER", "true").lower() == "true"
        
        # Ingest configuration
        self.ingest.schema_file = os.getenv("AS_SCHEMA_FILE", self.ingest.schema_file)
        self.ingest.default_batch_size = int(os.getenv("AS_BATCH_SIZE", str(self.ingest.default_batch_size)))
        self.ingest.log_file = os.getenv("AS_INGEST_LOG_FILE", self.ingest.log_file)
        self.ingest.enable_ip_extraction = os.getenv("AS_ENABLE_IP_EXTRACTION", "true").lower() == "true"
        self.ingest.enable_telemetry = os.getenv("AS_ENABLE_TELEMETRY", "true").lower() == "true"
        self.ingest.continue_on_error = os.getenv("AS_CONTINUE_ON_ERROR", "false").lower() == "true"
        
        # Runtime settings
        self.verbose = os.getenv("AS_VERBOSE", "false").lower() == "true"
        self.debug = os.getenv("AS_DEBUG", "false").lower() == "true"
    
    def load_config_file(self, config_file: str) -> None:
        """Load configuration from a file
        
        Args:
            config_file: Path to configuration file (JSON or YAML)
        """
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            self._apply_config_data(config_data)
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Invalid configuration file format: {e}")
    
    def _initialize_as_cli_setup(self) -> None:
        """Initialize complete as-cli directory structure and configuration"""
        
        # Check if this is first run (no profiles directory or empty)
        is_first_run = not Path(self.profiles_dir).exists() or not list(Path(self.profiles_dir).glob("*.yaml"))
        
        if is_first_run:
            print(f"Initializing AppSentinels CLI configuration in {self.config_dir}")
        
        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        Path(self.profiles_dir).mkdir(exist_ok=True)
        
        # Create main config file if it doesn't exist
        main_config_file = self.config_dir / "config.yaml"
        if not main_config_file.exists():
            self._save_main_config()
            if is_first_run:
                print(f"Created main configuration file: {main_config_file}")
        
        # Ensure default profile exists
        self._ensure_default_profile()
        
        # Create .env template if it doesn't exist
        env_template_file = self.config_dir / ".env.template"
        if not env_template_file.exists():
            self._create_env_template(env_template_file)
            if is_first_run:
                print(f"Created environment template: {env_template_file}")
        
        # Create README for the .as-cli directory
        readme_file = self.config_dir / "README.md"
        if not readme_file.exists():
            self._create_config_readme(readme_file)
            if is_first_run:
                print(f"Created configuration README: {readme_file}")
        
        if is_first_run:
            print("AppSentinels CLI initialization complete!")
            print(f"Configuration directory: {self.config_dir}")
            print("To get started:")
            print("  1. Copy .env.template to .env and configure your settings")
            print("  2. Run 'as-cli profile list' to see available profiles")
            print("  3. Run 'as-cli auth login' to authenticate")
    
    def _create_env_template(self, env_file: Path) -> None:
        """Create environment variables template file"""
        env_template = """# AppSentinels CLI Environment Variables
# Copy this file to .env and fill in your values

# API Configuration
AS_API_BASE_URL=https://api.appsentinels.com
AS_API_TIMEOUT=30
AS_API_MAX_RETRIES=3

# OAuth Configuration
AS_CLIENT_ID=your-client-id
AS_CLIENT_SECRET=your-client-secret
AS_AUTH_URL=https://auth.appsentinels.com
AS_TOKEN_URL=https://auth.appsentinels.com/oauth/token

# Database Configuration (for ingest operations)
AS_DB_URL=clickhouse://user:password@localhost:9000/database
AS_DB_USER=default
AS_DB_PASSWORD=your-database-password
AS_DB_HOST=localhost
AS_DB_PORT=9000
AS_DB_DATABASE=default

# Ingest Configuration
AS_SCHEMA_FILE=schema.json
AS_BATCH_SIZE=1000
AS_ENABLE_TELEMETRY=true
AS_ENABLE_IP_EXTRACTION=true

# Output Configuration
AS_OUTPUT_FORMAT=table
AS_OUTPUT_COLOR=true
AS_OUTPUT_MAX_WIDTH=120

# Global Settings
AS_VERBOSE=false
AS_DEBUG=false
"""
        with open(env_file, 'w') as f:
            f.write(env_template)
    
    def _create_config_readme(self, readme_file: Path) -> None:
        """Create README file for .as-cli directory"""
        readme_content = """# AppSentinels CLI Configuration

This directory contains your AppSentinels CLI configuration files.

## Files and Directories

- `config.yaml` - Main configuration file (current profile setting)
- `profiles/` - Directory containing individual profile configuration files
- `.env` - Environment variables (create from .env.template)
- `.env.template` - Template for environment variables

## Profile Management

Profiles are stored as individual YAML files in the `profiles/` directory:
- `profiles/default.yaml` - Default profile
- `profiles/production.yaml` - Production environment profile
- `profiles/staging.yaml` - Staging environment profile
- `profiles/[name].yaml` - Custom profiles

## Usage

```bash
# List profiles
as-cli profile list

# Switch profiles
as-cli profile switch production

# Create new profile
as-cli profile create my-env --description "My environment"

# Use specific profile for command
as-cli --profile production ingest config --show
```

## Environment Variables

Copy `.env.template` to `.env` and fill in your values:

```bash
cp .env.template .env
# Edit .env with your settings
```

Environment variables override profile settings.

## Documentation

For complete documentation, visit: https://docs.appsentinels.com/cli
"""
        with open(readme_file, 'w') as f:
            f.write(readme_content)

    def _migrate_legacy_config(self) -> None:
        """Migrate legacy single-file config to separate profile files"""
        # Check if we have old-style profiles section in main config
        # This happens when loading an old config file
        if hasattr(self, 'profiles') and self.profiles:
            print("Migrating legacy profile configuration to separate files...")
            
            # Migrate each profile to separate file
            for profile_name, profile in self.profiles.items():
                if isinstance(profile, ProfileConfig):
                    self._save_profile_file(profile_name, profile)
            
            # Clear the profiles from main config
            self.profiles = {}
            
            # Save updated main config without profiles section
            self._save_main_config()
            
            print(f"Migration complete. Profiles moved to {self.profiles_dir}/")
    
    def _ensure_default_profile(self) -> None:
        """Ensure default profile exists"""
        default_profile_path = Path(self.profiles_dir) / "default.yaml"
        if not default_profile_path.exists():
            default_profile = ProfileConfig(name="default", description="Default configuration")
            self._save_profile_file("default", default_profile)
    
    def _load_profile(self, profile_name: str) -> Optional[ProfileConfig]:
        """Load a profile from file
        
        Args:
            profile_name: Name of profile to load
            
        Returns:
            ProfileConfig or None if not found
        """
        # Check cache first
        if profile_name in self._profile_cache:
            return self._profile_cache[profile_name]
        
        profile_path = Path(self.profiles_dir) / f"{profile_name}.yaml"
        if not profile_path.exists():
            return None
        
        try:
            with open(profile_path, 'r') as f:
                profile_data = yaml.safe_load(f)
            
            profile = ProfileConfig.from_dict(profile_data)
            
            # Cache the loaded profile
            self._profile_cache[profile_name] = profile
            
            return profile
            
        except Exception as e:
            print(f"Warning: Failed to load profile '{profile_name}': {e}")
            return None
    
    def _save_profile_file(self, profile_name: str, profile: ProfileConfig) -> None:
        """Save a profile to its individual file
        
        Args:
            profile_name: Name of profile
            profile: ProfileConfig to save
        """
        profile_path = Path(self.profiles_dir) / f"{profile_name}.yaml"
        
        try:
            profile_data = profile.to_dict()
            with open(profile_path, 'w') as f:
                yaml.dump(profile_data, f, default_flow_style=False, indent=2)
            
            # Update cache
            self._profile_cache[profile_name] = profile
            
        except Exception as e:
            raise ValueError(f"Failed to save profile '{profile_name}': {e}")
    
    def _save_main_config(self) -> None:
        """Save main configuration file (without profiles)"""
        if not self.config_file:
            self.config_file = str(self.config_dir / "config.yaml")
        
        config_data = {
            "current_profile": self.current_profile
        }
        
        config_path = Path(self.config_file)
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
    
    def _activate_profile(self, profile_name: str) -> None:
        """Activate a specific profile
        
        Args:
            profile_name: Name of profile to activate
        """
        profile = self._load_profile(profile_name)
        if not profile:
            # Create default profile if it doesn't exist
            profile = ProfileConfig(name=profile_name)
            self._save_profile_file(profile_name, profile)
        
        self.current_profile = profile_name
        
        # Update current configuration from profile
        self.api = profile.api
        self.auth = profile.auth
        self.output = profile.output
        self.database = profile.database
        self.ingest = profile.ingest
    
    def switch_profile(self, profile_name: str) -> bool:
        """Switch to a different profile
        
        Args:
            profile_name: Name of profile to switch to
            
        Returns:
            True if successful, False if profile doesn't exist
        """
        profile = self._load_profile(profile_name)
        if not profile:
            return False
        
        self._activate_profile(profile_name)
        return True
    
    def create_profile(self, name: str, description: str = "", copy_from: str = None) -> ProfileConfig:
        """Create a new profile
        
        Args:
            name: Profile name
            description: Profile description
            copy_from: Name of existing profile to copy from
            
        Returns:
            Created ProfileConfig
        """
        if copy_from:
            source_profile = self._load_profile(copy_from)
            if source_profile:
                # Copy from existing profile
                profile_data = source_profile.to_dict()
                profile_data["name"] = name
                profile_data["description"] = description
                new_profile = ProfileConfig.from_dict(profile_data)
            else:
                # Fallback to default if source not found
                new_profile = ProfileConfig(name=name, description=description)
        else:
            # Create new profile with defaults
            new_profile = ProfileConfig(name=name, description=description)
        
        # Save to file
        self._save_profile_file(name, new_profile)
        return new_profile
    
    def delete_profile(self, name: str) -> bool:
        """Delete a profile
        
        Args:
            name: Profile name to delete
            
        Returns:
            True if deleted, False if profile doesn't exist or is current profile
        """
        profile_path = Path(self.profiles_dir) / f"{name}.yaml"
        if not profile_path.exists():
            return False
        
        if name == self.current_profile:
            return False  # Cannot delete current profile
        
        if name == "default":
            return False  # Cannot delete default profile
        
        try:
            profile_path.unlink()  # Delete the file
            
            # Remove from cache if present
            if name in self._profile_cache:
                del self._profile_cache[name]
            
            return True
        except Exception:
            return False
    
    def list_profiles(self) -> Dict[str, ProfileConfig]:
        """List all available profiles
        
        Returns:
            Dictionary of profile names to ProfileConfig objects
        """
        profiles = {}
        profiles_path = Path(self.profiles_dir)
        
        # Scan for profile files
        for profile_file in profiles_path.glob("*.yaml"):
            profile_name = profile_file.stem
            profile = self._load_profile(profile_name)
            if profile:
                profiles[profile_name] = profile
        
        return profiles
    
    def get_profile(self, name: str) -> Optional[ProfileConfig]:
        """Get a specific profile
        
        Args:
            name: Profile name
            
        Returns:
            ProfileConfig or None if not found
        """
        return self._load_profile(name)
    
    def _apply_config_data(self, config_data: Dict[str, Any]) -> None:
        """Apply configuration data from dictionary
        
        Args:
            config_data: Configuration dictionary
        """
        # Load global settings
        self.current_profile = config_data.get("current_profile", self.current_profile)
        
        # Handle legacy profiles in main config (will be migrated)
        if "profiles" in config_data:
            # Store for migration
            self.profiles = {}
            profiles_data = config_data["profiles"]
            for profile_name, profile_data in profiles_data.items():
                profile_data["name"] = profile_name  # Ensure name matches key
                self.profiles[profile_name] = ProfileConfig.from_dict(profile_data)
        
        # Handle legacy top-level config as default profile
        if any(key in config_data for key in ["api", "auth", "output", "database", "ingest"]):
            # Create default profile from top-level config
            default_profile = ProfileConfig(name="default", description="Default configuration")
            
            # Apply top-level configuration to default profile
            if "api" in config_data:
                api_config = config_data["api"]
                default_profile.api.base_url = api_config.get("base_url", default_profile.api.base_url)
                default_profile.api.timeout = api_config.get("timeout", default_profile.api.timeout)
                default_profile.api.max_retries = api_config.get("max_retries", default_profile.api.max_retries)
                default_profile.api.retry_delay = api_config.get("retry_delay", default_profile.api.retry_delay)
            
            if "auth" in config_data:
                auth_config = config_data["auth"]
                default_profile.auth.client_id = auth_config.get("client_id", default_profile.auth.client_id)
                default_profile.auth.client_secret = auth_config.get("client_secret", default_profile.auth.client_secret)
                default_profile.auth.auth_url = auth_config.get("auth_url", default_profile.auth.auth_url)
                default_profile.auth.token_url = auth_config.get("token_url", default_profile.auth.token_url)
                default_profile.auth.redirect_uri = auth_config.get("redirect_uri", default_profile.auth.redirect_uri)
                default_profile.auth.scope = auth_config.get("scope", default_profile.auth.scope)
            
            if "output" in config_data:
                output_config = config_data["output"]
                default_profile.output.default_format = output_config.get("default_format", default_profile.output.default_format)
                default_profile.output.max_width = output_config.get("max_width", default_profile.output.max_width)
                default_profile.output.truncate_long_values = output_config.get("truncate_long_values", default_profile.output.truncate_long_values)
                default_profile.output.show_headers = output_config.get("show_headers", default_profile.output.show_headers)
                default_profile.output.color_output = output_config.get("color_output", default_profile.output.color_output)
            
            if "database" in config_data:
                db_config = config_data["database"]
                default_profile.database.db_type = db_config.get("db_type", default_profile.database.db_type)
                default_profile.database.host = db_config.get("host", default_profile.database.host)
                default_profile.database.port = db_config.get("port", default_profile.database.port)
                default_profile.database.database = db_config.get("database", default_profile.database.database)
                default_profile.database.user = db_config.get("user", default_profile.database.user)
                default_profile.database.password = db_config.get("password", default_profile.database.password)
                default_profile.database.docker_container = db_config.get("docker_container", default_profile.database.docker_container)
                default_profile.database.use_docker = db_config.get("use_docker", default_profile.database.use_docker)
                default_profile.database.connection_timeout = db_config.get("connection_timeout", default_profile.database.connection_timeout)
            
            if "ingest" in config_data:
                ingest_config = config_data["ingest"]
                default_profile.ingest.schema_file = ingest_config.get("schema_file", default_profile.ingest.schema_file)
                default_profile.ingest.default_batch_size = ingest_config.get("default_batch_size", default_profile.ingest.default_batch_size)
                default_profile.ingest.log_file = ingest_config.get("log_file", default_profile.ingest.log_file)
                default_profile.ingest.overwrite_log = ingest_config.get("overwrite_log", default_profile.ingest.overwrite_log)
                default_profile.ingest.enable_ip_extraction = ingest_config.get("enable_ip_extraction", default_profile.ingest.enable_ip_extraction)
                default_profile.ingest.enable_telemetry = ingest_config.get("enable_telemetry", default_profile.ingest.enable_telemetry)
                default_profile.ingest.continue_on_error = ingest_config.get("continue_on_error", default_profile.ingest.continue_on_error)
            
            # Initialize profiles dict if needed for migration
            if not hasattr(self, 'profiles'):
                self.profiles = {}
            self.profiles["default"] = default_profile
    
    def get_api_url(self, endpoint: str) -> str:
        """Get full API URL for an endpoint
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full API URL
        """
        base_url = self.api.base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base_url}/{endpoint}"
    
    def get_auth_config(self) -> Dict[str, Any]:
        """Get authentication configuration as dictionary
        
        Returns:
            Authentication configuration
        """
        return {
            "client_id": self.auth.client_id,
            "client_secret": self.auth.client_secret,
            "auth_url": self.auth.auth_url,
            "token_url": self.auth.token_url,
            "redirect_uri": self.auth.redirect_uri,
            "scope": self.auth.scope
        }
    
    def validate(self) -> None:
        """Validate configuration settings
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.api.base_url:
            raise ValueError("API base URL is required")
        
        if not self.auth.client_id:
            raise ValueError("OAuth client ID is required")
        
        if self.api.timeout <= 0:
            raise ValueError("API timeout must be positive")
        
        if self.api.max_retries < 0:
            raise ValueError("Max retries must be non-negative")
        
        if self.output.max_width <= 0:
            raise ValueError("Output max width must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert main configuration to dictionary (without profiles)
        
        Returns:
            Main configuration as dictionary
        """
        return {
            "current_profile": self.current_profile
        }
    
    def save_config_file(self, config_file: str) -> None:
        """Save main configuration to file
        
        Args:
            config_file: Path to save configuration file
        """
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = self.to_dict()
        
        with open(config_path, 'w') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            else:
                json.dump(config_data, f, indent=2)

# Configuration instance
config = Config()