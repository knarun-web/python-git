"""reader.py - CSV reading utilities for Olist data."""

import csv


def read_csv(path: str) -> list[dict]:
    """Read a CSV file and return a list of dictionaries.

    Each dictionary represents one row, with column names as keys.

    Args:
        path: Path to the CSV file.

    Returns:
        A list of dicts, one per data row.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]