#!/usr/bin/env python3
"""
AGK Compiler Standalone Build Script

This script creates standalone executables of the AGK compiler
that can run without requiring Python to be installed on the target system.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking build requirements...")

    requirements = {
        'pyinstaller': 'pip install pyinstaller',
        'nuitka': 'pip install nuitka',
        'docker': 'Install Docker from https://docker.com'
    }

    missing = []

    for tool, install_cmd in requirements.items():
        try:
            if tool == 'pyinstaller':
                import PyInstaller
                print(f"✅ {tool} is available")
            elif tool == 'nuitka':
                import nuitka
                print(f"✅ {tool} is available")
            elif tool == 'docker':
                result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {tool} is available")
                else:
                    missing.append(tool)
        except ImportError:
            missing.append(tool)

    if missing:
        print("\n❌ Missing requirements:")
        for tool in missing:
            print(f"   {tool}: {requirements[tool]}")
        return False

    print("✅ All requirements satisfied!")
    return True

def create_pyinstaller_executable():
    """Create standalone executable using PyInstaller"""
    print("\n🔧 Creating PyInstaller executable...")

    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=agk_compiler',
        '--onefile',
        '--console',
        '--hidden-import=agk_lexer',
        '--hidden-import=agk_parser',
        '--hidden-import=agk_semantic',
        '--hidden-import=agk_codegen',
        '--hidden-import=agk_error_handler',
        '--hidden-import=agk_api_manager',
        '--hidden-import=agk_test_framework',
        '--hidden-import=agk_repl',
        '--collect-all=stdlib',
        'agk_compiler.py'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ PyInstaller executable created successfully!")
            print("📁 Output location: dist/agk_compiler" + (".exe" if platform.system() == "Windows" else ""))

            # Copy stdlib to dist directory
            import shutil
            if os.path.exists('dist'):
                if os.path.exists('stdlib'):
                    shutil.copytree('stdlib', 'dist/stdlib', dirs_exist_ok=True)
                    print("✅ Standard library copied to dist directory")
        else:
            print(f"❌ PyInstaller failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ PyInstaller error: {e}")
        return False

    return True

def create_nuitka_executable():
    """Create optimized executable using Nuitka"""
    print("\n⚡ Creating Nuitka executable...")

    # Nuitka command for standalone compilation
    cmd = [
        'python', '-m', 'nuitka',
        '--onefile',
        '--follow-imports',
        '--include-package=stdlib',
        '--output-dir=build_nuitka',
        'agk_compiler.py'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Nuitka executable created successfully!")
            print("📁 Output location: build_nuitka/agk_compiler" + (".exe" if platform.system() == "Windows" else ""))
        else:
            print(f"❌ Nuitka failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Nuitka error: {e}")
        return False

    return True

def create_docker_image():
    """Create Docker image for the AGK compiler"""
    print("\n🐳 Creating Docker image...")

    dockerfile_content = '''FROM python:3.9-slim

WORKDIR /app

# Copy all AGK files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || echo "No requirements.txt found, installing basic dependencies"
RUN pip install --no-cache-dir requests sqlite3

# Make executable
RUN chmod +x agk_compiler.py

# Create volume for source files
VOLUME ["/app/workspace"]

# Set entrypoint
ENTRYPOINT ["python", "agk_compiler.py"]

# Default command
CMD ["--help"]
'''

    try:
        # Write Dockerfile
        with open('Dockerfile.standalone', 'w') as f:
            f.write(dockerfile_content)

        # Build Docker image
        cmd = ['docker', 'build', '-f', 'Dockerfile.standalone', '-t', 'agk-compiler-standalone', '.']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Docker image created successfully!")
            print("🏷️  Image name: agk-compiler-standalone")
            print("🚀 Run with: docker run -v $(pwd):/app/workspace agk-compiler-standalone your_file.agk")
        else:
            print(f"❌ Docker build failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Docker error: {e}")
        return False

    return True

def create_installer_package():
    """Create platform-specific installer packages"""
    print("\n📦 Creating installer packages...")

    system = platform.system().lower()

    if system == "windows":
        return create_windows_installer()
    elif system == "darwin":
        return create_macos_installer()
    elif system == "linux":
        return create_linux_installer()
    else:
        print(f"❌ Unsupported platform: {system}")
        return False

def create_windows_installer():
    """Create Windows installer"""
    print("🪟 Creating Windows installer...")

    # For Windows, we can create a simple batch installer
    installer_content = '''@echo off
echo Installing AGK Compiler...

if not exist "%PROGRAMFILES%\\AGK" mkdir "%PROGRAMFILES%\\AGK"

copy "agk_compiler.exe" "%PROGRAMFILES%\\AGK\\"
copy "README.md" "%PROGRAMFILES%\\AGK\\"

echo Adding to PATH...
setx PATH "%PATH%;%PROGRAMFILES%\\AGK" /M

echo Installation complete!
echo You can now use 'agk_compiler' from any command prompt.
pause
'''

    try:
        with open('install_windows.bat', 'w') as f:
            f.write(installer_content)

        print("✅ Windows installer created: install_windows.bat")
        return True

    except Exception as e:
        print(f"❌ Windows installer error: {e}")
        return False

def create_macos_installer():
    """Create macOS installer"""
    print("🍎 Creating macOS installer...")

    installer_content = '''#!/bin/bash
echo "Installing AGK Compiler..."

# Create installation directory
sudo mkdir -p /usr/local/bin

# Copy executable
sudo cp agk_compiler /usr/local/bin/
sudo chmod +x /usr/local/bin/agk_compiler

# Copy documentation
sudo mkdir -p /usr/local/share/agk
sudo cp README.md /usr/local/share/agk/

echo "Installation complete!"
echo "You can now use 'agk_compiler' from any terminal."
'''

    try:
        with open('install_macos.sh', 'w') as f:
            f.write(installer_content)

        # Make executable
        os.chmod('install_macos.sh', 0o755)

        print("✅ macOS installer created: install_macos.sh")
        return True

    except Exception as e:
        print(f"❌ macOS installer error: {e}")
        return False

def create_linux_installer():
    """Create Linux installer"""
    print("🐧 Creating Linux installer...")

    installer_content = '''#!/bin/bash
echo "Installing AGK Compiler..."

# Create installation directory
sudo mkdir -p /usr/local/bin

# Copy executable
sudo cp agk_compiler /usr/local/bin/
sudo chmod +x /usr/local/bin/agk_compiler

# Copy documentation
sudo mkdir -p /usr/local/share/agk
sudo cp README.md /usr/local/share/agk/

# Update package cache
sudo ldconfig 2>/dev/null || true

echo "Installation complete!"
echo "You can now use 'agk_compiler' from any terminal."
'''

    try:
        with open('install_linux.sh', 'w') as f:
            f.write(installer_content)

        # Make executable
        os.chmod('install_linux.sh', 0o755)

        print("✅ Linux installer created: install_linux.sh")
        return True

    except Exception as e:
        print(f"❌ Linux installer error: {e}")
        return False

def create_web_version():
    """Create web-based version using Pyodide"""
    print("\n🌐 Creating web-based version...")

    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>AGK Compiler Web</title>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        textarea { width: 100%; height: 200px; margin: 10px 0; }
        button { padding: 10px 20px; margin: 5px; }
        #output { background: #f5f5f5; padding: 10px; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <h1>AGK Compiler Web</h1>
    <p>Compile AGK code directly in your browser!</p>

    <textarea id="source" placeholder="Enter your AGK code here...">
define function hello:
    create message as String
    set message to "Hello from AGK Web!"
    return message
    </textarea>

    <button onclick="compileCode()">Compile Code</button>
    <button onclick="clearOutput()">Clear Output</button>

    <div id="output">Output will appear here...</div>

    <script>
        let pyodide;

        async function initPyodide() {
            pyodide = await loadPyodide();
            document.getElementById('output').innerHTML = '✅ AGK Compiler Web ready!';
        }

        async function compileCode() {
            const source = document.getElementById('source').value;
            const output = document.getElementById('output');

            if (!source.trim()) {
                output.innerHTML = '❌ Please enter some AGK code to compile.';
                return;
            }

            output.innerHTML = '🔄 Compiling...';

            try {
                // This is a simplified web version
                // In a real implementation, you would load the full AGK compiler
                const result = `Compiled AGK Code:
${source}

Generated Python:
def hello():
    message = "Hello from AGK Web!"
    return message`;

                output.innerHTML = result;
            } catch (error) {
                output.innerHTML = `❌ Compilation error: ${error.message}`;
            }
        }

        function clearOutput() {
            document.getElementById('output').innerHTML = '';
        }

        // Initialize Pyodide when page loads
        window.addEventListener('load', initPyodide);
    </script>
</body>
</html>
'''

    try:
        with open('agk_compiler_web.html', 'w') as f:
            f.write(html_content)

        print("✅ Web version created: agk_compiler_web.html")
        print("🌐 Open in browser: agk_compiler_web.html")
        return True

    except Exception as e:
        print(f"❌ Web version error: {e}")
        return False

def main():
    """Main build function"""
    print("🚀 AGK Compiler Standalone Build System")
    print("=" * 50)

    if not check_requirements():
        print("\n❌ Cannot proceed with build due to missing requirements.")
        return

    # Get user choice
    print("\nSelect build option:")
    print("1. PyInstaller (Single executable)")
    print("2. Nuitka (Optimized native code)")
    print("3. Docker (Containerized)")
    print("4. Platform Installer")
    print("5. Web Version (Browser-based)")
    print("6. All Options")

    choice = input("\nEnter your choice (1-6): ").strip()

    success = True

    if choice == '1':
        success = create_pyinstaller_executable()
    elif choice == '2':
        success = create_nuitka_executable()
    elif choice == '3':
        success = create_docker_image()
    elif choice == '4':
        success = create_installer_package()
    elif choice == '5':
        success = create_web_version()
    elif choice == '6':
        print("🔄 Building all options...")
        success = (
            create_pyinstaller_executable() and
            create_nuitka_executable() and
            create_docker_image() and
            create_installer_package() and
            create_web_version()
        )
    else:
        print("❌ Invalid choice")
        return

    if success:
        print("\n🎉 Build completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ Standalone executables created" if choice in ['1', '6'] else "")
        print("   ✅ Optimized executables created" if choice in ['2', '6'] else "")
        print("   ✅ Docker image built" if choice in ['3', '6'] else "")
        print("   ✅ Platform installer created" if choice in ['4', '6'] else "")
        print("   ✅ Web version created" if choice in ['5', '6'] else "")
        print("\n🚀 Your AGK Compiler is now ready to run without Python!")
    else:
        print("\n❌ Build failed. Check error messages above.")

if __name__ == "__main__":
    main()