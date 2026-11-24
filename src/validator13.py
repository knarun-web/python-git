"""validator13.py - Row-level validation, bad record writing, and file-level checks."""

import csv
import re
from datetime import datetime
from pathlib import Path

from schema import SchemaError, FileFormatError, ALLOWED_ORDER_STATUSES


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

HEX_ID_RE    = re.compile(r"^[0-9a-f]{32}$")
ZIP_PREFIX_RE = re.compile(r"^\d{5}$")


# ---------------------------------------------------------------------------
# Task 1 & 2 — Row validation
# ---------------------------------------------------------------------------

def validate_row(
    row: dict,
    required_fields: list[str],
    filename: str,
    row_num: int,
) -> list[str]:
    """Validate a single row against schema and business rules.

    Args:
        row: Dict of field name to string value.
        required_fields: List of fields that must be non-empty.
        filename: Name of the source file (used for file-specific rules).
        row_num: 1-based row number for error messages.

    Returns:
        List of error strings. Empty list means the row is valid.
    """
    errors: list[str] = []

    # Task 2 — missing required fields
    for field in required_fields:
        if field not in row or (row[field] or "").strip() == "":
            errors.append(f"row {row_num}: missing required field '{field}'")

    if errors:
        return errors  # skip further checks if fields are missing

    # Task 4 — numeric price / freight
    for col in ("price", "freight_value", "payment_value"):
        if col in row:
            try:
                float(row[col])
            except ValueError:
                errors.append(f"row {row_num}: '{col}' is not numeric (got {row[col]!r})")

    # Task 4 — parseable dates
    for col in ("order_purchase_timestamp", "order_estimated_delivery_date",
                "order_delivered_carrier_date", "order_delivered_customer_date",
                "shipping_limit_date"):
        if col in row and row[col].strip():
            try:
                datetime.fromisoformat(row[col].strip())
            except ValueError:
                errors.append(f"row {row_num}: '{col}' is not a valid datetime (got {row[col]!r})")

    # Task 5 — price > 0
    if "price" in row:
        try:
            if float(row["price"]) <= 0:
                errors.append(f"row {row_num}: 'price' must be > 0 (got {row['price']})")
        except ValueError:
            pass  # already caught above

    # Task 5 — order_status in allowed list
    if "order_status" in row:
        status = row["order_status"].strip().lower()
        if status not in ALLOWED_ORDER_STATUSES:
            errors.append(f"row {row_num}: 'order_status' invalid (got {row['order_status']!r})")

    # Task 6 — zip prefix must be 5 digits
    for col in ("customer_zip_code_prefix", "seller_zip_code_prefix"):
        if col in row and row[col].strip():
            if not ZIP_PREFIX_RE.match(row[col].strip()):
                errors.append(f"row {row_num}: '{col}' must be 5 digits (got {row[col]!r})")

    # Task 6 — IDs must be 32 hex characters
    for col in ("order_id", "customer_id", "product_id", "seller_id",
                "customer_unique_id", "review_id"):
        if col in row and row[col].strip():
            if not HEX_ID_RE.match(row[col].strip()):
                errors.append(f"row {row_num}: '{col}' must be 32 hex chars (got {row[col]!r})")

    return errors


# ---------------------------------------------------------------------------
# Task 3 — Write bad records
# ---------------------------------------------------------------------------

def write_bad_records(bad_rows: list[dict], output_path: str) -> None:
    """Write rejected rows to a CSV file with a reason column.

    Args:
        bad_rows: List of dicts, each with original fields plus '_reason'.
        output_path: Path to write the bad_records.csv file.
    """
    if not bad_rows:
        return
    fieldnames = list(bad_rows[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bad_rows)


# ---------------------------------------------------------------------------
# Task 8 — Graceful missing/empty file handling
# ---------------------------------------------------------------------------

def load_file_safe(filepath: str) -> list[dict]:
    """Load a CSV file, raising FileFormatError if missing or empty.

    Args:
        filepath: Path to the CSV file.

    Returns:
        List of row dicts.

    Raises:
        FileFormatError: If the file does not exist or has no data rows.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileFormatError(f"File not found: {filepath}")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]
    if not rows:
        raise FileFormatError(f"File is empty (no data rows): {filepath}")
    return rows


# ---------------------------------------------------------------------------
# Task 9 & 10 — Validate a whole file, print summary, fail on threshold
# ---------------------------------------------------------------------------

def validate_file(
    filepath: str,
    required_fields: list[str],
    bad_records_path: str = "bad_records.csv",
    rejection_threshold: float = 0.20,
) -> dict:
    """Validate every row in a file and produce a summary.

    Args:
        filepath: Path to the CSV file.
        required_fields: Fields that must be present and non-empty.
        bad_records_path: Where to write rejected rows.
        rejection_threshold: Fraction of bad rows that triggers a SchemaError.

    Returns:
        Summary dict with keys: total, valid, rejected, rejection_rate.

    Raises:
        FileFormatError: If the file is missing or empty.
        SchemaError: If rejection rate exceeds the threshold.
    """
    filename = Path(filepath).name
    rows = load_file_safe(filepath)

    valid_rows: list[dict]  = []
    bad_rows:   list[dict]  = []

    for i, row in enumerate(rows, start=2):  # start=2 because row 1 is header
        errors = validate_row(row, required_fields, filename, i)
        if errors:
            bad_row = dict(row)
            bad_row["_reason"] = " | ".join(errors)
            bad_rows.append(bad_row)
        else:
            valid_rows.append(row)

    total    = len(rows)
    rejected = len(bad_rows)
    valid    = len(valid_rows)
    rate     = rejected / total if total else 0.0

    write_bad_records(bad_rows, bad_records_path)

    summary = {
        "file":           filename,
        "total":          total,
        "valid":          valid,
        "rejected":       rejected,
        "rejection_rate": round(rate, 4),
    }

    # Task 10 — fail if above threshold
    if rate > rejection_threshold:
        raise SchemaError(
            f"{filename}: rejection rate {rate:.1%} exceeds "
            f"threshold {rejection_threshold:.1%} "
            f"({rejected}/{total} rows rejected)"
        )

    return summary