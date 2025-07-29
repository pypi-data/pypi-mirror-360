# ES2InfluxDB

A  CLI tool for migrating Elasticsearch data to InfluxDB.


## Roadmap

- [x] Initial POC with basic CLI commands
- [x] Advanced regex field mapping with named capture groups
- [x] Added data transformations, cleaning fields
- [x] Add support for json lookup mapping
- [x] Add chunk based migration with resume functionality
- [x] Environment variable support for secure configuration management
- [ ] Open Source this library (Packaging, versioning....)

## Prerequisites

Before using es2influx, you need to install the following dependencies:

### 1. Node.js and elasticdump

```bash
# Install Node.js (if not already installed)
# On macOS with Homebrew:
brew install node

# On Ubuntu/Debian:
sudo apt update && sudo apt install nodejs npm

# Install elasticdump globally
npm install -g elasticdump
```

### 2. InfluxDB CLI

```bash
# On macOS with Homebrew:
brew install influxdb-cli

# On Ubuntu/Debian:
curl -s https://repos.influxdata.com/influxdb.key | gpg --dearmor > /usr/share/keyrings/influxdb-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/influxdb-archive-keyring.gpg] https://repos.influxdata.com/debian stable main" > /etc/apt/sources.list.d/influxdb.list
sudo apt update && sudo apt install influxdb2-cli

# Or download from: https://docs.influxdata.com/influxdb/v2.0/tools/influx-cli/
```

## Installation

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd es2influx

# Install dependencies and create virtual environment
uv sync

# Install the package in development mode
uv pip install -e .
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd es2influx

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Quick Start

### 1. Check Dependencies

First, verify that all required tools are installed:

```bash
es2influx check
```

### 2. Generate Configuration

Create a sample configuration file:

```bash
es2influx init-config --output my-config.yaml
```

### 3. Set Environment Variables

For security, use environment variables for sensitive data. You can either export them manually or use a `.env` file (recommended):

**Option A: Using .env file (recommended)**
```bash
# Create .env file (automatically loaded by es2influx)
cat > .env << EOF
ES2INFLUX_INFLUX_TOKEN=your-influxdb-token
ES2INFLUX_INFLUX_ORG=your-org
ES2INFLUX_INFLUX_BUCKET=your-bucket
ES2INFLUX_ES_URL=http://localhost:9200
ES2INFLUX_ES_INDEX=logs-*
ES2INFLUX_MEASUREMENT=logs
EOF

# Add .env to .gitignore to keep secrets safe
echo ".env" >> .gitignore
```

**Option B: Manual export**
```bash
# Required environment variables
export ES2INFLUX_INFLUX_TOKEN="your-influxdb-token"
export ES2INFLUX_INFLUX_ORG="your-org"
export ES2INFLUX_INFLUX_BUCKET="your-bucket"

# Optional environment variables (with defaults)
export ES2INFLUX_ES_URL="http://localhost:9200"
export ES2INFLUX_ES_INDEX="logs-*"
export ES2INFLUX_INFLUX_URL="http://localhost:8086"
export ES2INFLUX_MEASUREMENT="logs"

# For authentication (if needed)
export ES2INFLUX_ES_AUTH_USER="your-username"
export ES2INFLUX_ES_AUTH_PASSWORD="your-password"
```

### 4. Edit Configuration

Edit the generated configuration file to match your setup. The config file uses environment variables for sensitive data:

