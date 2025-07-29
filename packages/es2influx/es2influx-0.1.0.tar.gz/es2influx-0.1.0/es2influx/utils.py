"""
Utility functions for es2influx CLI tool
"""

import json
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from rich.console import Console
from rich.progress import Progress, TaskID

from .config import ChunkedMigrationConfig, MigrationConfig

console = Console()


def check_dependencies() -> Dict[str, bool]:
    """
    Check if required external dependencies are available

    Returns:
        Dictionary with dependency names and their availability status
    """
    dependencies = {}

    # Check for elasticdump
    try:
        result = subprocess.run(
            ["elasticdump", "--version"], capture_output=True, text=True, timeout=10
        )
        dependencies["elasticdump"] = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        dependencies["elasticdump"] = False

    # Check for influx CLI
    try:
        result = subprocess.run(
            ["influx", "version"], capture_output=True, text=True, timeout=10
        )
        dependencies["influx"] = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        dependencies["influx"] = False

    return dependencies


def dump_elasticsearch_data(
    config: MigrationConfig,
    output_file: Path,
    progress: Optional[Progress] = None,
    task_id: Optional[TaskID] = None,
    debug: bool = False,
) -> bool:
    """
    Use elasticdump to export data from Elasticsearch

    Args:
        config: Migration configuration
        output_file: Path to output JSON file
        progress: Optional progress bar
        task_id: Optional progress task ID

    Returns:
        True if successful, False otherwise
    """
    try:
        # Build elasticdump command
        cmd = [
            "elasticdump",
            "--input",
            config.elasticsearch.url + "/" + config.elasticsearch.index,
            "--output",
            str(output_file),
            "--type",
            "data",
            "--limit",
            str(config.elasticsearch.scroll_size),
            "--scrollTime",
            config.elasticsearch.scroll_timeout,
            "--overwrite",  # Allow overwriting existing files
            "--sourceOnly",  # Get only document source data (crucial!)
            "--concurrency",
            str(config.elasticsearch.concurrency),
            "--throttle",
            str(config.elasticsearch.throttle),
        ]

        # Add authentication if provided
        if config.elasticsearch.auth_user and config.elasticsearch.auth_password:
            auth_url = config.elasticsearch.url.replace(
                "://",
                f"://{config.elasticsearch.auth_user}:{config.elasticsearch.auth_password}@",
            )
            cmd[2] = auth_url + "/" + config.elasticsearch.index

        # Add custom query if provided
        if config.elasticsearch.query:
            query_json = json.dumps(config.elasticsearch.query)
            # Ensure the searchBody is properly quoted for shell execution
            cmd.extend(["--searchBody=" + query_json])

        if progress and task_id:
            progress.update(task_id, description="Exporting data from Elasticsearch...")
        else:
            console.print("🔄 Exporting data from Elasticsearch...")

        # Show command in debug mode
        if debug:
            console.print(f"🔍 Running elasticdump command:")
            console.print(f"   {' '.join(cmd)}")

        # Run elasticdump
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=3600  # 1 hour timeout
        )

        if result.returncode == 0:
            if debug:
                console.print(f"🔍 Elasticdump stdout: {result.stdout}")
                if result.stderr:
                    console.print(f"🔍 Elasticdump stderr: {result.stderr}")

            if progress and task_id:
                progress.update(
                    task_id, description="✅ Elasticsearch export completed"
                )
            else:
                console.print("✅ Elasticsearch export completed successfully")
            return True
        else:
            error_msg = f"Elasticdump failed with return code {result.returncode}"
            if result.stderr:
                error_msg += f": {result.stderr}"
            if result.stdout:
                error_msg += f" (stdout: {result.stdout})"

            if progress and task_id:
                progress.update(task_id, description=f"❌ {error_msg}")
            else:
                console.print(f"❌ {error_msg}")
            return False

    except subprocess.TimeoutExpired:
        error_msg = "Elasticdump timed out"
        if progress and task_id:
            progress.update(task_id, description=f"❌ {error_msg}")
        else:
            console.print(f"❌ {error_msg}")
        return False
    except Exception as e:
        error_msg = f"Error running elasticdump: {str(e)}"
        if progress and task_id:
            progress.update(task_id, description=f"❌ {error_msg}")
        else:
            console.print(f"❌ {error_msg}")
        return False


