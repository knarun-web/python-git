"""test_day13.py - pytest tests for schema, validator13 modules."""

import os
import csv
import tempfile
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from schema import SchemaError, FileFormatError
from validator13 import validate_row, validate_file, write_bad_records, load_file_safe


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_temp_csv(rows: list[dict], fieldnames: list[str] = None) -> str:
    """Write rows to a temp CSV and return the path."""
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else ["id"]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False,
                                     encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return f.name


# ---------------------------------------------------------------------------
# validate_row tests
# ---------------------------------------------------------------------------

def test_valid_order_row_returns_no_errors():
    row = {
        "order_id":                    "a" * 32,
        "customer_id":                 "b" * 32,
        "order_status":                "delivered",
        "order_purchase_timestamp":    "2021-01-01 10:00:00",
        "order_estimated_delivery_date": "2021-01-10 00:00:00",
    }
    errors = validate_row(row, list(row.keys()), "orders.csv", 2)
    assert errors == []


def test_missing_required_field():
    row = {"order_id": "a" * 32, "order_status": "delivered"}
    errors = validate_row(row, ["order_id", "customer_id", "order_status"], "orders.csv", 2)
    assert any("customer_id" in e for e in errors)


def test_invalid_order_status():
    row = {
        "order_id":     "a" * 32,
        "customer_id":  "b" * 32,
        "order_status": "unknown_status",
        "order_purchase_timestamp": "2021-01-01 10:00:00",
        "order_estimated_delivery_date": "2021-01-10 00:00:00",
    }
    errors = validate_row(row, list(row.keys()), "orders.csv", 2)
    assert any("order_status" in e for e in errors)


def test_price_not_numeric():
    row = {"order_id": "a"*32, "product_id": "b"*32, "seller_id": "c"*32,
           "price": "abc", "freight_value": "1.0", "shipping_limit_date": "2021-01-01 00:00:00"}
    errors = validate_row(row, list(row.keys()), "order_items.csv", 2)
    assert any("price" in e for e in errors)


def test_price_zero_fails():
    row = {"order_id": "a"*32, "product_id": "b"*32, "seller_id": "c"*32,
           "price": "0.0", "freight_value": "1.0", "shipping_limit_date": "2021-01-01 00:00:00"}
    errors = validate_row(row, list(row.keys()), "order_items.csv", 2)
    assert any("price" in e and "> 0" in e for e in errors)


def test_invalid_zip_prefix():
    row = {"customer_id": "a"*32, "customer_unique_id": "b"*32,
           "customer_zip_code_prefix": "123"}
    errors = validate_row(row, list(row.keys()), "customers.csv", 2)
    assert any("zip" in e for e in errors)


def test_invalid_hex_id():
    row = {"order_id": "not-a-hex-id", "customer_id": "b"*32,
           "order_status": "delivered",
           "order_purchase_timestamp": "2021-01-01 10:00:00",
           "order_estimated_delivery_date": "2021-01-10 00:00:00"}
    errors = validate_row(row, list(row.keys()), "orders.csv", 2)
    assert any("order_id" in e and "32 hex" in e for e in errors)


# ---------------------------------------------------------------------------
# load_file_safe tests
# ---------------------------------------------------------------------------

def test_load_file_safe_missing_raises():
    with pytest.raises(FileFormatError, match="not found"):
        load_file_safe("nonexistent_file.csv")


def test_load_file_safe_empty_raises():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False,
                                     encoding="utf-8") as f:
        f.write("id,name\n")
        path = f.name
    try:
        with pytest.raises(FileFormatError, match="empty"):
            load_file_safe(path)
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# validate_file threshold test
# ---------------------------------------------------------------------------

def test_validate_file_raises_on_high_rejection():
    rows = [
        {"order_id": "bad", "customer_id": "b"*32, "order_status": "delivered",
         "order_purchase_timestamp": "2021-01-01 10:00:00",
         "order_estimated_delivery_date": "2021-01-10 00:00:00"},
    ] * 5  # all rows are bad (invalid order_id)
    path = make_temp_csv(rows)
    bad_path = path + "_bad.csv"
    try:
        with pytest.raises(SchemaError, match="rejection rate"):
            validate_file(path, ["order_id", "customer_id", "order_status",
                                  "order_purchase_timestamp",
                                  "order_estimated_delivery_date"],
                          bad_records_path=bad_path,
                          rejection_threshold=0.20)
    finally:
        os.unlink(path)
        if os.path.exists(bad_path):
            os.unlink(bad_path)