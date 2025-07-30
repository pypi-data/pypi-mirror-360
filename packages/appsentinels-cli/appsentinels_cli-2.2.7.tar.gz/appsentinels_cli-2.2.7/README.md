# AppSentinels CLI (as-cli)

A modular, extensible command-line interface for AppSentinels API security management. Built with a lightweight core and powerful plugin architecture, this CLI provides essential functionality out-of-the-box while allowing users to install only the features they need through external plugins.

## 🌟 Architecture Overview

### 🎯 Lightweight Core
The AppSentinels CLI follows a **core + plugins** architecture:

- **Essential Commands Only**: Authentication, profiles, plugin management, and configuration
- **Minimal Dependencies**: Lean installation with just the basics
- **Fast Startup**: Quick command execution without loading unused features
- **Stable Foundation**: Core functionality that rarely changes

### 🔌 Plugin Ecosystem
Extended functionality through installable plugins:

- **Production-Ready Plugins**: Fully-featured external plugins for various needs
- **Community Extensible**: Framework for third-party and community plugins
- **Independent Updates**: Plugins can be updated without changing core CLI
- **Optional Installation**: Install only the features you need

## 🌟 Key Features

### Core CLI Features
- **🔐 OAuth 2.1 Authentication**: Secure authentication with PKCE support
- **🏢 Profile Management**: Multi-environment configuration with file-based storage
- **🔌 Plugin Management**: Discover, install, and manage CLI extensions
- **🔧 Auto-Configuration**: Automatic setup of required files and directories
- **⚙️ Flexible Configuration**: Environment variables, config files, and CLI options
- **📤 Multiple Output Formats**: Table, JSON, YAML, and raw output
- **💬 Interactive Mode**: REPL-style interface for interactive usage

### Plugin Capabilities
- **👋 Hello World Plugin**: Example plugin for development reference (included)  
- **🔌 External Plugins**: Install specialized plugins based on your needs
- **🔮 Custom Extensions**: Build your own plugins for specific workflows

## 🚀 Quick Start

### Core CLI Installation

Install the lightweight core CLI with essential commands:

#### From Source
```bash
git clone https://github.com/appsentinels/as-cli.git
cd as-cli
pip install -e .
```

#### Global Installation (When Available)
```bash
pip install appsentinels-cli
```

### What You Get Out-of-the-Box

The core CLI provides essential functionality:

```bash
# Available core commands after installation
as-cli auth login                    # OAuth authentication
as-cli profile list                  # Multi-environment profiles  
as-cli profile create prod          # Environment management
as-cli plugin list                  # Plugin discovery
as-cli init --show-only             # Configuration management
```

### Automatic Configuration

Installation automatically creates the complete configuration structure in `~/.as-cli/`:

```
~/.as-cli/
├── config.yaml              # Main configuration file
├── .env.template            # Environment variables template
├── README.md                # Configuration documentation
└── profiles/                # Profile-specific configurations
    ├── default.yaml         # Default profile
    └── [profile-name].yaml  # Additional profiles
```

**Initialization Features:**
1. 🏗️ Creates `~/.as-cli/` directory structure automatically
2. 📋 Generates default profile with sensible defaults
3. 📝 Creates environment variables template
4. 📖 Provides comprehensive configuration documentation
5. 💡 Shows helpful getting started instructions

### Manual Configuration Management

If you need to manually manage the configuration:

```bash
# Preview configuration structure
as-cli init --show-only

# Initialize or repair configuration
as-cli init

# Force complete re-initialization
as-cli init --force

# Check current configuration status
as-cli profile current
```

### First-Time Setup

1. **Configure Environment Variables** (Optional):
   ```bash
   cd ~/.as-cli
   cp .env.template .env
   # Edit .env with your specific values
   ```

2. **Authenticate**:
   ```bash
   as-cli auth login
   ```

3. **Create Environment-Specific Profiles**:
   ```bash
   as-cli profile create production --description "Production environment"
   as-cli profile create staging --description "Staging environment"
   ```

4. **Install Plugins** (Choose what you need):
   ```bash
   # Install example hello plugin (for development reference)
   cd external/as-cli-hello && pip install -e .
   
   # Install external plugins as needed
   # pip install <plugin-name>
   
   # Verify installed plugins
   as-cli plugin list
   ```

