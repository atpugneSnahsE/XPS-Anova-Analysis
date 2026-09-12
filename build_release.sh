#!/bin/bash
#
# Build ANOVA Release Package
#
# Creates a distributable .zip file with all necessary files
# for users to download and run the ANOVA analysis system.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Get version from git or use timestamp
VERSION=$(git describe --tags --always 2>/dev/null || date +%Y%m%d)
RELEASE_NAME="ANOVA-Release-${VERSION}"
RELEASE_FILE="${RELEASE_NAME}.zip"
TEMP_DIR="/tmp/anova-release-$$"

echo "=================================================="
echo "Building ANOVA Release: $RELEASE_FILE"
echo "=================================================="
echo ""

# Create temporary directory
mkdir -p "$TEMP_DIR/$RELEASE_NAME"
RELEASE_DIR="$TEMP_DIR/$RELEASE_NAME"

echo "📦 Collecting files..."

# Copy main files
cp -r web "$RELEASE_DIR/"
cp -r sample_data "$RELEASE_DIR/" 2>/dev/null || true
cp -r Docs "$RELEASE_DIR/" 2>/dev/null || true

# Copy Python files (excluding __pycache__)
for file in *.py; do
    if [ -f "$file" ] && [ "$file" != "*.py" ]; then
        cp "$file" "$RELEASE_DIR/"
    fi
done

# Copy scripts
cp start_web.sh start_web.bat "$RELEASE_DIR/" 2>/dev/null || true

# Copy documentation
cp START_HERE.md WEB_SETUP_GUIDE.md WEB_BUILD_SUMMARY.md README.md "$RELEASE_DIR/" 2>/dev/null || true

# Copy configuration
cp requirements.txt config.py "$RELEASE_DIR/" 2>/dev/null || true

# Copy .gitignore to help with future version control
cp .gitignore "$RELEASE_DIR/" 2>/dev/null || true

# Create a RELEASE_NOTES.md
cat > "$RELEASE_DIR/RELEASE_NOTES.md" << 'EOF'
# ANOVA Release Notes

## Version Information
- Release Date: $(date)
- Version: See filename for version

## What's Inside

This package contains the complete ANOVA analysis system with:
- XPS spectral analysis pipeline
- Two-way ANOVA statistical analysis
- Modern web interface for non-technical users
- Command-line interface for advanced users
- Complete documentation

## Quick Start

### For Web Interface (Recommended)

**Windows:**
1. Extract the ZIP file
2. Double-click `start_web.bat`
3. Your browser will open automatically
4. Upload your Excel file and click "Analyze"

**Mac/Linux:**
1. Extract the ZIP file
2. Open Terminal
3. Navigate to the folder
4. Run: `bash start_web.sh`
5. Your browser will open automatically
6. Upload your Excel file and click "Analyze"

### For Command Line

```bash
# XPS analysis only
python main.py

# Full ANOVA pipeline
bash start.sh anova
```

## Documentation

- **START_HERE.md** - Main entry point (read this first!)
- **WEB_SETUP_GUIDE.md** - Complete web interface guide
- **README.md** - Original documentation
- **WEB_BUILD_SUMMARY.md** - Technical details

## System Requirements

- Python 3.11 or later (automatically checked)
- 4 GB RAM minimum
- 1 GB free disk space
- Windows 7+, macOS 10.13+, or modern Linux

## Support

If you encounter any issues:
1. Check the troubleshooting section in WEB_SETUP_GUIDE.md
2. Ensure you have Python 3.11+ installed
3. Check error messages in the command window

## License

Same as original ANOVA project.
EOF

echo "✓ Files collected"
echo ""
echo "📦 Creating archive: $RELEASE_FILE"

# Create the ZIP file
cd "$TEMP_DIR"
zip -r -q "$SCRIPT_DIR/$RELEASE_FILE" "$RELEASE_NAME"

# Calculate file size
SIZE=$(du -sh "$SCRIPT_DIR/$RELEASE_FILE" | cut -f1)

# Cleanup
rm -rf "$TEMP_DIR"

echo "✓ Archive created: $SIZE"
echo ""
echo "=================================================="
echo "✅ Release package ready!"
echo "=================================================="
echo ""
echo "📦 File: $RELEASE_FILE"
echo "📍 Location: $(pwd)"
echo "📊 Size: $SIZE"
echo ""
echo "Next steps:"
echo "1. Place this file in a web server"
echo "2. Or share via file hosting service"
echo "3. Users can download and extract to get started"
echo ""
echo "=================================================="
