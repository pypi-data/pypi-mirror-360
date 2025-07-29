"""
Tests for utility functions
"""

import json
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from es2influx.config import (
    ChunkedMigrationConfig,
    ElasticsearchConfig,
    FieldMapping,
    InfluxDBConfig,
    MigrationConfig,
)
from es2influx.utils import (
    MigrationState,
    build_chunk_query,
    check_dependencies,
    check_influxdb_bucket_exists,
    create_influxdb_bucket,
    ensure_influxdb_bucket_exists,
    estimate_file_lines,
    generate_time_chunks,
    get_temp_file,
    parse_chunk_size,
    parse_time_string,
)


class TestDependencyChecking:
    """Test dependency checking functions"""

    @patch("subprocess.run")
    def test_check_dependencies_all_available(self, mock_run):
        """Test when all dependencies are available"""
        mock_run.return_value.returncode = 0

        deps = check_dependencies()
        assert deps["elasticdump"] is True
        assert deps["influx"] is True
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    def test_check_dependencies_missing(self, mock_run):
        """Test when dependencies are missing"""
        mock_run.side_effect = FileNotFoundError()

        deps = check_dependencies()
        assert deps["elasticdump"] is False
        assert deps["influx"] is False

    @patch("subprocess.run")
    def test_check_dependencies_timeout(self, mock_run):
        """Test when dependency check times out"""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["test"], timeout=10)

        deps = check_dependencies()
        assert deps["elasticdump"] is False
        assert deps["influx"] is False


class TestTimeHandling:
    """Test time parsing and manipulation functions"""

    def test_parse_time_string_now(self):
        """Test parsing 'now' time string"""
        result = parse_time_string("now")
        assert isinstance(result, datetime)
        # Should be close to current time (within 1 second)
        assert abs((datetime.utcnow() - result).total_seconds()) < 1

    def test_parse_time_string_relative_past(self):
        """Test parsing relative past time strings"""
        now = datetime.utcnow()

        # Test hours
        result = parse_time_string("now-1h")
        expected = now - timedelta(hours=1)
        assert abs((result - expected).total_seconds()) < 1

        # Test days
        result = parse_time_string("now-7d")
        expected = now - timedelta(days=7)
        assert abs((result - expected).total_seconds()) < 1

        # Test weeks
        result = parse_time_string("now-2w")
        expected = now - timedelta(weeks=2)
        assert abs((result - expected).total_seconds()) < 1

    def test_parse_time_string_relative_future(self):
        """Test parsing relative future time strings"""
        now = datetime.utcnow()

        result = parse_time_string("now+1h")
        expected = now + timedelta(hours=1)
        # Allow for small timing differences during test execution
        assert abs((result - expected).total_seconds()) < 5

    def test_parse_time_string_iso_format(self):
        """Test parsing ISO format time strings"""
        iso_string = "2024-01-01T12:00:00Z"
        result = parse_time_string(iso_string)
        expected = datetime(2024, 1, 1, 12, 0, 0)
        assert result == expected

    def test_parse_time_string_invalid_format(self):
        """Test parsing invalid time format"""
        with pytest.raises(ValueError):
            parse_time_string("invalid-time-format")

    def test_parse_chunk_size_valid(self):
        """Test parsing valid chunk sizes"""
        assert parse_chunk_size("1h") == timedelta(hours=1)
        assert parse_chunk_size("6h") == timedelta(hours=6)
        assert parse_chunk_size("1d") == timedelta(days=1)
        assert parse_chunk_size("7d") == timedelta(days=7)
        assert parse_chunk_size("1w") == timedelta(weeks=1)
        assert parse_chunk_size("30m") == timedelta(minutes=30)

    def test_parse_chunk_size_invalid(self):
        """Test parsing invalid chunk sizes"""
        with pytest.raises(ValueError):
            parse_chunk_size("invalid")

        with pytest.raises(ValueError):
            parse_chunk_size("1x")

    def test_generate_time_chunks(self):
        """Test generating time chunks"""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 3, 0, 0)
        chunk_size = timedelta(hours=1)

        chunks = generate_time_chunks(start, end, chunk_size)

        assert len(chunks) == 3
        assert chunks[0] == (start, start + chunk_size)
        assert chunks[1] == (start + chunk_size, start + 2 * chunk_size)
        assert chunks[2] == (start + 2 * chunk_size, end)

    def test_generate_time_chunks_uneven(self):
        """Test generating time chunks with uneven division"""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 2, 30, 0)  # 2.5 hours
        chunk_size = timedelta(hours=1)

        chunks = generate_time_chunks(start, end, chunk_size)

        assert len(chunks) == 3
        assert chunks[0] == (start, start + chunk_size)
        assert chunks[1] == (start + chunk_size, start + 2 * chunk_size)
        assert chunks[2] == (start + 2 * chunk_size, end)  # Last chunk is 30 minutes


