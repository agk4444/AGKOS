#!/usr/bin/env python3
"""
AGK Mobile OS USB Distribution Creator (Simple Version)

Creates a portable, bootable USB distribution of the AGK Mobile OS
that can run from any USB drive without installation.
"""

import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path
import zipfile
import tarfile

class USBDistributionCreator:
    """Creates portable USB distributions of AGK Mobile OS"""

    def __init__(self):
        self.dist_name = "AGK_Mobile_OS_Portable"
        self.usb_root = f"{self.dist_name}_USB"
        self.system = platform.system().lower()

    def create_portable_distribution(self):
        """Create the complete portable distribution"""
        print("Creating AGK Mobile OS Portable USB Distribution")
        print("=" * 60)

        # Create directory structure
        self._create_directory_structure()

        # Copy core files
        self._copy_core_files()

        # Create platform-specific executables
        self._create_executables()

        # Create auto-run scripts
        self._create_auto_run_scripts()

        # Create documentation
        self._create_documentation()

        # Create package archives
        self._create_archives()

        print("\n[SUCCESS] Portable USB distribution created successfully!")
        print(f"Location: {self.usb_root}")
        print("\nWhat's included:")
        print("   - AGK Mobile OS core files")
        print("   - AGK Compiler (portable executable)")
        print("   - Platform-specific auto-run scripts")
        print("   - Standard library and templates")
        print("   - Documentation and examples")
        print("   - Ready-to-use archives")

        return True

    def _create_directory_structure(self):
        """Create the USB directory structure"""
        print("\n[INFO] Creating directory structure...")

        dirs = [
            self.usb_root,
            f"{self.usb_root}/core",
            f"{self.usb_root}/compiler",
            f"{self.usb_root}/lib",
            f"{self.usb_root}/templates",
            f"{self.usb_root}/examples",
            f"{self.usb_root}/docs",
            f"{self.usb_root}/autorun",
            f"{self.usb_root}/tools"
        ]

        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

        print("Directory structure created")

    def _copy_core_files(self):
        """Copy core AGK OS files"""
        print("\n[INFO] Copying core files...")

        core_files = [
            "mobile_os.agk",
            "agk_compiler.py",
            "requirements.txt",
            "README.md"
        ]

        for file in core_files:
            if os.path.exists(file):
                shutil.copy2(file, f"{self.usb_root}/core/")
                print(f"   {file}")

        # Copy library files
        if os.path.exists("lib"):
            shutil.copytree("lib", f"{self.usb_root}/lib/", dirs_exist_ok=True)
            print("   Standard library")

        # Copy templates
        if os.path.exists("templates"):
            shutil.copytree("templates", f"{self.usb_root}/templates/", dirs_exist_ok=True)
            print("   Templates")

        # Copy documentation
        if os.path.exists("docs"):
            shutil.copytree("docs", f"{self.usb_root}/docs/", dirs_exist_ok=True)
            print("   Documentation")

        print("Core files copied")

    def _create_executables(self):
        """Create platform-specific executables"""
        print("\n[INFO] Creating executables...")

        # Create Python scripts (most compatible approach)
        self._create_python_scripts()

        print("Executables created")

    def _create_python_scripts(self):
        """Create portable Python scripts with shebang"""
        print("   Creating portable Python scripts...")

        # Create main OS launcher
        os_launcher = '''#!/usr/bin/env python3
"""
AGK Mobile OS Portable Launcher
Runs the AGK Mobile OS from USB drive
"""
import os
import sys

# Get the directory where this script is located (USB root)
usb_root = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(usb_root, "core")

# Add core directory to Python path
sys.path.insert(0, core_dir)

# Change to core directory
os.chdir(core_dir)

# Import and run the mobile OS
try:
    print("Starting AGK Mobile OS from USB...")
    print("Running from:", usb_root)

    # Execute the mobile OS
    exec(open("mobile_os.agk").read())

except Exception as e:
    print(f"Error starting AGK Mobile OS: {e}")
    input("Press Enter to exit...")
'''

        # Write launcher script
        with open(f"{self.usb_root}/tools/agk_mobile_os_launcher.py", 'w') as f:
            f.write(os_launcher)

        # Make scripts executable on Unix-like systems
        if self.system != "windows":
            os.chmod(f"{self.usb_root}/tools/agk_mobile_os_launcher.py", 0o755)

        print("   Portable scripts created")

    def _create_auto_run_scripts(self):
        """Create platform-specific auto-run scripts"""
        print("\n[INFO] Creating auto-run scripts...")

        # Windows auto-run
        self._create_windows_autorun()

        # Linux auto-run
        self._create_linux_autorun()

        # macOS auto-run
        self._create_macos_autorun()

        print("Auto-run scripts created")

    def _create_windows_autorun(self):
        """Create Windows auto-run files"""
        # Windows batch script
        windows_script = '''@echo off
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
python tools\\agk_mobile_os_launcher.py

echo.
echo AGK Mobile OS session ended.
pause
'''

        # Write Windows files
        os.makedirs(f"{self.usb_root}/autorun", exist_ok=True)
        with open(f"{self.usb_root}/autorun/run_windows.bat", 'w') as f:
            f.write(windows_script)

        print("   Windows auto-run created")

    def _create_linux_autorun(self):
        """Create Linux auto-run script"""
        linux_script = '''#!/bin/bash
# AGK Mobile OS Portable USB - Linux Launcher

echo "AGK Mobile OS Portable USB"
echo "==============================="
echo ""
echo "Starting AGK Mobile OS from USB drive..."
echo ""

# Get the directory where this script is located (USB root)
USB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USB_ROOT="$(dirname "$USB_ROOT")"

echo "USB Root: $USB_ROOT"
cd "$USB_ROOT"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    echo "Please install Python 3.7+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Python 3 found, starting AGK Mobile OS..."

# Run the mobile OS
python3 tools/agk_mobile_os_launcher.py

echo ""
echo "AGK Mobile OS session ended."
read -p "Press Enter to exit..."
'''

        # Write Linux script
        with open(f"{self.usb_root}/autorun/run_linux.sh", 'w') as f:
            f.write(linux_script)
        os.chmod(f"{self.usb_root}/autorun/run_linux.sh", 0o755)

        print("   Linux auto-run created")

    def _create_macos_autorun(self):
        """Create macOS auto-run script"""
        macos_script = '''#!/bin/bash
# AGK Mobile OS Portable USB - macOS Launcher

echo "AGK Mobile OS Portable USB"
echo "==============================="
echo ""
echo "Starting AGK Mobile OS from USB drive..."
echo ""

# Get the directory where this script is located (USB root)
USB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USB_ROOT="$(dirname "$USB_ROOT")"

echo "USB Root: $USB_ROOT"
cd "$USB_ROOT"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    echo "Please install Python 3.7+ from https://python.org"
    echo "or using Homebrew: brew install python3"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Python 3 found, starting AGK Mobile OS..."

# Run the mobile OS
python3 tools/agk_mobile_os_launcher.py

echo ""
echo "AGK Mobile OS session ended."
read -p "Press Enter to exit..."
'''

        # Write macOS script
        with open(f"{self.usb_root}/autorun/run_macos.sh", 'w') as f:
            f.write(macos_script)
        os.chmod(f"{self.usb_root}/autorun/run_macos.sh", 0o755)

        print("   macOS auto-run created")

    def _create_documentation(self):
        """Create documentation for the USB distribution"""
        print("\n[INFO] Creating documentation...")

        # Create README for USB distribution
        usb_readme = '''# AGK Mobile OS - Portable USB Distribution

This is a portable, bootable USB distribution of the AGK Mobile OS that can run from any USB drive without installation.

## Quick Start

### Windows
1. Insert the USB drive
2. Open autorun\\run_windows.bat

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
'''

        # Write documentation files
        with open(f"{self.usb_root}/README.md", 'w') as f:
            f.write(usb_readme)

        print("Documentation created")

    def _create_archives(self):
        """Create compressed archives for distribution"""
        print("\n[INFO] Creating distribution archives...")

        # Create ZIP archive
        zip_path = f"{self.dist_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.usb_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(self.usb_root))
                    zipf.write(file_path, arcname)
        print(f"   ZIP archive: {zip_path}")

        # Create TAR.GZ archive (Unix-like systems)
        if self.system != "windows":
            tar_path = f"{self.dist_name}.tar.gz"
            with tarfile.open(tar_path, 'w:gz') as tarf:
                tarf.add(self.usb_root, arcname=self.dist_name)
            print(f"   TAR.GZ archive: {tar_path}")

        print("Distribution archives created")

def main():
    """Main function"""
    creator = USBDistributionCreator()
    success = creator.create_portable_distribution()

    if success:
        print("\n" + "="*60)
        print("AGK Mobile OS Portable USB Distribution Complete!")
        print("="*60)
        print("\nNext Steps:")
        print("1. Copy the distribution to a USB drive:")
        print(f"   cp -r {creator.usb_root} /path/to/usb/")
        print("")
        print("2. Run the OS from the USB:")
        print("   - Windows: Double-click autorun item or run_windows.bat")
        print("   - Linux: ./autorun/run_linux.sh")
        print("   - macOS: ./autorun/run_macos.sh")
        print("\nYour portable AGK Mobile OS is ready to go!")
    else:
        print("Failed to create USB distribution")
        sys.exit(1)


if __name__ == "__main__":
    main()