### Basic Usage Examples

```bash
# List available profiles
as-cli profile list

# Switch to production profile
as-cli profile switch production

# List available plugins
as-cli plugin list

# Get help
as-cli --help
```

### Plugin Usage Examples

```bash
# Use hello plugin (example/development)
as-cli hello --name "World" --language es

# Use external plugins (after installation)
# The available commands depend on which plugins you install
# as-cli <plugin-command> [options]
```

## 🏗️ Modular Architecture

### Philosophy

The AppSentinels CLI embraces a **modular design philosophy**:

- **🎯 Core Focus**: Essential functionality that every user needs
- **📦 Plugin Extensions**: Advanced features available as separate packages
- **🚀 Performance**: Fast startup by loading only required components
- **🔧 Maintenance**: Independent versioning and updates for core vs plugins

### Core vs Plugins

#### Core CLI Commands
Commands that are always available after installing `appsentinels-cli`:

```bash
as-cli auth login              # OAuth 2.1 authentication
as-cli profile list            # Environment profile management  
as-cli profile create prod     # Create production profile
as-cli profile switch staging  # Switch between environments
as-cli plugin list            # Discover available plugins
as-cli plugin info <name>     # Get plugin information
as-cli init                   # Configuration management
as-cli --interactive          # Interactive mode
```

#### Plugin Commands
Commands that become available after installing specific plugins:

```bash
# After installing a plugin: pip install <plugin-name>
as-cli <plugin-command> [options]      # Plugin-specific commands

# Example with hello plugin:
as-cli hello --name "World"            # Example plugin command

# Plugin commands vary based on what you install
# Each plugin adds its own set of commands and features
```

### Plugin Benefits

**For Users:**
- 🎯 **Install Only What You Need**: Avoid bloating your environment
- 🚀 **Faster Performance**: Core CLI starts instantly
- 🔧 **Independent Updates**: Update plugins without affecting core
- 💾 **Reduced Dependencies**: Minimal requirements for core functionality

**For Developers:**
- 🔄 **Independent Development**: Plugins can evolve separately
- 📦 **Easier Distribution**: Publish plugins independently to PyPI
- 🧪 **Testing Isolation**: Test plugin functionality in isolation
- 🤝 **Community Contributions**: Framework for third-party plugins

## 🏢 Profile Management System

### Overview

Profiles enable you to manage multiple environments (development, staging, production) with completely separate configurations stored as individual files in `~/.as-cli/profiles/`.

### Profile Architecture

```
~/.as-cli/
├── config.yaml              # Current active profile only
└── profiles/                 # Individual profile files
    ├── default.yaml          # Default development profile
    ├── production.yaml       # Production environment
    ├── staging.yaml          # Staging environment
    └── custom-env.yaml       # Custom environments
```

### Profile Commands

```bash
# Profile Management
as-cli profile list                    # List all profiles
as-cli profile list --detailed         # Detailed profile information
as-cli profile current                 # Show current active profile
as-cli profile show [profile-name]     # Show profile configuration

# Profile Switching
as-cli profile switch production       # Switch to production profile
as-cli profile switch staging --save   # Switch and persist change

# Profile Creation
as-cli profile create dev --description "Development environment"
as-cli profile create prod --copy-from staging --description "Production"
as-cli profile copy staging my-staging --description "My staging setup"

# Profile Deletion
as-cli profile delete old-env
as-cli profile delete test-env --save  # Delete and save changes

# Use specific profile for commands
as-cli --profile production <command>
as-cli --profile staging <command>
```

### Profile Configuration Structure

Each profile contains comprehensive environment-specific settings:

```yaml
# profiles/production.yaml
name: production
description: Production environment
api:
  base_url: https://api.appsentinels.com
  timeout: 60
  max_retries: 5
  retry_delay: 2
auth:
  client_id: prod-client-id
  auth_url: https://auth.appsentinels.com
  token_url: https://auth.appsentinels.com/oauth/token
  redirect_uri: http://localhost:8080/callback
  scope: api:read api:write
output:
  default_format: table
  max_width: 120
  truncate_long_values: true
  show_headers: true
  color_output: true
# Additional plugin-specific configurations can be added here
```

