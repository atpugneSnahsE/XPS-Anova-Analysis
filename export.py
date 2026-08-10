"""CSV / Excel export of per-spectrum reports and the global summary."""

from __future__ import annotations

import pandas as pd

from fitting import FitResult


def _report_frame(sheet_name: str, fit: FitResult) -> pd.DataFrame:
    """Per-spectrum table: one row per fitted peak."""
    if len(fit.centers) == 0:
        return pd.DataFrame(columns=[
            "Filename", "Sheet", "Peak", "Binding Energy (eV)",
            "Height", "FWHM (eV)", "Area", "Fit Error (%)",
        ])
    return pd.DataFrame({
        "Filename": sheet_name,
        "Sheet": sheet_name,
        "Peak": [f"Peak {i + 1}" for i in range(len(fit.centers))],
        "Binding Energy (eV)": fit.centers,
        "Height": fit.heights,
        "FWHM (eV)": fit.fwhms,
        "Area": fit.areas,
        "Fit Error (%)": fit.area_errors,
    })


def write_report(sample_stem: str, sheet_name: str, fit: FitResult, out_dir) -> None:
    """Write ``report.csv`` and ``report.xlsx`` for one spectrum."""
    df = _report_frame(sheet_name, fit)
    df["Filename"] = f"{sample_stem}.xlsx"
    df.to_csv(out_dir / "report.csv", index=False)
    df.to_excel(out_dir / "report.xlsx", index=False)


def write_summary(summary_rows: list[dict], summary_dir) -> None:
    """Write ``all_peak_areas.csv``, ``all_peak_positions.csv`` and
    ``summary.xlsx`` across every analysed spectrum."""
    if not summary_rows:
        return

    df = pd.DataFrame(summary_rows)
    summary_dir.mkdir(parents=True, exist_ok=True)

    columns = ["Filename", "Sheet", "Peak Number", "Center", "Area", "Height", "FWHM", "R²", "Chi²"]
    df = df[columns]

    df.to_csv(summary_dir / "all_peak_areas.csv", index=False)
    df[["Filename", "Sheet", "Peak Number", "Center", "FWHM", "R²", "Chi²"]].to_csv(
        summary_dir / "all_peak_positions.csv", index=False)
    df.to_excel(summary_dir / "summary.xlsx", index=False, sheet_name="Summary")
