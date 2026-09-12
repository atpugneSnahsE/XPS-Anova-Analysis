# ANOVA Release Guide

This guide explains how to build and distribute releases of the ANOVA analysis system.

---

## Quick Start: Building a Release

### Automatic Build (Recommended)

```bash
bash build_release.sh
```

This creates a file like: `ANOVA-Release-20260912.zip`

### What Gets Included

✅ Web interface (HTML, CSS, JavaScript)  
✅ Flask backend (Python)  
✅ All pipeline code (XPS, ANOVA, utilities)  
✅ Startup scripts (Windows, Mac, Linux)  
✅ Complete documentation  
✅ Sample data (optional)  

❌ NOT included: .git, __pycache__, .venv, temporary files, results

---

## Distribution Options

### Option 1: Direct Download Link (Easiest)

1. Build the release: `bash build_release.sh`
2. Upload ZIP file to web server
3. Share download link with users
4. Users extract and run

**Example:**
```
https://yourserver.com/downloads/ANOVA-v1.0.zip
```

### Option 2: GitHub Releases

1. Push to GitHub: `git push origin main`
2. Create release on GitHub:
   - Go to your repo → Releases
   - Click "Create a new release"
   - Upload the ZIP file
   - Users download from GitHub

**Pros:** Professional, version tracking, statistics  
**Cons:** Requires GitHub account

### Option 3: PyPI Package (Python Package Index)

Make it installable with `pip install anova`:

1. Create `setup.py` (see below)
2. Build: `python setup.py sdist bdist_wheel`
3. Upload: `twine upload dist/*`
4. Users: `pip install anova`

**Pros:** Easy installation, automatic updates  
**Cons:** More complex setup, requires PyPI account

### Option 4: Docker Container

Users run it without any installation:

```bash
docker pull yourname/anova
docker run -p 5000:5000 yourname/anova
```

**Pros:** Zero setup, consistent across machines  
**Cons:** Requires Docker knowledge

### Option 5: Standalone Executable

Create `.exe` for Windows, `.dmg` for Mac:

```bash
pip install pyinstaller
pyinstaller --onefile web/run.py
```

**Pros:** Zero installation, one-click  
**Cons:** Large file (~100 MB), takes time to build

---

## Build Process in Detail

### Step 1: Prepare the Release

```bash
# Make sure everything is committed
git status

# No uncommitted changes?
git add .
git commit -m "Release v1.0"
```

### Step 2: Build the Release File

```bash
bash build_release.sh
```

This script:
1. Creates temporary directory
2. Copies all necessary files
3. Creates RELEASE_NOTES.md
4. Compresses to ZIP
5. Cleans up

### Step 3: Verify the Release

```bash
# Extract in a test directory
mkdir /tmp/test_release
cd /tmp/test_release
unzip /path/to/ANOVA-Release-*.zip

# Test it works
cd ANOVA-Release-*
bash start_web.sh  # Should start without errors
```

### Step 4: Upload to Server

**Using FTP/SFTP:**
```bash
sftp user@server.com
put ANOVA-Release-*.zip
```

**Using GitHub:**
1. Go to your GitHub repo
2. Click "Releases" → "Create a new release"
3. Upload ZIP file
4. Publish

**Using a File Hosting Service:**
- Dropbox, Google Drive, AWS S3, etc.
- Create shareable link
- Add to your website

---

## Creating a Website Download Page

### Option A: Use the Built-in Downloads Page

The web interface includes a downloads page at `/downloads`:

```
Start web server:
  bash start_web.sh

Visit:
  http://localhost:5000/downloads
```

### Option B: Create Your Own HTML Page

```html
<!DOCTYPE html>
<html>
<head>
    <title>ANOVA Downloads</title>
</head>
<body>
    <h1>Download ANOVA</h1>
    <a href="/downloads/ANOVA-v1.0.zip">Download Latest (50 MB)</a>
</body>
</html>
```

### Option C: Use GitHub Pages

1. Create `docs/` folder in your repo
2. Add `index.html` with download links
3. Enable GitHub Pages in repo settings
4. Your site is live at: `https://username.github.io/anova`

---

## Release Checklist

Before releasing, verify:

- [ ] All code committed to git
- [ ] Tests pass (if you have tests)
- [ ] Documentation updated
- [ ] Version number incremented
- [ ] CHANGELOG.md updated
- [ ] No secrets in the code
- [ ] README.md is current
- [ ] Example data included (or linked)
- [ ] All dependencies in requirements.txt
- [ ] Scripts are executable (chmod +x)

---

## Version Numbering

Use semantic versioning: `MAJOR.MINOR.PATCH`

Examples:
- `1.0.0` - First release
- `1.1.0` - New features added
- `1.0.1` - Bug fixes
- `2.0.0` - Major changes (incompatible)

Update version in:
- Filename: `ANOVA-v1.0.0.zip`
- Code: `__version__ = "1.0.0"` (if applicable)
- Documentation: `## Version 1.0.0`

---

## Creating a PyPI Package (Advanced)

### Step 1: Create setup.py

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="anova-analysis",
    version="1.0.0",
    author="Your Name",
    author_email="you@example.com",
    description="XPS and ANOVA analysis system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/anova",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "Flask==3.0.0",
        "Flask-CORS==4.0.0",
        "numpy==2.5.1",
        "scipy==1.18.0",
        "pandas==3.0.5",
        "lmfit==1.3.4",
        "statsmodels==0.14.6",
        "matplotlib==3.11.1",
        "seaborn==0.13.2",
        "openpyxl==3.1.5",
    ],
    entry_points={
        "console_scripts": [
            "anova-web=web.run:main",
        ],
    },
)
```

### Step 2: Build and Upload

```bash
# Install build tools
pip install build twine

