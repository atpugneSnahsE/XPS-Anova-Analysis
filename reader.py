"""Excel import for XPS data.

Each worksheet in an Avantage-style export holds one spectrum (a region such
as ``C 1s``). The worksheet is read as raw cells, the header row is located,
numeric columns are extracted and returned as a tidy DataFrame with two
columns:

* ``be``     - binding energy in eV (sorted ascending)
* ``intensity`` - counts per second

Metadata rows above the header and blank rows are ignored automatically.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

from utils import detect_columns, sanitize_name

logger = logging.getLogger("xps")


@dataclass
class Spectrum:
    """One extracted spectrum."""

    sheet_name: str
    be: np.ndarray
    intensity: np.ndarray
    positions: list[float] | None = None  # instrument-reported peak centres (eV)


def _read_positions(wb, sheet_name: str) -> list[float]:
    """Extract the 'Position' peak-centre row from the worksheet metadata."""
    ws = wb[sheet_name]
    for row in ws.iter_rows(values_only=True):
        if row and str(row[0]).strip().lower() == "position":
            values = []
            for v in row[2:]:
                try:
                    values.append(float(v))
                except (TypeError, ValueError):
                    continue
            return values
    return []


def _read_worksheet(wb, sheet_name: str) -> Spectrum | None:
    """Extract one worksheet into a Spectrum, or None if it has no data."""
    ws = wb[sheet_name]
    detected = detect_columns(ws)
    if detected is None:
        logger.warning("  no B.E./intensity header found in worksheet '%s'", sheet_name)
        return None

    data_start, (be_col, int_col) = detected

    rows: list[tuple[float, float]] = []
    for row in ws.iter_rows(values_only=True):
        be, intensity = row[be_col], row[int_col]
        # Skip non-numeric / empty cells (NaNs are dropped again below).
        try:
            be_f, int_f = float(be), float(intensity)
        except (TypeError, ValueError):
            continue
        if np.isfinite(be_f) and np.isfinite(int_f):
            rows.append((be_f, int_f))

    if not rows:
        logger.warning("  worksheet '%s' has no usable numeric data", sheet_name)
        return None

    df = pd.DataFrame(rows, columns=["be", "intensity"]).dropna().sort_values("be")
    if len(df) < 10:
        logger.warning("  worksheet '%s' has too few points (%d)", sheet_name, len(df))
        return None

    return Spectrum(
        sheet_name=sanitize_name(sheet_name),
        be=df["be"].to_numpy(dtype=float),
        intensity=df["intensity"].to_numpy(dtype=float),
        positions=_read_positions(wb, sheet_name),
    )


def read_excel(file_path: Path) -> list[Spectrum]:
    """Read every spectrum (worksheet) from an Excel workbook.

    Corrupted workbooks raise an exception that is caught by the caller, which
    skips the file and continues.
    """
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    spectra = []
    try:
        for sheet_name in wb.sheetnames:
            spectrum = _read_worksheet(wb, sheet_name)
            if spectrum is not None:
                spectra.append(spectrum)
    finally:
        wb.close()
    return spectra