### Multi-Environment Workflow

```bash
# Development workflow
as-cli profile create dev --description "Local development"
as-cli --profile dev <command>

# Staging validation
as-cli profile create staging --copy-from dev --description "Staging environment"
as-cli --profile staging <command>

# Production deployment
as-cli profile create prod --copy-from staging --description "Production environment"
as-cli --profile prod <command>
```

## 🔌 Plugin Ecosystem

### Overview

The AppSentinels CLI features a comprehensive plugin ecosystem that transforms the CLI from a monolithic tool into a modular platform. Plugins are distributed as standard Python packages and provide seamless integration with the core CLI.

### Plugin Management

```bash
# List available plugins
as-cli plugin list                     # All discoverable plugins
as-cli plugin list --installed-only    # Only installed plugins

# Get plugin information
as-cli plugin info <plugin-name>       # Detailed plugin information

# Load/unload plugins (runtime control)
as-cli plugin load <plugin-name>       # Load plugin for current session
as-cli plugin unload <plugin-name>     # Unload plugin from current session
```

### Available Plugins

#### 👋 Hello World Plugin (Development Example)

A simple plugin demonstrating CLI extension patterns, included with the core CLI for reference.

**Installation:**
```bash
cd external/as-cli-hello
pip install -e .
```

**Features:**
- ✅ Multi-language greetings
- ✅ Command-line argument handling
- ✅ Plugin lifecycle demonstration
- ✅ Best practices example

**Usage:**
```bash
as-cli hello --name "World"                    # Basic greeting
as-cli hello --name "CLI" --language es --caps # Spanish, uppercase
as-cli hello --name "Plugin" --repeat 3        # Repeat greeting
```

**Documentation:** [Hello Plugin README](external/as-cli-hello/README.md)

#### 🔌 External Plugins

The plugin architecture supports unlimited extensibility. Install external plugins based on your specific needs:

- **Data Processing**: Import, export, and transform data
- **Monitoring**: Real-time system monitoring and alerting
- **Analytics**: Security analytics and reporting  
- **Integrations**: Connect with external services and APIs
- **Automation**: Workflow automation and orchestration
- **Custom Tools**: Build plugins for your specific use cases

### Creating Custom Plugins

#### 1. Plugin Structure
```
my-plugin/
├── setup.py                          # Entry points configuration
├── my_plugin/
│   ├── __init__.py
│   ├── plugin.py                     # Plugin implementation
│   └── handler.py                    # Command handler
└── README.md
```

#### 2. Plugin Implementation

**my_plugin/plugin.py**:
```python
from appsentinels_cli.plugin import BasePlugin, PluginMetadata
from .handler import MyHandler

class MyPlugin(BasePlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            description="My custom plugin for AppSentinels CLI",
            author="Your Name",
            provides_commands=["my-command"]
        )
    
    def get_command_handlers(self):
        return {"my-command": MyHandler}
    
    def on_load(self, config, auth_context):
        super().on_load(config, auth_context)
        print("My plugin loaded!")
    
    def on_unload(self):
        super().on_unload()
        print("My plugin unloaded!")
```

**my_plugin/handler.py**:
```python
from appsentinels_cli.plugin import BaseCommandHandler

class MyHandler(BaseCommandHandler):
    @property
    def command_name(self):
        return "my-command"
    
    @property
    def command_description(self):
        return "My custom command with profile awareness"
    
    def add_subcommands(self, parser):
        parser.add_argument("--option", help="Custom option")
        parser.add_argument("--env-specific", help="Environment-specific setting")
    
    async def handle_command(self, args):
        # Access current profile
        current_profile = self.config.current_profile
        
        return self.format_success_response(
            {
                "option": args.option,
                "profile": current_profile,
                "api_url": self.config.api.base_url
            },
            f"Command executed with profile '{current_profile}'"
        )
```

#### 3. Entry Points Configuration

**setup.py**:
```python
from setuptools import setup, find_packages

setup(
    name="my-cli-plugin",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "as_cli.plugins": [
            "my-plugin = my_plugin.plugin:MyPlugin"
        ]
    },
    install_requires=["appsentinels-cli>=2.2.0"]
)
```

#### 4. Installation and Usage

