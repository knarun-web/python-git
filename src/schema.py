"""schema.py - Custom exceptions and required field definitions per Olist file."""


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class SchemaError(Exception):
    """Raised when a row is missing required fields or fails schema validation."""


class FileFormatError(Exception):
    """Raised when a file is missing, empty, or cannot be parsed."""


# ---------------------------------------------------------------------------
# Required fields per file
# ---------------------------------------------------------------------------

SCHEMA: dict[str, list[str]] = {
    "orders.csv": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_estimated_delivery_date",
    ],
    "order_items.csv": [
        "order_id",
        "product_id",
        "seller_id",
        "price",
        "freight_value",
        "shipping_limit_date",
    ],
    "customers.csv": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
    ],
    "products.csv": [
        "product_id",
    ],
    "sellers.csv": [
        "seller_id",
        "seller_zip_code_prefix",
    ],
    "order_payments.csv": [
        "order_id",
        "payment_value",
    ],
    "order_reviews.csv": [
        "review_id",
        "order_id",
    ],
}

# Allowed values for order_status business rule
ALLOWED_ORDER_STATUSES: set[str] = {
    "delivered",
    "shipped",
    "canceled",
    "unavailable",
    "invoiced",
    "processing",
    "approved",
    "created",
}