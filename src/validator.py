"""validator.py - Column name and schema validation utilities."""

import json
import re


def to_snake_case(name: str) -> str:
    """Convert a column name string to snake_case.

    Handles spaces, hyphens, and CamelCase.

    Args:
        name: Original column name.

    Returns:
        snake_case version of the name.

    Examples:
        >>> to_snake_case("OrderID")
        'order_id'
        >>> to_snake_case("freight value")
        'freight_value'
    """
    # Insert underscore before uppercase letters that follow lowercase
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # Replace spaces and hyphens with underscores
    name = re.sub(r"[\s\-]+", "_", name)
    return name.lower().strip("_")


def load_column_mapping(config_path: str) -> dict[str, str]:
    """Load a column mapping dictionary from a JSON config file.

    Args:
        config_path: Path to the JSON file containing the mapping.

    Returns:
        A dict mapping original column names to standard schema names.
    """
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def apply_column_mapping(rows: list[dict], mapping: dict[str, str]) -> list[dict]:
    """Rename columns in each row according to a mapping dictionary.

    Columns not in the mapping are kept unchanged.

    Args:
        rows: List of row dicts from read_csv.
        mapping: Dict of {original_name: standard_name}.

    Returns:
        New list of dicts with renamed keys.
    """
    return [
        {mapping.get(k, k): v for k, v in row.items()}
        for row in rows
    ]