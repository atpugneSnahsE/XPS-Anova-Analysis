# ANOVA Web Interface - Setup & Usage Guide

Welcome! This guide will help you get the ANOVA Web Interface running on your computer.

## What is the ANOVA Web Interface?

The ANOVA Web Interface allows you to analyze scientific data with just a few clicks. Simply:
1. Select your Excel file
2. Click "Analyze"
3. Download your results

No technical knowledge required!

---

## Installation & Setup

### Step 1: Install Python (if you don't have it)

The ANOVA system requires Python 3.11 or later.

**On Windows:**
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or later
3. Run the installer
4. **IMPORTANT**: Check the box "Add Python to PATH" during installation
5. Click "Install Now"

**On Mac:**
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or later for macOS
3. Run the installer
4. Follow the prompts

**On Linux:**
```bash
sudo apt-get install python3.11 python3.11-venv
```

### Step 2: Start the Web Server

**On Windows:**
1. Navigate to the ANOVA folder
2. Double-click `start_web.bat`
3. A command window will open and install dependencies (first time only, may take 2-3 minutes)
4. Once you see "Starting ANOVA Web Server", your browser should open automatically

**On Mac/Linux:**
1. Open Terminal
2. Navigate to the ANOVA folder: `cd /path/to/ANOVA`
3. Run: `bash start_web.sh`
4. You'll see "Starting ANOVA Web Server" and your browser should open automatically

### Step 3: Browser Opens Automatically

You should see a purple website with an upload area. If the browser doesn't open:
- Manually open: http://127.0.0.1:5000
- Or http://localhost:5000

---

## Using the Web Interface

### Uploading Your Data

**Option 1: Drag and Drop**
- Drag your Excel file onto the purple upload area
- The file name appears below

**Option 2: Click to Browse**
- Click the purple area
- Choose your file from the file browser

### Selecting Analysis Type

After uploading, choose what kind of analysis you want:

- **Auto-detect** (Recommended)
  - The system automatically figures out if it's XPS or ANOVA data

- **XPS Analysis**
  - For X-ray photoelectron spectroscopy spectral data
  - Single Excel file with spectral measurements

- **ANOVA Analysis**
  - For adsorption experiments across different materials
  - Multiple Excel files (automatic)

### Running Analysis

1. Click the blue **"Analyze"** button
2. A progress message appears: "Processing your analysis... This may take a minute"
3. Don't close the browser or turn off the computer
4. When done, you'll see "✅ Analysis Complete!"

### Downloading Results

Once analysis is complete:
1. Click **📥 Download Results (ZIP)**
2. A ZIP file downloads with all your results
3. Extract it to view:
   - CSV tables with data
   - PNG images and charts
   - Summary reports

---

## Understanding Your Results

### XPS Analysis Results

You'll receive a folder with:

- **Figures** (images for each sample):
  - Raw spectrum
  - Background removed
  - Detected peaks
  - Fitted peaks
  - Residuals (differences)

- **Reports** (CSV files with numbers):
  - Peak positions (binding energies)
  - Peak areas
  - Peak heights
  - FWHM (width of peaks)
  - Quality measures (R², Chi²)

- **Summary** (overview file):
  - All peaks from all samples
  - Easy to import into Excel

### ANOVA Analysis Results

You'll receive:

- **Statistical Tables** (CSV files):
  - ANOVA results (which factors are significant)
  - Effect sizes (how large the differences are)
  - Tukey comparisons (which pairs are different)
  - Confidence intervals (range of values)
  - Assumption checks (is the analysis valid?)

- **Diagnostic Figures** (images):
  - Boxplots (comparing groups)
  - Interaction plots (how factors work together)
  - Residual plots (checking if analysis is valid)
  - Heatmaps (showing patterns)

---

## Input File Formats

### For XPS Analysis

**Single Excel file** with spectral data:

```
Column 1: Binding Energy (B.E., BE, or similar)
Column 2: Intensity (CPS, Counts, Intensity, or similar)

Row 1: Headers
Row 2+: Data values

Multiple worksheets supported (different spectral regions)
```

Example:
| B.E. | CPS   |
|------|-------|
| 0    | 100   |
| 1    | 150   |
| 2    | 200   |
| ...  | ...   |

### For ANOVA Analysis

**Excel files** with adsorption experiment data:

```
File names: PE-pH.xlsx, PE-Temp.xlsx, etc.
(Materials: PE, PET, PS)
(Factors: pH, Temperature, Time, Concentration, Dosage)

Columns needed:
- Material (PE, PET, or PS)
- Factor (pH, Temp, time, analyte, or ad_dosage)
- Level (experiment number or value)
- Adsorbent (GO-CS, GO-MCC50, or GO-MCC90)
- Value or PctAdsorption (the measurement)

One row per data point
```

