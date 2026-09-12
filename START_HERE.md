# 🔬 ANOVA Analysis System - START HERE

Welcome! This is the ANOVA analysis system for XPS spectroscopy and statistical analysis.

---

## Choose Your Interface

### 👥 For Most Users: Use the Web Interface

**The easiest way to analyze your data - no technical knowledge needed!**

#### Quick Start (30 seconds)

**Windows:**
1. Double-click `start_web.bat`
2. Browser opens automatically
3. Drag and drop your Excel file
4. Click "Analyze"
5. Download results

**Mac/Linux:**
1. Open Terminal
2. Type: `bash start_web.sh`
3. Browser opens automatically
4. Drag and drop your Excel file
5. Click "Analyze"
6. Download results

#### For Detailed Instructions:
👉 Read **[WEB_SETUP_GUIDE.md](WEB_SETUP_GUIDE.md)**

This guide includes:
- Step-by-step installation
- Input file format specifications
- Output file descriptions
- 20+ troubleshooting solutions
- Tips for best results

---

### 💻 For Advanced Users: Use the Command Line

If you prefer working with Python and the terminal:

```bash
# XPS Analysis Only
python main.py

# Full ANOVA Pipeline
bash start.sh anova
```

See original [README.md](README.md) for command-line documentation.

---

## What Can You Analyze?

### 🔬 XPS Spectroscopy Analysis
Automatically fit and analyze X-ray photoelectron spectroscopy spectra:
- Peak detection and identification
- Curve fitting (Voigt/Gaussian/Lorentzian models)
- Publication-quality figures
- CSV reports with peak data

**Input**: Single Excel file with spectral data
**Output**: Figures + CSV reports + summary tables

### 📊 ANOVA Statistical Analysis
Two-way statistical analysis of adsorption experiments:
- Descriptive statistics
- ANOVA results with effect sizes
- Tukey HSD comparisons
- Assumption validation
- Confidence intervals
- Diagnostic plots

**Input**: Excel files with experiment data
**Output**: Statistical tables + diagnostic figures

---

## System Requirements

### Minimum
- **OS**: Windows 7+, macOS 10.13+, or Linux
- **RAM**: 4 GB
- **Disk**: 1 GB free space
- **Python**: 3.11+ (auto-installed for web interface)

### Recommended
- **OS**: Windows 10+, macOS 12+, or modern Linux
- **RAM**: 8 GB
- **Disk**: 2 GB free space
- **Internet**: For initial Python installation only

---

## Getting Started

### First Time Setup (Web Interface)

**Step 1: Prepare Your Data**
- Save your data as Excel file (.xlsx or .xls)
- Make sure columns are labeled clearly
- See [WEB_SETUP_GUIDE.md](WEB_SETUP_GUIDE.md) for exact format

**Step 2: Start the Web Server**
- Windows: Double-click `start_web.bat`
- Mac/Linux: Run `bash start_web.sh` in Terminal

**Step 3: Use the Web Interface**
- Browser opens to http://127.0.0.1:5000
- Upload your file
- Click "Analyze"
- Download results when done

### Subsequent Analyses

Just repeat Step 2 and 3. The first run installs dependencies (~2 minutes). Later runs start in <10 seconds.

---

## Input File Specifications

### For XPS Analysis

**Single Excel file** with these columns:

| Column Name | Typical Values | Units |
|-------------|---|---|
| Binding Energy | 0-1200 | eV |
| Intensity | Numbers | CPS or Counts |

Multiple worksheets supported (e.g., "C 1s", "N 1s", "O 1s")

### For ANOVA Analysis

**Multiple Excel files** with these columns:

| Column Name | Values | Notes |
|-------------|--------|-------|
| Material | PE, PET, PS | Polymer type |
| Factor | pH, Temp, time, etc. | Experimental factor |
| Level | 1, 2, 3... | Experiment number |
| Adsorbent | GO-CS, GO-MCC50, GO-MCC90 | Adsorbent type |
| PctAdsorption | 0-100 | Percentage |

