"""
Main CLI module for es2influx
"""

import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from . import __version__
from .config import MigrationConfig, create_sample_config, load_config
from .transform import (
    extract_regex_groups,
    get_nested_value,
    save_line_protocol,
    transform_documents,
    validate_line_protocol,
)
from .utils import (
    MigrationState,
    build_chunk_query,
    check_dependencies,
    cleanup_temp_files,
    dump_elasticsearch_data,
    ensure_influxdb_bucket_exists,
    estimate_file_lines,
    generate_time_chunks,
    get_temp_file,
    parse_chunk_size,
    parse_time_string,
    read_jsonl_file,
    write_to_influxdb,
)

app = typer.Typer(
    name="es2influx",
    help="CLI tool for migrating Elasticsearch data to InfluxDB",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit"""
    if value:
        console.print(f"es2influx version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    env: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment name for loading .env files (e.g., development, production, staging)",
    ),
) -> None:
    """
    ES2InfluxDB - Migrate Elasticsearch data to InfluxDB

    A powerful CLI tool that uses elasticdump to export data from Elasticsearch
    and converts it to InfluxDB line protocol format for ingestion.
    """
    # Set ES2INFLUX_ENV if specified via CLI
    if env:
        import os

        os.environ["ES2INFLUX_ENV"] = env


@app.command()
def init_config(
    output: Optional[Path] = typer.Option(
        Path("es2influx-config.yaml"),
        "--output",
        "-o",
        help="Output path for the sample configuration file",
    )
) -> None:
    """
    Generate a sample configuration file

    Creates a sample YAML configuration file with all the necessary
    settings for migrating data from Elasticsearch to InfluxDB.
    """
    try:
        if output.exists():
            overwrite = typer.confirm(
                f"Configuration file {output} already exists. Overwrite?"
            )
            if not overwrite:
                console.print("❌ Configuration generation cancelled")
                raise typer.Exit(1)

        create_sample_config(output)

        console.print(
            Panel.fit(
                f"✅ Sample configuration created at: [bold green]{output}[/bold green]",
                title="Configuration Generated",
                border_style="green",
            )
        )

        console.print("\n📝 Please edit the configuration file to match your setup:")
        console.print("  • Update Elasticsearch URL and index")
        console.print("  • Configure InfluxDB connection details")
        console.print("  • Customize field mappings")
        console.print("  • Adjust query parameters if needed")

    except Exception as e:
        console.print(f"❌ Error creating configuration: {e}")
        raise typer.Exit(1)


@app.command()
def check(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    )
) -> None:
    """
    Check dependencies and validate configuration

    Verifies that all required external tools (elasticdump, influx CLI)
    are available and validates the configuration file if provided.
    """
    # Check external dependencies
    console.print("🔍 Checking dependencies...\n")

    deps = check_dependencies()

    table = Table(title="Dependency Status")
    table.add_column("Tool", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Notes")

    for tool, available in deps.items():
        if available:
            table.add_row(tool, "✅ Available", "")
        else:
            table.add_row(tool, "❌ Missing", f"Install {tool} and ensure it's in PATH")

    console.print(table)

    # Check if all dependencies are available
    if not all(deps.values()):
        console.print(
            "\n⚠️  Some dependencies are missing. Please install them before proceeding."
        )

        if not deps.get("elasticdump"):
            console.print("  • Install elasticdump: npm install -g elasticdump")

        if not deps.get("influx"):
            console.print(
                "  • Install influx CLI: https://docs.influxdata.com/influxdb/v2.0/tools/influx-cli/"
            )

    # Validate configuration if provided
    if config_file:
        console.print(f"\n🔍 Validating configuration: {config_file}")

        try:
            config = load_config(config_file)
            console.print("✅ Configuration is valid")

            # Show configuration summary
            console.print("\n📋 Configuration Summary:")
            console.print(
                f"  • Elasticsearch: {config.elasticsearch.url}/{config.elasticsearch.index}"
            )
            console.print(f"  • InfluxDB: {config.influxdb.url}")
            console.print(f"  • Bucket: {config.influxdb.bucket}")
            console.print(f"  • Measurement: {config.influxdb.measurement}")
            console.print(f"  • Field mappings: {len(config.field_mappings)}")

        except Exception as e:
            console.print(f"❌ Configuration validation failed: {e}")
            raise typer.Exit(1)


@app.command()
def migrate(
    config_file: Path = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to configuration file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Perform a dry run without writing to InfluxDB"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Save line protocol to file (for debugging)"
    ),
    batch_size: Optional[int] = typer.Option(
        None, "--batch-size", help="Override batch size for processing documents"
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug mode (keep temporary files and show paths)"
    ),
    show_files: bool = typer.Option(
        False, "--show-files", help="Show paths to temporary files (implies --debug)"
    ),
    # Chunked migration options
    start_time: Optional[str] = typer.Option(
        None,
        "--start-time",
        help="Start time for chunked migration (ISO format or relative like 'now-7d'). Overrides config.",
    ),
    end_time: Optional[str] = typer.Option(
        None,
        "--end-time",
        help="End time for chunked migration (ISO format or relative like 'now'). Overrides config.",
    ),
    chunk_size: Optional[str] = typer.Option(
        None,
        "--chunk-size",
        help="Size of each chunk for chunked migration (e.g., '1h', '6h', '1d'). Overrides config.",
    ),
    resume: bool = typer.Option(
        False, "--resume", help="Resume from previous incomplete chunked migration"
    ),
    reset: bool = typer.Option(
        False, "--reset", help="Reset chunked migration state and start fresh"
    ),
    show_progress: bool = typer.Option(
        False,
        "--show-progress",
        help="Show current chunked migration progress and exit",
    ),
    auto_create_bucket: Optional[bool] = typer.Option(
        None,
        "--auto-create-bucket/--no-auto-create-bucket",
        help="Automatically create InfluxDB bucket if it doesn't exist (overrides config setting)",
    ),
) -> None:
    """
    Migrate data from Elasticsearch to InfluxDB

    This command automatically detects whether to use regular or chunked migration
    based on your configuration. For large datasets, enable chunked migration
    in your config file to get:

    - Resume functionality for interrupted migrations
    - Progress tracking and reporting
    - Automatic retry logic for failed chunks
    - Configurable chunk sizes (1h, 6h, 1d, 7d, etc.)
    - State persistence for long-running migrations

    Examples:
        # Regular migration
        es2influx migrate --config my-config.yaml

        # Chunked migration (if enabled in config)
        es2influx migrate --config my-config.yaml --start-time "now-7d" --end-time "now"

        # Resume interrupted chunked migration
        es2influx migrate --config my-config.yaml --resume

        # Check chunked migration progress
        es2influx migrate --config my-config.yaml --show-progress
    """
    # Enable debug mode if show_files is requested
    if show_files:
        debug = True

    # Load configuration
    try:
        config = load_config(config_file)
        if batch_size:
            config.influxdb.batch_size = batch_size
        # Override bucket creation setting if provided via CLI
        if auto_create_bucket is not None:
            config.influxdb.auto_create_bucket = auto_create_bucket
    except Exception as e:
        console.print(f"❌ Error loading configuration: {e}")
        raise typer.Exit(1)

    # Check if chunked migration is enabled
    if config.chunked_migration.enabled:
        # Use chunked migration logic
        _run_chunked_migration(
            config=config,
            start_time=start_time,
            end_time=end_time,
            chunk_size=chunk_size,
            dry_run=dry_run,
            resume=resume,
            reset=reset,
            show_progress=show_progress,
            debug=debug,
        )
    else:
        # Use regular migration logic
        _run_regular_migration(
            config=config,
            dry_run=dry_run,
            output_file=output_file,
            debug=debug,
            show_files=show_files,
        )


def _run_chunked_migration(
    config: MigrationConfig,
    start_time: Optional[str],
    end_time: Optional[str],
    chunk_size: Optional[str],
    dry_run: bool,
    resume: bool,
    reset: bool,
    show_progress: bool,
    debug: bool,
) -> None:
    """Run chunked migration logic"""
    console.print("🚀 Chunked migration mode enabled")

    # Initialize migration state
    state = MigrationState(config.chunked_migration.state_file)

    # Handle show progress
    if show_progress:
        summary = state.get_summary()
        if summary["migration_id"] is None:
            console.print("📊 No migration in progress")
        else:
            console.print(
                f"📊 Migration Progress (ID: {summary['migration_id'][:8]}...)"
            )
            console.print(
                f"   🎯 Completed: {summary['progress']['completed_chunks']}/{summary['progress']['total_chunks']} chunks ({summary['progress']['percentage']:.1f}%)"
            )
            console.print(f"   📄 Documents: {summary['documents_processed']:,}")
            console.print(f"   📈 Points written: {summary['points_written']:,}")
            console.print(f"   ❌ Failures: {summary['failures']}")
            console.print(f"   📅 Started: {summary['created_at']}")
            console.print(f"   ⏰ Updated: {summary['updated_at']}")
        return

    # Handle reset
    if reset:
        if state.state_file.exists():
            state.state_file.unlink()
            console.print("🔄 Migration state reset")
        else:
            console.print("📊 No migration state to reset")
        return

    # Determine time range
    if resume and state.state["migration_id"] is not None:
        console.print(
            f"🔄 Resuming migration (ID: {state.state['migration_id'][:8]}...)"
        )
        start_dt = parse_time_string(state.state["start_time"])
        end_dt = parse_time_string(state.state["end_time"])
        chunk_size_str = state.state["chunk_size"]
    else:
        # Use command line arguments or config defaults
        start_str = start_time or config.chunked_migration.start_time
        end_str = end_time or config.chunked_migration.end_time
        chunk_size_str = chunk_size or config.chunked_migration.chunk_size

        if not start_str or not end_str:
            console.print(
                "❌ Start and end times must be specified either in config or command line"
            )
            console.print(
                "   Configure chunked_migration.start_time and chunked_migration.end_time in your config"
            )
            console.print("   Or use --start-time and --end-time options")
            raise typer.Exit(1)

        try:
            start_dt = parse_time_string(start_str)
            end_dt = parse_time_string(end_str)
        except ValueError as e:
            console.print(f"❌ Invalid time format: {e}")
            raise typer.Exit(1)

    # Validate time range
    if start_dt >= end_dt:
        console.print("❌ Start time must be before end time")
        raise typer.Exit(1)

    # Parse chunk size
    try:
        chunk_size_td = parse_chunk_size(chunk_size_str)
    except ValueError as e:
        console.print(f"❌ Invalid chunk size: {e}")
        raise typer.Exit(1)

    # Generate time chunks
    chunks = generate_time_chunks(start_dt, end_dt, chunk_size_td)

    # Initialize migration if not resuming
    if not resume or state.state["migration_id"] is None:
        state.initialize_migration(start_dt, end_dt, chunk_size_str, len(chunks))
        console.print(
            f"🚀 Starting new chunked migration (ID: {state.state['migration_id'][:8]}...)"
        )

    console.print(f"📅 Time range: {start_dt.isoformat()} to {end_dt.isoformat()}")
    console.print(f"📦 Chunk size: {chunk_size_str}")
    console.print(f"📊 Total chunks: {len(chunks)}")

    # Check dependencies
    deps = check_dependencies()
    if not all(deps.values()):
        console.print("❌ Missing dependencies. Run 'es2influx check' for details.")
        raise typer.Exit(1)

    # Ensure InfluxDB bucket exists (unless dry run)
    if not dry_run:
        if not ensure_influxdb_bucket_exists(
            config, config.influxdb.auto_create_bucket
        ):
            console.print("❌ Failed to ensure InfluxDB bucket exists")
            raise typer.Exit(1)

    # Track overall progress
    completed, failed, total = state.get_progress()
    console.print(
        f"📈 Current progress: {completed}/{total} completed, {failed} failed"
    )

    # Process chunks
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:

        overall_task = progress.add_task("Processing chunks...", total=len(chunks))

        processed_count = 0
        for chunk_start, chunk_end in chunks:
            # Skip if already completed
            if state.is_chunk_completed(chunk_start, chunk_end):
                processed_count += 1
                progress.update(overall_task, completed=processed_count)
                continue

            # Check retry count
            retry_count = state.get_chunk_retry_count(chunk_start, chunk_end)
            if retry_count >= config.chunked_migration.max_retries:
                console.print(
                    f"⚠️  Skipping chunk {chunk_start.isoformat()} to {chunk_end.isoformat()} - max retries exceeded"
                )
                processed_count += 1
                progress.update(overall_task, completed=processed_count)
                continue

            # Process chunk
            chunk_desc = f"Chunk {chunk_start.strftime('%Y-%m-%d %H:%M')} to {chunk_end.strftime('%Y-%m-%d %H:%M')}"
            if retry_count > 0:
                chunk_desc += f" (retry {retry_count})"

            progress.update(overall_task, description=f"Processing {chunk_desc}")

            try:
                # Process single chunk
                documents_processed, points_written = process_single_chunk(
                    config, chunk_start, chunk_end, dry_run, debug, progress
                )

                # Mark as completed
                state.mark_chunk_completed(
                    chunk_start, chunk_end, documents_processed, points_written
                )

                if debug:
                    console.print(
                        f"✅ Chunk completed: {documents_processed} documents processed, {points_written} points written"
                    )

            except Exception as e:
                error_msg = str(e)
                state.mark_chunk_failed(chunk_start, chunk_end, error_msg)

                console.print(f"❌ Chunk failed: {error_msg}")

                # Wait before retrying
                if retry_count < config.chunked_migration.max_retries - 1:
                    console.print(
                        f"⏳ Waiting {config.chunked_migration.retry_delay} seconds before continuing..."
                    )
                    time.sleep(config.chunked_migration.retry_delay)

            processed_count += 1
            progress.update(overall_task, completed=processed_count)

        # Final summary
        completed, failed, total = state.get_progress()
        summary = state.get_summary()

        console.print(
            Panel.fit(
                f"📊 Chunked Migration Summary\n"
                f"🎯 Completed: {completed}/{total} chunks ({summary['progress']['percentage']:.1f}%)\n"
                f"❌ Failed: {failed} chunks\n"
                f"📄 Documents processed: {summary['documents_processed']:,}\n"
                f"📈 Points written: {summary['points_written']:,}\n"
                f"📅 Duration: {start_dt.isoformat()} to {end_dt.isoformat()}\n"
                f"🔍 Migration ID: {summary['migration_id'][:8]}...",
                title=(
                    "Chunked Migration Complete"
                    if completed == total
                    else "Chunked Migration Paused"
                ),
                border_style="green" if completed == total else "yellow",
            )
        )

        if failed > 0:
            console.print(
                f"\n⚠️  {failed} chunks failed. Use --resume to retry failed chunks."
            )

        if completed == total:
            console.print("\n🎉 All chunks processed successfully!")


def _run_regular_migration(
    config: MigrationConfig,
    dry_run: bool,
    output_file: Optional[Path],
    debug: bool,
    show_files: bool,
) -> None:
    """Run regular migration logic"""
    console.print("🚀 Regular migration mode")

    # Check dependencies
    deps = check_dependencies()
    if not all(deps.values()):
        console.print("❌ Missing dependencies. Run 'es2influx check' for details.")
        raise typer.Exit(1)

    # Ensure InfluxDB bucket exists (unless dry run)
    if not dry_run:
        if not ensure_influxdb_bucket_exists(
            config, config.influxdb.auto_create_bucket
        ):
            console.print("❌ Failed to ensure InfluxDB bucket exists")
            raise typer.Exit(1)

    # Create temporary files
    temp_files = []
    try:
        es_dump_file = get_temp_file(".jsonl")
        line_protocol_file = get_temp_file(".lp")
        temp_files.extend([es_dump_file, line_protocol_file])

        if debug or show_files:
            console.print(f"🔍 Debug mode enabled")
            console.print(f"📄 ES dump file: {es_dump_file}")
            console.print(f"📝 Line protocol file: {line_protocol_file}")
            if debug:
                console.print(f"🗂️  Files will be kept after migration for inspection")

    except Exception as e:
        console.print(f"❌ Error creating temporary files: {e}")
        cleanup_temp_files(temp_files)
        raise typer.Exit(1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:

            # Step 1: Export from Elasticsearch
            dump_task = progress.add_task("Exporting from Elasticsearch...", total=None)

            success = dump_elasticsearch_data(
                config, es_dump_file, progress, dump_task, debug
            )
            if not success:
                console.print("❌ Failed to export data from Elasticsearch")
                console.print(
                    "   Check your Elasticsearch configuration and connectivity"
                )
                raise typer.Exit(1)

            # Estimate number of documents for progress tracking
            estimated_docs = estimate_file_lines(es_dump_file)
            progress.update(dump_task, total=estimated_docs, completed=estimated_docs)

            if debug:
                file_size = es_dump_file.stat().st_size if es_dump_file.exists() else 0
                console.print(f"🔍 ES dump file size: {file_size:,} bytes")
                console.print(f"🔍 Estimated documents: {estimated_docs:,}")

            # Step 2: Transform data
            transform_task = progress.add_task(
                "Transforming to line protocol...", total=estimated_docs
            )

            # Initialize empty line protocol file
            with open(line_protocol_file, "w", encoding="utf-8") as f:
                pass  # Create empty file

            processed_docs = 0
            total_lines = 0
            batch_lines = []

            # Process documents in batches
            for doc in read_jsonl_file(es_dump_file):
                processed_docs += 1

                # Transform single document to get line protocol
                lines = transform_documents([doc], config)
                batch_lines.extend(lines)

                # Process batch when it reaches the configured size
                if len(batch_lines) >= config.influxdb.batch_size:
                    # Validate line protocol format
                    valid_lines = []
                    for line in batch_lines:
                        if validate_line_protocol(line):
                            valid_lines.append(line)
                        else:
                            if debug:
                                console.print(
                                    f"🔍 Invalid line protocol (full): {line}"
                                )
                            else:
                                console.print(
                                    f"⚠️  Warning: Invalid line protocol: {line[:100]}..."
                                )

                    # Write batch to file with proper flushing
                    with open(line_protocol_file, "a", encoding="utf-8") as f:
                        for line in valid_lines:
                            f.write(line + "\n")
                        f.flush()  # Ensure data is written to disk

                    total_lines += len(valid_lines)
                    batch_lines = []

                # Update progress
                progress.update(transform_task, completed=processed_docs)

            # Process remaining lines
            if batch_lines:
                valid_lines = []
                for line in batch_lines:
                    if validate_line_protocol(line):
                        valid_lines.append(line)
                    else:
                        if debug:
                            console.print(f"🔍 Invalid line protocol (full): {line}")
                        else:
                            console.print(
                                f"⚠️  Warning: Invalid line protocol: {line[:100]}..."
                            )

                with open(line_protocol_file, "a", encoding="utf-8") as f:
                    for line in valid_lines:
                        f.write(line + "\n")
                    f.flush()  # Ensure data is written to disk

                total_lines += len(valid_lines)

            progress.update(transform_task, completed=processed_docs)

            # Ensure all data is written to disk
            import os

            if line_protocol_file.exists():
                # Force filesystem sync
                with open(line_protocol_file, "r+b") as f:
                    f.flush()
                    os.fsync(f.fileno())

                if debug:
                    lp_file_size = line_protocol_file.stat().st_size
                    console.print(f"🔍 Line protocol file size: {lp_file_size:,} bytes")
                    console.print(f"🔍 Total documents processed: {processed_docs:,}")
                    console.print(f"🔍 Valid line protocol entries: {total_lines:,}")

                    # Show first few lines of line protocol for debugging
                    if lp_file_size > 0:
                        console.print(f"🔍 First few lines of line protocol:")
                        with open(line_protocol_file, "r", encoding="utf-8") as f:
                            for i, line in enumerate(f):
                                if i >= 3:  # Show first 3 lines
                                    break
                                console.print(f"   {i+1}: {line.strip()}")
                    else:
                        console.print(f"⚠️  Line protocol file is empty!")
            else:
                console.print(f"❌ Line protocol file does not exist!")

            # Save line protocol file if requested
            if output_file:
                import shutil

                shutil.copy2(line_protocol_file, output_file)
                console.print(f"💾 Line protocol saved to: {output_file}")

            # Track points written to InfluxDB
            points_written = 0

            # Step 3: Write to InfluxDB (unless dry run)
            if not dry_run:
                # Check if we have data to write
                if total_lines == 0:
                    console.print("⚠️  No valid data to write to InfluxDB")
                    console.print("   Check your field mappings and source data")
                else:
                    write_task = progress.add_task("Writing to InfluxDB...", total=None)

                    # Verify file exists and has content
                    if (
                        not line_protocol_file.exists()
                        or line_protocol_file.stat().st_size == 0
                    ):
                        console.print("❌ Line protocol file is empty or missing")
                        raise typer.Exit(1)

                    success, points_written = write_to_influxdb(
                        line_protocol_file, config, progress, write_task
                    )
                    if not success:
                        raise typer.Exit(1)

                    progress.update(write_task, total=1, completed=1)
            else:
                console.print("🏃 Dry run completed - no data written to InfluxDB")
                points_written = (
                    total_lines  # In dry run, show what would have been written
                )

        # Success summary
        summary_lines = [
            f"✅ Migration completed successfully!",
            f"📊 Processed: {processed_docs:,} documents",
            f"📝 Generated: {total_lines:,} line protocol entries",
        ]

        if not dry_run:
            summary_lines.append(f"📈 Written to InfluxDB: {points_written:,} points")
        else:
            summary_lines.append(
                f"📈 Would write to InfluxDB: {points_written:,} points (dry run)"
            )

        summary_lines.append(
            f"🎯 Target: {config.influxdb.bucket}/{config.influxdb.measurement}"
        )

        console.print(
            Panel.fit(
                "\n".join(summary_lines),
                title="Migration Summary",
                border_style="green",
            )
        )

    except KeyboardInterrupt:
        console.print("\n⏹️  Migration cancelled by user")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n❌ Migration failed: {e}")
        raise typer.Exit(1)
    finally:
        # Clean up temporary files (unless in debug mode)
        if debug:
            console.print(f"\n🔍 Debug mode: Temporary files preserved for inspection:")
            console.print(
                f"   📄 ES dump: {es_dump_file if 'es_dump_file' in locals() else 'N/A'}"
            )
            console.print(
                f"   📝 Line protocol: {line_protocol_file if 'line_protocol_file' in locals() else 'N/A'}"
            )
        else:
            cleanup_temp_files(temp_files)


def process_single_chunk(
    config: MigrationConfig,
    chunk_start: datetime,
    chunk_end: datetime,
    dry_run: bool,
    debug: bool,
    progress: Optional[Progress] = None,
) -> Tuple[int, int]:
    """
    Process a single time chunk

    Args:
        config: Migration configuration
        chunk_start: Start time for chunk
        chunk_end: End time for chunk
        dry_run: Whether to perform a dry run
        debug: Whether to enable debug mode
        progress: Optional progress tracker

    Returns:
        Tuple of (documents_processed, points_written)
    """
    # Create temporary files
    temp_files = []
    try:
        es_dump_file = get_temp_file(".jsonl")
        line_protocol_file = get_temp_file(".lp")
        temp_files.extend([es_dump_file, line_protocol_file])

        # Build query for this chunk
        chunk_query = build_chunk_query(
            config.elasticsearch.query, config.timestamp_field, chunk_start, chunk_end
        )

        # Create a temporary config with the chunk query
        chunk_config = config.copy(deep=True)
        chunk_config.elasticsearch.query = chunk_query

        # Step 1: Export from Elasticsearch
        success = dump_elasticsearch_data(chunk_config, es_dump_file, debug=debug)
        if not success:
            raise Exception("Failed to export data from Elasticsearch")

        # Count documents and generate line protocol
        documents_processed = 0
        total_points = 0

        # Step 2: Transform data
        with open(line_protocol_file, "w", encoding="utf-8") as lp_file:
            batch_lines = []

            for doc in read_jsonl_file(es_dump_file):
                documents_processed += 1

                # Transform document
                lines = transform_documents([doc], chunk_config)
                batch_lines.extend(lines)

                # Write batch when it reaches size limit
                if len(batch_lines) >= chunk_config.influxdb.batch_size:
                    valid_lines = []
                    for line in batch_lines:
                        if validate_line_protocol(line):
                            valid_lines.append(line)

                    for line in valid_lines:
                        lp_file.write(line + "\n")

                    total_points += len(valid_lines)
                    batch_lines = []

            # Write remaining lines
            if batch_lines:
                valid_lines = []
                for line in batch_lines:
                    if validate_line_protocol(line):
                        valid_lines.append(line)

                for line in valid_lines:
                    lp_file.write(line + "\n")

                total_points += len(valid_lines)

        # Step 3: Write to InfluxDB (unless dry run)
        points_written = 0
        if not dry_run and total_points > 0:
            success, points_written = write_to_influxdb(
                line_protocol_file, chunk_config
            )
            if not success:
                raise Exception("Failed to write data to InfluxDB")
        else:
            points_written = (
                total_points  # In dry run, count what would have been written
            )

        return documents_processed, points_written

    finally:
        # Clean up temporary files (unless in debug mode)
        if not debug:
            cleanup_temp_files(temp_files)


@app.command()
def validate(
    config_file: Path = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to configuration file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    sample_size: int = typer.Option(
        10,
        "--sample-size",
        "-n",
        help="Number of sample documents to transform and validate",
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug mode (keep temporary files and show paths)"
    ),
) -> None:
    """
    Validate configuration by testing transformation on sample data

    Exports a small sample of data from Elasticsearch and tests the
    transformation to InfluxDB line protocol format to verify that
    the field mappings work correctly.
    """
    try:
        config = load_config(config_file)

        # Override scroll size for sampling
        config.elasticsearch.scroll_size = sample_size

    except Exception as e:
        console.print(f"❌ Error loading configuration: {e}")
        raise typer.Exit(1)

    # Check dependencies
    deps = check_dependencies()
    if not deps.get("elasticdump"):
        console.print("❌ elasticdump is required for validation")
        raise typer.Exit(1)

    # Create temporary file
    temp_files = []
    try:
        temp_file = get_temp_file(".jsonl")
        temp_files.append(temp_file)

        if debug:
            console.print(f"🔍 Debug mode enabled")
            console.print(f"📄 ES dump file: {temp_file}")

    except Exception as e:
        console.print(f"❌ Error creating temporary file: {e}")
        raise typer.Exit(1)

    try:
        console.print(
            f"🔍 Validating configuration with {sample_size} sample documents..."
        )

        # Export sample data
        success = dump_elasticsearch_data(config, temp_file, debug=debug)
        if not success:
            raise typer.Exit(1)

        # Transform and validate
        sample_docs = []
        for i, doc in enumerate(read_jsonl_file(temp_file)):
            if i >= sample_size:
                break
            sample_docs.append(doc)

        if not sample_docs:
            console.print("⚠️  No documents found in sample")
            return

        console.print(f"📄 Processing {len(sample_docs)} sample documents...")

        # Transform documents
        line_protocol_lines = transform_documents(sample_docs, config)

        if not line_protocol_lines:
            console.print("❌ No valid line protocol generated from sample documents")
            console.print("   Check your field mappings and ensure source fields exist")
            raise typer.Exit(1)

        # Validate line protocol format
        valid_count = 0
        invalid_count = 0

        console.print("\n📝 Sample line protocol output:")
        console.print("=" * 80)

        for i, line in enumerate(line_protocol_lines[:5]):  # Show first 5 lines
            if validate_line_protocol(line):
                console.print(f"✅ {line}")
                valid_count += 1
            else:
                console.print(f"❌ {line}")
                invalid_count += 1

        if len(line_protocol_lines) > 5:
            console.print(f"... and {len(line_protocol_lines) - 5} more lines")

        console.print("=" * 80)

        # Summary
        total_valid = sum(
            1 for line in line_protocol_lines if validate_line_protocol(line)
        )
        total_invalid = len(line_protocol_lines) - total_valid

        console.print(f"\n📊 Validation Results:")
        console.print(f"  • Valid line protocol entries: {total_valid}")
        console.print(f"  • Invalid line protocol entries: {total_invalid}")
        console.print(
            f"  • Success rate: {total_valid/len(line_protocol_lines)*100:.1f}%"
        )

        if total_invalid > 0:
            console.print(
                "\n⚠️  Some entries failed validation. Check your field mappings."
            )
        else:
            console.print("\n✅ All entries are valid! Configuration looks good.")

    except Exception as e:
        console.print(f"❌ Validation failed: {e}")
        raise typer.Exit(1)
    finally:
        # Clean up temporary files (unless in debug mode)
        if debug:
            console.print(f"\n🔍 Debug mode: Temporary files preserved for inspection:")
            console.print(
                f"   📄 ES dump: {temp_file if 'temp_file' in locals() else 'N/A'}"
            )
        else:
            cleanup_temp_files(temp_files)


@app.command()
def troubleshoot(
    config_file: Path = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to configuration file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    )
) -> None:
    """
    Troubleshoot Elasticsearch connectivity and data availability

    Runs diagnostic checks to help identify why no data is being retrieved.
    """
    try:
        config = load_config(config_file)
    except Exception as e:
        console.print(f"❌ Error loading configuration: {e}")
        raise typer.Exit(1)

    console.print("🔍 Running Elasticsearch diagnostics...\n")

    # Test 1: Check if elasticdump can connect
    console.print("1️⃣ Testing elasticdump connectivity...")
    cmd = [
        "elasticdump",
        "--input",
        config.elasticsearch.url,
        "--output",
        "$",
        "--type",
        "mapping",
        "--limit",
        "1",
    ]

    console.print(f"   Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            console.print("   ✅ Connection successful")
            if result.stdout:
                console.print(f"   📋 Sample output: {result.stdout[:200]}...")
        else:
            console.print(f"   ❌ Connection failed: {result.stderr}")
    except Exception as e:
        console.print(f"   ❌ Error: {e}")

    # Test 2: Try without index filter
    console.print("\n2️⃣ Testing basic index listing...")
    cmd = [
        "elasticdump",
        "--input",
        config.elasticsearch.url + "/_cat/indices",
        "--output",
        "$",
        "--limit",
        "10",
    ]

    console.print(f"   Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            console.print("   ✅ Index listing successful")
            if result.stdout:
                console.print(f"   📋 Available indices: {result.stdout[:300]}...")
        else:
            console.print(f"   ❌ Index listing failed: {result.stderr}")
    except Exception as e:
        console.print(f"   ❌ Error: {e}")

    # Test 3: Try the exact configuration without query
    console.print("\n3️⃣ Testing configured index without query...")
    cmd = [
        "elasticdump",
        "--input",
        config.elasticsearch.url + "/" + config.elasticsearch.index,
        "--output",
        "$",
        "--type",
        "data",
        "--limit",
        "1",
    ]

    console.print(f"   Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            console.print("   ✅ Index access successful")
            if result.stdout:
                console.print(f"   📋 Sample data: {result.stdout[:300]}...")
            else:
                console.print("   ⚠️  No data returned (index might be empty)")
        else:
            console.print(f"   ❌ Index access failed: {result.stderr}")
    except Exception as e:
        console.print(f"   ❌ Error: {e}")

    # Test 4: Try with the configured query
    if config.elasticsearch.query:
        console.print("\n4️⃣ Testing with configured query...")
        import json

        query_json = json.dumps(config.elasticsearch.query)
        cmd = [
            "elasticdump",
            "--input",
            config.elasticsearch.url + "/" + config.elasticsearch.index,
            "--output",
            "$",
            "--type",
            "data",
            "--limit",
            "1",
            "--searchBody=" + query_json,
        ]

        console.print(f"   Command: {' '.join(cmd)}")
        console.print(f"   Query: {query_json}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                console.print("   ✅ Query successful")
                if result.stdout:
                    console.print(f"   📋 Sample data: {result.stdout[:300]}...")
                else:
                    console.print(
                        "   ⚠️  No data returned (query might be too restrictive)"
                    )
            else:
                console.print(f"   ❌ Query failed: {result.stderr}")
        except Exception as e:
            console.print(f"   ❌ Error: {e}")
    else:
        console.print("\n4️⃣ No custom query configured - skipping query test")

    console.print("\n📊 Troubleshooting Summary:")
    console.print(
        "   • If connection tests fail: Check Elasticsearch URL and authentication"
    )
    console.print(
        "   • If index listing works but your index fails: Check index name/pattern"
    )
    console.print(
        "   • If index works but query fails: Your query might be too restrictive"
    )
    console.print(
        "   • If everything works but no data: Your index might be empty or query returns no results"
    )


@app.command()
def inspect(
    file_path: Path = typer.Argument(
        ..., help="Path to ES dump (.jsonl) or line protocol (.lp) file to inspect"
    ),
    lines: int = typer.Option(10, "--lines", "-n", help="Number of lines to show"),
    file_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="File type: 'es' for ES dump, 'lp' for line protocol (auto-detected if not specified)",
    ),
) -> None:
    """
    Inspect ES dump or line protocol files

    Useful for debugging migration issues by examining the actual file contents.
    """
    if not file_path.exists():
        console.print(f"❌ File not found: {file_path}")
        raise typer.Exit(1)

    # Auto-detect file type if not specified
    if file_type is None:
        if file_path.suffix == ".jsonl":
            file_type = "es"
        elif file_path.suffix == ".lp":
            file_type = "lp"
        else:
            console.print("⚠️  Cannot auto-detect file type. Please specify with --type")
            raise typer.Exit(1)

    file_size = file_path.stat().st_size
    console.print(f"📄 File: {file_path}")
    console.print(f"📏 Size: {file_size:,} bytes")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if file_type == "es":
                console.print(f"\n📋 First {lines} ES documents:")
                console.print("=" * 80)
                for i, line in enumerate(f):
                    if i >= lines:
                        break
                    if line.strip():
                        try:
                            import json

                            doc = json.loads(line.strip())
                            console.print(f"Document {i+1}:")
                            console.print(
                                json.dumps(doc, indent=2)[:500] + "..."
                                if len(json.dumps(doc, indent=2)) > 500
                                else json.dumps(doc, indent=2)
                            )
                            console.print("-" * 40)
                        except json.JSONDecodeError:
                            console.print(
                                f"Invalid JSON on line {i+1}: {line[:100]}..."
                            )

            elif file_type == "lp":
                console.print(f"\n📋 First {lines} line protocol entries:")
                console.print("=" * 80)
                for i, line in enumerate(f):
                    if i >= lines:
                        break
                    if line.strip():
                        console.print(f"{i+1}: {line.strip()}")

        # Count total lines
        with open(file_path, "r", encoding="utf-8") as f:
            total_lines = sum(1 for line in f if line.strip())

        console.print("=" * 80)
        console.print(f"📊 Total non-empty lines: {total_lines:,}")

    except Exception as e:
        console.print(f"❌ Error reading file: {e}")
        raise typer.Exit(1)


@app.command()
def test_regex(
    config_file: Path = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to configuration file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    sample_size: int = typer.Option(
        5,
        "--sample-size",
        "-n",
        help="Number of sample documents to test regex patterns against",
    ),
    regex_name: Optional[str] = typer.Option(
        None,
        "--regex-name",
        "-r",
        help="Test only a specific regex mapping by field name",
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug mode (keep temporary files and show paths)"
    ),
) -> None:
    """
    Test regex patterns against sample data

    This command helps you test and debug regex patterns by showing exactly
    what would be extracted from sample documents in your Elasticsearch index.
    """
    try:
        config = load_config(config_file)

        if not config.regex_mappings:
            console.print("❌ No regex mappings found in configuration")
            console.print("   Add regex_mappings section to your config file")
            raise typer.Exit(1)

        # Override scroll size for sampling
        config.elasticsearch.scroll_size = sample_size

    except Exception as e:
        console.print(f"❌ Error loading configuration: {e}")
        raise typer.Exit(1)

    # Check dependencies
    deps = check_dependencies()
    if not deps.get("elasticdump"):
        console.print("❌ elasticdump is required for testing regex patterns")
        raise typer.Exit(1)

    # Create temporary file
    temp_files = []
    try:
        temp_file = get_temp_file(".jsonl")
        temp_files.append(temp_file)

        if debug:
            console.print(f"🔍 Debug mode enabled")
            console.print(f"📄 ES dump file: {temp_file}")

    except Exception as e:
        console.print(f"❌ Error creating temporary file: {e}")
        raise typer.Exit(1)

    try:
        console.print(
            f"🔍 Testing regex patterns with {sample_size} sample documents..."
        )

        # Export sample data
        success = dump_elasticsearch_data(config, temp_file, debug=debug)
        if not success:
            raise typer.Exit(1)

        # Load sample documents
        sample_docs = []
        for i, doc in enumerate(read_jsonl_file(temp_file)):
            if i >= sample_size:
                break
            sample_docs.append(doc)

        if not sample_docs:
            console.print("⚠️  No documents found in sample")
            return

        console.print(f"📄 Testing against {len(sample_docs)} sample documents...\n")

        # Test each regex mapping
        for regex_mapping in config.regex_mappings:
            # Skip if specific regex requested and this isn't it
            if regex_name and regex_mapping.es_field != regex_name:
                continue

            console.print(
                f"🔍 Testing regex mapping for field: [bold]{regex_mapping.es_field}[/bold]"
            )
            console.print(f"   Pattern: [yellow]{regex_mapping.regex_pattern}[/yellow]")
            console.print(
                f"   Groups: {', '.join(group.name for group in regex_mapping.groups)}"
            )

            matches_found = 0
            for i, doc in enumerate(sample_docs):
                source_doc = doc.get("_source", doc)
                source_value = get_nested_value(source_doc, regex_mapping.es_field)

                if source_value is None:
                    console.print(f"   📄 Doc {i+1}: Field not found")
                    continue

                # Test the regex pattern
                extracted_groups = extract_regex_groups(
                    str(source_value), regex_mapping.regex_pattern
                )

                if extracted_groups:
                    matches_found += 1
                    console.print(f"   📄 Doc {i+1}: [green]✅ Match found[/green]")
                    console.print(
                        f"      Source: [cyan]{str(source_value)[:100]}{'...' if len(str(source_value)) > 100 else ''}[/cyan]"
                    )

                    for group in regex_mapping.groups:
                        group_value = extracted_groups.get(group.name, "[not captured]")
                        console.print(
                            f"      {group.name}: [magenta]{group_value}[/magenta] → {group.influx_field} ({group.field_type})"
                        )
                else:
                    console.print(f"   📄 Doc {i+1}: [red]❌ No match[/red]")
                    console.print(
                        f"      Source: [cyan]{str(source_value)[:100]}{'...' if len(str(source_value)) > 100 else ''}[/cyan]"
                    )

            console.print(
                f"   📊 Results: {matches_found}/{len(sample_docs)} documents matched"
            )

            if matches_found == 0:
                console.print(
                    "   [red]⚠️  No matches found! Check your regex pattern.[/red]"
                )
            elif matches_found < len(sample_docs):
                console.print(
                    f"   [yellow]⚠️  Only {matches_found}/{len(sample_docs)} documents matched. Consider adding fallback handling.[/yellow]"
                )
            else:
                console.print(
                    "   [green]✅ All documents matched successfully![/green]"
                )

            console.print()

        if regex_name and not any(
            rm.es_field == regex_name for rm in config.regex_mappings
        ):
            console.print(f"❌ No regex mapping found for field: {regex_name}")
            console.print("Available regex mappings:")
            for rm in config.regex_mappings:
                console.print(f"   • {rm.es_field}")

    except Exception as e:
        console.print(f"❌ Regex testing failed: {e}")
        raise typer.Exit(1)
    finally:
        # Clean up temporary files (unless in debug mode)
        if debug:
            console.print(f"🔍 Debug mode: Temporary files preserved for inspection:")
            console.print(
                f"   📄 ES dump: {temp_file if 'temp_file' in locals() else 'N/A'}"
            )
        else:
            cleanup_temp_files(temp_files)


@app.command()
def empty_bucket(
    config_file: Path = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to configuration file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    bucket: Optional[str] = typer.Option(
        None, "--bucket", "-b", help="Bucket name to empty (overrides config file)"
    ),
    measurement: Optional[str] = typer.Option(
        None, "--measurement", "-m", help="Only delete data from specific measurement"
    ),
    start_time: Optional[str] = typer.Option(
        None,
        "--start",
        help="Start time for deletion (RFC3339 format, e.g., 2023-01-01T00:00:00Z)",
    ),
    stop_time: Optional[str] = typer.Option(
        None,
        "--stop",
        help="Stop time for deletion (RFC3339 format, e.g., 2023-12-31T23:59:59Z)",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be deleted without actually deleting"
    ),
    force: bool = typer.Option(
        False, "--force", help="Skip confirmation prompt (DANGEROUS!)"
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug mode with verbose output"
    ),
) -> None:
    """
    Empty an InfluxDB bucket or delete data within time ranges

    ⚠️  WARNING: This is a destructive operation that permanently deletes data!

    Examples:
      # Empty entire bucket (with confirmation)
      es2influx empty-bucket --config config.yaml --bucket metrics-test

      # Empty with time range
      es2influx empty-bucket --config config.yaml --start 2024-01-01T00:00:00Z --stop 2024-01-31T23:59:59Z

      # Dry run to preview deletion
      es2influx empty-bucket --config config.yaml --dry-run

      # Delete specific measurement
      es2influx empty-bucket --config config.yaml --measurement requests
    """
    try:
        config = load_config(config_file)

        # Use bucket from command line or config
        target_bucket = bucket or config.influxdb.bucket
        target_measurement = measurement or config.influxdb.measurement

    except Exception as e:
        console.print(f"❌ Error loading configuration: {e}")
        raise typer.Exit(1)

    # Check dependencies
    deps = check_dependencies()
    if not deps.get("influx"):
        console.print("❌ influx CLI is required for bucket operations")
        console.print(
            "   Install from: https://docs.influxdata.com/influxdb/v2.0/tools/influx-cli/"
        )
        raise typer.Exit(1)

    # Build the influx delete command
    cmd = [
        "influx",
        "delete",
        "--bucket",
        target_bucket,
        "--org",
        config.influxdb.org,
        "--token",
        config.influxdb.token,
        "--host",
        config.influxdb.url,
    ]

    # Add time range if specified
    if start_time:
        cmd.extend(["--start", start_time])
    if stop_time:
        cmd.extend(["--stop", stop_time])

    # Add measurement filter if specified
    predicate_parts = []
    if target_measurement:
        predicate_parts.append(f'_measurement="{target_measurement}"')

    if predicate_parts:
        cmd.extend(["--predicate", " AND ".join(predicate_parts)])

    # Show what will be deleted
    console.print("🗑️  InfluxDB Data Deletion Preview")
    console.print("=" * 50)
    console.print(f"📍 InfluxDB: {config.influxdb.url}")
    console.print(f"🏷️  Bucket: {target_bucket}")
    console.print(f"🏢 Organization: {config.influxdb.org}")

    if target_measurement:
        console.print(f"📊 Measurement: {target_measurement}")
    else:
        console.print("📊 Measurement: ALL measurements")

    if start_time or stop_time:
        console.print(
            f"📅 Time Range: {start_time or 'beginning'} to {stop_time or 'end'}"
        )
    else:
        console.print("📅 Time Range: ALL time (entire bucket)")

    console.print("=" * 50)

    if debug:
        console.print(f"🔍 Command to execute: {' '.join(cmd)}")

    if dry_run:
        console.print("🔍 DRY RUN MODE - No data will be deleted")
        console.print("✅ Command validated successfully")
        console.print("💡 Remove --dry-run to execute the deletion")
        return

    # Safety confirmation
    if not force:
        console.print(
            "\n⚠️  [bold red]WARNING: This will permanently delete data from InfluxDB![/bold red]"
        )
        console.print("   This operation cannot be undone!")
        console.print("   Make sure you have backups if needed.")

        if not typer.confirm("\nDo you want to continue?"):
            console.print("❌ Operation cancelled")
            return

    # Execute the deletion
    try:
        console.print("\n🔄 Deleting data from InfluxDB...")

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300  # 5 minutes timeout
        )

        if result.returncode == 0:
            console.print("✅ Data deletion completed successfully!")
            if result.stdout:
                console.print(f"📝 Output: {result.stdout}")
        else:
            console.print(
                f"❌ Data deletion failed with return code {result.returncode}"
            )
            if result.stderr:
                console.print(f"❌ Error: {result.stderr}")
            if result.stdout:
                console.print(f"📝 Output: {result.stdout}")
            raise typer.Exit(1)

    except subprocess.TimeoutExpired:
        console.print("❌ Data deletion timed out")
        console.print("   The operation may still be running in InfluxDB")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Error executing deletion: {e}")
        raise typer.Exit(1)

    console.print("\n📊 Deletion Summary:")
    console.print(f"   • Bucket: {target_bucket}")
    console.print(f"   • Measurement: {target_measurement or 'ALL'}")
    console.print(
        f"   • Time Range: {start_time or 'beginning'} to {stop_time or 'end'}"
    )
    console.print("\n💡 Next steps:")
    console.print("   • Verify the deletion worked as expected")
    console.print("   • Check InfluxDB UI to confirm data is gone")
    console.print("   • Consider running a new migration if needed")


if __name__ == "__main__":
    app()