```yaml
elasticsearch:
  url: "${ES2INFLUX_ES_URL:-http://localhost:9200}"
  index: "${ES2INFLUX_ES_INDEX:-logs-*}"
  scroll_size: 1000
  scroll_timeout: "10m"
  # Optional: Add authentication
  # auth_user: "${ES2INFLUX_ES_AUTH_USER}"
  # auth_password: "${ES2INFLUX_ES_AUTH_PASSWORD}"
  # Optional: Custom query
  query:
    query:
      range:
        "@timestamp":
          gte: "now-1d"

influxdb:
  url: "${ES2INFLUX_INFLUX_URL:-http://localhost:8086}"
  token: "${ES2INFLUX_INFLUX_TOKEN}"
  org: "${ES2INFLUX_INFLUX_ORG}"
  bucket: "${ES2INFLUX_INFLUX_BUCKET}"
  measurement: "${ES2INFLUX_MEASUREMENT:-logs}"
  batch_size: 5000

timestamp_field: "@timestamp"

field_mappings:
  - es_field: "@timestamp"
    influx_field: "time"
    field_type: "timestamp"
    data_type: "timestamp"
  
  - es_field: "host.name"
    influx_field: "host"
    field_type: "tag"
    data_type: "string"
  
  - es_field: "service.name"
    influx_field: "service"
    field_type: "tag"
    data_type: "string"
  
  - es_field: "message"
    influx_field: "message"
    field_type: "field"
    data_type: "string"
  
  - es_field: "http.response.status_code"
    influx_field: "status_code"
    field_type: "field"
    data_type: "int"
```

### 5. Validate Configuration

Test your configuration with sample data:

```bash
es2influx validate --config my-config.yaml --sample-size 10
```

### 6. Run Migration

Perform the actual migration:

```bash
# Dry run first (recommended)
es2influx migrate --config my-config.yaml --dry-run

# Regular migration
es2influx migrate --config my-config.yaml

# Chunked migration (if enabled in config)
es2influx migrate --config my-config.yaml --start-time "now-7d" --end-time "now"
```

## Commands

### Global Options

All commands support these global options:

- `--env, -e`: Environment name for loading `.env` files (e.g., development, production, staging)
- `--version`: Show version and exit

### `init-config`

Generate a sample configuration file:

```bash
es2influx init-config [--output PATH]
es2influx --env development init-config [--output PATH]
```

**Options:**
- `--output, -o`: Output path for the configuration file (default: `es2influx-config.yaml`)

### `check`

Check dependencies and validate configuration:

```bash
es2influx check [--config PATH]
```

**Options:**
- `--config, -c`: Path to configuration file to validate

### `validate`

Test configuration with sample data:

```bash
es2influx validate --config PATH [--sample-size N]
```

**Options:**
- `--config, -c`: Path to configuration file (required)
- `--sample-size, -n`: Number of sample documents to test (default: 10)

### `migrate`

Perform data migration from Elasticsearch to InfluxDB. Automatically detects whether to use regular or chunked migration based on configuration:

```bash
es2influx migrate --config PATH [OPTIONS]
```

**Regular Migration Options:**
- `--config, -c`: Path to configuration file (required)
- `--dry-run`: Perform a dry run without writing to InfluxDB
- `--output, -o`: Save line protocol to file for debugging
- `--batch-size`: Override batch size for processing
- `--debug`: Enable debug mode (keep temporary files)
- `--show-files`: Show paths to temporary files
- `--auto-create-bucket/--no-auto-create-bucket`: Override config setting for bucket creation

**Chunked Migration Options** (when `chunked_migration.enabled: true` in config):
- `--start-time`: Start time for migration (ISO format or relative like 'now-7d')
- `--end-time`: End time for migration (ISO format or relative like 'now')
- `--chunk-size`: Size of each chunk (e.g., '1h', '6h', '1d', '7d')
- `--resume`: Resume from previous incomplete migration
- `--reset`: Reset migration state and start fresh
- `--show-progress`: Show current migration progress and exit

**Examples:**
```bash
# Regular migration (chunked_migration.enabled: false)
es2influx migrate --config my-config.yaml

# Chunked migration (chunked_migration.enabled: true)
es2influx migrate --config my-config.yaml --start-time "now-7d" --end-time "now"

# Resume interrupted chunked migration
es2influx migrate --config my-config.yaml --resume

# Check chunked migration progress
es2influx migrate --config my-config.yaml --show-progress

# Reset chunked migration state
es2influx migrate --config my-config.yaml --reset

# Disable bucket auto-creation for this migration
es2influx migrate --config my-config.yaml --no-auto-create-bucket
```

