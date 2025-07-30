# Profile Configuration Examples

This directory contains example profile configurations for the AppSentinels CLI. Profiles allow you to manage different environments (development, staging, production) with separate configuration settings stored as individual files.

## Overview

Profiles enable you to:
- Switch between different API endpoints (dev, staging, prod)
- Use different database connections
- Configure environment-specific settings
- Manage multiple accounts/environments easily
- Store configurations as separate files for better organization

## Automatic Configuration

The AppSentinels CLI automatically creates the required configuration structure when first run:

```
~/.as-cli/
├── config.yaml              # Main configuration (current profile)
├── .env.template            # Environment variables template
├── README.md                # Configuration documentation
└── profiles/                # Individual profile files
    ├── default.yaml         # Default profile
    └── [profile-name].yaml  # Additional profiles
```

## Manual Configuration Setup

If you want to manually set up example profiles, you can copy the example configuration:

```bash
# Option 1: Copy example as starting point (legacy format - will be migrated)
cp examples/profiles-config.yaml ~/.as-cli/config.yaml

# Option 2: Use the CLI to create profiles (recommended)
as-cli profile create production --description "Production environment"
as-cli profile create staging --description "Staging environment"
```

## Available Example Profiles

### `default`
- **Purpose**: Default development environment
- **API**: https://api-dev.appsentinels.com
- **Database**: Local ClickHouse (Docker)
- **Settings**: Development-friendly with verbose logging

### `staging`
- **Purpose**: Staging environment for testing
- **API**: https://api-staging.appsentinels.com  
- **Database**: Staging database server
- **Settings**: Higher batch sizes, continue on error

### `production`
- **Purpose**: Production environment
- **API**: https://api.appsentinels.com
- **Database**: Production cluster
- **Settings**: Conservative settings, no Docker, extensive retries

### `local`
- **Purpose**: Local development with Docker
- **API**: http://localhost:3000
- **Database**: Local ClickHouse (different port)
- **Settings**: Fast settings for local testing

## Profile Management Commands

### List Profiles
```bash
# List all available profiles
as-cli profile list

# List with detailed information
as-cli profile list --detailed
```

### Switch Profiles
```bash
# Switch to production profile
as-cli profile switch production

# Switch and save to config file
as-cli profile switch production --save
```

### Create New Profiles
```bash
# Create a new profile
as-cli profile create my-env --description "My custom environment"

# Create by copying existing profile
as-cli profile create my-prod --copy-from production --description "My production setup"

# Create and save to config file
as-cli profile create my-env --save
```

### View Profile Details
```bash
# Show current profile configuration
as-cli profile show

# Show specific profile
as-cli profile show production
```

### Delete Profiles
```bash
# Delete a profile
as-cli profile delete my-env

# Delete and save changes
as-cli profile delete my-env --save
```

## Using Profiles with Commands

### Command-line Profile Selection
```bash
# Use specific profile for a command
as-cli --profile production ingest config --show

# Use staging profile for data ingestion
as-cli --profile staging ingest records --file data.parquet --table-name logs
```

### Environment Variables
You can still override profile settings with environment variables:

```bash
# Override database password for production profile
AS_DB_PASSWORD=secret as-cli --profile production ingest config --show
```

## Profile Configuration Structure

Each profile contains the following sections:

### API Configuration
```yaml
api:
  base_url: https://api.example.com
  timeout: 30
  max_retries: 3
  retry_delay: 1
```

### Authentication
```yaml
auth:
  client_id: your-client-id
  auth_url: https://auth.example.com
  token_url: https://auth.example.com/oauth/token
  redirect_uri: http://localhost:8080/callback
  scope: api:read api:write
```

### Database
```yaml
database:
  db_type: clickhouse
  host: localhost
  port: 9000
  database: logs_db
  user: default
  docker_container: clickhouse-server
  use_docker: true
  connection_timeout: 30
```

### Output Settings
```yaml
output:
  default_format: table  # table, json, yaml, raw
  max_width: 120
  truncate_long_values: true
  show_headers: true
  color_output: true
```

### Ingest Settings
```yaml
ingest:
  schema_file: schema.json
  default_batch_size: 1000
  log_file: ingestion.log
  overwrite_log: true
  enable_ip_extraction: true
  enable_telemetry: true
  continue_on_error: false
  supported_formats: [parquet, json, csv]
```

## Best Practices

1. **Environment Separation**: Use different profiles for each environment
2. **Descriptive Names**: Use clear, descriptive profile names
3. **Security**: Don't store sensitive credentials in config files - use environment variables
4. **Backup**: Keep backup copies of your profile configurations
5. **Documentation**: Document what each profile is used for

## Environment Variables Override

Environment variables always take precedence over profile settings:

```bash
# Override database settings
export AS_DB_HOST=custom-host
export AS_DB_PASSWORD=secret-password

# Use profile with overrides
as-cli --profile production ingest config --show
```

## Migration from Legacy Configuration

The CLI automatically handles migration from legacy configurations:

1. **Single-file configs**: If you have an existing `~/.as-cli/config.yaml` with profiles, it will be automatically migrated to separate files in `~/.as-cli/profiles/`
2. **Backup preservation**: Your original configuration is preserved during migration
3. **Seamless upgrade**: Migration happens automatically on first run after upgrade

### Migration Process

```bash
# Before migration: Single file with all profiles
~/.as-cli/config.yaml  # Contains all profile data

# After migration: Separate files
~/.as-cli/
├── config.yaml              # Only current_profile setting
└── profiles/
    ├── default.yaml         # Individual profile files
    ├── production.yaml
    └── staging.yaml
```

### Manual Migration

If you need to manually trigger migration or initialization:

```bash
# Check what would be migrated
as-cli init --show-only

# Force re-initialization if needed
as-cli init --force

# Verify migration
as-cli profile list
```