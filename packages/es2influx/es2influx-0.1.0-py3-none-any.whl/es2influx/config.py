"""
Configuration models and utilities for es2influx
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, validator
from rich.console import Console

console = Console()


class ValueTransformation(BaseModel):
    """Value transformation configuration for cleaning and normalizing data"""

    type: str = Field(
        ...,
        description="Transformation type: 'normalize_text', 'regex_replace', 'case_convert', 'character_replace', 'custom_mapping'",
    )

    # Conditional transformation - only apply if condition is met
    condition: Optional[str] = Field(
        default=None,
        description="Condition to check before applying transformation: 'equals', 'regex', 'contains', 'starts_with', 'ends_with'",
    )
    condition_value: Optional[str] = Field(
        default=None,
        description="Value to check against (exact match, regex pattern, or substring)",
    )
    condition_values: Optional[List[str]] = Field(
        default=None,
        description="List of values to check against (for multiple conditions)",
    )

    # For normalize_text
    lowercase: bool = Field(default=True, description="Convert to lowercase")
    replace_spaces: bool = Field(
        default=True, description="Replace spaces with underscores"
    )
    remove_special: bool = Field(default=True, description="Remove special characters")

    # For regex_replace
    pattern: Optional[str] = Field(default=None, description="Regex pattern to find")
    replacement: Optional[str] = Field(default=None, description="Replacement string")

    # For case_convert
    case_type: Optional[str] = Field(
        default=None,
        description="Case type: 'upper', 'lower', 'title', 'snake_case', 'camel_case'",
    )

    # For character_replace
    find_chars: Optional[str] = Field(default=None, description="Characters to find")
    replace_chars: Optional[str] = Field(
        default=None, description="Characters to replace with"
    )

    # For custom_mapping
    mappings: Optional[Dict[str, str]] = Field(
        default=None, description="Direct value mappings"
    )

    @validator("type")
    def validate_type(cls, v: str) -> str:
        allowed = {
            "normalize_text",
            "regex_replace",
            "case_convert",
            "character_replace",
            "custom_mapping",
        }
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return v

    @validator("condition")
    def validate_condition(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"equals", "regex", "contains", "starts_with", "ends_with"}
            if v not in allowed:
                raise ValueError(f"condition must be one of {allowed}")
        return v

    @validator("pattern")
    def validate_pattern(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v

    @validator("condition_value")
    def validate_condition_value(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Optional[str]:
        condition = values.get("condition")
        if condition == "regex" and v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern in condition_value: {e}")
        return v


class FieldMapping(BaseModel):
    """Mapping configuration for a single field"""

    es_field: str = Field(..., description="Source field name in Elasticsearch")
    influx_field: str = Field(..., description="Target field name in InfluxDB")
    field_type: str = Field(
        default="field",
        description="InfluxDB field type: 'field', 'tag', or 'timestamp'",
    )
    data_type: str = Field(
        default="string",
        description="Data type: 'string', 'float', 'int', 'bool', 'timestamp'",
    )
    default_value: Optional[Any] = Field(
        default=None, description="Default value if field is missing"
    )
    regex_pattern: Optional[str] = Field(
        default=None,
        description="Optional regex pattern to apply to the source field value",
    )
    regex_group: Optional[str] = Field(
        default=None, description="Named capture group to extract from regex pattern"
    )
    transformations: List[ValueTransformation] = Field(
        default_factory=list,
        description="List of transformations to apply to the field value",
    )

    @validator("field_type")
    def validate_field_type(cls, v: str) -> str:
        allowed = {"field", "tag", "timestamp"}
        if v not in allowed:
            raise ValueError(f"field_type must be one of {allowed}")
        return v

    @validator("data_type")
    def validate_data_type(cls, v: str) -> str:
        allowed = {"string", "float", "int", "bool", "timestamp"}
        if v not in allowed:
            raise ValueError(f"data_type must be one of {allowed}")
        return v

    @validator("regex_pattern")
    def validate_regex_pattern(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v


class RegexFieldGroup(BaseModel):
    """A group of fields extracted from a single source field using regex"""

    name: str = Field(..., description="Name for this regex group")
    influx_field: str = Field(..., description="Target field name in InfluxDB")
    field_type: str = Field(
        default="field",
        description="InfluxDB field type: 'field', 'tag', or 'timestamp'",
    )
    data_type: str = Field(
        default="string",
        description="Data type: 'string', 'float', 'int', 'bool', 'timestamp'",
    )
    default_value: Optional[Any] = Field(
        default=None, description="Default value if group is not captured"
    )
    transformations: List[ValueTransformation] = Field(
        default_factory=list,
        description="List of transformations to apply to the extracted value",
    )

    @validator("field_type")
    def validate_field_type(cls, v: str) -> str:
        allowed = {"field", "tag", "timestamp"}
        if v not in allowed:
            raise ValueError(f"field_type must be one of {allowed}")
        return v

    @validator("data_type")
    def validate_data_type(cls, v: str) -> str:
        allowed = {"string", "float", "int", "bool", "timestamp"}
        if v not in allowed:
            raise ValueError(f"data_type must be one of {allowed}")
        return v


class RegexFieldMapping(BaseModel):
    """Advanced regex-based field mapping that can extract multiple fields from one source"""

    es_field: str = Field(..., description="Source field name in Elasticsearch")
    regex_pattern: str = Field(
        ..., description="Regex pattern with named capture groups"
    )
    priority: int = Field(
        default=100,
        description="Priority for matching (lower numbers = higher priority)",
    )
    groups: List[RegexFieldGroup] = Field(
        ..., description="List of named groups to extract"
    )

    @validator("regex_pattern")
    def validate_regex_pattern(cls, v: str) -> str:
        try:
            compiled_pattern = re.compile(v)
            if not compiled_pattern.groupindex:
                raise ValueError("Regex pattern must contain named capture groups")
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v

    @validator("groups")
    def validate_groups_match_pattern(
        cls, v: List[RegexFieldGroup], values: Dict[str, Any]
    ) -> List[RegexFieldGroup]:
        if "regex_pattern" in values:
            try:
                compiled_pattern = re.compile(values["regex_pattern"])
                pattern_groups = set(compiled_pattern.groupindex.keys())
                config_groups = set(group.name for group in v)

                # Check if all configured groups exist in the pattern
                missing_groups = config_groups - pattern_groups
                if missing_groups:
                    raise ValueError(
                        f"Groups not found in regex pattern: {missing_groups}"
                    )

            except re.error:
                # Pattern validation will be handled by regex_pattern validator
                pass
        return v


class ComputedFieldCondition(BaseModel):
    """Condition for conditional regex logic in computed fields"""

    pattern: str = Field(..., description="Regex pattern to match")
    value: str = Field(..., description="Value to return if pattern matches")


class ComputedField(BaseModel):
    """Computed field that derives values from other fields or logic"""

    name: str = Field(..., description="Name of the computed field")
    influx_field: str = Field(..., description="Target field name in InfluxDB")
    field_type: str = Field(
        default="field",
        description="InfluxDB field type: 'field', 'tag', or 'timestamp'",
    )
    data_type: str = Field(
        default="string",
        description="Data type: 'string', 'float', 'int', 'bool', 'timestamp'",
    )
    logic: str = Field(
        ...,
        description="Logic type: 'regex_match', 'conditional_regex', 'numeric_comparison', 'static_value'",
    )

    # For regex_match logic
    source_field: Optional[str] = Field(
        default=None, description="Source field to evaluate"
    )
    patterns: Optional[List[str]] = Field(
        default=None, description="List of regex patterns for regex_match logic"
    )

    # For conditional_regex logic
    conditions: Optional[List[ComputedFieldCondition]] = Field(
        default=None, description="List of conditions for conditional_regex logic"
    )

    # For numeric_comparison logic
    operator: Optional[str] = Field(
        default=None, description="Comparison operator: 'lt', 'gt', 'eq', 'gte', 'lte'"
    )
    threshold: Optional[float] = Field(
        default=None, description="Threshold value for numeric comparison"
    )

    # For static_value logic
    value: Optional[Any] = Field(default=None, description="Static value to assign")

    # Default value if logic doesn't produce a result
    default_value: Optional[Any] = Field(
        default=None, description="Default value if logic fails"
    )

    # Optimization: whether to omit this tag when it has default/empty values
    omit_default: bool = Field(
        default=True,
        description="Skip this tag when it has default/meaningless values to reduce cardinality",
    )

    # Transformations to apply to the computed value
    transformations: List[ValueTransformation] = Field(
        default_factory=list,
        description="List of transformations to apply to the computed value",
    )

    @validator("field_type")
    def validate_field_type(cls, v: str) -> str:
        if v not in ["field", "tag", "timestamp"]:
            raise ValueError("field_type must be 'field', 'tag', or 'timestamp'")
        return v

    @validator("data_type")
    def validate_data_type(cls, v: str) -> str:
        if v not in ["string", "float", "int", "bool", "timestamp"]:
            raise ValueError(
                "data_type must be 'string', 'float', 'int', 'bool', or 'timestamp'"
            )
        return v

    @validator("logic")
    def validate_logic(cls, v: str) -> str:
        valid_logic = [
            "regex_match",
            "conditional_regex",
            "numeric_comparison",
            "static_value",
        ]
        if v not in valid_logic:
            raise ValueError(f"logic must be one of: {valid_logic}")
        return v


class LookupFieldGroup(BaseModel):
    """A group of fields extracted from a single source field using JSON lookup"""

    name: str = Field(..., description="Name of the field in the lookup JSON")
    influx_field: str = Field(..., description="Target field name in InfluxDB")
    field_type: str = Field(
        default="field",
        description="InfluxDB field type: 'field', 'tag', or 'timestamp'",
    )
    data_type: str = Field(
        default="string",
        description="Data type: 'string', 'float', 'int', 'bool', 'timestamp'",
    )
    default_value: Optional[Any] = Field(
        default=None, description="Default value if lookup key is not found"
    )
    transformations: List[ValueTransformation] = Field(
        default_factory=list,
        description="List of transformations to apply to the extracted value",
    )

    @validator("field_type")
    def validate_field_type(cls, v: str) -> str:
        allowed = {"field", "tag", "timestamp"}
        if v not in allowed:
            raise ValueError(f"field_type must be one of {allowed}")
        return v

    @validator("data_type")
    def validate_data_type(cls, v: str) -> str:
        allowed = {"string", "float", "int", "bool", "timestamp"}
        if v not in allowed:
            raise ValueError(f"data_type must be one of {allowed}")
        return v


class LookupFieldMapping(BaseModel):
    """JSON lookup-based field mapping that can extract multiple fields from one source"""

    es_field: str = Field(
        ..., description="Source field name in Elasticsearch (the lookup key)"
    )
    lookup_file: str = Field(
        ..., description="Path to JSON file containing the lookup mappings"
    )
    priority: int = Field(
        default=100,
        description="Priority for matching (lower numbers = higher priority)",
    )
    groups: List[LookupFieldGroup] = Field(
        ..., description="List of fields to extract from lookup result"
    )

    @validator("lookup_file")
    def validate_lookup_file(cls, v: str) -> str:
        lookup_path = Path(v)
        if not lookup_path.exists():
            raise ValueError(f"Lookup file not found: {v}")

        try:
            with open(lookup_path, "r") as f:
                lookup_data = json.load(f)

            if not isinstance(lookup_data, dict):
                raise ValueError("Lookup file must contain a JSON object")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in lookup file: {e}")
        except Exception as e:
            raise ValueError(f"Error reading lookup file: {e}")

        return v

    @validator("groups")
    def validate_groups_exist_in_lookup(
        cls, v: List[LookupFieldGroup], values: Dict[str, Any]
    ) -> List[LookupFieldGroup]:
        if "lookup_file" in values:
            try:
                lookup_path = Path(values["lookup_file"])
                if lookup_path.exists():
                    with open(lookup_path, "r") as f:
                        lookup_data = json.load(f)

                    # Check if lookup data has the expected structure
                    if lookup_data:
                        # Get first entry to check structure
                        first_entry = next(iter(lookup_data.values()))
                        if isinstance(first_entry, dict):
                            available_fields = set(first_entry.keys())
                            config_fields = set(group.name for group in v)

                            # Check if all configured fields exist in the lookup data
                            missing_fields = config_fields - available_fields
                            if missing_fields:
                                raise ValueError(
                                    f"Fields not found in lookup data: {missing_fields}"
                                )

            except Exception:
                # Validation will be handled by lookup_file validator
                pass
        return v


class ElasticsearchConfig(BaseModel):
    """Elasticsearch connection and query configuration"""

    url: str = Field(..., description="Elasticsearch URL")
    index: str = Field(..., description="Elasticsearch index name")
    query: Optional[Dict[str, Any]] = Field(
        default=None, description="Custom Elasticsearch query (optional)"
    )
    scroll_size: int = Field(
        default=1000, description="Number of documents per scroll request"
    )
    scroll_timeout: str = Field(default="10m", description="Scroll timeout duration")
    concurrency: int = Field(
        default=1, description="Number of concurrent connections to use"
    )
    throttle: int = Field(
        default=100, description="Delay in milliseconds between requests"
    )
    auth_user: Optional[str] = Field(default=None, description="Basic auth username")
    auth_password: Optional[str] = Field(
        default=None, description="Basic auth password"
    )


class InfluxDBConfig(BaseModel):
    """InfluxDB connection configuration"""

    url: str = Field(..., description="InfluxDB URL")
    token: str = Field(..., description="InfluxDB access token")
    org: str = Field(..., description="InfluxDB organization")
    bucket: str = Field(..., description="InfluxDB bucket name")
    measurement: str = Field(..., description="InfluxDB measurement name")
    batch_size: int = Field(
        default=5000, description="Number of points to write in each batch"
    )
    auto_create_bucket: bool = Field(
        default=True,
        description="Automatically create bucket if it doesn't exist with unlimited retention",
    )


class ChunkedMigrationConfig(BaseModel):
    """Configuration for chunked migration"""

    enabled: bool = Field(
        default=False, description="Enable chunked migration for large datasets"
    )
    chunk_size: str = Field(
        default="1h", description="Size of each chunk (e.g., '1h', '6h', '1d', '7d')"
    )
    start_time: Optional[str] = Field(
        default=None,
        description="Start time for migration (ISO format or relative like 'now-7d')",
    )
    end_time: Optional[str] = Field(
        default=None,
        description="End time for migration (ISO format or relative like 'now')",
    )
    state_file: str = Field(
        default="migration_state.json",
        description="File to store migration state for resume functionality",
    )
    max_retries: int = Field(
        default=3, description="Maximum number of retries per chunk"
    )
    retry_delay: int = Field(default=60, description="Delay in seconds between retries")
    parallel_chunks: int = Field(
        default=1,
        description="Number of chunks to process in parallel (use with caution)",
    )

    @validator("chunk_size")
    def validate_chunk_size(cls, v: str) -> str:
        """Validate chunk size format"""
        import re

        pattern = r"^(\d+)([hmwd])$"
        if not re.match(pattern, v):
            raise ValueError("chunk_size must be in format like '1h', '6h', '1d', '7d'")
        return v


class MigrationConfig(BaseModel):
    """Complete migration configuration"""

    elasticsearch: ElasticsearchConfig
    influxdb: InfluxDBConfig
    chunked_migration: ChunkedMigrationConfig = Field(
        default_factory=ChunkedMigrationConfig,
        description="Configuration for chunked migration",
    )
    field_mappings: List[FieldMapping] = Field(default_factory=list)
    regex_mappings: List[RegexFieldMapping] = Field(default_factory=list)
    lookup_mappings: List[LookupFieldMapping] = Field(default_factory=list)
    computed_fields: List[ComputedField] = Field(default_factory=list)
    timestamp_field: str = Field(
        default="@timestamp", description="Field to use as the timestamp"
    )
    output_file: Optional[str] = Field(
        default=None,
        description="Output file for line protocol (optional, for debugging)",
    )

    @validator("field_mappings")
    def validate_timestamp_mapping(
        cls, v: List[FieldMapping], values: Dict[str, Any]
    ) -> List[FieldMapping]:
        # Count timestamp fields from regular mappings
        timestamp_fields = [m for m in v if m.field_type == "timestamp"]

        # Also check regex mappings if they exist
        regex_mappings = values.get("regex_mappings", [])
        for regex_mapping in regex_mappings:
            timestamp_fields.extend(
                group
                for group in regex_mapping.groups
                if group.field_type == "timestamp"
            )

        # Check lookup mappings if they exist
        lookup_mappings = values.get("lookup_mappings", [])
        for lookup_mapping in lookup_mappings:
            timestamp_fields.extend(
                group
                for group in lookup_mapping.groups
                if group.field_type == "timestamp"
            )

        if len(timestamp_fields) != 1:
            raise ValueError("Exactly one field must be mapped as 'timestamp'")
        return v


def substitute_env_variables(config_data: dict) -> dict:
    """
    Recursively substitute environment variables in configuration data.

    Supports formats:
    - ${ENV_VAR} - Required environment variable
    - ${ENV_VAR:-default_value} - Environment variable with default
    - $ENV_VAR - Simple environment variable reference

    Args:
        config_data: Configuration dictionary

    Returns:
        Configuration dictionary with environment variables substituted
    """
    if isinstance(config_data, dict):
        return {
            key: substitute_env_variables(value) for key, value in config_data.items()
        }
    elif isinstance(config_data, list):
        return [substitute_env_variables(item) for item in config_data]
    elif isinstance(config_data, str):
        return substitute_env_vars_in_string(config_data)
    else:
        return config_data


def substitute_env_vars_in_string(text: str) -> str:
    """
    Substitute environment variables in a string.

    Supports:
    - ${VAR} - Required variable, raises error if not found
    - ${VAR:-default} - Variable with default value
    - $VAR - Simple variable reference (deprecated, use ${VAR})
    """

    def replace_var(match):
        var_expr = match.group(1)

        # Handle ${VAR:-default} format
        if ":-" in var_expr:
            var_name, default_value = var_expr.split(":-", 1)
            return os.getenv(var_name.strip(), default_value)

        # Handle ${VAR} format
        var_name = var_expr.strip()
        value = os.getenv(var_name)
        if value is None:
            raise ValueError(f"Required environment variable '{var_name}' is not set")
        return value

    # Handle ${VAR} and ${VAR:-default} patterns
    text = re.sub(r"\$\{([^}]+)\}", replace_var, text)

    # Handle simple $VAR pattern (legacy support)
    def replace_simple_var(match):
        var_name = match.group(1)
        value = os.getenv(var_name)
        if value is None:
            console.print(
                f"⚠️  Warning: Environment variable '{var_name}' not found, keeping original value"
            )
            return match.group(0)  # Return original if not found
        return value

    text = re.sub(r"\$([A-Z_][A-Z0-9_]*)", replace_simple_var, text)

    return text


def _load_dotenv_files(config_path: Path) -> None:
    """
    Load environment variables from .env files.

    Searches for .env files in the following order (later files override earlier ones):
    1. .env in the current working directory
    2. .env in the same directory as the config file
    3. Environment-specific files based on ES2INFLUX_ENV (.env.development, .env.production, etc.)
    4. .env.local in the same directory as the config file (for local overrides)

    Args:
        config_path: Path to the configuration file
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        # python-dotenv not installed, skip .env file loading
        return

    config_dir = config_path.parent
    current_dir = Path.cwd()

    # Get environment name from ES2INFLUX_ENV or NODE_ENV
    env_name = os.getenv("ES2INFLUX_ENV") or os.getenv("NODE_ENV")

    # Base .env files (in order of precedence)
    env_files = [
        current_dir / ".env",  # Global .env in current directory
        config_dir / ".env",  # .env next to config file
    ]

    # Add environment-specific files if environment is specified
    if env_name:
        env_files.extend(
            [
                current_dir
                / f".env.{env_name}",  # Environment-specific in current directory
                config_dir / f".env.{env_name}",  # Environment-specific next to config
            ]
        )

    # Add local override files (highest precedence)
    env_files.extend(
        [
            current_dir / ".env.local",  # Local overrides in current directory
            config_dir / ".env.local",  # Local overrides next to config
        ]
    )

    loaded_files = []
    for env_file in env_files:
        if env_file.exists():
            load_dotenv(env_file, override=True)
            loaded_files.append(str(env_file))

    if loaded_files:
        console.print(
            f"🔧 Loaded environment variables from: {', '.join(loaded_files)}"
        )

    if env_name:
        console.print(f"🌍 Environment: {env_name}")


