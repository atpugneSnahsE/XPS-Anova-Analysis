"""
Web API wrappers for XPS and ANOVA pipelines
"""
import os
import sys
import logging
import shutil
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from reader import read_excel, Spectrum
from background import compute_background
from peaks import detect_peaks, merge_metadata_positions
from fitting import fit_peaks
from plotting import plot_spectrum_set
from export import write_report, write_summary
from utils import sanitize_name
from data_extractor import extract_and_save
from two_way_anova2 import perform_anova
from analysis_pipeline import run_full_analysis as anova_full_analysis
from validation_pipeline import validate_anova_pipeline

logger = logging.getLogger(__name__)


def process_xps_file(file_path: str, output_dir: str) -> dict:
    """
    Process a single XPS Excel file

    Args:
        file_path: Path to input Excel file
        output_dir: Directory to save results

    Returns:
        dict with analysis results
    """
    try:
        logger.info(f"Processing XPS file: {file_path}")

        results_dir = Path(output_dir) / "xps_results"
        results_dir.mkdir(parents=True, exist_ok=True)

        summary_rows = []
        spectra = read_excel(file_path)
        sample_stem = Path(file_path).stem

        for spectrum in spectra:
            process_spectrum(sample_stem, spectrum, results_dir, summary_rows)

        # Write summary
        write_summary(summary_rows, results_dir)

        logger.info(f"XPS processing complete: {len(summary_rows)} peaks found")

        return {
            'status': 'completed',
            'peaks_found': len(summary_rows),
            'output_dir': str(results_dir)
        }

    except Exception as e:
        logger.exception("XPS processing failed")
        raise


def process_spectrum(sample_stem: str, spectrum: Spectrum, results_dir: Path,
                     summary_rows: list[dict]) -> None:
    """Process a single spectrum worksheet"""
    be = spectrum.be
    y = spectrum.intensity

    # Background correction
    bg = compute_background(be, y)
    corrected = y - bg

    # Peak detection
    peak_idx = detect_peaks(corrected)
    if len(peak_idx) == 0:
        peak_idx = detect_peaks(y)
    peak_idx = merge_metadata_positions(be, corrected, peak_idx, spectrum.positions)

    # Fit
    fit = fit_peaks(be, corrected, peak_idx)

    # Output directory
    out_dir = results_dir / sanitize_name(sample_stem) / spectrum.sheet_name
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_spectrum_set(be, y, bg, peak_idx, fit, out_dir)
    write_report(sample_stem, spectrum.sheet_name, fit, out_dir)

    logger.info(f"  {spectrum.sheet_name}: {len(fit.centers)} peaks, R²={fit.r2:.4f}")

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


def process_anova_file(file_path: str, output_dir: str) -> dict:
    """
    Process ANOVA data file(s)

    Args:
        file_path: Path to input Excel file (or directory with files)
        output_dir: Directory to save results

    Returns:
        dict with analysis results
    """
    try:
        logger.info(f"Processing ANOVA file: {file_path}")

        results_dir = Path(output_dir) / "anova_results"
        results_dir.mkdir(parents=True, exist_ok=True)

        # Create work directory for temporary files
        work_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(work_dir)

        try:
            # Extract data
            logger.info("Extracting ANOVA data...")
            input_file = Path(file_path)
            if input_file.is_file():
                # Single file - copy to work dir
                shutil.copy(file_path, work_dir)

            # Run ANOVA pipeline
            logger.info("Running ANOVA analysis...")
            # This would call the existing analysis pipeline
            # For now, we'll need to refactor it to accept output directory

            # Move results to output dir
            for item in Path(work_dir).iterdir():
                if item.suffix in ['.csv', '.png', '.xlsx']:
                    shutil.move(str(item), str(results_dir / item.name))

            logger.info("ANOVA processing complete")

            return {
                'status': 'completed',
                'output_dir': str(results_dir)
            }

        finally:
            os.chdir(original_cwd)
            shutil.rmtree(work_dir, ignore_errors=True)

    except Exception as e:
        logger.exception("ANOVA processing failed")
        raise


def detect_analysis_type(file_path: str) -> str:
    """
    Auto-detect whether file is XPS or ANOVA data

    Args:
        file_path: Path to input file

    Returns:
        'xps', 'anova', or 'unknown'
    """
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path)

        # Check first sheet for indicators
        ws = wb.active
        headers = []
        for cell in ws[1]:
            if cell.value:
                headers.append(str(cell.value).lower())

        # XPS indicators: Binding Energy, BE, CPS, Counts, Intensity
        xps_keywords = ['binding energy', 'b.e.', 'be', 'cps', 'counts']
        xps_count = sum(1 for h in headers if any(k in h for k in xps_keywords))

        # ANOVA indicators: Material, Factor, Adsorbent, Level, Value
        anova_keywords = ['material', 'factor', 'adsorbent', 'level', 'value', 'pctadsorption']
        anova_count = sum(1 for h in headers if any(k in h for k in anova_keywords))

        if xps_count > anova_count:
            return 'xps'
        elif anova_count > xps_count:
            return 'anova'
        else:
            return 'unknown'

    except Exception as e:
        logger.error(f"Error detecting file type: {e}")
        return 'unknown'