class TestMigrationState:
    """Test migration state management"""

    def test_migration_state_initialization(self):
        """Test migration state initialization"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            state = MigrationState(temp_path)
            assert state.state["migration_id"] is None
            assert state.state["completed_chunks"] == []
            assert state.state["failed_chunks"] == []
            assert state.state["total_documents"] == 0
            assert state.state["total_points_written"] == 0
            assert state.state["total_failures"] == 0

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_migration_state_persistence(self):
        """Test that migration state persists across instances"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Initialize and modify state
            state1 = MigrationState(temp_path)
            start_time = datetime(2024, 1, 1, 0, 0, 0)
            end_time = datetime(2024, 1, 1, 1, 0, 0)
            state1.initialize_migration(start_time, end_time, "1h", 1)

            migration_id = state1.state["migration_id"]
            assert migration_id is not None

            # Create new instance and check persistence
            state2 = MigrationState(temp_path)
            assert state2.state["migration_id"] == migration_id
            assert state2.state["start_time"] == start_time.isoformat()
            assert state2.state["end_time"] == end_time.isoformat()

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_migration_state_chunk_completion(self):
        """Test marking chunks as completed"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            state = MigrationState(temp_path)
            start_time = datetime(2024, 1, 1, 0, 0, 0)
            end_time = datetime(2024, 1, 1, 1, 0, 0)

            state.mark_chunk_completed(start_time, end_time, 100, 95)

            assert state.state["total_documents"] == 100
            assert state.state["total_points_written"] == 95
            assert len(state.state["completed_chunks"]) == 1
            assert state.is_chunk_completed(start_time, end_time) is True

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_migration_state_chunk_failure(self):
        """Test marking chunks as failed"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            state = MigrationState(temp_path)
            start_time = datetime(2024, 1, 1, 0, 0, 0)
            end_time = datetime(2024, 1, 1, 1, 0, 0)

            state.mark_chunk_failed(start_time, end_time, "Test error")

            assert state.state["total_failures"] == 1
            assert len(state.state["failed_chunks"]) == 1
            assert state.get_chunk_retry_count(start_time, end_time) == 1

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_migration_state_progress_tracking(self):
        """Test progress tracking functionality"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            state = MigrationState(temp_path)
            start_time = datetime(2024, 1, 1, 0, 0, 0)
            end_time = datetime(2024, 1, 1, 3, 0, 0)
            state.initialize_migration(start_time, end_time, "1h", 3)

            # Complete first chunk
            chunk1_start = datetime(2024, 1, 1, 0, 0, 0)
            chunk1_end = datetime(2024, 1, 1, 1, 0, 0)
            state.mark_chunk_completed(chunk1_start, chunk1_end, 100, 95)

            # Fail second chunk
            chunk2_start = datetime(2024, 1, 1, 1, 0, 0)
            chunk2_end = datetime(2024, 1, 1, 2, 0, 0)
            state.mark_chunk_failed(chunk2_start, chunk2_end, "Test error")

            completed, failed, total = state.get_progress()
            assert completed == 1
            assert failed == 1
            assert total == 3

            summary = state.get_summary()
            assert summary["progress"]["completed_chunks"] == 1
            assert summary["progress"]["total_chunks"] == 3
            assert summary["progress"]["percentage"] == pytest.approx(33.33, rel=1e-2)
            assert summary["documents_processed"] == 100
            assert summary["points_written"] == 95
            assert summary["failures"] == 1

        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestQueryBuilding:
    """Test query building functions"""

    def test_build_chunk_query_no_base_query(self):
        """Test building chunk query without base query"""
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        end_time = datetime(2024, 1, 1, 1, 0, 0)

        query = build_chunk_query(None, "@timestamp", start_time, end_time)

        expected = {
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": start_time.isoformat(),
                        "lt": end_time.isoformat(),
                    }
                }
            }
        }
        assert query == expected

    def test_build_chunk_query_with_base_query(self):
        """Test building chunk query with existing base query"""
        base_query = {"query": {"term": {"service.name": "web-server"}}}

        start_time = datetime(2024, 1, 1, 0, 0, 0)
        end_time = datetime(2024, 1, 1, 1, 0, 0)

        query = build_chunk_query(base_query, "@timestamp", start_time, end_time)

        # Should wrap both queries in a bool query
        assert "query" in query
        assert "bool" in query["query"]
        assert "must" in query["query"]["bool"]
        assert len(query["query"]["bool"]["must"]) == 2

    def test_build_chunk_query_with_bool_query(self):
        """Test building chunk query with existing bool query"""
        base_query = {
            "query": {"bool": {"must": [{"term": {"service.name": "web-server"}}]}}
        }

        start_time = datetime(2024, 1, 1, 0, 0, 0)
        end_time = datetime(2024, 1, 1, 1, 0, 0)

        query = build_chunk_query(base_query, "@timestamp", start_time, end_time)

        # Should add time range to existing must clause
        assert len(query["query"]["bool"]["must"]) == 2
        assert (
            query["query"]["bool"]["must"][1]["range"]["@timestamp"]["gte"]
            == start_time.isoformat()
        )


class TestFileOperations:
    """Test file operation utilities"""

    def test_get_temp_file(self):
        """Test temporary file creation"""
        temp_file = get_temp_file(".test")
        assert temp_file.suffix == ".test"
        assert not temp_file.exists()  # Should not exist initially

    def test_estimate_file_lines(self):
        """Test file line estimation"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("line1\nline2\nline3\n")
            temp_path = Path(f.name)

        try:
            lines = estimate_file_lines(temp_path)
            assert lines == 3
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_estimate_file_lines_empty(self):
        """Test file line estimation for empty file"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = Path(f.name)

        try:
            lines = estimate_file_lines(temp_path)
            assert lines == 0
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestInfluxDBBucketOperations:
    """Test InfluxDB bucket creation and checking"""

    def _create_mock_config(self):
        """Create a mock migration config for testing"""
        return MigrationConfig(
            elasticsearch=ElasticsearchConfig(
                url="http://localhost:9200", index="test-*"
            ),
            influxdb=InfluxDBConfig(
                url="http://localhost:8086",
                token="test-token",
                org="test-org",
                bucket="test-bucket",
                measurement="test-measurement",
            ),
            timestamp_field="@timestamp",
            field_mappings=[
                FieldMapping(
                    es_field="@timestamp",
                    influx_field="time",
                    field_type="timestamp",
                    data_type="timestamp",
                )
            ],
            chunked_migration=ChunkedMigrationConfig(),
        )

    @patch("subprocess.run")
    def test_check_influxdb_bucket_exists_true(self, mock_run):
        """Test checking if bucket exists - bucket exists"""
        mock_run.return_value.returncode = 0
        config = self._create_mock_config()

        result = check_influxdb_bucket_exists(config)
        assert result is True

        # Verify correct command was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "influx" in args
        assert "bucket" in args
        assert "list" in args
        assert "--name" in args
        assert "test-bucket" in args

    @patch("subprocess.run")
    def test_check_influxdb_bucket_exists_false(self, mock_run):
        """Test checking if bucket exists - bucket doesn't exist"""
        mock_run.return_value.returncode = 1
        config = self._create_mock_config()

        result = check_influxdb_bucket_exists(config)
        assert result is False

    @patch("subprocess.run")
    def test_check_influxdb_bucket_exists_error(self, mock_run):
        """Test checking if bucket exists - error occurs"""
        mock_run.side_effect = Exception("Connection error")
        config = self._create_mock_config()

        result = check_influxdb_bucket_exists(config)
        assert result is True  # Should assume exists on error

    @patch("subprocess.run")
    def test_create_influxdb_bucket_success(self, mock_run):
        """Test creating InfluxDB bucket - success"""
        mock_run.return_value.returncode = 0
        config = self._create_mock_config()

        result = create_influxdb_bucket(config, auto_create=True)
        assert result is True

        # Verify correct command was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "influx" in args
        assert "bucket" in args
        assert "create" in args
        assert "--name" in args
        assert "test-bucket" in args
        assert "--retention" in args
        assert "0s" in args  # Unlimited retention

    @patch("subprocess.run")
    def test_create_influxdb_bucket_failure(self, mock_run):
        """Test creating InfluxDB bucket - failure"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Permission denied"
        config = self._create_mock_config()

        result = create_influxdb_bucket(config, auto_create=True)
        assert result is False

    @patch("es2influx.utils.check_influxdb_bucket_exists")
    @patch("es2influx.utils.create_influxdb_bucket")
    def test_ensure_influxdb_bucket_exists_already_exists(
        self, mock_create, mock_check
    ):
        """Test ensuring bucket exists when it already exists"""
        mock_check.return_value = True
        config = self._create_mock_config()

        result = ensure_influxdb_bucket_exists(config, auto_create=True)
        assert result is True

        # Should not attempt to create bucket
        mock_create.assert_not_called()

    @patch("es2influx.utils.check_influxdb_bucket_exists")
    @patch("es2influx.utils.create_influxdb_bucket")
    def test_ensure_influxdb_bucket_exists_create_success(
        self, mock_create, mock_check
    ):
        """Test ensuring bucket exists when it needs to be created"""
        mock_check.return_value = False
        mock_create.return_value = True
        config = self._create_mock_config()

        result = ensure_influxdb_bucket_exists(config, auto_create=True)
        assert result is True

        # Should attempt to create bucket
        mock_create.assert_called_once_with(config, auto_create=True)

    @patch("es2influx.utils.check_influxdb_bucket_exists")
    @patch("es2influx.utils.create_influxdb_bucket")
    def test_ensure_influxdb_bucket_exists_create_failure(
        self, mock_create, mock_check
    ):
        """Test ensuring bucket exists when creation fails"""
        mock_check.return_value = False
        mock_create.return_value = False
        config = self._create_mock_config()

        result = ensure_influxdb_bucket_exists(config, auto_create=True)
        assert result is False
