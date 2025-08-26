# AGK Mobile OS - Portable USB Distribution

This is a portable, bootable USB distribution of the AGK Mobile OS that can run from any USB drive without installation.

## Quick Start

### Windows
1. Insert the USB drive
2. Open autorun\run_windows.bat

### Linux
1. Insert the USB drive
2. Open a terminal and navigate to the USB drive
3. Run: ./autorun/run_linux.sh

### macOS
1. Insert the USB drive
2. Open a terminal and navigate to the USB drive
3. Run: ./autorun/run_macos.sh

## Directory Structure

AGK_Mobile_OS_Portable_USB/
|-- core/              # Core AGK OS files
|-- compiler/          # AGK Compiler
|-- lib/               # Standard library
|-- templates/         # Code templates
|-- examples/          # Example programs
|-- docs/              # Documentation
|-- autorun/           # Platform-specific launchers
-- tools/             # Additional utilities

## System Requirements

- Python 3.7+
- 256 MB RAM minimum
- USB drive with 1 GB free space

## What's Included

### Core Components
- AGK Mobile OS: Complete mobile operating system
- AGK Compiler: Multi-platform code compiler
- Standard Library: Pre-built functions and modules
- Templates: Ready-to-use code templates

### Features
- Portable: Runs from any USB drive
- Multi-platform: Windows, Linux, macOS support
- No Installation: Just plug and play
- Auto-run: Automatic detection and launching

## Manual Usage

If auto-run doesn't work, you can manually start the system:

# Navigate to the USB drive
cd /path/to/usb/AGK_Mobile_OS_Portable_USB

# Run the mobile OS
python3 tools/agk_mobile_os_launcher.py

## Troubleshooting

### Python Not Found
- Windows: Download from https://python.org
- Linux: sudo apt install python3 (Ubuntu/Debian)
- macOS: brew install python3 (Homebrew)

### Permission Errors
- Linux/macOS: Make scripts executable: chmod +x autorun/*.sh

### Missing Dependencies
Run: pip install -r core/requirements.txt
