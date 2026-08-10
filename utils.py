"""Shared helper functions: logging, progress reporting, column detection."""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import pandas as pd


def setup_logging(level: str = "INFO", log_file: str = "xps_pipeline.log") -> logging.Logger:
    """Configure a root logger that writes to both console and a log file."""
    logger = logging.getLogger("xps")
    if logger.handlers:  # already configured
        return logger
    logger.setLevel(level.upper())

    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S")

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(sh)
    return logger


def sanitize_name(name: str) -> str:
    """Turn an arbitrary worksheet name into a safe filesystem name."""
    cleaned = re.sub(r"[^\w\-]+", "_", str(name)).strip("_")
    return cleaned or "sheet"


def parse_number(value) -> float | None:
    """Coerce a raw Excel cell to float, returning None if not numeric."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def detect_columns(sheet) -> tuple[int, int] | None:
    """Locate the data header row and the Binding Energy / Intensity columns.

    Scans every row of the worksheet looking for the first row whose cells
    contain a binding-energy header (``B.E.``) and an intensity header
    (``CPS`` / ``Counts`` / ``Intensity``). Returns ``(data_start_row,
    (be_col, int_col))`` or ``None`` if no usable header is found.

    The first row index is the one *after* the header row, i.e. where the
    numeric data begins.
    """
    header_keywords_be = {"b.e.", "binding energy", "be"}
    header_keywords_int = {"cps", "counts", "intensity", "cts/s"}

    for row_idx, row in enumerate(sheet.iter_rows(values_only=True)):
        cells = {str(v).strip().lower() if v is not None else "" for v in row}
        be_cols = cells & header_keywords_be
        int_cols = cells & header_keywords_int
        if be_cols and int_cols:
            header_row = row
            be_col = next(
                i for i, v in enumerate(header_row)
                if v is not None and str(v).strip().lower() in header_keywords_be
            )
            int_col = next(
                i for i, v in enumerate(header_row)
                if v is not None and str(v).strip().lower() in header_keywords_int
            )
            return row_idx + 1, (be_col, int_col)
    return None


def report_progress(current: int, total: int) -> None:
    """Print ``Processing k/N`` style progress to stdout."""
    print(f"Processing {current}/{total}")