---

## Output Files Explained

### 📁 Results Folder Structure

```
ANOVA_Results_2026-09-12/
├── XPS Results (if XPS analysis)
│   ├── [Sample Name]/
│   │   ├── [Region]/
│   │   │   ├── spectrum_raw.png
│   │   │   ├── spectrum_background.png
│   │   │   ├── spectrum_detected.png
│   │   │   ├── spectrum_fitted.png
│   │   │   ├── spectrum_residual.png
│   │   │   ├── report.csv
│   │   │   └── report.xlsx
│   └── summary/
│       ├── all_peak_areas.csv
│       ├── all_peak_positions.csv
│       └── summary.xlsx
│
└── ANOVA Results (if ANOVA analysis)
    ├── table_anova.csv
    ├── table_tukey.csv
    ├── table_assumptions.csv
    ├── figure_boxplot_*. png
    ├── figure_interaction_*.png
    └── ...
```

### 📊 Understanding Your Results

**For XPS:**
- Look at figures to see peak fits visually
- Check CSV for numerical values
- R² > 0.95 indicates good fit

**For ANOVA:**
- Check `table_anova.csv` for p-values
- p-value < 0.05 means statistically significant
- Check diagnostic figures to validate assumptions
- Read `table_assumptions.csv` for details

See [WEB_SETUP_GUIDE.md](WEB_SETUP_GUIDE.md) for complete output descriptions.

---

## Common Issues & Solutions

### Python Not Found
- Windows: Install Python from python.org (check "Add to PATH")
- Mac: Install Python from python.org
- Linux: Run `sudo apt-get install python3.11`

### Port 5000 Already in Use
- Change port in `web/run.py` line ~40 to 5001, 5002, etc.
- Or close the other program using port 5000

### Analysis Takes Very Long
- Large files (>100 MB) naturally take time
- XPS: ~2-5 minutes per 100 peaks
- ANOVA: ~1-3 minutes per 15 datasets
- This is normal!

### More Issues?
👉 See **[WEB_SETUP_GUIDE.md](WEB_SETUP_GUIDE.md)** → Troubleshooting section

---

## Documentation

| Document | For | Read If |
|----------|-----|---------|
| **WEB_SETUP_GUIDE.md** | End Users | You want to analyze data |
| **README.md** | Developers | You want command-line docs |
| **WEB_BUILD_SUMMARY.md** | Technical | You want architecture details |
| **web/README.md** | Developers | You want web API docs |

---

## Keyboard Shortcuts

### Browser
- `Ctrl+O` (Windows) or `Cmd+O` (Mac): Open file dialog
- `Ctrl+L`: Go to address bar
- `F5`: Refresh page

### Web Interface
- Tab: Move between fields
- Enter: Submit (when Analyze button is focused)
- Click: Standard interactions

---

## Tips for Success

1. **Start Simple**: Test with a small file first
2. **Check Format**: Follow the input specifications exactly
3. **Save as .xlsx**: Excel format, not .xls
4. **No Empty Rows**: Remove any blank rows from data
5. **Clear Headers**: Use descriptive column names
6. **Keep Server Running**: Don't close the command window
7. **Review Outputs**: Look at both figures and CSV files
8. **Note Error Messages**: They often tell you what's wrong

---

## For Different User Groups

### 🎓 Student/Researcher
1. Read "Getting Started" section above
2. Follow [WEB_SETUP_GUIDE.md](WEB_SETUP_GUIDE.md)
3. Use web interface for analysis
4. Download and analyze results

### 👨‍🔬 Scientist/Lab Manager
1. Install Python 3.11+ first
2. Run `bash start_web.sh` or `start_web.bat`
3. Share the resulting analysis with team
4. Use results in papers/presentations

### 👨‍💻 Developer/Administrator
1. Read [WEB_BUILD_SUMMARY.md](WEB_BUILD_SUMMARY.md)
2. Review code in `web/` directory
3. Modify as needed for your setup
4. Deploy on lab server if desired

