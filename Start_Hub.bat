@echo off
title ProctorHub Server
cd /d "%~dp0"
echo ========================================================
echo   Launching ProctorHub & Opening Dashboard...
echo ========================================================
python hub.py
pause