### `test-regex`

Test regex patterns against sample data:

```bash
es2influx test-regex --config PATH [OPTIONS]
```

**Options:**
- `--config, -c`: Path to configuration file (required)
- `--sample-size, -n`: Number of sample documents to test (default: 5)
- `--regex-name, -r`: Test only a specific regex mapping by field name
- `--debug`: Enable debug mode (keep temporary files)

## Configuration Reference

### Environment Variables

ES2InfluxDB supports environment variable substitution for secure configuration management. This prevents sensitive data like tokens from being stored in configuration files.

#### Supported Formats

- `${VAR}` - Required environment variable (migration fails if not set)
- `${VAR:-default}` - Environment variable with default value
- `$VAR` - Simple variable reference (deprecated, use `${VAR}` instead)

#### Common Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ES2INFLUX_ES_URL` | Elasticsearch URL | No | `http://localhost:9200` |
| `ES2INFLUX_ES_INDEX` | Elasticsearch index pattern | No | `logs-*` |
| `ES2INFLUX_ES_AUTH_USER` | Elasticsearch username | No | None |
| `ES2INFLUX_ES_AUTH_PASSWORD` | Elasticsearch password | No | None |
| `ES2INFLUX_INFLUX_URL` | InfluxDB URL | No | `http://localhost:8086` |
| `ES2INFLUX_INFLUX_TOKEN` | InfluxDB access token | **Yes** | None |
| `ES2INFLUX_INFLUX_ORG` | InfluxDB organization | **Yes** | None |
| `ES2INFLUX_INFLUX_BUCKET` | InfluxDB bucket | **Yes** | None |
| `ES2INFLUX_MEASUREMENT` | InfluxDB measurement name | No | `logs` |

#### Setting Environment Variables

```bash
# Production example
export ES2INFLUX_ES_URL="https://prod-elasticsearch.company.com:9200"
export ES2INFLUX_ES_AUTH_USER="readonly-user"
export ES2INFLUX_ES_AUTH_PASSWORD="secure-password"
export ES2INFLUX_INFLUX_URL="https://prod-influxdb.company.com:8086"
export ES2INFLUX_INFLUX_TOKEN="your-production-token"
export ES2INFLUX_INFLUX_ORG="engineering"
export ES2INFLUX_INFLUX_BUCKET="production-logs"

# Run migration
es2influx migrate --config production-config.yaml
```

#### Environment Files (.env)

ES2InfluxDB automatically loads environment variables from multiple `.env` files with support for environment-specific configurations!

**Supported .env file locations (in order of precedence):**
1. `.env` in current working directory (base configuration)
2. `.env` in the same directory as your config file (base configuration)
3. `.env.{environment}` environment-specific files (e.g., `.env.development`, `.env.production`)
4. `.env.local` in both locations (local overrides - highest precedence)

**Environment Selection:**
- Set via `ES2INFLUX_ENV` environment variable
- Set via `NODE_ENV` environment variable (fallback)
- Set via `--env` CLI option: `es2influx --env production migrate --config config.yaml`

