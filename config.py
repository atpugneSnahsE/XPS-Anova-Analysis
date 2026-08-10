"""Central configuration for the XPS analysis pipeline.

Every tunable parameter lives here so the pipeline can be re-run on new data
without touching the code. Change values, then run ``python main.py``.
"""

# ---------------------------------------------------------------------------
# Input / output
# ---------------------------------------------------------------------------
# Folder scanned for *.xlsx spectra (searched in this order; the second entry
# tolerates the space that is present in the actual folder name on disk).
INPUT_DIRS = ["FW_xps", "FW_ xps"]
RESULTS_DIR = "results"
SUMMARY_DIR = "summary"

# File extensions treated as spectra.
INPUT_PATTERNS = ["*.xlsx", "*.xls"]

# ---------------------------------------------------------------------------
# Peak detection (scipy.signal.find_peaks)
# ---------------------------------------------------------------------------
DETECT = {
    "prominence_pct": 2.0,   # minimum prominence as % of (max - min) intensity
    "height_pct": 1.0,       # minimum peak height as % of (max - min) intensity
    "distance": 5,           # minimum horizontal distance between peaks (points)
    "max_peaks": 12,         # hard cap on number of peaks fitted per spectrum
}

# ---------------------------------------------------------------------------
# Smoothing (Savitzky-Golay, applied before detection and used for fitting)
# ---------------------------------------------------------------------------
SMOOTH = {
    "enabled": True,
    "window": 11,     # window length (points), must be odd and < n_points
    "polyorder": 3,   # polynomial order, must be < window
}

# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------
# "shirley" or "tougaard"
BACKGROUND_METHOD = "shirley"
SHIRLEY_MAX_ITER = 200
SHIRLEY_TOL = 1e-4

# ---------------------------------------------------------------------------
# Peak fitting (lmfit)
# ---------------------------------------------------------------------------
# Model for each component: "voigt", "gaussian" or "lorentzian".
MODEL = "voigt"

# Voigt FWHM is not simply 2.355 * sigma, so this is used as the initial
# sigma guess: FWHM_guess / SIGMA_FWHM_RATIO.
SIGMA_FWHM_RATIO = 2.0
# Multiplicative range around the detected position within which the fitted
# center is allowed to move.
CENTER_DRIFT_FRACTION = 0.35

# After fitting, peaks whose area is below this fraction of the total fitted
# area (or whose height is below this fraction of the tallest peak) are
# discarded as ghosts. Set to 0 to keep every fitted peak.
MIN_PEAK_AREA_FRACTION = 0.01
MIN_PEAK_HEIGHT_FRACTION = 0.005

# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
PLOT = {
    "dpi": 300,
    "font_size": 14,
    "x_label": "Binding Energy (eV)",
    "y_label": "Intensity (a.u.)",
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FILE = "xps_pipeline.log"
LOG_LEVEL = "INFO"
