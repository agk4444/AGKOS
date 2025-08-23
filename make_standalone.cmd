@echo off
REM AGK Compiler Standalone Build Script for Windows CMD
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

REM Get Python version
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python is available: %PYTHON_VERSION%

REM Install requirements
echo 📦 Installing build requirements...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)
echo ✅ Build requirements installed successfully

REM Run the build script
echo 🔧 Starting build process...
python build_standalone.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Build process failed
    pause
    exit /b 1
)

echo.
echo 🎉 Build process completed successfully!
echo.
echo 📋 Build output locations:
echo   - dist\ (PyInstaller executables)
echo   - build_nuitka\ (Nuitka executables)
echo   - Docker image: agk-compiler-standalone
echo   - Installers: install_*.bat
echo   - Web version: agk_compiler_web.html

echo.
pause