```bash
# Base configuration (.env)
cat > .env << EOF
ES2INFLUX_INFLUX_TOKEN=default-token
ES2INFLUX_INFLUX_ORG=default-org
ES2INFLUX_INFLUX_BUCKET=default-bucket
ES2INFLUX_ES_URL=http://localhost:9200
EOF

# Development environment (.env.development)
cat > .env.development << EOF
ES2INFLUX_INFLUX_TOKEN=dev-token
ES2INFLUX_INFLUX_ORG=dev-org
ES2INFLUX_INFLUX_BUCKET=dev-bucket
ES2INFLUX_MEASUREMENT=dev-logs
EOF

# Production environment (.env.production)
cat > .env.production << EOF
ES2INFLUX_INFLUX_TOKEN=prod-token
ES2INFLUX_INFLUX_ORG=prod-org
ES2INFLUX_INFLUX_BUCKET=prod-bucket
ES2INFLUX_ES_URL=https://prod-elasticsearch.company.com:9200
ES2INFLUX_MEASUREMENT=production-logs
EOF

# Local overrides (.env.local) - never commit to version control
cat > .env.local << EOF
ES2INFLUX_INFLUX_TOKEN=my-local-token
EOF

# Usage examples:
# Development environment
es2influx --env development migrate --config config.yaml

# Production environment  
ES2INFLUX_ENV=production es2influx migrate --config config.yaml

# Base environment (uses .env + .env.local)
es2influx migrate --config config.yaml
```

**Benefits of multiple .env files:**
- **Environment isolation**: Separate configs for dev/staging/prod
- **Automatic loading**: No need to `source` or `export`
- **Secure defaults**: Keep sensitive data out of version control
- **Local overrides**: Personal settings without affecting team config
- **CLI flexibility**: Switch environments with `--env` option
- **Precedence control**: Later files override earlier ones

**Recommended .gitignore:**
```bash
# Add to .gitignore to keep secrets safe
.env
.env.local
.env.*.local
# You can commit .env.example, .env.development, .env.production (without real secrets)
```

### Elasticsearch Configuration

```yaml
elasticsearch:
  url: "${ES2INFLUX_ES_URL:-http://localhost:9200}"    # Elasticsearch URL
  index: "${ES2INFLUX_ES_INDEX:-logs-*}"               # Index pattern to export
  scroll_size: 1000                     # Documents per scroll request
  scroll_timeout: "10m"                 # Scroll timeout
  auth_user: "${ES2INFLUX_ES_AUTH_USER}"               # Optional: Basic auth username
  auth_password: "${ES2INFLUX_ES_AUTH_PASSWORD}"       # Optional: Basic auth password
  query:                                # Optional: Custom query
    query:
      range:
        "@timestamp":
          gte: "now-1d"
```

### InfluxDB Configuration

```yaml
influxdb:
  url: "${ES2INFLUX_INFLUX_URL:-http://localhost:8086}" # InfluxDB URL
  token: "${ES2INFLUX_INFLUX_TOKEN}"                    # InfluxDB access token
  org: "${ES2INFLUX_INFLUX_ORG}"                       # InfluxDB organization
  bucket: "${ES2INFLUX_INFLUX_BUCKET}"                 # Target bucket
  measurement: "${ES2INFLUX_MEASUREMENT:-logs}"        # Measurement name
  batch_size: 5000                      # Batch size for writes
  auto_create_bucket: true              # Auto-create bucket if it doesn't exist
```

#### Bucket Auto-Creation

ES2InfluxDB can automatically create the target InfluxDB bucket if it doesn't exist. This feature is enabled by default and creates buckets with **unlimited retention** (no data expiration).

**Configuration:**
- `auto_create_bucket: true` (default) - Automatically create bucket if needed
- `auto_create_bucket: false` - Require bucket to exist before migration

**CLI Override:**
```bash
# Force bucket creation even if config disables it
es2influx migrate --config my-config.yaml --auto-create-bucket

# Disable bucket creation even if config enables it
es2influx migrate --config my-config.yaml --no-auto-create-bucket
```

**Benefits:**
- Simplified setup - no need to manually create buckets
- Consistent retention policy - unlimited retention by default
- Fail-safe operation - migration stops if bucket creation fails
- Permissions validation - confirms write access to InfluxDB

### Chunked Migration Configuration

For large datasets (>1TB), use chunked migration to process data in time-based chunks:

