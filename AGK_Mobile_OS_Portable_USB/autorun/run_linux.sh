#!/bin/bash
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
