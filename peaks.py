"""Automatic peak detection with scipy.signal.find_peaks."""

from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks, savgol_filter

from config import DETECT, SMOOTH


def smooth(y: np.ndarray) -> np.ndarray:
    """Apply the configured Savitzky-Golay filter (returns a copy)."""
    window = min(SMOOTH["window"], len(y) if len(y) % 2 else len(y) - 1)
    if not SMOOTH["enabled"] or window < 5 or SMOOTH["polyorder"] >= window:
        return np.array(y)
    return savgol_filter(y, window, SMOOTH["polyorder"])


def detect_peaks(y: np.ndarray) -> np.ndarray:
    """Return indices of detected peaks on the smoothed spectrum.

    Thresholds in the config are given as percentages of the data range and
    converted to absolute values here, so they stay meaningful for spectra of
    any scale.
    """
    ys = smooth(y)
    span = float(ys.max() - ys.min()) or 1.0

    height = DETECT["height_pct"] / 100.0 * span
    prominence = DETECT["prominence_pct"] / 100.0 * span

    peaks, _ = find_peaks(
        ys,
        height=height,
        prominence=prominence,
        distance=DETECT["distance"],
    )

    # Sort by prominence (strongest first) and cap the number to fit.
    strengths = np.array([ys[p] for p in peaks])
    order = np.argsort(strengths)[::-1]
    peaks = peaks[order]

    max_peaks = DETECT.get("max_peaks")
    if max_peaks and len(peaks) > max_peaks:
        peaks = peaks[:max_peaks]

    return np.sort(peaks)


def merge_metadata_positions(be: np.ndarray, y: np.ndarray, peak_idx: np.ndarray,
                             positions: list[float] | None) -> np.ndarray:
    """Merge instrument-reported peak centres into the detected peak set.

    A metadata position is kept only if it falls inside the energy range and
    is farther than the configured distance from every already-detected peak.
    This recovers narrow/shoulder peaks that ``find_peaks`` misses, using the
    peak positions the instrument software already identified.
    """
    if not positions:
        return peak_idx

    candidates = list(peak_idx)
    existing = [be[i] for i in peak_idx]
    min_gap = DETECT["distance"] * float(np.median(np.abs(np.diff(be))) if len(be) > 1 else 1.0)

    for pos in positions:
        if not (be[0] <= pos <= be[-1]):
            continue
        if all(abs(pos - e) >= min_gap for e in existing):
            idx = int(np.argmin(np.abs(be - pos)))
            candidates.append(idx)
            existing.append(pos)

    return np.sort(np.unique(candidates))
