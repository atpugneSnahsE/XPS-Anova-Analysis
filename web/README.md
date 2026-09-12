# ANOVA Web Interface

A user-friendly web interface for running XPS and ANOVA analysis without requiring technical knowledge.

## Quick Start

### Option 1: Run from project root
```bash
bash start_web.sh
```

This will:
1. Set up Python virtual environment
2. Install dependencies
3. Start the web server
4. Automatically open your browser to http://127.0.0.1:5000

### Option 2: Manual setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (first time only)
pip install -r web/requirements.txt

# Run the server
python web/run.py
```

## Usage

1. **Open the web interface** - Your browser opens automatically at http://127.0.0.1:5000
2. **Upload your Excel file** - Drag and drop or click to browse
3. **Choose analysis type**:
   - **Auto-detect** - System automatically detects XPS or ANOVA
   - **XPS Analysis** - For spectral peak fitting
   - **ANOVA Analysis** - For statistical adsorption experiments
4. **Click "Analyze"** - Processing begins (may take a minute for large files)
5. **Download results** - ZIP file with all outputs (CSV, figures, reports)

## Supported File Formats

- **XPS Data**: Single Excel file (.xlsx or .xls) with spectral data
  - Expected columns: Binding Energy (B.E., BE), Intensity (CPS, Counts, Intensity)
  - Multiple worksheets supported (different spectral regions)

- **ANOVA Data**: Excel files (.xlsx or .xls) with adsorption experiment data
  - Format: `{PE,PET,PS}-{pH,Temp,time,analyte,ad.dosage}.xlsx`
  - Expected columns: Material, Factor, Level, Adsorbent, Value/PctAdsorption

## Output Files

Your results include:

### XPS Analysis
- **Figures** (per spectrum):
  - Raw spectrum
  - Background subtraction
  - Detected peaks
  - Fitted peaks
  - Residuals
- **CSV Reports** (peak centers, areas, heights, FWHM)
- **Summary tables** (all peaks across all samples)

### ANOVA Analysis
- **Statistical tables**:
  - ANOVA results
  - Tukey HSD comparisons
  - Assumption tests (Shapiro-Wilk, Levene)
  - Effect sizes (η², ω², Cohen's f)
  - Confidence intervals
- **Diagnostic figures**:
  - Boxplots
  - Interaction plots
  - Residual plots
  - Heatmaps

## Troubleshooting

**Port 5000 already in use?**
- Edit `web/run.py` and change `port=5000` to a different number

**Dependencies not installing?**
- Make sure you're using Python 3.11+
- Try: `pip install --upgrade --force-reinstall -r web/requirements.txt`

**Analysis takes too long?**
- Large files may take several minutes
- Keep browser window open during processing

**Browser doesn't open automatically?**
- Manually open: http://127.0.0.1:5000

## For Developers

The web interface consists of:

- **`app.py`** - Flask backend API
- **`web_api.py`** - Wrappers for XPS and ANOVA pipelines
- **`templates/index.html`** - Frontend UI (HTML/CSS/JavaScript)
- **`run.py`** - Server startup script
- **`requirements.txt`** - Python dependencies

To modify the interface:
1. Edit HTML in `templates/index.html`
2. Modify API endpoints in `app.py`
3. Update pipeline integration in `web_api.py`
4. Restart the server

## License

Same as main ANOVA project
