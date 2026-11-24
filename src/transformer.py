"""transformer.py - Type conversion and aggregation utilities."""

from datetime import datetime


def convert_types(rows: list[dict], float_cols: list[str], datetime_cols: list[str]) -> list[dict]:
    """Convert specified columns to float and datetime types.

    Invalid or empty values are set to None.

    Args:
        rows: List of row dicts.
        float_cols: Column names to convert to float.
        datetime_cols: Column names to convert to datetime.

    Returns:
        New list of dicts with converted values.
    """
    result = []
    for row in rows:
        new_row = dict(row)
        for col in float_cols:
            if col in new_row:
                try:
                    new_row[col] = float(new_row[col]) if new_row[col] else None
                except (ValueError, TypeError):
                    new_row[col] = None
        for col in datetime_cols:
            if col in new_row:
                try:
                    new_row[col] = datetime.fromisoformat(new_row[col]) if new_row[col] else None
                except (ValueError, TypeError):
                    new_row[col] = None
        result.append(new_row)
    return result


def calculate_order_totals(rows: list[dict], id_col: str = "order_id",
                           price_col: str = "price", freight_col: str = "freight_value") -> dict[str, float]:
    """Calculate total spend (price + freight) per order_id.

    Args:
        rows: List of row dicts from order_items, with types already converted.
        id_col: Column name for the order identifier.
        price_col: Column name for item price.
        freight_col: Column name for freight value.

    Returns:
        Dict of {order_id: total_amount}.
    """
    totals: dict[str, float] = {}
    for row in rows:
        oid = row.get(id_col)
        price = row.get(price_col) or 0.0
        freight = row.get(freight_col) or 0.0
        if oid:
            totals[oid] = totals.get(oid, 0.0) + price + freight
    return totals