# Build
python -m build

# Upload to PyPI
twine upload dist/*
```

### Step 3: Users Install with

```bash
pip install anova-analysis
anova-web
```

---

## Creating a Standalone Executable (Windows)

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Build Executable

```bash
pyinstaller --onefile --windowed \
  --name "ANOVA" \
  --icon app_icon.ico \
  --add-data "web/templates:web/templates" \
  --add-data "web/static:web/static" \
  web/run.py
```

### Step 3: Distribute

- File: `dist/ANOVA.exe`
- Size: ~100-150 MB
- Users: Double-click to run
- Distribution: Upload to your website

---

## Distribution Channels

### Tier 1: Free (Recommended for Starting)

- [GitHub Releases](https://github.com) - Version control + downloads
- [Dropbox](https://www.dropbox.com) - File sharing with public link
- [Google Drive](https://drive.google.com) - Easy sharing
- Your own website - Full control

### Tier 2: Professional

- [PyPI](https://pypi.org) - Python package installation
- [Conda](https://conda.io) - Scientific package manager
- [Docker Hub](https://hub.docker.com) - Container images

### Tier 3: Enterprise

- Private server (AWS, Azure, GCP)
- Organization app store
- Software licensing system
- Automatic update mechanism

---

## Hosting Considerations

### For GitHub

✅ Pros:
- Free
- Professional
- Version tracking
- Statistics
- Release notes

❌ Cons:
- Requires GitHub account
- 2 GB file size limit per release

### For Your Own Server

✅ Pros:
- Full control
- Can host large files
- Custom branding
- Download statistics

❌ Cons:
- Need web server
- You manage bandwidth
- You manage uptime

### For Cloud Storage (Google Drive, Dropbox)

✅ Pros:
- Free tier available
- Easy to share
- No maintenance

❌ Cons:
- Share links can expire
- Less professional
- No version history

---

## Download Page Example

The repository includes a complete downloads page at:
- `web/templates/downloads.html`

To use it:
1. Run the web server: `bash start_web.sh`
2. Visit: `http://localhost:5000/downloads`
3. Customize the HTML with your links

---

## Marketing Your Release

### Announcement

```markdown
# 🎉 ANOVA 1.0 Released!

We're excited to announce the release of ANOVA 1.0 with:
- Beautiful web interface
- XPS spectral analysis
- ANOVA statistics
- One-click analysis

## Download

https://github.com/yourrepo/releases/tag/v1.0

## What's New

- Added web interface (no command line needed!)
- Improved peak fitting accuracy
- New visualization options
- Better documentation

## Install

bash start_web.sh

Questions? Read START_HERE.md
```

### Share On

- GitHub Releases
- Lab/University website
- Research networks
- Social media
- Email to colleagues

---

## Versioning Best Practices

### Semantic Versioning

```
v[MAJOR].[MINOR].[PATCH]

Examples:
- v1.0.0 → First stable release
- v1.1.0 → New features (backward compatible)
- v1.1.1 → Bug fix
- v2.0.0 → Major changes (may break old code)
```

### Changelog Format

```markdown
## v1.1.0 (2026-09-15)

### Added
- New feature description
- Another feature

### Fixed
- Bug fix description
- Another fix

### Changed
- Breaking change description
```

---

## Automation: Continuous Deployment

### Using GitHub Actions

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build release
        run: bash build_release.sh
      - name: Upload to Release
        uses: softprops/action-gh-release@v1
        with:
          files: ANOVA-Release-*.zip
```

Now, just tag a commit:
```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub automatically builds and releases!

---

## Support & Feedback

After releasing, monitor:
- Download statistics
- User feedback
- Bug reports
- Feature requests

Iterate and improve for the next release.

---

## Release Checklist Template

```bash
# Copy this to a release planning document

## Pre-Release (1 week before)
- [ ] Test on Windows
- [ ] Test on Mac
- [ ] Test on Linux
- [ ] Update documentation
- [ ] Update CHANGELOG
- [ ] Get feedback from team

## Release Day
- [ ] Final commit
- [ ] Run: bash build_release.sh
- [ ] Test extracted ZIP
- [ ] Upload to server/GitHub
- [ ] Update downloads page
- [ ] Announce on social media
- [ ] Send email to users

## Post-Release (1 week after)
- [ ] Monitor feedback
- [ ] Fix critical bugs
- [ ] Plan next release
```

---

## Quick Commands Reference

```bash
# Build release
bash build_release.sh

# Check what's in it
unzip -l ANOVA-Release-*.zip | head -20

# Test it
mkdir /tmp/test && cd /tmp/test
unzip /path/to/ANOVA-Release-*.zip
cd ANOVA-Release-*
bash start_web.sh

# Upload to GitHub (requires git)
git tag v1.0.0
git push origin v1.0.0
# Then go to GitHub Releases and upload the ZIP

# Upload to web server
scp ANOVA-Release-*.zip user@server.com:/var/www/downloads/
```

---

## Questions?

Refer to:
- `README.md` - Original documentation
- `START_HERE.md` - User guide
- `WEB_SETUP_GUIDE.md` - Setup instructions
- `build_release.sh` - Build script details

---

## Next Steps

1. **Build the first release**: `bash build_release.sh`
2. **Test it**: Extract and verify it works
3. **Upload**: Put on your server or GitHub
4. **Share**: Tell users where to download
5. **Iterate**: Gather feedback for v1.1

Happy releasing! 🚀