### 🔧 System Administrator
1. Read "Deployment Options" in [WEB_BUILD_SUMMARY.md](WEB_BUILD_SUMMARY.md)
2. Consider Docker containerization
3. Set up on shared server
4. Configure SSL/TLS for security

---

## FAQ

**Q: Is my data safe?**
A: Yes! Data stays on your computer. Nothing is sent over the internet.

**Q: Can I analyze multiple files?**
A: Yes, one at a time. Upload, analyze, download, then upload next file.

**Q: How long does analysis take?**
A: XPS: 2-5 min. ANOVA: 1-3 min. Large files take longer.

**Q: What formats are supported?**
A: Only Excel (.xlsx and .xls files) supported.

**Q: Can I modify the interface?**
A: Yes! All code is open. Edit `web/templates/index.html` for design changes.

**Q: Can I run this on a server?**
A: Yes, with proper security setup. See [WEB_BUILD_SUMMARY.md](WEB_BUILD_SUMMARY.md).

**Q: Do I need internet?**
A: Only for initial installation. After that, runs locally offline.

**Q: What if analysis fails?**
A: Check error message, verify input file format, try again. See Troubleshooting in [WEB_SETUP_GUIDE.md](WEB_BUILD_SUMMARY.md).

---

## Getting Help

### If Something Doesn't Work
1. Read the error message carefully
2. Check [WEB_SETUP_GUIDE.md](WEB_SETUP_GUIDE.md) Troubleshooting section
3. Review your input file format
4. Try with a smaller file
5. Check server window for error details
6. Contact development team if still stuck

### To Report a Bug
- Note the exact error message
- Describe what you were doing
- Include your input file (if possible)
- Contact development team

### To Request a Feature
- Describe what you want to do
- Explain why it would be useful
- Contact development team

---

## Quick Reference

```bash
# Start web interface (Mac/Linux)
bash start_web.sh

# Start web interface (Windows)
start_web.bat

# Command line XPS analysis only
python main.py

# Full command line pipeline
bash start.sh anova

# Stop web server
Ctrl+C (in the command window)
```

---

## What's Next?

1. **Right Now**: Read this page to the end
2. **Next Step**: Follow [WEB_SETUP_GUIDE.md](WEB_SETUP_GUIDE.md)
3. **First Run**: Test with sample data
4. **Regular Use**: Upload your data and analyze
5. **Problems**: Check troubleshooting section
6. **Questions**: Review relevant documentation

---

## Version Info

- **System**: ANOVA 2.0 (Web + CLI)
- **Web Version**: 1.0
- **Release Date**: September 12, 2026
- **Python**: 3.11+
- **Status**: Production Ready

---

## License & Attribution

This system builds on:
- Original ANOVA pipeline (XPS + statistical analysis)
- Flask web framework (Python)
- Scientific computing stack (numpy, scipy, statsmodels, etc.)

See original README.md for full attribution.

---

## Quick Links

- 📖 **Full User Guide**: [WEB_SETUP_GUIDE.md](WEB_SETUP_GUIDE.md)
- 🏗️ **Technical Details**: [WEB_BUILD_SUMMARY.md](WEB_BUILD_SUMMARY.md)
- 📝 **Original Docs**: [README.md](README.md)
- 🌐 **Web API**: [web/README.md](web/README.md)

---

**Ready to get started?** 👇

<details>
<summary>Click here for Windows users</summary>

1. Right-click `start_web.bat`
2. Click "Run"
3. Wait for browser
4. Drag file to upload box
5. Click "Analyze"
6. Download results
</details>

<details>
<summary>Click here for Mac/Linux users</summary>

1. Open Terminal
2. `cd /path/to/ANOVA`
3. `bash start_web.sh`
4. Wait for browser
5. Drag file to upload box
6. Click "Analyze"
7. Download results
</details>

---

**Questions?** Check [WEB_SETUP_GUIDE.md](WEB_SETUP_GUIDE.md)

**Happy analyzing!** 🔬📊