```bash
# Install your plugin
pip install -e .

# Verify plugin is discovered
as-cli plugin list

# Use your plugin with different profiles
as-cli my-command --option test
as-cli --profile production my-command --option prod-value
```

### Plugin Development Best Practices

- **Profile Awareness**: Always consider current profile settings
- **Error Handling**: Implement comprehensive error handling
- **Documentation**: Include detailed help and examples
- **Testing**: Test with multiple profiles and environments
- **Versioning**: Use semantic versioning
- **Dependencies**: Minimize external dependencies
- **Compatibility**: Ensure compatibility with core CLI versions

## ⚙️ Configuration System

### Configuration Hierarchy

The configuration system follows a clear hierarchy (highest priority first):

1. **Command-line arguments**: `--profile production`
2. **Environment variables**: `AS_DB_PASSWORD=secret`
3. **Profile configuration files**: `~/.as-cli/profiles/[name].yaml`
4. **Default values**: Built-in sensible defaults

### Environment Variables

Create `~/.as-cli/.env` from the template:

```bash
# Copy template and edit
cd ~/.as-cli
cp .env.template .env
```

**Available Environment Variables**:

```bash
# API Configuration
AS_API_BASE_URL=https://api.appsentinels.com
AS_API_TIMEOUT=30
AS_API_MAX_RETRIES=3

# OAuth Configuration
AS_CLIENT_ID=your-client-id
AS_CLIENT_SECRET=your-client-secret
AS_AUTH_URL=https://auth.appsentinels.com
AS_TOKEN_URL=https://auth.appsentinels.com/oauth/token

# Output Configuration
AS_OUTPUT_FORMAT=table
AS_OUTPUT_COLOR=true
AS_OUTPUT_MAX_WIDTH=120

# Global Settings
AS_VERBOSE=false
AS_DEBUG=false

# Plugin-specific environment variables
# Define based on your installed plugins
```

### Configuration Migration

The CLI automatically handles configuration migration:

- **Legacy single-file configs**: Automatically migrated to separate profile files
- **Version updates**: Seamless migration between configuration versions
- **Backup creation**: Original configurations are preserved during migration

## 🖥️ Interactive Mode

```bash
# Enter interactive mode
as-cli --interactive
```

**Interactive Session Example**:
```
as-cli> profile list
as-cli> profile switch production
as-cli> plugin list
as-cli> hello --name "Interactive Mode"
as-cli> help
as-cli> exit
```

## 📤 Output Formats

### Table Format (Default)
```bash
as-cli profile list
```
```
┌─────────────┬─────────┬─────────────────────────┐
│ Name        │ Current │ Description             │
├─────────────┼─────────┼─────────────────────────┤
│ default     │ ✓       │ Default configuration   │
│ production  │         │ Production environment  │
│ staging     │         │ Staging environment     │
└─────────────┴─────────┴─────────────────────────┘
```

### JSON Format
```bash
as-cli profile list --output-format json
```
```json
{
  "success": true,
  "data": {
    "profiles": [
      {
        "Name": "default",
        "Current": "✓",
        "Description": "Default configuration"
      }
    ]
  }
}
```

### YAML Format
```bash
as-cli profile list --output-format yaml
```
```yaml
success: true
data:
  profiles:
    - Name: default
      Current: "✓"
      Description: Default configuration
```

## 🏗️ Architecture

### Project Structure

```
as-cli/
├── as_cli.py                        # Main entry point
├── pyproject.toml                   # Modern Python packaging
├── requirements.txt                 # Python dependencies
├── src/                             # Source code
│   ├── config.py                    # Configuration management with profiles
│   ├── post_install.py              # Post-installation setup
│   ├── core/                        # Core infrastructure
│   │   ├── base_handler.py          # Base command handler
│   │   ├── cli_processor.py         # CLI processing and routing
│   │   ├── auth_context.py          # Authentication context
│   │   ├── plugin_manager.py        # Plugin discovery and lifecycle
│   │   └── plugin_interface.py      # Plugin base classes and validation
│   └── commands/                    # Core command handlers
│       ├── auth_handler.py          # Authentication commands
│       ├── profile_handler.py       # Profile management commands
│       ├── plugin_handler.py        # Plugin management commands
│       └── init_handler.py          # Configuration initialization
├── external/                        # External plugins directory
│   ├── as-cli-hello/                # Example hello world plugin (included)
│   └── README.md                    # Plugin development guide
├── examples/                        # Configuration examples
│   ├── profiles-config.yaml         # Multi-environment setup example
│   └── README-profiles.md           # Profile configuration guide
├── docs/                            # Additional documentation
└── tests/                           # Test files
```

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Entry     │───▶│  Profile System  │───▶│  Configuration  │
│   Point         │    │                  │    │   Management    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Plugin System   │    │ Command Routing  │    │ Auto Initialize │
│ Discovery       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Command        │    │  Plugin          │    │  Authentication │
│  Handlers       │    │  Commands        │    │  & API Access   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Plugin Architecture