```yaml
chunked_migration:
  enabled: true                         # Enable chunked migration
  chunk_size: "1h"                      # Chunk size (1h, 6h, 1d, 7d)
  start_time: "now-7d"                  # Start time (ISO or relative)
  end_time: "now"                       # End time (ISO or relative)
  state_file: "migration_state.json"    # State file for resume
  max_retries: 3                        # Max retries per chunk
  retry_delay: 60                       # Delay between retries (seconds)
  parallel_chunks: 1                    # Parallel processing (experimental)
```

**Time Formats:**
- Relative: `now-7d`, `now-24h`, `now-1w`
- ISO: `2024-01-01T00:00:00Z`, `2024-01-01T00:00:00`

**Chunk Sizes:**
- `1h`, `6h`, `12h` - For high-volume data
- `1d`, `7d` - For moderate volume data
- `1w`, `1m` - For low volume data

### Field Mappings

Field mappings define how Elasticsearch fields are transformed to InfluxDB format:

```yaml
field_mappings:
  - es_field: "source.field.path"       # Dot notation for nested fields
    influx_field: "target_field"         # InfluxDB field name
    field_type: "field"                  # "field", "tag", or "timestamp"
    data_type: "string"                  # Data type conversion
    default_value: "default"             # Optional: default if missing
    regex_pattern: "pattern"             # Optional: regex to apply to field
    regex_group: "group_name"            # Optional: named group to extract
```

### Advanced Regex Mappings

For complex data parsing (like user agent strings), you can use regex mappings to extract multiple fields from a single source field:

```yaml
regex_mappings:
  - es_field: "userAgent"                # Source field to parse
    regex_pattern: "speakeasy-sdk/(?P<Language>\\w+)\\s+(?P<SDKVersion>[\\d\\.]+)\\s+(?P<GenVersion>[\\d\\.]+)\\s+(?P<DocVersion>[\\d\\.]+)\\s+(?P<PackageName>[\\w\\.-]+)"
    groups:                              # Named groups to extract
      - name: "Language"
        influx_field: "sdk_language"
        field_type: "tag"
        data_type: "string"
      - name: "SDKVersion"
        influx_field: "sdk_version"
        field_type: "tag"
        data_type: "string"
```

#### Field Types

- **`field`**: Regular InfluxDB field (measurable values)
- **`tag`**: InfluxDB tag (indexed metadata)
- **`timestamp`**: Timestamp field (exactly one required)

#### Data Types

- **`string`**: Text values
- **`int`**: Integer numbers
- **`float`**: Floating point numbers
- **`bool`**: Boolean values
- **`timestamp`**: Timestamp values (automatically converted to nanoseconds)

## Advanced Usage

### Chunked Migration for Large Datasets

For large datasets (>1TB), enable chunked migration in your config and use the regular migrate command:

```bash
# Enable chunked migration in config (chunked_migration.enabled: true)
# Then start migration with 1-hour chunks
es2influx migrate --config my-config.yaml --chunk-size 1h --start-time "now-7d" --end-time "now"

# Resume an interrupted migration
es2influx migrate --config my-config.yaml --resume

# Check progress of current migration
es2influx migrate --config my-config.yaml --show-progress

# Reset and start fresh
es2influx migrate --config my-config.yaml --reset
```

**Benefits of Chunked Migration:**
- **Resume capability**: If migration fails, resume from where it left off
- **Progress tracking**: Monitor migration progress and completion percentage
- **Resource management**: Process data in smaller chunks to avoid memory issues
- **Fault tolerance**: Automatic retry logic for failed chunks
- **State persistence**: Migration state is saved to disk for recovery

**Configuration Example:**
```yaml
chunked_migration:
  enabled: true
  chunk_size: "1h"                    # Start with 1-hour chunks for testing
  start_time: "now-7d"               # Process last 7 days
  end_time: "now"                    # Up to current time
  state_file: "migration_state.json" # State file for resume
  max_retries: 3                     # Retry failed chunks up to 3 times
  retry_delay: 60                    # Wait 60 seconds between retries
```

