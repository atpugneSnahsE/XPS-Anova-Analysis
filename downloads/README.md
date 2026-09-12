# ANOVA Release Downloads

This directory contains distributable release packages of the ANOVA analysis system.

## Available Releases

### ANOVA v1.0 (Latest)
- **File**: `ANOVA-v1.0.zip` (1.9 MB)
- **Release Date**: September 12, 2026
- **Status**: Stable
- **Features**:
  - Web interface for non-technical users
  - XPS spectral analysis
  - ANOVA statistical analysis
  - Auto Python setup
  - Works on Windows, Mac, Linux

## How to Use

### Option 1: Download and Run Locally

1. **Download**: Click on `ANOVA-v1.0.zip` above
2. **Extract**: Unzip the file on your computer
3. **Run**:
   - **Windows**: Double-click `start_web.bat`
   - **Mac/Linux**: Open Terminal, navigate to folder, run `bash start_web.sh`
4. **Use**: Your browser opens automatically
5. **Analyze**: Upload your Excel file and click "Analyze"

### Option 2: View Web Interface

Access the web interface at:
- **Main**: http://localhost:5000
- **Downloads**: http://localhost:5000/downloads
- **Analysis**: http://localhost:5000/

## Hosting These Releases

### For Your Own Website

1. **Download this entire `downloads` folder** with all files
2. **Upload to your web server**:
   ```bash
   scp -r downloads/ user@yourserver.com:/var/www/
   ```
3. **Users visit**: `https://yoursite.com/downloads/`

### Using GitHub Releases

1. Go to your GitHub repo
2. Click "Releases" → "Create a new release"
3. Upload the ZIP file
4. Publish
5. Share the GitHub release link

### Using Cloud Storage

**Dropbox:**
1. Upload `ANOVA-v1.0.zip` to Dropbox
2. Right-click → Share
3. Get shareable link
4. Change `?dl=0` to `?dl=1` for direct download

**Google Drive:**
1. Upload `ANOVA-v1.0.zip`
2. Right-click → Get link
3. Make sure "Anyone with link" can view

**AWS S3:**
```bash
aws s3 cp ANOVA-v1.0.zip s3://your-bucket/downloads/
aws s3api put-object-acl --bucket your-bucket --key downloads/ANOVA-v1.0.zip --acl public-read
```

## Building New Releases

From the project root directory:

```bash
bash build_release.sh
```

This creates a new release file with format: `ANOVA-Release-[DATE].zip`

Then move it to this downloads directory:
```bash
mv ANOVA-Release-*.zip downloads/ANOVA-v1.1.zip
```

## Release File Contents

Each release ZIP contains:

```
ANOVA-v1.0/
├── web/                    # Web interface
├── *.py                    # Python pipeline files
├── start_web.sh            # Mac/Linux launcher
├── start_web.bat           # Windows launcher
├── START_HERE.md           # Main documentation
├── WEB_SETUP_GUIDE.md      # Complete user guide
├── README.md               # Original documentation
├── requirements.txt        # Python dependencies
└── data/                   # Sample data (optional)
```

## System Requirements

- **Python 3.11+** (automatically checked)
- **4 GB RAM** minimum
- **1 GB free disk space**
- **Windows 7+, macOS 10.13+, or modern Linux**

## Version History

### v1.0 (2026-09-12)
- ✅ Initial release
- ✅ Web interface
- ✅ XPS analysis
- ✅ ANOVA statistics
- ✅ Complete documentation

## How to Link to These Releases

### For Your Website

```html
<a href="https://yoursite.com/downloads/ANOVA-v1.0.zip">
    Download ANOVA v1.0
</a>
```

### For GitHub README

```markdown
[Download ANOVA v1.0](../../releases/download/v1.0/ANOVA-v1.0.zip)
```

### For Email

```
Download: https://yoursite.com/downloads/ANOVA-v1.0.zip

User Guide: https://yoursite.com/downloads/index.html
```

## Troubleshooting

**Where should I download from?**
- Use the official downloads page: `/downloads/index.html`
- Or visit: `http://localhost:5000/downloads`

**What if my browser blocks the download?**
- Right-click the download link → "Save link as..."
- Or use command line: `wget https://yoursite.com/downloads/ANOVA-v1.0.zip`

**The ZIP is corrupted?**
- Try downloading again
- Check file size: should be ~1.9 MB
- Use a different browser

**After extraction, what do I do?**
- Read the `START_HERE.md` file inside
- Follow the Quick Start guide
- Run the startup script

## Support

Users having issues?

1. **First**: Read `START_HERE.md` in the extracted folder
2. **Then**: Check `WEB_SETUP_GUIDE.md` (includes troubleshooting)
3. **Finally**: Report bug on GitHub if needed

## Release Naming Convention

```
ANOVA-v[MAJOR].[MINOR].[PATCH].zip

Examples:
- ANOVA-v1.0.0.zip    (Initial release)
- ANOVA-v1.1.0.zip    (New features)
- ANOVA-v1.0.1.zip    (Bug fixes)
- ANOVA-v2.0.0.zip    (Major changes)
```

## Next Release

For v1.1, planned features:
- Batch processing (multiple files)
- Progress bar with real-time updates
- Parameter customization UI
- Advanced visualization options

---

**Last Updated**: September 12, 2026
**Current Release**: v1.0
**Next Release**: TBD
