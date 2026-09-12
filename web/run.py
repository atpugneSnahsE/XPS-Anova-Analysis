#!/usr/bin/env python3
"""
Run the ANOVA web server
"""
import os
import sys
import webbrowser
from pathlib import Path
from threading import Timer

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app


def open_browser():
    """Open browser after short delay to ensure server is ready"""
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    # Open browser after 2 seconds
    timer = Timer(2.0, open_browser)
    timer.daemon = True
    timer.start()

    print("\n" + "="*60)
    print("🚀 ANOVA Web Server")
    print("="*60)
    print("Server starting at: http://127.0.0.1:5000")
    print("Opening browser automatically...")
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")

    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
