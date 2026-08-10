# 🧪 XPS & ANOVA Analysis Pipeline

**From raw instrument files to publication-ready results — automatically.**

This project bundles two fully automated scientific analysis pipelines in one
place. You drop in your raw data, run **one command**, and get back fitted
spectra, statistical tests, and thesis-quality figures and tables. No manual
peak-picking, no hand-typed statistics.

| Pipeline | What it does | Input | Output |
|---|---|---|---|
| **XPS Peak Analysis** | Detects, fits and quantifies X-ray photoelectron spectroscopy peaks in every spectrum | Excel files in `FW_ xps/` | Fitted figures + per-spectrum and global reports |
| **ANOVA Statistics** | Two-way ANOVA, Tukey tests, effect sizes, assumptions and multiple-testing corrections for adsorption experiments | Excel sheets in `data/` | Dozens of `*.csv` tables, ranking tables and diagnostic figures |

---

## 🚀 Quick start (non-technical)

You only need two things:

1. **Python 3.11 or newer** — if you don't have it, download it free from
   <https://www.python.org/downloads/> and install it (leave every box
   ticked on the first screen).
2. **This project folder.**

Then open a terminal in this folder and run:

```bash
bash start.sh
```

That's it. The script does everything for you:

- creates a private Python environment (` .venv/`) so it never touches your
  system,
- installs all required packages,
- runs the full XPS analysis on your spectra.

To also run the ANOVA statistics pipeline:

```bash
bash start.sh anova
```

When it finishes you'll see a `Processing 1/12`, `Processing 2/12` … progress
counter and your results will be waiting in the folders described below.

> **Tip:** if the script says "Python 3.11 or newer is required", you're on an
> older Python. Download the latest from <https://www.python.org/downloads/>
> and re-run the same command.

---

## 📥 What you need to provide

Keep your data files in the right folder and the pipelines find them by
themselves.

```
ANOVA/
├── FW_ xps/          ← (XPS) drop your Avantage-style .xlsx spectrum exports here
│   ├── SampleA.xlsx        one workbook per sample;
│   └── SampleB.xlsx        every worksheet in a workbook = one region/spectrum
├── data/             ← (ANOVA) drop your adsorption experiment sheets here
│   ├── PE-pH.xlsx          name = <Material>-<Factor>.xlsx
│   ├── PE-Temp.xlsx        Material: PE, PET or PS
│   └── PS-ad.dosage.xlsx   Factor:  pH, Temp, time, analyte, ad.dosage
└── start.sh          ← just run this
```

No configuration files to edit, no options to pass. Put files in, run the
command, collect results.

---

## 📦 What you get back

### XPS pipeline (`results/` and `summary/`)

For **every** spectrum a folder is created with five 300-dpi figures and two
data files:

```
results/SampleA/C 1s/
├── raw_spectrum.png    # the imported data
├── background.png      # data + background + background-subtracted
├── detected_peaks.png  # where the peaks were found
├── fitted.png          # data, total fit and each individual peak
├── residual.png        # what's left after the fit
├── report.csv          # Peak / Binding Energy / Height / FWHM / Area / Fit Error
└── report.xlsx         # same, in Excel
```

Plus global summaries across all samples in `summary/`:

- `all_peak_areas.csv` — every fitted peak, every sample
- `all_peak_positions.csv` — centres, widths and quality metrics
- `summary.xlsx` — combined table with R² and χ² per fit

### ANOVA pipeline (tables in the project root, figures in `figures/`)

