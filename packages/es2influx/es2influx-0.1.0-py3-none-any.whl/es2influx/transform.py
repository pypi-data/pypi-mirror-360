"""
Data transformation utilities for converting ES documents to InfluxDB line protocol
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from dateutil.parser import parse as parse_date

from .config import (
    FieldMapping,
    LookupFieldMapping,
    MigrationConfig,
    RegexFieldMapping,
    ValueTransformation,
)

# Global cache for lookup data to avoid reading JSON files repeatedly
_lookup_cache = {}


def load_lookup_data(lookup_file: str) -> Dict[str, Any]:
    """
    Load lookup data from JSON file with caching

    Args:
        lookup_file: Path to the JSON lookup file

    Returns:
        Dictionary containing the lookup data
    """
    if lookup_file not in _lookup_cache:
        try:
            with open(lookup_file, "r") as f:
                _lookup_cache[lookup_file] = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load lookup file {lookup_file}: {e}")
            _lookup_cache[lookup_file] = {}

    return _lookup_cache[lookup_file]


def apply_value_transformations(
    value: Any, transformations: List[ValueTransformation]
) -> Any:
    """
    Apply a sequence of transformations to a value

    Args:
        value: The input value to transform
        transformations: List of transformation configurations

    Returns:
        The transformed value
    """
    if not transformations or value is None:
        return value

    # Convert to string for transformations
    str_value = str(value)

    for transform in transformations:
        str_value = apply_single_transformation(str_value, transform)

    return str_value


def apply_single_transformation(value: str, transform: ValueTransformation) -> str:
    """
    Apply a single transformation to a string value

    Args:
        value: The input string value
        transform: The transformation configuration

    Returns:
        The transformed string value
    """
    # Check condition first (if specified)
    if transform.condition is not None:
        condition_met = check_transformation_condition(value, transform)
        if not condition_met:
            return value  # Skip transformation if condition not met

    if transform.type == "normalize_text":
        # Normalize text by cleaning up common issues
        result = value

        # Convert to lowercase
        if transform.lowercase:
            result = result.lower()

        # Replace spaces with underscores
        if transform.replace_spaces:
            result = re.sub(r"\s+", "_", result)

        # Remove special characters except letters, numbers, and underscores
        if transform.remove_special:
            result = re.sub(r"[^a-zA-Z0-9_]", "", result)

        return result

    elif transform.type == "regex_replace":
        # Replace using regex pattern
        if transform.pattern and transform.replacement is not None:
            try:
                return re.sub(transform.pattern, transform.replacement, value)
            except re.error:
                return value
        return value

    elif transform.type == "case_convert":
        # Convert case according to specified type
        if transform.case_type == "upper":
            return value.upper()
        elif transform.case_type == "lower":
            return value.lower()
        elif transform.case_type == "title":
            return value.title()
        elif transform.case_type == "snake_case":
            # Convert to snake_case
            result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", value)
            return re.sub(r"[^a-zA-Z0-9_]", "_", result).lower()
        elif transform.case_type == "camel_case":
            # Convert to camelCase
            components = re.split(r"[^a-zA-Z0-9]", value)
            return components[0].lower() + "".join(
                word.capitalize() for word in components[1:]
            )
        return value

    elif transform.type == "character_replace":
        # Replace specific characters
        if transform.find_chars and transform.replace_chars is not None:
            result = value
            for find_char in transform.find_chars:
                result = result.replace(find_char, transform.replace_chars)
            return result
        return value

    elif transform.type == "custom_mapping":
        # Direct value mapping (lookup table)
        if transform.mappings and value in transform.mappings:
            return transform.mappings[value]
        return value

    return value


def check_transformation_condition(value: str, transform: ValueTransformation) -> bool:
    """
    Check if a transformation condition is met

    Args:
        value: The input string value
        transform: The transformation configuration

    Returns:
        True if the condition is met, False otherwise
    """
    if transform.condition is None:
        return True  # No condition means always apply

    condition = transform.condition
    condition_value = transform.condition_value
    condition_values = transform.condition_values or []

    # If we have multiple condition values, check against all of them
    if condition_values:
        for cond_val in condition_values:
            if check_single_condition(value, condition, cond_val):
                return True
        return False

    # Single condition value
    if condition_value is not None:
        return check_single_condition(value, condition, condition_value)

    return True


def check_single_condition(value: str, condition: str, condition_value: str) -> bool:
    """
    Check a single condition against a value

    Args:
        value: The input string value
        condition: The condition type
        condition_value: The value to check against

    Returns:
        True if the condition matches, False otherwise
    """
    if condition == "equals":
        return value == condition_value
    elif condition == "regex":
        try:
            return bool(re.search(condition_value, value))
        except re.error:
            return False
    elif condition == "contains":
        return condition_value in value
    elif condition == "starts_with":
        return value.startswith(condition_value)
    elif condition == "ends_with":
        return value.endswith(condition_value)

    return False


def get_nested_value(document: Dict[str, Any], field_path: str) -> Any:
    """
    Get a nested value from a document using dot notation

    Args:
        document: The source document
        field_path: Dot-separated path to the field (e.g., "host.name")

    Returns:
        The value at the specified path, or None if not found
    """
    try:
        value = document
        for key in field_path.split("."):
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    except (KeyError, TypeError):
        return None


def apply_regex_pattern(
    value: str, pattern: str, group_name: Optional[str] = None
) -> Optional[str]:
    """
    Apply a regex pattern to a value and optionally extract a named group

    Args:
        value: The input string value
        pattern: The regex pattern to apply
        group_name: Optional named group to extract

    Returns:
        The extracted value or None if no match
    """
    if not isinstance(value, str):
        value = str(value)

    try:
        match = re.search(pattern, value)
        if match:
            if group_name:
                return match.groupdict().get(group_name)
            else:
                return match.group(1) if match.groups() else match.group(0)
        return None
    except re.error:
        return None


def extract_regex_groups(value: str, pattern: str) -> Dict[str, str]:
    """
    Extract all named groups from a regex pattern match

    Args:
        value: The input string value
        pattern: The regex pattern with named groups

    Returns:
        Dictionary of group names to extracted values
    """
    if not isinstance(value, str):
        value = str(value)

    try:
        match = re.search(pattern, value)
        if match:
            return match.groupdict()
        return {}
    except re.error:
        return {}


def convert_data_type(value: Any, target_type: str) -> Any:
    """
    Convert a value to the specified data type

    Args:
        value: The value to convert
        target_type: Target data type ('string', 'int', 'float', 'bool', 'timestamp')

    Returns:
        The converted value
    """
    if value is None:
        return None

    try:
        if target_type == "string":
            return str(value)
        elif target_type == "int":
            if isinstance(value, str):
                # Handle string numbers
                return int(float(value))
            return int(value)
        elif target_type == "float":
            return float(value)
        elif target_type == "bool":
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return bool(value)
        elif target_type == "timestamp":
            if isinstance(value, (int, float)):
                # Assume timestamp is in milliseconds if > 1e10, otherwise seconds
                if value > 1e10:
                    return int(value * 1000000)  # Convert to nanoseconds
                else:
                    return int(value * 1000000000)  # Convert to nanoseconds
            elif isinstance(value, str):
                # Parse string timestamp
                dt = parse_date(value)
                return int(dt.timestamp() * 1000000000)  # Convert to nanoseconds
            else:
                return value
        else:
            return value
    except (ValueError, TypeError, OverflowError):
        return None


def escape_string_value(value: str) -> str:
    """
    Escape a string value for InfluxDB line protocol

    Args:
        value: The string value to escape

    Returns:
        The escaped string value
    """
    # Escape backslashes and quotes in field values
    return value.replace("\\", "\\\\").replace('"', '\\"')


def escape_tag_value(value: str) -> str:
    """
    Escape a tag value for InfluxDB line protocol

    Args:
        value: The tag value to escape

    Returns:
        The escaped tag value
    """
    # Escape spaces, commas, and equals signs in tag values
    return value.replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def format_tag_value(value: Any) -> str:
    """
    Format a tag value for InfluxDB line protocol

    Args:
        value: The tag value to format

    Returns:
        The formatted and escaped tag value string (properly formatted for InfluxDB)
    """
    # Handle booleans specially to ensure lowercase format
    if isinstance(value, bool):
        formatted_value = "true" if value else "false"
    else:
        # For all other types, convert to string
        formatted_value = str(value)

    # Apply escaping for special characters
    return escape_tag_value(formatted_value)


def format_field_value(value: Any, data_type: str) -> str:
    """
    Format a field value for InfluxDB line protocol

    Args:
        value: The field value
        data_type: The data type of the field

    Returns:
        The formatted field value string
    """
    if value is None:
        return '""'

    if data_type == "string":
        return f'"{escape_string_value(str(value))}"'
    elif data_type == "int":
        return f"{int(value)}i"
    elif data_type == "float":
        return str(float(value))
    elif data_type == "bool":
        return "true" if value else "false"
    else:
        return f'"{escape_string_value(str(value))}"'


def document_to_line_protocol(
    document: Dict[str, Any], config: MigrationConfig
) -> Optional[str]:
    """
    Convert an ES document to InfluxDB line protocol format

    Args:
        document: The ES document
        config: The migration configuration

    Returns:
        The line protocol string, or None if conversion failed
    """
    tags = []
    fields = []
    timestamp = None

    # Process regular field mappings
    for mapping in config.field_mappings:
        # Get the value from the document
        value = get_nested_value(document, mapping.es_field)

        # Check if value is empty (None, empty string, or whitespace-only)
        is_empty = value is None or (isinstance(value, str) and not value.strip())

        # Use default value if field is empty or missing
        if (
            is_empty
            and hasattr(mapping, "default_value")
            and mapping.default_value is not None
        ):
            value = mapping.default_value

        # For tags, we must have a value (cannot be empty)
        if mapping.field_type == "tag" and (
            value is None or (isinstance(value, str) and not value.strip())
        ):
            if hasattr(mapping, "default_value") and mapping.default_value is not None:
                value = mapping.default_value
            else:
                continue  # Skip this tag if no default value

        # Skip empty values for fields (but not timestamp)
        if value is None and mapping.field_type == "field":
            continue

        # Apply regex pattern if specified
        if mapping.regex_pattern and value is not None:
            extracted_value = apply_regex_pattern(
                str(value), mapping.regex_pattern, mapping.regex_group
            )
            if extracted_value is not None:
                value = extracted_value
            elif mapping.default_value is not None:
                value = mapping.default_value
            else:
                continue  # Skip if regex didn't match and no default

        # Apply value transformations
        if (
            hasattr(mapping, "transformations")
            and mapping.transformations
            and value is not None
        ):
            value = apply_value_transformations(value, mapping.transformations)

        # Convert the data type
        converted_value = convert_data_type(value, mapping.data_type)
        if converted_value is None and mapping.field_type != "timestamp":
            continue

        # Handle different field types
        if mapping.field_type == "tag":
            # Ensure we have a non-empty string value for tags
            if converted_value is None or (
                isinstance(converted_value, str) and not converted_value.strip()
            ):
                # This shouldn't happen due to our earlier checks, but let's be safe
                continue
            tag_value = format_tag_value(converted_value)
            tags.append(f"{mapping.influx_field}={tag_value}")
        elif mapping.field_type == "field":
            field_value = format_field_value(converted_value, mapping.data_type)
            fields.append(f"{mapping.influx_field}={field_value}")
        elif mapping.field_type == "timestamp":
            timestamp = converted_value

    # Process regex-based field mappings with priority-based matching
    # Group regex mappings by source field to implement priority
    regex_by_field = {}
    for regex_mapping in config.regex_mappings:
        field = regex_mapping.es_field
        if field not in regex_by_field:
            regex_by_field[field] = []
        regex_by_field[field].append(regex_mapping)

    # Process each source field with priority-based matching
    for field_name, regex_mappings in regex_by_field.items():
        # Get the source value
        source_value = get_nested_value(document, field_name)
        if source_value is None:
            continue

        # Sort regex mappings by priority (lower numbers = higher priority)
        sorted_mappings = sorted(
            regex_mappings, key=lambda x: getattr(x, "priority", 999)
        )

        # Try each regex pattern in priority order, stop on first match
        matched = False
        for regex_mapping in sorted_mappings:
            if matched:
                break  # Priority-based: stop after first match

            # Extract all named groups using the regex pattern
            extracted_groups = extract_regex_groups(
                str(source_value), regex_mapping.regex_pattern
            )

            # Check if this pattern matched
            if extracted_groups:
                matched = (
                    True  # Mark as matched to prevent other patterns from processing
                )

                # Process each configured group from the matched pattern
                for group in regex_mapping.groups:
                    # Get the extracted value for this group
                    group_value = extracted_groups.get(group.name)

                    # Check if group value is empty (None, empty string, or whitespace-only)
                    is_empty = group_value is None or (
                        isinstance(group_value, str) and not group_value.strip()
                    )

                    # Use default value if group wasn't captured or is empty
                    if (
                        is_empty
                        and hasattr(group, "default_value")
                        and group.default_value is not None
                    ):
                        group_value = group.default_value

                    # For tags, we must have a value (cannot be empty)
                    if group.field_type == "tag" and (
                        group_value is None
                        or (isinstance(group_value, str) and not group_value.strip())
                    ):
                        if (
                            hasattr(group, "default_value")
                            and group.default_value is not None
                        ):
                            group_value = group.default_value
                        else:
                            continue  # Skip this tag if no default value

                    # Skip empty values for fields (but not timestamp)
                    if group_value is None and group.field_type == "field":
                        continue

                    # Apply value transformations
                    if (
                        hasattr(group, "transformations")
                        and group.transformations
                        and group_value is not None
                    ):
                        group_value = apply_value_transformations(
                            group_value, group.transformations
                        )

                    # Convert the data type
                    converted_value = convert_data_type(group_value, group.data_type)
                    if converted_value is None and group.field_type != "timestamp":
                        continue

                    # Handle different field types
                    if group.field_type == "tag":
                        # Ensure we have a non-empty string value for tags
                        if converted_value is None or (
                            isinstance(converted_value, str)
                            and not converted_value.strip()
                        ):
                            # This shouldn't happen due to our earlier checks, but let's be safe
                            continue
                        tag_value = format_tag_value(converted_value)
                        tags.append(f"{group.influx_field}={tag_value}")
                    elif group.field_type == "field":
                        field_value = format_field_value(
                            converted_value, group.data_type
                        )
                        fields.append(f"{group.influx_field}={field_value}")
                    elif group.field_type == "timestamp":
                        timestamp = converted_value

    # Process lookup-based field mappings with priority-based matching
    # Group lookup mappings by source field to implement priority
    lookup_by_field = {}
    for lookup_mapping in config.lookup_mappings:
        field = lookup_mapping.es_field
        if field not in lookup_by_field:
            lookup_by_field[field] = []
        lookup_by_field[field].append(lookup_mapping)

    # Process each source field with priority-based matching
    for field_name, lookup_mappings in lookup_by_field.items():
        # Get the source value (lookup key)
        source_value = get_nested_value(document, field_name)
        if source_value is None:
            continue

        # Sort lookup mappings by priority (lower numbers = higher priority)
        sorted_mappings = sorted(
            lookup_mappings, key=lambda x: getattr(x, "priority", 999)
        )

        # Try each lookup mapping in priority order, stop on first match
        matched = False
        for lookup_mapping in sorted_mappings:
            if matched:
                break  # Priority-based: stop after first match

            # Load lookup data from JSON file
            lookup_data = load_lookup_data(lookup_mapping.lookup_file)

            # Check if the source value exists in the lookup data
            lookup_key = str(source_value)
            if lookup_key in lookup_data:
                matched = (
                    True  # Mark as matched to prevent other mappings from processing
                )
                lookup_result = lookup_data[lookup_key]

                # Process each configured group from the matched lookup
                for group in lookup_mapping.groups:
                    # Get the value for this group from the lookup result
                    if isinstance(lookup_result, dict):
                        group_value = lookup_result.get(group.name)
                    else:
                        # If lookup result is not a dict, skip this group
                        continue

                    # Check if group value is empty (None, empty string, or whitespace-only)
                    is_empty = group_value is None or (
                        isinstance(group_value, str) and not group_value.strip()
                    )

                    # Use default value if group wasn't found or is empty
                    if (
                        is_empty
                        and hasattr(group, "default_value")
                        and group.default_value is not None
                    ):
                        group_value = group.default_value

                    # For tags, we must have a value (cannot be empty)
                    if group.field_type == "tag" and (
                        group_value is None
                        or (isinstance(group_value, str) and not group_value.strip())
                    ):
                        if (
                            hasattr(group, "default_value")
                            and group.default_value is not None
                        ):
                            group_value = group.default_value
                        else:
                            continue  # Skip this tag if no default value

                    # Skip empty values for fields (but not timestamp)
                    if group_value is None and group.field_type == "field":
                        continue

                    # Apply value transformations
                    if (
                        hasattr(group, "transformations")
                        and group.transformations
                        and group_value is not None
                    ):
                        group_value = apply_value_transformations(
                            group_value, group.transformations
                        )

                    # Convert the data type
                    converted_value = convert_data_type(group_value, group.data_type)
                    if converted_value is None and group.field_type != "timestamp":
                        continue

                    # Handle different field types
                    if group.field_type == "tag":
                        # Ensure we have a non-empty string value for tags
                        if converted_value is None or (
                            isinstance(converted_value, str)
                            and not converted_value.strip()
                        ):
                            # This shouldn't happen due to our earlier checks, but let's be safe
                            continue
                        tag_value = format_tag_value(converted_value)
                        tags.append(f"{group.influx_field}={tag_value}")
                    elif group.field_type == "field":
                        field_value = format_field_value(
                            converted_value, group.data_type
                        )
                        fields.append(f"{group.influx_field}={field_value}")
                    elif group.field_type == "timestamp":
                        timestamp = converted_value

    # Process computed fields (derived from other fields or logic)
    if hasattr(config, "computed_fields") and config.computed_fields:
        for computed_field in config.computed_fields:
            computed_value = None

            # Handle different logic types
            if computed_field.logic == "regex_match":
                # Boolean result based on pattern matching
                source_value = get_nested_value(document, computed_field.source_field)
                if source_value is not None:
                    for pattern in computed_field.patterns:
                        if re.search(pattern, str(source_value)):
                            computed_value = True
                            break
                if computed_value is None:
                    computed_value = computed_field.default_value

            elif computed_field.logic == "conditional_regex":
                # String value based on pattern conditions
                source_value = get_nested_value(document, computed_field.source_field)
                if source_value is not None:
                    for condition in computed_field.conditions:
                        if re.search(condition.pattern, str(source_value)):
                            computed_value = condition.value
                            break
                if computed_value is None:
                    computed_value = computed_field.default_value

            elif computed_field.logic == "numeric_comparison":
                # Boolean result based on numeric comparisons
                source_value = get_nested_value(document, computed_field.source_field)
                if source_value is not None:
                    try:
                        numeric_value = float(source_value)
                        if computed_field.operator == "lt":
                            computed_value = numeric_value < computed_field.threshold
                        elif computed_field.operator == "gt":
                            computed_value = numeric_value > computed_field.threshold
                        elif computed_field.operator == "eq":
                            computed_value = numeric_value == computed_field.threshold
                        elif computed_field.operator == "gte":
                            computed_value = numeric_value >= computed_field.threshold
                        elif computed_field.operator == "lte":
                            computed_value = numeric_value <= computed_field.threshold
                    except (ValueError, TypeError):
                        computed_value = computed_field.default_value
                if computed_value is None:
                    computed_value = computed_field.default_value

            elif computed_field.logic == "static_value":
                # Fixed value for all records
                computed_value = computed_field.value

            # Apply the computed value if we have one
            if computed_value is not None:
                # Apply value transformations to the computed value
                if (
                    hasattr(computed_field, "transformations")
                    and computed_field.transformations
                ):
                    computed_value = apply_value_transformations(
                        computed_value, computed_field.transformations
                    )

                # Convert the data type
                converted_value = convert_data_type(
                    computed_value, computed_field.data_type
                )
                if converted_value is not None:
                    # Handle different field types
                    if computed_field.field_type == "tag":
                        # OPTIMIZATION: Only include tags with meaningful values if omit_default is enabled
                        should_omit = False
                        if (
                            hasattr(computed_field, "omit_default")
                            and computed_field.omit_default
                        ):
                            is_default_value = (
                                converted_value == computed_field.default_value
                                or converted_value
                                in [False, "false", "none", "unknown", "", 0]
                            )
                            should_omit = is_default_value

                        # Only add tag if it has a meaningful value (or omit_default is disabled)
                        if (
                            not should_omit
                            and converted_value is not None
                            and not (
                                isinstance(converted_value, str)
                                and not converted_value.strip()
                            )
                        ):
                            tag_value = format_tag_value(converted_value)
                            tags.append(f"{computed_field.influx_field}={tag_value}")
                    elif computed_field.field_type == "field":
                        field_value = format_field_value(
                            converted_value, computed_field.data_type
                        )
                        fields.append(f"{computed_field.influx_field}={field_value}")
                    elif computed_field.field_type == "timestamp":
                        timestamp = converted_value

    # Must have at least one field
    if not fields:
        return None

    # Build the line protocol string
    line_parts = [config.influxdb.measurement]

    # Add tags
    if tags:
        line_parts.append("," + ",".join(tags))

    # Add fields
    line_parts.append(" " + ",".join(fields))

    # Add timestamp
    if timestamp is not None:
        line_parts.append(f" {timestamp}")

    return "".join(line_parts)


def transform_documents(
    documents: List[Dict[str, Any]], config: MigrationConfig
) -> List[str]:
    """
    Transform a batch of ES documents to InfluxDB line protocol

    Args:
        documents: List of ES documents
        config: The migration configuration

    Returns:
        List of line protocol strings
    """
    line_protocol_lines = []

    for doc in documents:
        # Extract the source document if it's wrapped in ES format
        source_doc = doc.get("_source", doc)

        # Convert to line protocol
        line = document_to_line_protocol(source_doc, config)
        if line:
            line_protocol_lines.append(line)

    return line_protocol_lines


def save_line_protocol(lines: List[str], output_file: str) -> None:
    """
    Save line protocol lines to a file

    Args:
        lines: List of line protocol strings
        output_file: Path to the output file
    """
    with open(output_file, "w") as f:
        for line in lines:
            f.write(line + "\n")


def validate_line_protocol(line: str) -> bool:
    """
    Basic validation of line protocol format

    Args:
        line: The line protocol string to validate

    Returns:
        True if the line appears to be valid, False otherwise
    """
    # More lenient validation - just check basic structure
    line = line.strip()
    if not line:
        return False

    # Split on first space to separate measurement+tags from fields+timestamp
    parts = line.split(" ", 1)
    if len(parts) < 2:
        return False

    measurement_and_tags = parts[0]
    fields_and_timestamp = parts[1]

    # Check measurement+tags part: should have at least measurement name
    if not measurement_and_tags or "=" in measurement_and_tags.split(",")[0]:
        return False

    # Check fields part: should have at least one field
    fields_part = fields_and_timestamp.split(" ")[0]
    if "=" not in fields_part:
        return False

    return True
