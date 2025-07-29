"""
Tests for configuration loading and validation
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from es2influx.config import (
    ChunkedMigrationConfig,
    ElasticsearchConfig,
    FieldMapping,
    InfluxDBConfig,
    MigrationConfig,
    create_sample_config,
    load_config,
    substitute_env_variables,
)


class TestEnvironmentSubstitution:
    """Test environment variable substitution"""

    def test_substitute_env_variables_required(self):
        """Test substitution of required environment variables"""
        os.environ["TEST_VAR"] = "test_value"

        config = {"key": "${TEST_VAR}"}
        result = substitute_env_variables(config)
        assert result["key"] == "test_value"

        # Cleanup
        del os.environ["TEST_VAR"]

    def test_substitute_env_variables_with_default(self):
        """Test substitution with default values"""
        config = {"key": "${NONEXISTENT_VAR:-default_value}"}
        result = substitute_env_variables(config)
        assert result["key"] == "default_value"

    def test_substitute_env_variables_missing_required(self):
        """Test error when required environment variable is missing"""
        config = {"key": "${NONEXISTENT_VAR}"}

        with pytest.raises(
            ValueError,
            match="Required environment variable 'NONEXISTENT_VAR' is not set",
        ):
            substitute_env_variables(config)

    def test_substitute_env_variables_nested(self):
        """Test substitution in nested dictionaries"""
        os.environ["TEST_VAR"] = "nested_value"

        config = {"nested": {"key": "${TEST_VAR}", "other": "static_value"}}
        result = substitute_env_variables(config)
        assert result["nested"]["key"] == "nested_value"
        assert result["nested"]["other"] == "static_value"

        # Cleanup
        del os.environ["TEST_VAR"]

    def test_substitute_env_variables_list(self):
        """Test substitution in lists"""
        os.environ["TEST_VAR"] = "list_value"

        config = {"list": ["${TEST_VAR}", "static"]}
        result = substitute_env_variables(config)
        assert result["list"] == ["list_value", "static"]

        # Cleanup
        del os.environ["TEST_VAR"]


class TestConfigModels:
    """Test configuration model validation"""

    def test_influxdb_config_valid(self):
        """Test valid InfluxDB configuration"""
        config = InfluxDBConfig(
            url="http://localhost:8086",
            token="test_token",
            org="test_org",
            bucket="test_bucket",
            measurement="test_measurement",
        )
        assert config.url == "http://localhost:8086"
        assert config.auto_create_bucket is True  # Default value

    def test_influxdb_config_custom_batch_size(self):
        """Test InfluxDB configuration with custom batch size"""
        config = InfluxDBConfig(
            url="http://localhost:8086",
            token="test_token",
            org="test_org",
            bucket="test_bucket",
            measurement="test_measurement",
            batch_size=10000,
            auto_create_bucket=False,
        )
        assert config.batch_size == 10000
        assert config.auto_create_bucket is False

    def test_elasticsearch_config_valid(self):
        """Test valid Elasticsearch configuration"""
        config = ElasticsearchConfig(url="http://localhost:9200", index="test_index")
        assert config.url == "http://localhost:9200"
        assert config.scroll_size == 1000  # Default value

    def test_field_mapping_valid(self):
        """Test valid field mapping"""
        mapping = FieldMapping(
            es_field="test_field",
            influx_field="test_influx_field",
            field_type="tag",
            data_type="string",
        )
        assert mapping.es_field == "test_field"
        assert mapping.field_type == "tag"

    def test_chunked_migration_config_valid(self):
        """Test valid chunked migration configuration"""
        config = ChunkedMigrationConfig(
            enabled=True, chunk_size="1h", start_time="now-1d", end_time="now"
        )
        assert config.enabled is True
        assert config.chunk_size == "1h"
        assert config.max_retries == 3  # Default value


class TestConfigLoading:
    """Test configuration file loading"""

    def test_load_config_file_not_found(self):
        """Test loading non-existent config file"""
        with pytest.raises(FileNotFoundError):
            load_config(Path("/nonexistent/config.yaml"))

    def test_create_sample_config(self):
        """Test creating sample configuration file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = Path(f.name)

        try:
            create_sample_config(temp_path)
            assert temp_path.exists()

            # Load and validate the created config
            with open(temp_path, "r") as f:
                content = f.read()
                assert "elasticsearch:" in content
                assert "influxdb:" in content
                assert "field_mappings:" in content
                assert "${ES2INFLUX_INFLUX_TOKEN}" in content

        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

    def test_load_config_with_env_vars(self):
        """Test loading config with environment variable substitution"""
        # Set up environment variables
        os.environ.update(
            {
                "TEST_ES_URL": "http://test-es:9200",
                "TEST_INFLUX_TOKEN": "test_token",
                "TEST_INFLUX_ORG": "test_org",
                "TEST_INFLUX_BUCKET": "test_bucket",
            }
        )

        config_data = {
            "elasticsearch": {"url": "${TEST_ES_URL}", "index": "test-*"},
            "influxdb": {
                "url": "http://localhost:8086",
                "token": "${TEST_INFLUX_TOKEN}",
                "org": "${TEST_INFLUX_ORG}",
                "bucket": "${TEST_INFLUX_BUCKET}",
                "measurement": "test_measurement",
            },
            "timestamp_field": "@timestamp",
            "field_mappings": [
                {
                    "es_field": "@timestamp",
                    "influx_field": "time",
                    "field_type": "timestamp",
                    "data_type": "timestamp",
                }
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = Path(f.name)

        try:
            config = load_config(temp_path)
            assert config.elasticsearch.url == "http://test-es:9200"
            assert config.influxdb.token == "test_token"
            assert config.influxdb.org == "test_org"
            assert config.influxdb.bucket == "test_bucket"

        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()
            for key in [
                "TEST_ES_URL",
                "TEST_INFLUX_TOKEN",
                "TEST_INFLUX_ORG",
                "TEST_INFLUX_BUCKET",
            ]:
                if key in os.environ:
                    del os.environ[key]

    def test_load_config_invalid_yaml(self):
        """Test loading invalid YAML file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = Path(f.name)

        try:
            with pytest.raises(yaml.YAMLError):
                load_config(temp_path)
        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

    def test_load_config_missing_required_fields(self):
        """Test loading config with missing required fields"""
        config_data = {
            "elasticsearch": {"url": "http://localhost:9200", "index": "test-*"},
            # Missing influxdb configuration
            "timestamp_field": "@timestamp",
            "field_mappings": [],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(Exception):  # Should raise validation error
                load_config(temp_path)
        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()
