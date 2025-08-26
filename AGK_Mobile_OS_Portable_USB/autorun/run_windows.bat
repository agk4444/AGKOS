@echo off
echo AGK Mobile OS Portable USB
echo ================================
echo.
echo Starting AGK Mobile OS from USB drive...
echo.

cd /d "%~dp0"
cd ..

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo Python found, starting AGK Mobile OS...

REM Run the mobile OS
python tools\agk_mobile_os_launcher.py

echo.
echo AGK Mobile OS session ended.
pause
