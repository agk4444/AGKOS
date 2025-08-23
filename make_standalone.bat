@echo off

REM AGK Compiler Standalone Build Script for Windows
REM Quick build script for creating standalone executables

echo 🚀 AGK Compiler Standalone Build
echo =================================

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is required but not installed.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install requirements
echo 📦 Installing build requirements...
pip install -r requirements.txt

REM Run the build script
echo 🔧 Starting build process...
python build_standalone.py

echo.
echo 🎉 Build process completed!
echo Check the output directories for your standalone executables:
echo   - dist\ (PyInstaller executables)
echo   - build_nuitka\ (Nuitka executables)
echo   - Docker image: agk-compiler-standalone
echo   - Installers: install_*.bat
echo   - Web version: agk_compiler_web.html

pause