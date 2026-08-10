import re
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"

ADSORBENT_MAP = {
    "GO-CO": "GO-CS",
    "GO-CS": "GO-CS",
    "GO-MCC50": "GO-MCC50",
    "GO-MCC-50": "GO-MCC50",
    "GO-MCC50µm": "GO-MCC50",
    "GO-MCC90": "GO-MCC90",
    "G-MCC90": "GO-MCC90",
    "GO-MCC90µm": "GO-MCC90",
}

FACTOR_MAP = {
    "ad.dosage": "ad_dosage",
    "analyte": "analyte",
    "pH": "pH",
    "Temp": "Temp",
    "time": "time",
}


def _level_value(raw):
    if isinstance(raw, str):
        raw = re.sub(r"[^\d.+-eE]", "", raw)
        try:
            return float(raw)
        except ValueError:
            return None
    return raw


rows = []
for fpath in sorted(DATA_DIR.glob("*.xlsx")):
    stem = fpath.stem  # e.g. "PE-ad.dosage"
    mat, factor_raw = stem.split("-", 1)
    factor = FACTOR_MAP[factor_raw]

    import openpyxl

    wb = openpyxl.load_workbook(fpath, data_only=True)
    ws = wb.active

    # Find all GO-* section markers in any column
    markers = []
    for r in range(1, ws.max_row + 1):
        for c in range(1, min(ws.max_column + 1, 14)):
            v = ws.cell(r, c).value
            if v and isinstance(v, str):
                vu = v.strip().upper()
                if vu.startswith("GO-") or vu.startswith("G-"):
                    markers.append((r, v.strip()))
                    break

    # Map: section_marker_row -> adsorbent name
    marker_map = {}
    for r, label in markers:
        for k, v in ADSORBENT_MAP.items():
            if k in label.upper().replace(" ", ""):
                marker_map[r] = v
                break

    # Collect data rows: walk through, track current adsorbent from nearest marker
    current_adsorbent = None
    for r in range(1, ws.max_row + 1):
        if r in marker_map:
            current_adsorbent = marker_map[r]

        level_raw = ws.cell(r, 2).value
        pct = ws.cell(r, 7).value

        if current_adsorbent is None or level_raw is None or pct is None:
            continue
        if not isinstance(pct, (int, float)):
            continue
        if pct > 100 or pct < 0:
            continue

        lv_str = str(level_raw).lower().strip()
        if any(k in lv_str for k in ["conc", "ana.", "ad.ds", "adsorbent", "time", "temp", "ph"]):
            continue

        level = _level_value(level_raw)
        if level is None:
            continue

        rows.append(
            {
                "Material": mat,
                "Factor": factor,
                "Level": level,
                "Adsorbent": current_adsorbent,
                "PctAdsorption": pct,
            }
        )

tidy = pd.DataFrame(rows)
# Remove duplicates caused by data appearing in multiple sections
tidy = tidy.drop_duplicates(subset=["Material", "Factor", "Level", "Adsorbent"]).reset_index(drop=True)
tidy = tidy.sort_values(["Material", "Factor", "Level", "Adsorbent"]).reset_index(drop=True)
tidy.to_csv("tidy_data.csv", index=False)
print(f"Extracted {len(tidy)} rows to tidy_data.csv")
print(f"Columns: {list(tidy.columns)}")
print(f"Materials: {sorted(tidy['Material'].unique())}")
print(f"Factors: {sorted(tidy['Factor'].unique())}")
print(f"Adsorbents: {sorted(tidy['Adsorbent'].unique())}")
