"""Peak fitting with lmfit (Gaussian / Lorentzian / Voigt).

Two-stage fitting:

1. *Initialisation* — each peak is fitted quickly and locally to the residual
   (peeling, strongest first). This seeds every component near its data.
2. *Joint refinement* — all peaks are fitted simultaneously with a hard cap on
   iterations, which lets overlapping shoulders share intensity correctly.

The better of the two results (by R²) is kept. Note that lmfit's Voigt
``amplitude`` parameter is the integrated area, not the peak height, so peak
heights are reported from the actual evaluated component curve.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from lmfit.models import GaussianModel, LorentzianModel, VoigtModel

from config import (CENTER_DRIFT_FRACTION, MIN_PEAK_AREA_FRACTION,
                    MIN_PEAK_HEIGHT_FRACTION, MODEL, SIGMA_FWHM_RATIO)

MODEL_CLASSES = {
    "gaussian": GaussianModel,
    "lorentzian": LorentzianModel,
    "voigt": VoigtModel,
}

JOINT_REFINE_NFEV = 800  # iteration budget for the joint refinement


@dataclass
class FitResult:
    """Outcome of one spectrum fit."""

    centers: np.ndarray
    heights: np.ndarray
    fwhms: np.ndarray
    areas: np.ndarray
    area_errors: np.ndarray      # relative error of area, in %
    r2: float
    reduced_chi2: float
    best_fit: np.ndarray         # summed model on the data grid
    components: np.ndarray       # shape (n_peaks, n_points)
    residual: np.ndarray
    converged: bool


def _initial_fwhm(be: np.ndarray, y: np.ndarray, peak_idx: int) -> float:
    """Crude FWHM guess from the half-maximum crossings around a peak."""
    half = 0.5 * (y[peak_idx] - y.min()) + y.min()
    left = peak_idx
    while left > 0 and y[left] > half:
        left -= 1
    right = peak_idx
    while right < len(y) - 1 and y[right] > half:
        right += 1
    fwhm = be[min(right, len(be) - 1)] - be[left]
    return max(fwhm, 0.2) if np.isfinite(fwhm) else 1.0


def _make_model(i: int, center: float, height: float, fwhm: float,
                model: str):
    """Build a parameterised model for peak ``i`` with sane bounds."""
    model_cls = MODEL_CLASSES[model.lower()]
    m = model_cls(prefix=f"p{i}_")
    drift = CENTER_DRIFT_FRACTION * max(fwhm, 0.5)
    m.set_param_hint("center", value=center, min=center - drift, max=center + drift)
    m.set_param_hint("amplitude", value=max(height, 1e-3), min=0.0)
    m.set_param_hint("sigma", value=fwhm / SIGMA_FWHM_RATIO,
                     min=0.05 * fwhm, max=5 * fwhm)
    if hasattr(m, "gamma"):  # Lorentzian / Voigt width
        m.set_param_hint("gamma", value=fwhm / SIGMA_FWHM_RATIO,
                         min=0.01 * fwhm, max=5 * fwhm)
    return m


def _local_fit(be: np.ndarray, r: np.ndarray, center: float, height: float,
               fwhm: float, i: int, model: str):
    """Fit a single peak to the residual in a window around ``center``."""
    window = max(2.0 * fwhm, 1.5)
    mask = (be >= center - window) & (be <= center + window)
    if mask.sum() < 5:
        mask = np.ones_like(be, dtype=bool)
    m = _make_model(i, center, height, fwhm, model)
    result = m.fit(r[mask], x=be[mask])
    return m, result.params


def _peel(be: np.ndarray, y: np.ndarray, peak_idx: np.ndarray,
          model: str) -> list:
    """Fit peaks one at a time (strongest first) to the residual."""
    residual = np.asarray(y, dtype=float)
    fitted: list = []
    for i, j in enumerate(np.argsort(y[peak_idx])[::-1]):
        idx = peak_idx[j]
        center = be[idx]
        fwhm = _initial_fwhm(be, residual, idx)
        window = max(2.0 * fwhm, 1.5)
        mask = (be >= center - window) & (be <= center + window)
        height = residual[mask].max() if mask.any() else residual.max()
        m, params = _local_fit(be, residual, center, max(height, 1e-3), fwhm, i, model)
        residual = residual - m.eval(x=be, params=params)
        fitted.append((m, params))
    return fitted


def _evaluate(fitted: list, be: np.ndarray):
    """Components, total fit, per-peak heights/centres/fwhms from params."""
    components, centers, fwhms = [], [], []
    for m, p in fitted:
        prefix = next(k[: k.index("_") + 1] for k in p if k.endswith("_center"))
        components.append(m.eval(x=be, params=p))
        centers.append(p[prefix + "center"].value)
        fwhms.append(p[prefix + "fwhm"].value)
    components = np.stack(components)
    best_fit = components.sum(axis=0)
    heights = components.max(axis=1)
    return components, best_fit, heights, np.array(centers), np.array(fwhms)


def _stats(y: np.ndarray, best_fit: np.ndarray, n_params: int) -> tuple:
    residual = np.asarray(y) - best_fit
    dof = max(len(y) - n_params, 1)
    reduced_chi2 = float(np.sum(residual**2) / dof)
    ss_tot = float(np.sum((np.asarray(y) - np.asarray(y).mean())**2))
    r2 = 1.0 - float(np.sum(residual**2)) / ss_tot if ss_tot > 0 else 0.0
    return r2, reduced_chi2, residual


def _param_errors(composite, params, be: np.ndarray, y: np.ndarray) -> dict:
    """1-sigma parameter errors from a finite-difference residual covariance.

    lmfit only computes covariance when its solver converges naturally; the
    capped joint fit never does, so this provides consistent error bars for
    every fitted parameter.
    """
    varying = [n for n in params if params[n].vary]
    if not varying:
        return {}

    def residual(values: np.ndarray) -> np.ndarray:
        p = params.copy()
        for name, v in zip(varying, values):
            p[name].value = v
        return np.asarray(y) - composite.eval(x=be, params=p)

    s0 = np.array([params[n].value for n in varying])
    r0 = residual(s0)
    dof = max(len(r0) - len(varying), 1)
    s2 = float(np.sum(r0**2) / dof)

    J = np.zeros((len(r0), len(varying)))
    h = 1e-4 * np.maximum(np.abs(s0), 1e-6)
    for j in range(len(varying)):
        s1 = s0.copy()
        s1[j] += h[j]
        J[:, j] = (residual(s1) - r0) / h[j]

    try:
        cov = s2 * np.linalg.inv(J.T @ J)
        return {name: float(np.sqrt(max(cov[j, j], 0.0)))
                for j, name in enumerate(varying)}
    except np.linalg.LinAlgError:
        return {}


def fit_peaks(be: np.ndarray, y: np.ndarray, peak_idx: np.ndarray,
              model: str = MODEL) -> FitResult:
    """Fit one peak model per detected peak. ``y`` must be background-free."""
    if model.lower() not in MODEL_CLASSES:
        raise ValueError(f"unknown model: {model!r}; use one of {list(MODEL_CLASSES)}")
    n_peaks = len(peak_idx)
    if n_peaks == 0:
        return FitResult(
            centers=np.array([]), heights=np.array([]), fwhms=np.array([]),
            areas=np.array([]), area_errors=np.array([]),
            r2=0.0, reduced_chi2=np.nan, best_fit=y, components=y[None, :],
            residual=np.zeros_like(y), converged=False,
        )

    peeled = _peel(be, y, peak_idx, model)
    comps_p, fit_p, heights_p, centers_p, fwhms_p = _evaluate(peeled, be)
    r2_p, chi2_p, _ = _stats(y, fit_p, 3 * n_peaks)

    # Joint refinement with a bounded iteration budget.
    composite = peeled[0][0]
    for m, _ in peeled[1:]:
        composite = composite + m
    joint = composite.fit(np.asarray(y), x=be, max_nfev=JOINT_REFINE_NFEV)

    comps_j, fit_j, heights_j, centers_j, fwhms_j = _evaluate(peeled, be)
    r2_j, chi2_j, resid_j = _stats(y, fit_j, joint.nvarys)

    if r2_j >= r2_p:
        components, best_fit = comps_j, fit_j
        heights, centers, fwhms = heights_j, centers_j, fwhms_j
        r2, reduced_chi2, residual = r2_j, chi2_j, resid_j
        params = joint.params
        converged = bool(joint.success)
    else:
        components, best_fit = comps_p, fit_p
        heights, centers, fwhms = heights_p, centers_p, fwhms_p
        r2, reduced_chi2, residual = r2_p, chi2_p, np.asarray(y) - fit_p
        params = peeled[0][1]
        for _, p in peeled[1:]:
            params.update(p)
        converged = True

    areas = np.array([np.trapezoid(components[i], be) for i in range(n_peaks)])

    # Drop ghost peaks with negligible area/height relative to the spectrum.
    keep = np.where(
        (areas >= MIN_PEAK_AREA_FRACTION * areas.sum())
        & (heights >= MIN_PEAK_HEIGHT_FRACTION * heights.max())
    )[0]
    if len(keep) < n_peaks:
        peeled = [(m, p) for i, (m, p) in enumerate(peeled) if i in set(keep)]
        n_peaks = len(peeled)
        components, best_fit, heights, centers, fwhms = _evaluate(peeled, be)
        areas = np.array([np.trapezoid(components[i], be) for i in range(n_peaks)])
        r2, reduced_chi2, residual = _stats(y, best_fit, 3 * n_peaks)

    # Consistent 1-sigma errors from the residual covariance.
    composite = peeled[0][0]
    for m, _ in peeled[1:]:
        composite = composite + m
    params = peeled[0][1]
    for _, p in peeled[1:]:
        params.update(p)
    errors = _param_errors(composite, params, be, y)
    prefixes = [next(k[: k.index("_") + 1] for k in p if k.endswith("_center"))
                for _, p in peeled]
    amp_errs = np.array([errors.get(f"{prefix}amplitude", np.nan)
                         for prefix in prefixes])
    area_errors = np.abs(amp_errs / np.maximum(areas, 1e-12)) * 100.0

    return FitResult(
        centers=centers, heights=heights, fwhms=fwhms, areas=areas,
        area_errors=area_errors, r2=r2, reduced_chi2=reduced_chi2,
        best_fit=best_fit, components=components, residual=residual,
        converged=converged,
    )