### Custom Queries

You can specify custom Elasticsearch queries to filter data:

```yaml
elasticsearch:
  query:
    query:
      bool:
        must:
          - range:
              "@timestamp":
                gte: "2024-01-01"
                lte: "2024-01-31"
          - term:
              "service.name": "web-server"
        must_not:
          - term:
              "log.level": "debug"
```

### Nested Field Access

Use dot notation to access nested fields:

```yaml
field_mappings:
  - es_field: "kubernetes.pod.name"
    influx_field: "pod_name"
    field_type: "tag"
    data_type: "string"
  
  - es_field: "http.request.headers.user-agent"
    influx_field: "user_agent"
    field_type: "field"
    data_type: "string"
```

### Using Regex Patterns

You can use regex patterns in two ways:

#### Simple Regex on Field Mappings

Apply a regex pattern to extract a value from a field:

```yaml
field_mappings:
  - es_field: "message"
    influx_field: "error_code"
    field_type: "tag"
    data_type: "string"
    regex_pattern: "ERROR\\s+(\\d+):"     # Extract error code
    regex_group: "1"                      # Use first capture group
    default_value: "unknown"              # Default if no match
```

#### Advanced Multi-field Regex Extraction

Extract multiple fields from a single source using named groups:

```yaml
regex_mappings:
  - es_field: "request_info"
    regex_pattern: "(?P<Method>GET|POST|PUT|DELETE)\\s+(?P<Path>/[^\\s]*)\\s+HTTP/(?P<Version>[\\d\\.]+)"
    groups:
      - name: "Method"
        influx_field: "http_method"
        field_type: "tag"
        data_type: "string"
      - name: "Path"
        influx_field: "http_path"
        field_type: "tag"
        data_type: "string"
      - name: "Version"
        influx_field: "http_version"
        field_type: "field"
        data_type: "string"
```

#### Testing Regex Patterns

Before running the full migration, test your regex patterns:

```bash
# Test all regex mappings
es2influx test-regex --config my-config.yaml

# Test a specific regex mapping
es2influx test-regex --config my-config.yaml --regex-name userAgent

# Test with more sample documents
es2influx test-regex --config my-config.yaml --sample-size 20
```

### Performance Tuning

For large datasets, consider adjusting these parameters:

```yaml
elasticsearch:
  scroll_size: 5000                     # Increase for faster export
  scroll_timeout: "30m"                 # Longer timeout for large datasets

influxdb:
  batch_size: 10000                     # Larger batches for better throughput
```

### Debugging

Save line protocol output for debugging:

```bash
es2influx migrate --config my-config.yaml --output debug.lp --dry-run
```

This creates a file with the line protocol format that would be sent to InfluxDB.

## Troubleshooting

### Common Issues

1. **"Environment variable error: Required environment variable 'VAR_NAME' is not set"**
   - Create a `.env` file with your variables (recommended), or export them manually
   - Check that all required environment variables are set before running
   - Required variables: `ES2INFLUX_INFLUX_TOKEN`, `ES2INFLUX_INFLUX_ORG`, `ES2INFLUX_INFLUX_BUCKET`
   - If using `.env` files, ensure the file is in the correct location (current directory or config directory)

2. **"elasticdump not found"**
   - Install elasticdump: `npm install -g elasticdump`
   - Ensure Node.js is installed

3. **"influx not found"**
   - Install InfluxDB CLI from the official documentation
   - Ensure it's in your PATH

4. **"Invalid line protocol"**
   - Check field mappings in your configuration
   - Use `validate` command to test with sample data
   - Ensure timestamp field is properly mapped

5. **"Connection refused"**
   - Verify Elasticsearch/InfluxDB URLs are correct
   - Check authentication credentials
   - Ensure services are running

