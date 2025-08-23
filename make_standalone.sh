#!/bin/bash

# AGK Compiler Standalone Build Script
# Quick build script for creating standalone executables

echo "🚀 AGK Compiler Standalone Build"
echo "================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install requirements
echo "📦 Installing build requirements..."
pip install -r requirements.txt

# Run the build script
echo "🔧 Starting build process..."
python build_standalone.py

echo "🎉 Build process completed!"
echo "Check the output directories for your standalone executables:"
echo "  - dist/ (PyInstaller executables)"
echo "  - build_nuitka/ (Nuitka executables)"
echo "  - Docker image: agk-compiler-standalone"
echo "  - Installers: install_*.sh or install_*.bat"
echo "  - Web version: agk_compiler_web.html"