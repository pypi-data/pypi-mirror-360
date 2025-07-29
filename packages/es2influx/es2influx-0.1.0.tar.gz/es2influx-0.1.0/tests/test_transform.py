"""
Tests for data transformation functions
"""

from datetime import datetime

import pytest

from es2influx.config import (
    ChunkedMigrationConfig,
    ElasticsearchConfig,
    FieldMapping,
    InfluxDBConfig,
    MigrationConfig,
)
from es2influx.transform import (
    convert_data_type,
    document_to_line_protocol,
    escape_string_value,
    format_field_value,
    format_tag_value,
    transform_documents,
    validate_line_protocol,
)


class TestDataTypeConversion:
    """Test data type conversion functions"""

    def test_convert_data_type_string(self):
        """Test converting to string"""
        assert convert_data_type(123, "string") == "123"
        assert convert_data_type(True, "string") == "True"
        assert convert_data_type(None, "string") is None

    def test_convert_data_type_int(self):
        """Test converting to int"""
        assert convert_data_type("123", "int") == 123
        assert convert_data_type("123.45", "int") == 123
        assert convert_data_type(123.45, "int") == 123

    def test_convert_data_type_float(self):
        """Test converting to float"""
        assert convert_data_type("123.45", "float") == 123.45
        assert convert_data_type(123, "float") == 123.0

    def test_convert_data_type_bool(self):
        """Test converting to bool"""
        assert convert_data_type("true", "bool") is True
        assert convert_data_type("false", "bool") is False
        assert convert_data_type("1", "bool") is True
        assert convert_data_type("0", "bool") is False


class TestFieldFormatting:
    """Test field formatting functions"""

    def test_escape_string_value(self):
        """Test escaping string values"""
        assert escape_string_value("simple") == "simple"
        assert escape_string_value('with"quotes') == 'with\\"quotes'
        assert escape_string_value("with\\backslash") == "with\\\\backslash"

    def test_format_field_value_string(self):
        """Test formatting string field values"""
        assert format_field_value("test", "string") == '"test"'

    def test_format_field_value_int(self):
        """Test formatting integer field values"""
        assert format_field_value(123, "int") == "123i"

    def test_format_field_value_bool(self):
        """Test formatting boolean field values"""
        assert format_field_value(True, "bool") == "true"
        assert format_field_value(False, "bool") == "false"

    def test_format_tag_value(self):
        """Test formatting tag values"""
        assert format_tag_value("simple") == "simple"


class TestLineProtocolValidation:
    """Test line protocol validation"""

    def test_validate_line_protocol_valid(self):
        """Test validating valid line protocol"""
        valid_line = (
            'measurement,tag1=value1 field1=1i,field2="value" 1640995200000000000'
        )
        assert validate_line_protocol(valid_line) is True

    def test_validate_line_protocol_invalid(self):
        """Test validating invalid line protocol"""
        invalid_lines = [
            "",  # Empty line
            "measurement",  # No fields
        ]

        for line in invalid_lines:
            assert validate_line_protocol(line) is False


class TestDocumentTransformation:
    """Test document to line protocol transformation"""

    def _create_basic_config(self):
        """Create a basic migration config for testing"""
        return MigrationConfig(
            elasticsearch=ElasticsearchConfig(
                url="http://localhost:9200", index="test-*"
            ),
            influxdb=InfluxDBConfig(
                url="http://localhost:8086",
                token="test-token",
                org="test-org",
                bucket="test-bucket",
                measurement="test_measurement",
            ),
            timestamp_field="@timestamp",
            field_mappings=[
                FieldMapping(
                    es_field="@timestamp",
                    influx_field="time",
                    field_type="timestamp",
                    data_type="timestamp",
                ),
                FieldMapping(
                    es_field="service.name",
                    influx_field="service",
                    field_type="tag",
                    data_type="string",
                    default_value="unknown",
                ),
                FieldMapping(
                    es_field="message",
                    influx_field="message",
                    field_type="field",
                    data_type="string",
                ),
                FieldMapping(
                    es_field="status_code",
                    influx_field="status",
                    field_type="field",
                    data_type="int",
                ),
            ],
            chunked_migration=ChunkedMigrationConfig(),
        )

    def test_document_to_line_protocol_basic(self):
        """Test basic document to line protocol conversion"""
        config = self._create_basic_config()

        document = {
            "@timestamp": "2024-01-01T00:00:00Z",
            "service": {"name": "web-server"},
            "message": "Test message",
            "status_code": 200,
        }

        result = document_to_line_protocol(document, config)

        assert result is not None
        assert result.startswith("test_measurement,service=web-server")
        assert 'message="Test message"' in result
        assert "status=200i" in result