def read_jsonl_file(file_path: Path) -> Iterator[Dict[str, Any]]:
    """
    Read a JSON Lines file (one JSON object per line)

    Args:
        file_path: Path to the JSONL file

    Yields:
        Dictionary objects from the file
    """
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    console.print(f"⚠️  Warning: Failed to parse JSON line: {e}")
                    continue


def check_influxdb_bucket_exists(config: MigrationConfig) -> bool:
    """
    Check if the InfluxDB bucket exists

    Args:
        config: Migration configuration

    Returns:
        True if bucket exists, False otherwise
    """
    try:
        # Build influx bucket list command
        cmd = [
            "influx",
            "bucket",
            "list",
            "--org",
            config.influxdb.org,
            "--token",
            config.influxdb.token,
            "--name",
            config.influxdb.bucket,
        ]

        # Add host if not default
        if config.influxdb.url != "http://localhost:8086":
            cmd.extend(["--host", config.influxdb.url])

        # Run command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        # Check if bucket was found (exit code 0 means found)
        return result.returncode == 0

    except Exception as e:
        console.print(f"⚠️  Warning: Could not check bucket existence: {e}")
        return True  # Assume it exists to avoid creating duplicates


def create_influxdb_bucket(config: MigrationConfig, auto_create: bool = True) -> bool:
    """
    Create InfluxDB bucket with unlimited retention

    Args:
        config: Migration configuration
        auto_create: Whether to auto-create without prompting

    Returns:
        True if bucket was created successfully, False otherwise
    """
    try:
        if not auto_create:
            import typer

            create = typer.confirm(
                f"Bucket '{config.influxdb.bucket}' does not exist. Create it with unlimited retention?"
            )
            if not create:
                return False

        console.print(f"🪣 Creating InfluxDB bucket: {config.influxdb.bucket}")

        # Build influx bucket create command
        cmd = [
            "influx",
            "bucket",
            "create",
            "--org",
            config.influxdb.org,
            "--token",
            config.influxdb.token,
            "--name",
            config.influxdb.bucket,
            "--retention",
            "0s",  # 0s means unlimited retention
        ]

        # Add host if not default
        if config.influxdb.url != "http://localhost:8086":
            cmd.extend(["--host", config.influxdb.url])

        # Run command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            console.print(
                f"✅ Bucket '{config.influxdb.bucket}' created successfully with unlimited retention"
            )
            return True
        else:
            error_msg = result.stderr or result.stdout or "Unknown error"
            console.print(f"❌ Failed to create bucket: {error_msg}")
            return False

    except Exception as e:
        console.print(f"❌ Error creating bucket: {e}")
        return False


def ensure_influxdb_bucket_exists(
    config: MigrationConfig, auto_create: bool = True
) -> bool:
    """
    Ensure InfluxDB bucket exists, create if it doesn't

    Args:
        config: Migration configuration
        auto_create: Whether to auto-create bucket if it doesn't exist

    Returns:
        True if bucket exists or was created successfully, False otherwise
    """
    # Check if bucket exists
    if check_influxdb_bucket_exists(config):
        console.print(f"🪣 InfluxDB bucket '{config.influxdb.bucket}' exists")
        return True

    # Bucket doesn't exist, try to create it
    console.print(f"🪣 InfluxDB bucket '{config.influxdb.bucket}' does not exist")

    if auto_create:
        return create_influxdb_bucket(config, auto_create=True)
    else:
        return create_influxdb_bucket(config, auto_create=False)


