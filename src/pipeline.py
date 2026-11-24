"""pipeline.py - Logging, config loading, output writing, manifest and run summary."""

import csv
import json
import logging
import os
import time
from datetime import UTC, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Task 1 & 2 — Logging setup
# ---------------------------------------------------------------------------

def setup_logging(log_folder: str) -> logging.Logger:
    """Configure a logger that writes to console and a timestamped log file.

    Args:
        log_folder: Directory where log files are written.

    Returns:
        Configured logger instance.
    """
    Path(log_folder).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_folder, f"pipeline_{timestamp}.log")

    logger = logging.getLogger("olist_pipeline")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

    # File handler
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logger.info(f"Logging started — log file: {log_path}")
    return logger


# ---------------------------------------------------------------------------
# Task 3 — Load config.yaml
# ---------------------------------------------------------------------------

def load_config(config_path: str) -> dict:
    """Load pipeline configuration from a YAML file.

    Args:
        config_path: Path to config.yaml.

    Returns:
        Dict of configuration values.
    """
    try:
        import yaml
    except ImportError as e:
        raise ImportError("PyYAML is required: pip install pyyaml") from e

    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Task 4 — Write clean output as CSV and JSON
# ---------------------------------------------------------------------------

def write_output_csv(rows: list[dict], output_path: str) -> None:
    """Write a list of dicts to a CSV file.

    Args:
        rows: List of row dicts to write.
        output_path: Destination file path.
    """
    if not rows:
        return
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_output_json(data: object, output_path: str) -> None:
    """Write data to a JSON file.

    Args:
        data: Any JSON-serialisable object.
        output_path: Destination file path.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


# ---------------------------------------------------------------------------
# Task 5 — Run summary JSON
# ---------------------------------------------------------------------------

def write_run_summary(summaries: list[dict], start_time: float, output_path: str) -> None:
    """Write a run summary JSON with counts and duration.

    Args:
        summaries: List of per-file summary dicts.
        start_time: Unix timestamp from time.time() at pipeline start.
        output_path: Where to write the summary JSON.
    """
    duration = round(time.time() - start_time, 3)
    summary = {
        "run_at": datetime.now(UTC).isoformat(),
        "duration_seconds": duration,
        "files_processed": len(summaries),
        "totals": {
            "total_rows": sum(s.get("total", 0) for s in summaries),
            "valid_rows": sum(s.get("valid", 0) for s in summaries),
            "rejected_rows": sum(s.get("rejected", 0) for s in summaries),
        },
        "per_file": summaries,
    }
    write_output_json(summary, output_path)


# ---------------------------------------------------------------------------
# Task 6 — Manifest: track processed files, skip on re-run
# ---------------------------------------------------------------------------

def load_manifest(manifest_path: str) -> dict:
    """Load the manifest of previously processed files.

    Args:
        manifest_path: Path to manifest JSON file.

    Returns:
        Dict of {filename: processed_at timestamp}.
    """
    path = Path(manifest_path)
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest: dict, manifest_path: str) -> None:
    """Save the updated manifest to disk.

    Args:
        manifest: Dict of {filename: processed_at timestamp}.
        manifest_path: Path to write the manifest JSON.
    """
    write_output_json(manifest, manifest_path)


def is_already_processed(filename: str, manifest: dict) -> bool:
    """Check if a file has already been processed in a previous run.

    Args:
        filename: Name of the CSV file.
        manifest: Loaded manifest dict.

    Returns:
        True if the file is in the manifest.
    """
    return filename in manifest