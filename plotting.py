"""Publication-quality figures for the XPS pipeline.

One figure per spectrum, saved at 300 dpi with inverted (XPS-convention) x
axis and scientific labels. Figure files written to ``results/<sample>/``:

1. ``raw_spectrum.png``    - the imported data
2. ``background.png``      - data + Shirley/Tougaard background + corrected
3. ``detected_peaks.png``  - smoothed data with detected peak markers
4. ``fitted.png``          - corrected data, total fit and individual peaks
5. ``residual.png``        - fit residuals
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import PLOT
from peaks import smooth

plt.rcParams.update({
    "font.size": PLOT["font_size"],
    "axes.labelsize": PLOT["font_size"],
    "xtick.labelsize": PLOT["font_size"] - 2,
    "ytick.labelsize": PLOT["font_size"] - 2,
    "legend.fontsize": PLOT["font_size"] - 2,
    "axes.titlesize": PLOT["font_size"] + 2,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def _new_axes(ylabel: str, xlabel: str | None = None):
    """One axes with the shared styling: inverted x axis, tight box."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlabel(xlabel or PLOT["x_label"])
    ax.set_ylabel(ylabel)
    ax.invert_xaxis()
    return fig, ax


def _save(fig, path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=PLOT["dpi"], bbox_inches="tight")
    plt.close(fig)


def plot_raw(be, y, path) -> None:
    fig, ax = _new_axes(PLOT["y_label"])
    ax.plot(be, y, color="black", lw=1.0, label="Raw data")
    ax.legend()
    _save(fig, path)


def plot_background(be, y, bg, path) -> None:
    fig, ax = _new_axes(PLOT["y_label"])
    ax.plot(be, y, color="black", lw=1.0, label="Raw data")
    ax.plot(be, bg, color="red", lw=1.4, label="Background")
    ax.plot(be, y - bg, color="blue", lw=1.0, label="Background-subtracted")
    ax.legend()
    _save(fig, path)


def plot_detected(be, y, peak_idx, path) -> None:
    fig, ax = _new_axes(PLOT["y_label"])
    ax.plot(be, y, color="black", lw=1.0, label="Smoothed data")
    ax.plot(be[peak_idx], y[peak_idx], "o", color="red", ms=7, label="Detected peaks")
    ax.legend()
    _save(fig, path)


def plot_fit(be, y, fit, path) -> None:
    fig, ax = _new_axes(PLOT["y_label"])
    ax.plot(be, y, color="black", lw=1.0, label="Background-subtracted data")
    ax.plot(be, fit.best_fit, color="red", lw=1.6, label="Total fit")
    for i, comp in enumerate(fit.components):
        ax.plot(be, comp, "--", lw=1.0, label=f"Peak {i + 1} ({fit.centers[i]:.2f} eV)")
    ax.legend()
    _save(fig, path)


def plot_residual(be, y, fit, path) -> None:
    fig, ax = _new_axes(PLOT["y_label"])
    ax.plot(be, fit.residual, color="black", lw=1.0, label="Residual")
    ax.axhline(0.0, color="red", lw=0.8, ls="--")
    m = abs(fit.residual).max()
    if m > 0:
        ax.set_ylim(-1.2 * m, 1.2 * m)
    ax.legend()
    _save(fig, path)


def plot_spectrum_set(be, y, bg, peak_idx, fit, out_dir) -> None:
    """Render all five figures for one spectrum into ``out_dir``."""
    plot_raw(be, y, out_dir / "raw_spectrum.png")
    plot_background(be, y, bg, out_dir / "background.png")
    plot_detected(be, smooth(y), peak_idx, out_dir / "detected_peaks.png")
    plot_fit(be, y - bg, fit, out_dir / "fitted.png")
    plot_residual(be, y - bg, fit, out_dir / "residual.png")
