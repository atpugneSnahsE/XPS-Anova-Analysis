#!/usr/bin/env bash
# One-command setup + run for the XPS / ANOVA analysis pipelines.
#
#   bash start.sh          # run the XPS peak analysis
#   bash start.sh anova    # run the full ANOVA statistics pipeline
#
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Checking Python..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed."
    echo "Install it from https://www.python.org/downloads/ (3.11 or newer), then re-run."
    exit 1
fi
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    echo "Python 3.11 or newer is required (you have $(python3 --version))."
    echo "Install it from https://www.python.org/downloads/, then re-run."
    exit 1
fi

echo "==> Creating private Python environment (first run only)..."
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

echo "==> Installing dependencies..."
python -m pip install --upgrade pip -q
python -m pip install -q -r requirements.txt

if [ "${1:-}" = "anova" ]; then
    echo "==> Running ANOVA statistics pipeline..."
    python data_extractor.py
    python two_way_anova2.py
    python analysis_pipeline.py
    python validation_pipeline.py
else
    echo "==> Running XPS peak analysis..."
    python main.py
fi

echo "==> Done. Results are in results/, summary/ (XPS) and the *.csv tables / figures/ (ANOVA)."
