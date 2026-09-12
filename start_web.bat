@echo off
REM Start ANOVA Web Server (Windows)
REM
REM This script sets up the Python environment and starts the web server

setlocal enabledelayedexpansion

echo.
echo ======================================
echo ANOVA Web Server Setup
echo ======================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python: %PYTHON_VERSION%

REM Create virtual environment if needed
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r web\requirements.txt

REM Run server
echo.
echo ======================================
echo Starting ANOVA Web Server...
echo ======================================
echo.

cd web
python run.py
pause
