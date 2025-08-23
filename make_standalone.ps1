# AGK Compiler Standalone Build Script for Windows PowerShell
# Quick build script for creating standalone executables

Write-Host "🚀 AGK Compiler Standalone Build" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python is available: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "❌ Python is required but not installed." -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install requirements
Write-Host "📦 Installing build requirements..." -ForegroundColor Yellow
try {
    & pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Build requirements installed successfully" -ForegroundColor Green
    } else {
        throw "Installation failed"
    }
} catch {
    Write-Host "❌ Failed to install requirements: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the build script
Write-Host "🔧 Starting build process..." -ForegroundColor Yellow
try {
    & python build_standalone.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "" -ForegroundColor Green
        Write-Host "🎉 Build process completed successfully!" -ForegroundColor Green
        Write-Host "" -ForegroundColor Green
        Write-Host "📋 Build output locations:" -ForegroundColor Cyan
        Write-Host "   - dist\ (PyInstaller executables)" -ForegroundColor White
        Write-Host "   - build_nuitka\ (Nuitka executables)" -ForegroundColor White
        Write-Host "   - Docker image: agk-compiler-standalone" -ForegroundColor White
        Write-Host "   - Installers: install_*.bat" -ForegroundColor White
        Write-Host "   - Web version: agk_compiler_web.html" -ForegroundColor White
    } else {
        throw "Build script failed"
    }
} catch {
    Write-Host "❌ Build process failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "" -ForegroundColor Green
Write-Host "Press Enter to exit" -ForegroundColor Yellow
Read-Host