5. **"Chunked migration stuck or slow"**
   - Check your chunk size - start with 1h for testing
   - Monitor Elasticsearch and InfluxDB performance
   - Use `es2influx migrate --config config.yaml --show-progress` to check status
   - Consider reducing batch size in config

6. **"Too many failed chunks"**
   - Check timestamp field mapping
   - Verify time range contains data
   - Increase `max_retries` in chunked_migration config
   - Use `--debug` to see detailed error messages

7. **"Failed to ensure InfluxDB bucket exists"** or **"Failed to create bucket"**
   - Verify your InfluxDB token has write permissions for the organization
   - Check that the InfluxDB URL is correct and accessible
   - Ensure your token has bucket creation permissions (Admin or Write access)
   - Test connection: `influx bucket list --org YOUR_ORG --token YOUR_TOKEN`
   - Disable auto-creation and manually create bucket: `--no-auto-create-bucket`

### Debug Mode

For detailed output, you can run with verbose logging by checking the elasticdump and influx CLI outputs in the console.

## Examples

### Migrating Application Logs

```yaml
elasticsearch:
  url: "${ES2INFLUX_ES_URL:-http://es.company.com:9200}"
  index: "${ES2INFLUX_ES_INDEX:-app-logs-*}"
  query:
    query:
      range:
        "@timestamp":
          gte: "now-7d"

influxdb:
  url: "${ES2INFLUX_INFLUX_URL:-http://influx.company.com:8086}"
  token: "${ES2INFLUX_INFLUX_TOKEN}"
  org: "${ES2INFLUX_INFLUX_ORG:-engineering}"
  bucket: "${ES2INFLUX_INFLUX_BUCKET:-application-metrics}"
  measurement: "${ES2INFLUX_MEASUREMENT:-app_logs}"

field_mappings:
  - es_field: "@timestamp"
    influx_field: "time"
    field_type: "timestamp"
    data_type: "timestamp"
  
  - es_field: "app.name"
    influx_field: "application"
    field_type: "tag"
    data_type: "string"
  
  - es_field: "log.level"
    influx_field: "level"
    field_type: "tag"
    data_type: "string"
  
  - es_field: "response_time"
    influx_field: "response_time_ms"
    field_type: "field"
    data_type: "float"
```

### Migrating System Metrics

```yaml
elasticsearch:
  url: "${ES2INFLUX_ES_URL:-http://localhost:9200}"
  index: "${ES2INFLUX_ES_INDEX:-metricbeat-*}"

influxdb:
  url: "${ES2INFLUX_INFLUX_URL:-http://localhost:8086}"
  token: "${ES2INFLUX_INFLUX_TOKEN}"
  org: "${ES2INFLUX_INFLUX_ORG:-ops}"
  bucket: "${ES2INFLUX_INFLUX_BUCKET:-system-metrics}"
  measurement: "${ES2INFLUX_MEASUREMENT:-system}"

field_mappings:
  - es_field: "@timestamp"
    influx_field: "time"
    field_type: "timestamp"
    data_type: "timestamp"
  
  - es_field: "host.hostname"
    influx_field: "host"
    field_type: "tag"
    data_type: "string"
  
  - es_field: "system.cpu.user.pct"
    influx_field: "cpu_user_percent"
    field_type: "field"
    data_type: "float"
  
  - es_field: "system.memory.used.bytes"
    influx_field: "memory_used_bytes"
    field_type: "field"
    data_type: "int"
```

### Parsing User Agent Strings with Regex