def write_to_influxdb(
    line_protocol_file: Path,
    config: MigrationConfig,
    progress: Optional[Progress] = None,
    task_id: Optional[TaskID] = None,
) -> Tuple[bool, int]:
    """
    Use influx CLI to write line protocol data to InfluxDB

    Args:
        line_protocol_file: Path to file containing line protocol data
        config: Migration configuration
        progress: Optional progress bar
        task_id: Optional progress task ID

    Returns:
        Tuple of (success: bool, points_written: int)
    """
    try:
        # Count the number of lines in the file (each line is a point)
        points_to_write = 0
        try:
            with open(line_protocol_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():  # Only count non-empty lines
                        points_to_write += 1
        except Exception as e:
            console.print(f"⚠️  Warning: Could not count points in file: {e}")
            points_to_write = 0

        # Build influx write command
        cmd = [
            "influx",
            "write",
            "--bucket",
            config.influxdb.bucket,
            "--org",
            config.influxdb.org,
            "--token",
            config.influxdb.token,
            "--file",
            str(line_protocol_file),
        ]

        # Add host if not default
        if config.influxdb.url != "http://localhost:8086":
            cmd.extend(["--host", config.influxdb.url])

        if progress and task_id:
            progress.update(task_id, description="Writing data to InfluxDB...")
        else:
            console.print("🔄 Writing data to InfluxDB...")

        # Run influx write command
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=3600  # 1 hour timeout
        )

        if result.returncode == 0:
            if progress and task_id:
                progress.update(
                    task_id, description="✅ Data written successfully to InfluxDB"
                )
            else:
                console.print("✅ Data written successfully to InfluxDB")
            return True, points_to_write
        else:
            error_msg = result.stderr or result.stdout or "Unknown error"
            console.print(f"❌ Failed to write data to InfluxDB: {error_msg}")
            return False, 0

    except subprocess.TimeoutExpired:
        console.print("❌ Timeout while writing data to InfluxDB")
        return False, 0
    except Exception as e:
        console.print(f"❌ Error writing data to InfluxDB: {e}")
        return False, 0


