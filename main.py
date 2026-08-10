"""Automated XPS analysis pipeline.

Reads every Excel file inside ``FW_xps`` (or ``FW_ xps``), detects and fits
peaks in every worksheet, produces publication-quality figures and exports
per-spectrum and global reports.

Usage:
    python main.py

Outputs:
    results/<sample>/<sheet>/   five figures + report.csv + report.xlsx
    summary/                    all_peak_areas.csv, all_peak_positions.csv, summary.xlsx
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from background import compute_background
from config import INPUT_DIRS, INPUT_PATTERNS, RESULTS_DIR, SUMMARY_DIR
from export import write_report, write_summary
from fitting import fit_peaks
from peaks import detect_peaks, merge_metadata_positions
from plotting import plot_spectrum_set
from reader import read_excel, Spectrum
from utils import report_progress, sanitize_name, setup_logging

logger = logging.getLogger("xps")


def find_input_dir() -> Path | None:
    """Return the first existing input directory from the config."""
    for name in INPUT_DIRS:
        path = Path(name)
        if path.is_dir():
            return path
    return None


def list_spectra_files(input_dir: Path) -> list[Path]:
    """Return every matching input file, sorted for stable output."""
    files: list[Path] = []
    for pattern in INPUT_PATTERNS:
        files.extend(input_dir.glob(pattern))
    return sorted(dict.fromkeys(files))


def process_spectrum(sample_stem: str, spectrum: Spectrum, results_dir: Path,
                     summary_rows: list[dict]) -> None:
    """Run the full pipeline on one worksheet and export its results."""
    be = spectrum.be
    y = spectrum.intensity

    # Background correction
    bg = compute_background(be, y)
    corrected = y - bg

    # Peak detection on the background-corrected data (smoothed internally);
    # falls back to the raw spectrum if nothing is found there, then merges
    # the instrument-reported peak centres from the worksheet metadata.
    peak_idx = detect_peaks(corrected)
    if len(peak_idx) == 0:
        peak_idx = detect_peaks(y)
    peak_idx = merge_metadata_positions(be, corrected, peak_idx, spectrum.positions)

    # Fit
    fit = fit_peaks(be, corrected, peak_idx)

    # Output directory per sample/sheet
    out_dir = results_dir / sanitize_name(sample_stem) / spectrum.sheet_name
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_spectrum_set(be, y, bg, peak_idx, fit, out_dir)
    write_report(sample_stem, spectrum.sheet_name, fit, out_dir)

    logger.info("  %s: %d peaks, R²=%.4f, χ²=%.3g", spectrum.sheet_name,
                len(fit.centers), fit.r2, fit.reduced_chi2)

    # Accumulate summary rows
    for i in range(len(fit.centers)):
        summary_rows.append({
            "Filename": f"{sample_stem}.xlsx",
            "Sheet": spectrum.sheet_name,
            "Peak Number": i + 1,
            "Center": fit.centers[i],
            "Area": fit.areas[i],
            "Height": fit.heights[i],
            "FWHM": fit.fwhms[i],
            "R²": fit.r2,
            "Chi²": fit.reduced_chi2,
        })


def main() -> int:
    setup_logging()
    logger.info("XPS pipeline started")

    input_dir = find_input_dir()
    if input_dir is None:
        logger.error("No input directory found (looked for %s)", INPUT_DIRS)
        return 1

    files = list_spectra_files(input_dir)
    if not files:
        logger.error("No Excel files found in %s", input_dir)
        return 1

    results_dir = Path(RESULTS_DIR)
    summary_rows: list[dict] = []
    total = len(files)

    for index, file_path in enumerate(files, start=1):
        report_progress(index, total)
        logger.info("Processing %s", file_path.name)
        try:
            spectra = read_excel(file_path)
            for spectrum in spectra:
                process_spectrum(file_path.stem, spectrum, results_dir, summary_rows)
        except Exception:
            logger.exception("Skipping corrupted/unreadable file: %s", file_path.name)
            continue

    write_summary(summary_rows, Path(SUMMARY_DIR))
    logger.info("Done: %d file(s), %d peak row(s) in summary", total, len(summary_rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
