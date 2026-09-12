#!/bin/bash
#
# Start ANOVA Web Server
#
# This script sets up the Python environment and starts the web server
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "ANOVA Web Server Setup"
echo "======================================"

# Check Python version
PYTHON_CMD=python3
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD=python
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Python: $PYTHON_VERSION"

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r web/requirements.txt

# Run the web server
echo ""
echo "======================================"
echo "Starting ANOVA Web Server..."
echo "======================================"
echo ""

cd "$SCRIPT_DIR/web"
$PYTHON_CMD run.py
