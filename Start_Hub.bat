@echo off
title ProctorHub Server
cd /d "%~dp0"

echo ========================================================
echo   ProctorHub: Initializing System...
echo ========================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH!
    echo Please install Python 3.10 or newer from python.org.
    echo IMPORTANT: Make sure to check the box "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b
)

:: 2. Auto-Install Dependencies
echo [*] Verifying and installing required packages...
echo     (This may take a moment if running for the first time)
python -m pip install -r requirements.txt --quiet

echo [*] Dependencies verified.
echo.
echo ========================================================
echo   Launching ProctorHub Dashboard...
echo ========================================================
python hub.py

pause