```
Plugin Discovery → Plugin Validation → Plugin Loading → Command Registration
      ↓                     ↓                 ↓                   ↓
Entry Points    →    BasePlugin    →    Lifecycle    →    CLI Integration
                     Validation         Hooks
```

### Profile System Flow

```
Installation → Auto Initialize → Profile Loading → Profile Switching → Command Execution
      ↓              ↓               ↓                ↓                     ↓
Setup Files → Create Defaults → Load Active → Switch Context → Profile-Aware Commands
```

## 🧪 Development

### Setting up Development Environment

#### Core CLI Development

```bash
# Clone and setup core CLI
git clone https://github.com/appsentinels/as-cli.git
cd as-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core CLI in development mode
pip install -e .[dev]

# Verify core functionality
as-cli --help
as-cli profile list
as-cli plugin list        # Should show no plugins initially
```

#### Plugin Development Setup

```bash
# Install example plugin for development (editable mode)
cd external/as-cli-hello && pip install -e . && cd ../..

# Verify plugin installation
as-cli plugin list        # Should show installed plugins
as-cli hello --help       # Test hello plugin
```

### 🛠️ Development Mode Workflow

Development mode allows rapid iteration on plugin functionality:

```bash
# 1. Install plugin in editable mode (one time)
cd external/my-plugin
pip install -e .

# 2. Make code changes
vim my_plugin/handler.py

# 3. Test immediately (no reinstall needed)
as-cli my-command --help
as-cli my-command --test-option

# 4. Test with profiles
as-cli --profile dev my-command
as-cli --profile prod my-command

# 5. Debug plugin
as-cli plugin info my-plugin
as-cli plugin load my-plugin
```

**Key Benefits:**
- **🔄 Instant Updates**: Changes are immediately available
- **🚫 No Reinstall**: Skip reinstallation after modifications
- **🔍 Full Debugging**: Use logging and Python debugger
- **🏢 Profile Testing**: Test with different environments

### Creating New Plugins

```bash
# Use existing plugin as template
cp -r external/as-cli-hello external/my-plugin
cd external/my-plugin

# Update plugin configuration
# 1. Edit setup.py: Change name and entry points
# 2. Edit plugin.py: Update metadata (name, commands)  
# 3. Edit handler.py: Implement command logic

# Install in development mode
pip install -e .

# Start developing with live testing
as-cli plugin list                # Verify discovery
as-cli my-command --help         # Test immediately
```

### Testing with Multiple Profiles

```bash
# Create test environments
as-cli profile create test-dev --description "Test development"
as-cli profile create test-prod --description "Test production"

# Test profile switching
as-cli --profile test-dev <command>
as-cli --profile test-prod <command>

# Verify isolation
as-cli profile show test-dev
as-cli profile show test-prod
```

### Running Tests

```bash
# Install test dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_profiles.py -v
```

### Code Quality

```bash
# Code formatting
black src/
black external/

# Linting
flake8 src/
flake8 external/

# Type checking
mypy src/
```

## 📚 Examples

### Complete Multi-Environment Setup

#### Step 1: Core CLI Setup
```bash
# Install and authenticate
pip install appsentinels-cli
as-cli auth login

# Set up environment profiles
as-cli profile create dev --description "Development environment"
as-cli profile create staging --description "Staging environment"  
as-cli profile create prod --description "Production environment"

# Verify core setup
as-cli profile list
```

