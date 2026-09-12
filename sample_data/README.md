# Sample Data for ANOVA Analysis

This folder contains example data files for testing and learning the ANOVA analysis system.

## Contents

### ANOVA Adsorption Experiment Data (15 files)

Grouped by polymer material (PE, PET, PS) and experimental factors:

**PE (Polyethylene):**
- `PE-pH.xlsx` - pH variation experiments
- `PE-Temp.xlsx` - Temperature variation experiments
- `PE-time.xlsx` - Contact time variation experiments
- `PE-analyte.xlsx` - Analyte concentration variation
- `PE-ad.dosage.xlsx` - Adsorbent dosage variation

**PET (Polyethylene Terephthalate):**
- `PET-pH.xlsx` - pH variation experiments
- `PET-Temp.xlsx` - Temperature variation experiments
- `PET-time.xlsx` - Contact time variation experiments
- `PET-analyte.xlsx` - Analyte concentration variation
- `PET-ad.dosage.xlsx` - Adsorbent dosage variation

**PS (Polystyrene):**
- `PS-pH.xlsx` - pH variation experiments
- `PS-Temp.xlsx` - Temperature variation experiments
- `PS-time.xlsx` - Contact time variation experiments
- `PS-analyte.xlsx` - Analyte concentration variation
- `PS-ad.dosage.xlsx` - Adsorbent dosage variation

### XPS Spectroscopy Sample Data (12 files)

Spectroscopic measurements for different materials:

**GO (Graphene Oxide) Samples:**
- `GOCS.xlsx` - Graphene oxide with chitosan
- `GOMCC50.xlsx` - Graphene oxide with microcrystalline cellulose (50%)
- `GOMCC90.xlsx` - Graphene oxide with microcrystalline cellulose (90%)

**PE (Polyethylene) Samples:**
- `PE50.xlsx` - Polyethylene treatment 1
- `PE90.xlsx` - Polyethylene treatment 2
- `PECS.xlsx` - Polyethylene with chitosan

**PS (Polystyrene) Samples:**
- `PS50.xlsx` - Polystyrene treatment 1
- `PS90.xlsx` - Polystyrene treatment 2
- `PSCS.xlsx` - Polystyrene with chitosan

**PT (Polytetrafluoroethylene) Samples:**
- `PT50.xlsx` - PTFE treatment 1
- `PT90.xlsx` - PTFE treatment 2
- `PTCS.xlsx` - PTFE with chitosan

## How to Use

### For ANOVA Analysis
1. Select any of the `*-*.xlsx` files (PE-pH.xlsx, PET-Temp.xlsx, etc.)
2. Upload to the ANOVA web interface
3. Click "Analyze" → Download results

### For XPS Analysis
1. Select any of the XPS sample files (GOCS.xlsx, PE50.xlsx, etc.)
2. Upload to the ANOVA web interface
3. Click "Analyze" → Download results

## File Information

- **Total Files**: 27
- **Total Size**: 1.8 MB
- **Format**: Microsoft Excel (.xlsx)
- **Metadata**: Removed for privacy
- **Created**: September 2026

## Data Structure

### ANOVA Files
Each file contains:
- **Columns**: Material, Factor, Level, Adsorbent, PctAdsorption
- **Rows**: Experimental data points
- **Format**: Tidy data format (one observation per row)

**Example:**
```
Material | Factor | Level | Adsorbent | PctAdsorption
---------|--------|-------|-----------|---------------
PE       | pH     | 1     | GO-CS     | 45.5
PE       | pH     | 2     | GO-CS     | 52.3
...      | ...    | ...   | ...       | ...
```

### XPS Files
Each file contains:
- **Multiple worksheets**: One per spectral region (C 1s, N 1s, O 1s, etc.)
- **Columns**: Binding Energy (B.E.), Intensity (CPS or Counts)
- **Rows**: Spectral data points

**Example worksheet:**
```
B.E.  | CPS
------|------
0     | 100
1     | 150
2     | 200
...   | ...
```

## Using for Learning

### Quick Start
1. Download the web interface: `/Users/mac/ANOVA/downloads/ANOVA-v1.0.zip`
2. Extract and run
3. Upload any file from this folder
4. Analyze and explore results

### Experiment Ideas
1. **ANOVA**: Upload different factor files and compare results
2. **XPS**: Upload different sample files and compare spectra
3. **Validation**: Cross-check results between different files
4. **Troubleshooting**: Use to test error handling

## File Characteristics

- **Clean data**: No missing values
- **Properly formatted**: Ready to analyze immediately
- **Well-organized**: Clear naming conventions
- **Diverse samples**: Multiple materials and conditions
- **Realistic scale**: Representative of actual experiments

## Sample Data Sources

- ANOVA data: Adsorption experiments on polymer materials
- XPS data: Surface analysis of modified materials
- Materials: PE, PET, PS, PTFE with graphene oxide adsorbents

## Notes

- All metadata (creator, timestamps, comments) has been removed
- Files are optimized for analysis (1.8 MB total)
- Data is for example/testing purposes only
- No modifications have been made to actual data values

## Next Steps

1. Extract the ANOVA release ZIP
2. Copy files from this folder to test the analysis
3. Explore the web interface with sample data
4. Try different analysis types
5. Review the comprehensive documentation included

---

**Last Updated**: September 2026  
**Data Version**: 1.0  
**Status**: Ready for use  

For questions, see the documentation in the main release.