def get_temp_file(suffix: str = "") -> Path:
    """
    Get a temporary file path

    Args:
        suffix: File suffix/extension

    Returns:
        Path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.close()
    temp_path = Path(temp_file.name)

    # Ensure the file doesn't exist before returning the path
    if temp_path.exists():
        temp_path.unlink()

    return temp_path


def cleanup_temp_files(files: List[Path]) -> None:
    """
    Clean up temporary files

    Args:
        files: List of file paths to clean up
    """
    for file_path in files:
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            console.print(f"⚠️  Warning: Failed to clean up {file_path}: {e}")


def estimate_file_lines(file_path: Path) -> int:
    """
    Estimate the number of lines in a file

    Args:
        file_path: Path to the file

    Returns:
        Estimated number of lines
    """
    try:
        # Quick estimate by reading a sample and extrapolating
        sample_size = 8192  # 8KB sample
        with open(file_path, "rb") as f:
            sample = f.read(sample_size)
            if not sample:
                return 0

            lines_in_sample = sample.count(b"\n")
            if lines_in_sample == 0:
                return 1

            # Get total file size
            f.seek(0, 2)  # Seek to end
            total_size = f.tell()

            if total_size <= sample_size:
                return lines_in_sample

            # Extrapolate
            estimated_lines = int((total_size / sample_size) * lines_in_sample)
            return max(1, estimated_lines)
    except Exception:
        return 0


def parse_time_string(time_str: str) -> datetime:
    """
    Parse time string in various formats to datetime object

    Args:
        time_str: Time string (ISO format or relative like 'now-7d')

    Returns:
        datetime object (timezone-naive)
    """
    if time_str.startswith("now"):
        # Parse relative time like 'now-7d', 'now-1h', etc.
        if time_str == "now":
            return datetime.utcnow()

        # Extract the relative part
        relative_part = time_str[3:]  # Remove 'now'
        if relative_part.startswith("-"):
            relative_part = relative_part[1:]
            multiplier = -1
        elif relative_part.startswith("+"):
            relative_part = relative_part[1:]
            multiplier = 1
        else:
            raise ValueError(f"Invalid relative time format: {time_str}")

        # Parse the number and unit
        import re

        match = re.match(r"^(\d+)([hmwd])$", relative_part)
        if not match:
            raise ValueError(f"Invalid relative time format: {time_str}")

        number = int(match.group(1))
        unit = match.group(2)

        # Convert to timedelta
        if unit == "h":
            delta = timedelta(hours=number)
        elif unit == "m":
            delta = timedelta(minutes=number)
        elif unit == "d":
            delta = timedelta(days=number)
        elif unit == "w":
            delta = timedelta(weeks=number)
        else:
            raise ValueError(f"Invalid time unit: {unit}")

        return datetime.utcnow() + (delta * multiplier)
    else:
        # Try to parse as ISO format
        try:
            dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            # Convert to timezone-naive UTC datetime
            if dt.tzinfo is not None:
                dt = dt.utctimetuple()
                dt = datetime(*dt[:6])
            return dt
        except ValueError:
            # Try other common formats
            from dateutil.parser import parse as parse_date

            dt = parse_date(time_str)
            # Convert to timezone-naive UTC datetime
            if dt.tzinfo is not None:
                dt = dt.utctimetuple()
                dt = datetime(*dt[:6])
            return dt


def parse_chunk_size(chunk_size: str) -> timedelta:
    """
    Parse chunk size string to timedelta

    Args:
        chunk_size: Chunk size string like '1h', '6h', '1d'

    Returns:
        timedelta object
    """
    import re

    match = re.match(r"^(\d+)([hmwd])$", chunk_size)
    if not match:
        raise ValueError(f"Invalid chunk size format: {chunk_size}")

    number = int(match.group(1))
    unit = match.group(2)

    if unit == "h":
        return timedelta(hours=number)
    elif unit == "m":
        return timedelta(minutes=number)
    elif unit == "d":
        return timedelta(days=number)
    elif unit == "w":
        return timedelta(weeks=number)
    else:
        raise ValueError(f"Invalid time unit: {unit}")


def generate_time_chunks(
    start_time: datetime, end_time: datetime, chunk_size: timedelta
) -> List[Tuple[datetime, datetime]]:
    """
    Generate time chunks for migration

    Args:
        start_time: Start time for migration
        end_time: End time for migration
        chunk_size: Size of each chunk

    Returns:
        List of (start, end) tuples for each chunk
    """
    chunks = []
    current_start = start_time

    while current_start < end_time:
        current_end = min(current_start + chunk_size, end_time)
        chunks.append((current_start, current_end))
        current_start = current_end

    return chunks


class MigrationState:
    """Manages migration state for resume functionality"""

    def __init__(self, state_file: str):
        self.state_file = Path(state_file)
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load migration state from file"""
        if not self.state_file.exists():
            return {
                "migration_id": None,
                "start_time": None,
                "end_time": None,
                "chunk_size": None,
                "completed_chunks": [],
                "failed_chunks": [],
                "total_chunks": 0,
                "total_documents": 0,
                "total_points_written": 0,
                "total_failures": 0,
                "created_at": None,
                "updated_at": None,
            }

        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
                # Ensure new field exists for backward compatibility
                if "total_points_written" not in state:
                    state["total_points_written"] = 0
                return state
        except (json.JSONDecodeError, FileNotFoundError):
            console.print(
                f"⚠️  Warning: Invalid state file {self.state_file}, creating new state"
            )
            return {
                "migration_id": None,
                "start_time": None,
                "end_time": None,
                "chunk_size": None,
                "completed_chunks": [],
                "failed_chunks": [],
                "total_chunks": 0,
                "total_documents": 0,
                "total_points_written": 0,
                "total_failures": 0,
                "created_at": None,
                "updated_at": None,
            }

    def _save_state(self):
        """Save current state to file"""
        self.state["updated_at"] = datetime.utcnow().isoformat()
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def initialize_migration(
        self,
        start_time: datetime,
        end_time: datetime,
        chunk_size: str,
        total_chunks: int,
    ):
        """Initialize a new migration"""
        import uuid

        self.state = {
            "migration_id": str(uuid.uuid4()),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "chunk_size": chunk_size,
            "completed_chunks": [],
            "failed_chunks": [],
            "total_chunks": total_chunks,
            "total_documents": 0,
            "total_points_written": 0,
            "total_failures": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self._save_state()

    def is_chunk_completed(self, chunk_start: datetime, chunk_end: datetime) -> bool:
        """Check if a chunk has been completed"""
        chunk_key = f"{chunk_start.isoformat()}_{chunk_end.isoformat()}"
        return chunk_key in self.state["completed_chunks"]

    def is_chunk_failed(self, chunk_start: datetime, chunk_end: datetime) -> bool:
        """Check if a chunk has failed"""
        chunk_key = f"{chunk_start.isoformat()}_{chunk_end.isoformat()}"
        return any(fc["chunk_key"] == chunk_key for fc in self.state["failed_chunks"])

    def get_chunk_retry_count(self, chunk_start: datetime, chunk_end: datetime) -> int:
        """Get the number of retries for a chunk"""
        chunk_key = f"{chunk_start.isoformat()}_{chunk_end.isoformat()}"
        for fc in self.state["failed_chunks"]:
            if fc["chunk_key"] == chunk_key:
                return fc.get("retry_count", 0)
        return 0

    def mark_chunk_completed(
        self,
        chunk_start: datetime,
        chunk_end: datetime,
        documents_processed: int,
        points_written: int,
    ):
        """Mark a chunk as completed"""
        chunk_key = f"{chunk_start.isoformat()}_{chunk_end.isoformat()}"
        if chunk_key not in self.state["completed_chunks"]:
            self.state["completed_chunks"].append(chunk_key)
            self.state["total_documents"] += documents_processed
            self.state["total_points_written"] += points_written

            # Remove from failed chunks if it was there
            self.state["failed_chunks"] = [
                fc for fc in self.state["failed_chunks"] if fc["chunk_key"] != chunk_key
            ]

            self._save_state()

    def mark_chunk_failed(
        self, chunk_start: datetime, chunk_end: datetime, error_message: str
    ):
        """Mark a chunk as failed"""
        chunk_key = f"{chunk_start.isoformat()}_{chunk_end.isoformat()}"

        # Update existing failure or add new one
        for fc in self.state["failed_chunks"]:
            if fc["chunk_key"] == chunk_key:
                fc["retry_count"] = fc.get("retry_count", 0) + 1
                fc["last_error"] = error_message
                fc["last_attempt"] = datetime.utcnow().isoformat()
                self._save_state()
                return

        # Add new failure
        self.state["failed_chunks"].append(
            {
                "chunk_key": chunk_key,
                "chunk_start": chunk_start.isoformat(),
                "chunk_end": chunk_end.isoformat(),
                "retry_count": 1,
                "last_error": error_message,
                "last_attempt": datetime.utcnow().isoformat(),
            }
        )
        self.state["total_failures"] += 1
        self._save_state()

    def get_progress(self) -> Tuple[int, int, int]:
        """Get migration progress"""
        completed = len(self.state["completed_chunks"])
        failed = len(self.state["failed_chunks"])
        total = self.state["total_chunks"]
        return completed, failed, total

    def get_summary(self) -> Dict[str, Any]:
        """Get migration summary"""
        completed, failed, total = self.get_progress()
        return {
            "migration_id": self.state["migration_id"],
            "progress": {
                "completed_chunks": completed,
                "failed_chunks": failed,
                "total_chunks": total,
                "percentage": (completed / total * 100) if total > 0 else 0,
            },
            "documents_processed": self.state["total_documents"],
            "points_written": self.state.get("total_points_written", 0),
            "failures": self.state["total_failures"],
            "created_at": self.state["created_at"],
            "updated_at": self.state["updated_at"],
        }


def build_chunk_query(
    base_query: Optional[Dict[str, Any]],
    timestamp_field: str,
    start_time: datetime,
    end_time: datetime,
) -> Dict[str, Any]:
    """
    Build Elasticsearch query for a specific time chunk

    Args:
        base_query: Base query from configuration
        timestamp_field: Field name for timestamp filtering
        start_time: Start time for chunk
        end_time: End time for chunk

    Returns:
        Modified query with time range filter
    """
    # Create time range filter
    time_range = {
        "range": {
            timestamp_field: {"gte": start_time.isoformat(), "lt": end_time.isoformat()}
        }
    }

    if base_query is None:
        # No base query, just use time range
        return {"query": time_range}

    # Merge with existing query
    if "query" not in base_query:
        return {"query": time_range}

    existing_query = base_query["query"]

    # If existing query is a bool query, add time range to must clause
    if isinstance(existing_query, dict) and "bool" in existing_query:
        bool_query = existing_query["bool"]
        if "must" not in bool_query:
            bool_query["must"] = []
        elif not isinstance(bool_query["must"], list):
            bool_query["must"] = [bool_query["must"]]

        bool_query["must"].append(time_range)
        return base_query

    # Otherwise, wrap both in a bool query
    return {"query": {"bool": {"must": [existing_query, time_range]}}}