| File | Content |
|---|---|
| `table_anova.csv` | F, p, effect sizes (η², ω², Cohen's f) for every factor × material × source |
| `table_tukey.csv` | which adsorbents differ from which, pairwise |
| `table_assumptions.csv` | Shapiro-Wilk + Levene normality/homoscedasticity checks |
| `table_confidence_intervals.csv` | 95% CI per adsorbent |
| `table_ranking_factors_by_effectsize.csv` | what matters most, ranked |
| `table_adsorbent_overall_ranking.csv` / `table_material_overall_ranking.csv` | best performers |
| `table_multiple_testing_correction.csv` | Holm / Benjamini-Hochberg corrections |
| `figures/boxplot_*.png`, `figures/interaction_*.png`, `figures/diagnostics_*.png`, `figures/heatmap_mean_adsorption.png` | visual summaries |

The scripts also print a plain-language summary to the terminal: the most
influential factors per material, the most robust adsorbent, significant
comparisons, limitations, and even simulated reviewer comments — useful
when preparing a thesis or paper.

---

## 🛠️ How it works

### XPS pipeline

1. **Read** (`reader.py`) — every worksheet is scanned for the binding-energy
   (`B.E.`) and intensity (`CPS`) columns; metadata rows above the data are
   ignored automatically.
2. **Background** (`background.py`) — an iterative **Shirley** background
   (or **Tougaard**) is subtracted so only the chemistry remains.
3. **Detect** (`peaks.py`) — `scipy.signal.find_peaks` locates candidate peaks
   on the smoothed spectrum; the instrument's own reported peak positions are
   merged in to catch narrow shoulders.
4. **Fit** (`fitting.py`) — each peak is modelled with **Voigt / Gaussian /
   Lorentzian** curves using `lmfit`, seeded one-by-one and refined together,
   so overlapping peaks share intensity correctly. Ghost peaks (negligible
   area) are pruned automatically.
5. **Plot & export** (`plotting.py`, `export.py`) — five figures per spectrum,
   plus CSV/Excel reports and the global summary.

### ANOVA pipeline

1. **Extract** (`data_extractor.py`) — converts your raw Excel sheets into one
   tidy table `tidy_data.csv`.
2. **Two-way ANOVA** (`two_way_anova2.py`) — additive model
   `Level + Adsorbent` (two-factor design without replication, matching
   Excel's "Anova: Two-Factor Without Replication").
3. **Full analysis** (`analysis_pipeline.py`) — effect sizes, Tukey HSD
   post-hoc, confidence intervals, normality/assumption checks, multiple-testing
   corrections, robustness (CV), and every output table.
4. **Validate** (`validation_pipeline.py`) — re-derives every result from
   scratch and reports which checks passed, with an honest limitations list
   (this design cannot estimate interactions — the tooling keeps you honest).

---

## ⚙️ Configuration

All tunable parameters for the XPS pipeline live in one file: `config.py`.
Commonly adjusted settings:

| Setting | What it does |
|---|---|
| `INPUT_DIRS` | which folders to scan for `.xlsx` spectra |
| `DETECT.prominence_pct` / `height_pct` / `distance` | peak-detection sensitivity (scale-free percentages) |
| `DETECT.max_peaks` | cap on peaks fitted per spectrum |
| `BACKGROUND_METHOD` | `"shirley"` or `"tougaard"` |
| `MODEL` | `"voigt"`, `"gaussian"` or `"lorentzian"` |
| `MIN_PEAK_AREA_FRACTION` / `MIN_PEAK_HEIGHT_FRACTION` | ghost-peak pruning (0 keeps everything) |
| `PLOT.dpi` / `font_size` | figure quality |

For very noisy regions, raise `DETECT.prominence_pct` to ~4–5 and/or increase
`SMOOTH.window`; the per-peak `Fit Error (%)` and `R²` columns flag weak fits.

---

## 📁 Project structure

| File | Purpose |
|---|---|
| `start.sh` | one-command install + run |
| `requirements.txt` | pinned Python dependencies |
| `main.py` | XPS batch loop, progress, error handling |
| `reader.py` | Excel import and column detection |
| `background.py` | Shirley / Tougaard background |
| `peaks.py` | peak detection + instrument-position merging |
| `fitting.py` | Voigt/Gaussian/Lorentzian fitting with `lmfit` |
| `plotting.py` | publication-quality figures |
| `export.py` | CSV / Excel reports and summaries |
| `utils.py` | logging, progress, header-detection helpers |
| `config.py` | all tunable parameters |
| `data_extractor.py` | raw experiment sheets → `tidy_data.csv` |
| `two_way_anova2.py` | two-way ANOVA (no replication) |
| `analysis_pipeline.py` | full statistical analysis + tables + figures |
| `validation_pipeline.py` | independent re-derivation & quality gate |

---

## ❓ FAQ / Troubleshooting

**"No Excel files found"** — make sure your `.xlsx` files are inside `FW_ xps/`
(XPS) or `data/` (ANOVA).

**A file is skipped** — corrupted or unreadable workbooks are logged and
skipped; the rest still processes. Full log: `xps_pipeline.log`.

**Figures look wrong / too many small peaks** — raise `DETECT.prominence_pct`
in `config.py`, then re-run the same command.

**"command not found: bash"** — you're on Windows. Run PowerShell as
administrator and use:
```powershell
py -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; python main.py
```

---

## 🧰 Requirements

- Python 3.11+ (installer: <https://www.python.org/downloads/>)
- Dependencies are listed in `requirements.txt` and installed automatically
  by `start.sh`:
  `numpy`, `pandas`, `scipy`, `matplotlib`, `openpyxl`, `lmfit`,
  `statsmodels`, `seaborn`.