def load_config(config_path: Union[str, Path]) -> MigrationConfig:
    """Load configuration from YAML file with environment variable substitution"""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Load environment variables from .env files
    _load_dotenv_files(config_path)

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)

    # Substitute environment variables
    try:
        config_data = substitute_env_variables(config_data)
    except ValueError as e:
        console.print(f"❌ Environment variable error: {e}")
        console.print("   Make sure all required environment variables are set")
        raise

    return MigrationConfig(**config_data)


def create_sample_config(output_path: Path) -> None:
    """Create a sample configuration file with environment variable examples"""
    sample_config = {
        "elasticsearch": {
            "url": "${ES2INFLUX_ES_URL:-http://localhost:9200}",
            "index": "${ES2INFLUX_ES_INDEX:-logs-*}",
            "scroll_size": 1000,
            "scroll_timeout": "10m",
            "concurrency": 4,
            "throttle": 100,
            # Optional authentication (uncomment if needed)
            # "auth_user": "${ES2INFLUX_ES_AUTH_USER}",
            # "auth_password": "${ES2INFLUX_ES_AUTH_PASSWORD}",
            "query": {"query": {"range": {"@timestamp": {"gte": "now-1d"}}}},
        },
        "influxdb": {
            "url": "${ES2INFLUX_INFLUX_URL:-http://localhost:8086}",
            "token": "${ES2INFLUX_INFLUX_TOKEN}",
            "org": "${ES2INFLUX_INFLUX_ORG}",
            "bucket": "${ES2INFLUX_INFLUX_BUCKET}",
            "measurement": "${ES2INFLUX_MEASUREMENT:-logs}",
            "batch_size": 5000,
            "auto_create_bucket": True,
        },
        "chunked_migration": {
            "enabled": False,
            "chunk_size": "1h",
            "start_time": "now-7d",
            "end_time": "now",
            "state_file": "migration_state.json",
            "max_retries": 3,
            "retry_delay": 60,
            "parallel_chunks": 1,
        },
        "timestamp_field": "@timestamp",
        "field_mappings": [
            {
                "es_field": "@timestamp",
                "influx_field": "time",
                "field_type": "timestamp",
                "data_type": "timestamp",
            },
            {
                "es_field": "host.name",
                "influx_field": "host",
                "field_type": "tag",
                "data_type": "string",
            },
            {
                "es_field": "service.name",
                "influx_field": "service",
                "field_type": "tag",
                "data_type": "string",
            },
            {
                "es_field": "message",
                "influx_field": "message",
                "field_type": "field",
                "data_type": "string",
            },
            {
                "es_field": "http.response.status_code",
                "influx_field": "status_code",
                "field_type": "field",
                "data_type": "int",
            },
            {
                "es_field": "http.response.body.bytes",
                "influx_field": "response_bytes",
                "field_type": "field",
                "data_type": "int",
            },
        ],
        "regex_mappings": [
            {
                "es_field": "userAgent",
                "regex_pattern": "speakeasy-sdk/(?P<Language>\\w+)\\s+(?P<SDKVersion>[\\d\\.]+)\\s+(?P<GenVersion>[\\d\\.]+)\\s+(?P<DocVersion>[\\d\\.]+)\\s+(?P<PackageName>[\\w\\.-]+)",
                "priority": 1,
                "groups": [
                    {
                        "name": "Language",
                        "influx_field": "sdk_language",
                        "field_type": "tag",
                        "data_type": "string",
                    },
                    {
                        "name": "SDKVersion",
                        "influx_field": "sdk_version",
                        "field_type": "tag",
                        "data_type": "string",
                    },
                ],
            }
        ],
    }

    # Write YAML file with environment variable comments
    with open(output_path, "w") as f:
        f.write("# ES2InfluxDB Configuration\n")
        f.write(
            "# Environment variables for sensitive data - set these before running:\n"
        )
        f.write("# \n")
        f.write("# Required:\n")
        f.write('# export ES2INFLUX_INFLUX_TOKEN="your-influxdb-token"\n')
        f.write('# export ES2INFLUX_INFLUX_ORG="your-org"\n')
        f.write('# export ES2INFLUX_INFLUX_BUCKET="your-bucket"\n')
        f.write("# \n")
        f.write("# Optional (with defaults):\n")
        f.write('# export ES2INFLUX_ES_URL="http://localhost:9200"\n')
        f.write('# export ES2INFLUX_ES_INDEX="logs-*"\n')
        f.write('# export ES2INFLUX_INFLUX_URL="http://localhost:8086"\n')
        f.write('# export ES2INFLUX_MEASUREMENT="logs"\n')
        f.write("# \n")
        f.write("# For authentication (if needed):\n")
        f.write('# export ES2INFLUX_ES_AUTH_USER="your-username"\n')
        f.write('# export ES2INFLUX_ES_AUTH_PASSWORD="your-password"\n')
        f.write("# \n")

        import yaml

        yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)

    console.print(f"✅ Sample configuration created at: {output_path}")
    console.print("📝 Edit this file to match your Elasticsearch and InfluxDB settings")
    console.print(
        "🔐 Set required environment variables before running (see comments in file)"
    )
    console.print("📘 For chunked migration, set chunked_migration.enabled to true")