#### Step 2: Install Required Plugins
```bash
# Install plugins based on your needs
pip install <plugin-name>

# Verify plugin availability
as-cli plugin list
as-cli plugin info <plugin-name>
```

#### Step 3: Configure Each Environment
```bash
# Configure plugins for each environment using profiles
as-cli --profile dev <plugin-command> --configure
as-cli --profile staging <plugin-command> --configure
as-cli --profile prod <plugin-command> --configure
```

#### Step 4: Environment-Specific Workflows
```bash
# Development workflow
as-cli --profile dev <plugin-command> [options]

# Staging validation
as-cli --profile staging <plugin-command> [options]

# Production deployment
as-cli --profile prod <plugin-command> [options]
```

### Plugin Development Workflow

```bash
# 1. Create your plugin
mkdir external/my-custom-plugin
cd external/my-custom-plugin

# 2. Implement plugin (see plugin development section)
# 3. Install and test
pip install -e .
as-cli plugin list
as-cli my-command --help

# 4. Test with different profiles
as-cli --profile dev my-command
as-cli --profile prod my-command
```

## 🤝 Contributing

### Plugin Contributions

1. **Develop your plugin** following the plugin development guidelines
2. **Test thoroughly** with multiple profiles and environments
3. **Include comprehensive documentation** and examples
4. **Submit as separate repository** with proper entry points
5. **Add to community plugin registry**

### Core Contributions

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Test with multiple profiles**: Ensure profile compatibility
4. **Update documentation**: Include profile-aware examples
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open Pull Request**

### Development Guidelines

- **Profile Awareness**: All features should work with multiple profiles
- **Backward Compatibility**: Maintain compatibility with existing configurations
- **Auto-Initialization**: Features should work with automatic setup
- **Documentation**: Update both README and inline documentation
- **Testing**: Include tests for both single and multi-profile scenarios

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **📖 Documentation**: https://docs.appsentinels.com/cli
- **🐛 Issues**: https://github.com/appsentinels/as-cli/issues
- **🔌 Plugin Development**: See [Plugin Development Guide](external/README.md)
- **🏢 Profile Examples**: See [Profile Configuration Guide](examples/README-profiles.md)
- **📧 Email**: support@appsentinels.com

## 📋 Changelog

### v2.2.0 (Current) - Modular Architecture Release

#### 🏗️ Complete Architectural Overhaul
- **Lightweight Core CLI**: Essential commands only (auth, profile, plugin, init)
- **Plugin-Based Extensions**: Advanced features moved to external plugins
- **Modular Installation**: Install only the features you need
- **Performance Optimization**: Faster startup with reduced dependencies

#### 🔧 Auto-Configuration System
- **Automatic initialization** on first run or installation
- **Template file generation** (`.env.template`, `README.md`)
- **Manual initialization command** (`as-cli init`)
- **Configuration repair and validation**
- **Smart first-run detection** with helpful guidance

#### 🏢 Enhanced Profile Management  
- **File-based profile storage** in `~/.as-cli/profiles/`
- **Automatic legacy migration** from single-file configs
- **Profile isolation** with individual configuration files
- **Enhanced profile commands** with detailed information
- **Backup and restore** capabilities

#### 🔌 Advanced Plugin System
- **Enhanced plugin discovery** via Python entry points
- **Lifecycle management** with load/unload commands
- **Plugin metadata** and validation system
- **Profile integration**: Plugins fully compatible with multi-environment profiles
- **Error isolation**: Plugin failures don't affect core CLI functionality

## 🎯 Roadmap

### Immediate
- **🏪 Plugin Marketplace**: PyPI-based plugin discovery and installation
- **📚 Plugin Development Kit**: Comprehensive SDK and documentation
- **🤝 Community Plugin Registry**: Central listing of available plugins

### Future Vision
- **🌐 Plugin Ecosystem Marketplace**: Community-driven plugin repository
- **🔒 Enhanced Security Framework**: Plugin sandboxing and permission system
- **🚀 Performance Engine**: Advanced caching and optimization framework
- **🤖 Automation Platform**: Full workflow automation and orchestration

### Community Goals
- **👥 Open Source Plugins**: Encourage community plugin development
- **🎓 Educational Resources**: Tutorials, workshops, and certification programs
- **🤝 Partnership Program**: Integration with security and DevOps tool vendors