```yaml
elasticsearch:
  url: "${ES2INFLUX_ES_URL:-http://localhost:9200}"
  index: "${ES2INFLUX_ES_INDEX:-api-logs-*}"

influxdb:
  url: "${ES2INFLUX_INFLUX_URL:-http://localhost:8086}"
  token: "${ES2INFLUX_INFLUX_TOKEN}"
  org: "${ES2INFLUX_INFLUX_ORG:-product}"
  bucket: "${ES2INFLUX_INFLUX_BUCKET:-api-telemetry}"
  measurement: "${ES2INFLUX_MEASUREMENT:-api_requests}"

field_mappings:
  - es_field: "@timestamp"
    influx_field: "time"
    field_type: "timestamp"
    data_type: "timestamp"
  
  - es_field: "api.endpoint"
    influx_field: "endpoint"
    field_type: "tag"
    data_type: "string"

regex_mappings:
  # Parse Speakeasy SDK user agent strings
  - es_field: "userAgent"
    regex_pattern: "speakeasy-sdk/(?P<Language>\\w+)\\s+(?P<SDKVersion>[\\d\\.]+)\\s+(?P<GenVersion>[\\d\\.]+)\\s+(?P<DocVersion>[\\d\\.]+)\\s+(?P<PackageName>[\\w\\.-]+)"
    groups:
      - name: "Language"
        influx_field: "sdk_language"
        field_type: "tag"
        data_type: "string"
      - name: "SDKVersion"
        influx_field: "sdk_version"
        field_type: "tag"
        data_type: "string"
      - name: "GenVersion"
        influx_field: "gen_version"
        field_type: "field"
        data_type: "string"
      - name: "DocVersion"
        influx_field: "doc_version"
        field_type: "field"
        data_type: "string"
      - name: "PackageName"
        influx_field: "package_name"
        field_type: "tag"
        data_type: "string"
```

### Large Dataset Migration with Chunking

For migrating large datasets (>1TB), use chunked migration:

```yaml
elasticsearch:
  url: "${ES2INFLUX_ES_URL:-http://production-es.company.com:9200}"
  index: "${ES2INFLUX_ES_INDEX:-logs-2024-*}"
  scroll_size: 5000
  scroll_timeout: "30m"
  concurrency: 4
  throttle: 50

influxdb:
  url: "${ES2INFLUX_INFLUX_URL:-http://production-influx.company.com:8086}"
  token: "${ES2INFLUX_INFLUX_TOKEN}"
  org: "${ES2INFLUX_INFLUX_ORG:-engineering}"
  bucket: "${ES2INFLUX_INFLUX_BUCKET:-production-logs}"
  measurement: "${ES2INFLUX_MEASUREMENT:-application_logs}"
  batch_size: 10000

chunked_migration:
  enabled: true
  chunk_size: "1h"                    # Start with 1-hour chunks
  start_time: "2024-01-01T00:00:00Z"  # Specific start date
  end_time: "2024-01-31T23:59:59Z"    # Specific end date
  state_file: "prod_migration_state.json"
  max_retries: 5
  retry_delay: 120                    # 2 minutes between retries
  parallel_chunks: 1                  # Conservative for production

timestamp_field: "@timestamp"

field_mappings:
  - es_field: "@timestamp"
    influx_field: "time"
    field_type: "timestamp"
    data_type: "timestamp"
  
  - es_field: "application.name"
    influx_field: "app"
    field_type: "tag"
    data_type: "string"
  
  - es_field: "log.level"
    influx_field: "level"
    field_type: "tag"
    data_type: "string"
  
  - es_field: "response_time_ms"
    influx_field: "response_time"
    field_type: "field"
    data_type: "float"
```

**Migration Commands:**
```bash
# Start the migration using production environment
es2influx --env production migrate --config production-config.yaml

# Alternative: set environment variable
ES2INFLUX_ENV=production es2influx migrate --config production-config.yaml

# Check progress (run in another terminal)
es2influx --env production migrate --config production-config.yaml --show-progress

# Resume if interrupted
es2influx --env production migrate --config production-config.yaml --resume
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create a new issue with detailed information about your problem

## Related Projects

- [elasticdump](https://github.com/elasticsearch-dump/elasticsearch-dump) - The underlying tool for Elasticsearch data export
- [InfluxDB](https://www.influxdata.com/) - Time series database
- [Typer](https://typer.tiangolo.com/) - CLI framework used for this tool 
