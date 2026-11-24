"""test_day12.py - pytest tests for reader, validator, and transformer."""

import os
import csv
import tempfile
import pytest

from reader import read_csv
from validator import to_snake_case, apply_column_mapping
from transformer import convert_types, calculate_order_totals


# ---------------------------------------------------------------------------
# read_csv tests
# ---------------------------------------------------------------------------

def test_read_csv_returns_list_of_dicts():
    """read_csv should return a list of dicts with correct keys and values."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False,
                                     encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "value"])
        writer.writerow(["1", "alpha", "9.99"])
        writer.writerow(["2", "beta", "4.50"])
        tmp_path = f.name
    try:
        rows = read_csv(tmp_path)
        assert len(rows) == 2
        assert rows[0] == {"id": "1", "name": "alpha", "value": "9.99"}
        assert rows[1]["name"] == "beta"
    finally:
        os.unlink(tmp_path)


def test_read_csv_empty_file_returns_empty_list():
    """read_csv on a header-only file should return an empty list."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False,
                                     encoding="utf-8", newline="") as f:
        f.write("id,name\n")
        tmp_path = f.name
    try:
        rows = read_csv(tmp_path)
        assert rows == []
    finally:
        os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# to_snake_case tests
# ---------------------------------------------------------------------------

def test_to_snake_case_spaces():
    assert to_snake_case("freight value") == "freight_value"


def test_to_snake_case_camel():
    assert to_snake_case("OrderID") == "order_id"


def test_to_snake_case_already_snake():
    assert to_snake_case("order_id") == "order_id"


def test_to_snake_case_hyphens():
    assert to_snake_case("order-status") == "order_status"


# ---------------------------------------------------------------------------
# calculate_order_totals tests
# ---------------------------------------------------------------------------

def test_calculate_order_totals_basic():
    rows = [
        {"order_id": "A", "price": 10.0, "freight_value": 2.0},
        {"order_id": "A", "price": 5.0,  "freight_value": 1.0},
        {"order_id": "B", "price": 20.0, "freight_value": 3.0},
    ]
    totals = calculate_order_totals(rows)
    assert totals["A"] == pytest.approx(18.0)
    assert totals["B"] == pytest.approx(23.0)


def test_calculate_order_totals_missing_freight():
    """Rows with None freight should treat it as 0."""
    rows = [
        {"order_id": "X", "price": 7.5, "freight_value": None},
    ]
    totals = calculate_order_totals(rows)
    assert totals["X"] == pytest.approx(7.5)


def test_calculate_order_totals_empty():
    assert calculate_order_totals([]) == {}