Example:
| Material | Factor | Level | Adsorbent | PctAdsorption |
|----------|--------|-------|-----------|---------------|
| PE       | pH     | 1     | GO-CS     | 45.5          |
| PE       | pH     | 2     | GO-CS     | 52.3          |
| ...      | ...    | ...   | ...       | ...           |

---

## Troubleshooting

### "Python not found" error

**Windows:**
- You need to install Python first (see Installation Step 1)
- Make sure you checked "Add Python to PATH" during installation

**Mac/Linux:**
- Type: `python3 --version` to check if Python is installed
- If not found, install Python 3.11+ from python.org

### Server won't start / "Port already in use" error

Another program is using port 5000:

**Windows:**
1. Close the command window
2. Open another command window
3. Type: `netstat -ano | findstr :5000`
4. Note the PID number
5. Type: `taskkill /PID [number] /F`
6. Try `start_web.bat` again

**Mac/Linux:**
1. Open Terminal
2. Type: `lsof -i :5000`
3. Type: `kill -9 [PID]`
4. Try `start_web.sh` again

Or change the port in `web/run.py` (line: `port=5000`) to a different number like 5001.

### Browser doesn't open automatically

1. Check if you're running the correct script:
   - Windows: `start_web.bat`
   - Mac/Linux: `bash start_web.sh`

2. Wait a few seconds after the command window opens
3. Manually open: http://127.0.0.1:5000 in your browser

### Analysis takes a very long time

Large files can take several minutes to process. This is normal!
- Don't close the browser or command window
- Don't turn off the computer
- Keep the browser focused on the web page
- Very large files (>100MB) may take 10+ minutes

### "Error: Only Excel files allowed"

Make sure your file is:
- In Excel format (.xlsx or .xls)
- Not corrupted
- Less than 500MB

Try opening the file in Excel to verify it's not damaged.

### Results ZIP file is empty

This can happen if the analysis partially failed:
1. Download again
2. Check the server window for error messages
3. Try with a smaller file first

---

## Tips for Best Results

1. **Format your Excel correctly**
   - Use clear column headers
   - No empty rows in the middle
   - Save as .xlsx (not .xls)

2. **One file per upload**
   - Upload one XPS sample at a time
   - Or upload one ANOVA dataset

3. **Check results carefully**
   - Review CSV tables first
   - Look at diagnostic plots
   - Check if R² values are > 0.95 for good fits

4. **Keep the web server running**
   - Don't close the command window
   - Server can process multiple files
   - Close when you're done with Ctrl+C

---

## Getting Help

If you encounter issues:

1. **Read the error message** carefully - it often tells you what's wrong
2. **Check this guide** - most common issues are listed above
3. **Review your input file** - is it in the right format?
4. **Try with a small test file** - to see if the system works at all
5. **Check the command window** - error details appear there

---

## Advanced: Running Multiple Analyses

The web server stays running after each analysis:

1. Start the server with `start_web.sh` or `start_web.bat`
2. Analyze first file → Download results
3. Click "Reset"
4. Upload second file → Analyze → Download
5. Repeat as many times as you want
6. When done, close the command window (Ctrl+C)

---

## Windows Batch Details

The `start_web.bat` script:
1. Checks if Python is installed
2. Creates a virtual environment (isolated Python setup)
3. Installs required packages
4. Starts the web server
5. Automatically opens your browser

If it asks "Do you want to continue?" → Type Y and press Enter

---

## Mac/Linux Bash Details

The `start_web.sh` script:
1. Checks if Python 3 is available
2. Creates a virtual environment
3. Installs required packages
4. Starts the web server
5. Automatically opens your browser

To stop: Press Ctrl+C in the Terminal

---

## For System Administrators

To deploy on a shared server:

```bash
# Clone/copy the ANOVA folder
cd /path/to/ANOVA

# Set up
source .venv/bin/activate
pip install -r web/requirements.txt

# Run with specific host/port
python web/run.py --host 0.0.0.0 --port 8000

# Access from: http://server-ip:8000
```

---

## Security Note

This web interface:
- Runs on your local computer (http://127.0.0.1:5000)
- Does NOT send your data to the internet
- All processing happens locally
- Temporary files are automatically deleted after download
- Do NOT access from outside your network without proper security setup

---

## Questions?

For issues or feature requests, check the main README.md or contact the development team.

Thank you for using ANOVA! 🔬
