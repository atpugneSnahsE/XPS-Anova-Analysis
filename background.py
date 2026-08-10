"""Background correction: Shirley (default) and Tougaard (optional)."""

from __future__ import annotations

import numpy as np

from config import BACKGROUND_METHOD, SHIRLEY_MAX_ITER, SHIRLEY_TOL


def shirley(y: np.ndarray, max_iter: int = SHIRLEY_MAX_ITER,
            tol: float = SHIRLEY_TOL) -> np.ndarray:
    """Iterative Shirley background.

    The background is anchored at the intensity *minima* of the first and last
    ``max(5, 1% of points)`` channels rather than the raw endpoint values, so
    spectra whose energy window ends inside a peak do not overshoot. The
    background is also clipped to never exceed the data.
    """
    y = np.asarray(y, dtype=float)
    n = len(y)
    w = max(5, n // 100)

    # Endpoint anchors from the flat tails, not the raw first/last channel.
    y0 = float(np.min(y[:w]))
    yN = float(np.min(y[n - w:]))
    b = np.full(n, 0.5 * (y0 + yN))  # initial guess: linear average

    for _ in range(max_iter):
        integral = np.zeros(n)
        for i in range(1, n):
            integral[i] = integral[i - 1] + 0.5 * (y[i - 1] - b[i - 1] + y[i] - b[i])
        if integral[-1] <= 0:  # degenerate: no intensity above the background
            break
        b_new = y0 - integral / integral[-1] * (y0 - yN)
        b_new = np.minimum(b_new, y)  # never above the data
        if np.allclose(b_new, b, atol=tol):
            b = b_new
            break
        b = b_new
    return b


def tougaard(y: np.ndarray, e: np.ndarray, B: float = 2866, C: float = 1643,
             D: float = 1.0, E0: float = 0.0) -> np.ndarray:
    """Tougaard background using the universal cross-section.

    ``B(E) ~ integral of B*T / (C + D*T^2)^2`` with ``T = E - E0``, integrated
    over the energy range and anchored at the low-binding-energy end.
    ponytail: simplified universal-cross-section version; the full Tougaard
    integral (to +infinity) can be added if spectra need it.
    """
    y = np.asarray(y, dtype=float)
    e = np.asarray(e, dtype=float)
    T = e - E0
    integrand = (B * T) / (C + D * T**2) ** 2

    bg = np.concatenate([[0.0], np.cumsum(0.5 * np.diff(e) * (integrand[1:] + integrand[:-1]))])
    if bg[-1] <= 0:
        return np.full_like(y, y[0])
    bg = bg / bg[-1] * (y[-1] - y[0]) + y[0]
    return bg


def compute_background(be: np.ndarray, y: np.ndarray,
                       method: str = BACKGROUND_METHOD) -> np.ndarray:
    """Return the background for the chosen method (subtract it from ``y``
    yourself, or use ``shirley``/``tougaard`` directly)."""
    if method.lower() == "shirley":
        return shirley(y)
    if method.lower() == "tougaard":
        return tougaard(y, be)
    raise ValueError(f"unknown background method: {method!r}")
