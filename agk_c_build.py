#!/usr/bin/env python3
"""
AGK Language C Build System

Build system integration for compiling AGK to native executables,
with support for cross-platform builds and OS development.
"""

import os
import sys
import platform
import subprocess
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class CBuildSystem:
    """C build system for AGK compilation"""

    def __init__(self, project_name: str = "agk_system_app"):
        self.project_name = project_name
        self.source_files: List[str] = []
        self.include_dirs: List[str] = []
        self.library_dirs: List[str] = []
        self.libraries: List[str] = []
        self.compiler_flags: List[str] = []
        self.linker_flags: List[str] = []
        self.build_type: str = "release"
        self.target_platform: str = self._detect_platform()
        self.cross_compile: bool = False
        self.cross_compiler_prefix: str = ""

        # Set default compiler flags
        self._set_default_flags()

    def _detect_platform(self) -> str:
        """Detect the current platform"""
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "linux":
            return "linux"
        elif system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        elif system == "freebsd":
            return "freebsd"
        elif system == "openbsd":
            return "openbsd"
        else:
            return "unknown"

    def _set_default_flags(self):
        """Set default compiler and linker flags"""
        # Common flags
        self.compiler_flags = [
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic"
        ]

        # Platform-specific flags
        if self.target_platform == "linux":
            self.compiler_flags.extend([
                "-D_GNU_SOURCE",
                "-pthread"
            ])
            self.libraries.extend([
                "pthread",
                "m"
            ])
        elif self.target_platform == "windows":
            self.compiler_flags.extend([
                "-DWIN32",
                "-D_WIN32"
            ])
            self.libraries.extend([
                "ws2_32",
                "user32",
                "kernel32"
            ])
        elif self.target_platform == "macos":
            self.compiler_flags.extend([
                "-D_DARWIN_C_SOURCE"
            ])
            self.libraries.extend([
                "pthread",
                "m"
            ])

        # Build type specific flags
        if self.build_type == "debug":
            self.compiler_flags.extend([
                "-g",
                "-O0",
                "-DDEBUG"
            ])
        else:  # release
            self.compiler_flags.extend([
                "-O3",
                "-DNDEBUG"
            ])

    def add_source_file(self, file_path: str):
        """Add a source file to the build"""
        self.source_files.append(file_path)

    def add_include_dir(self, dir_path: str):
        """Add an include directory"""
        self.include_dirs.append(dir_path)

    def add_library_dir(self, dir_path: str):
        """Add a library directory"""
        self.library_dirs.append(dir_path)

    def add_library(self, library: str):
        """Add a library to link against"""
        self.libraries.append(library)

    def set_build_type(self, build_type: str):
        """Set the build type (debug/release)"""
        if build_type.lower() in ["debug", "release"]:
            self.build_type = build_type.lower()
            self._set_default_flags()

    def set_cross_compile(self, target: str, compiler_prefix: str = ""):
        """Set cross-compilation target"""
        self.cross_compile = True
        self.cross_compiler_prefix = compiler_prefix or f"{target}-"
        self.target_platform = target

    def generate_makefile(self, output_dir: str = ".") -> str:
        """Generate a Makefile for the project"""
        makefile_path = os.path.join(output_dir, "Makefile")

        # Prepare compiler and flags
        cc = f"{self.cross_compiler_prefix}gcc"
        cflags = " ".join(self.compiler_flags)
        ldflags = " ".join(self.linker_flags)

        # Add include directories
        for inc_dir in self.include_dirs:
            cflags += f" -I{inc_dir}"

        # Add library directories
        for lib_dir in self.library_dirs:
            ldflags += f" -L{lib_dir}"

        # Add libraries
        libs = " ".join([f"-l{lib}" for lib in self.libraries])

        # Generate Makefile content
        makefile_content = f"""# Generated Makefile for {self.project_name}
CC = {cc}
CFLAGS = {cflags}
LDFLAGS = {ldflags}
LIBS = {libs}

TARGET = {self.project_name}
SOURCES = {" ".join([os.path.basename(f) for f in self.source_files])}
OBJECTS = $(SOURCES:.c=.o)

.PHONY: all clean debug release

all: $(TARGET)

$(TARGET): $(OBJECTS)
\t$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

%.o: %.c
\t$(CC) $(CFLAGS) -c $< -o $@

debug:
\tmake clean
\tmake CFLAGS="$(CFLAGS) -g -O0 -DDEBUG" all

release:
\tmake clean
\tmake CFLAGS="$(CFLAGS) -O3 -DNDEBUG" all

clean:
\trm -f $(OBJECTS) $(TARGET)

install: $(TARGET)
\tinstall -d $(DESTDIR)/usr/bin
\tinstall -m 755 $(TARGET) $(DESTDIR)/usr/bin/

help:
\t@echo "Available targets:"
\t@echo "  all      - Build the project"
\t@echo "  debug    - Build with debug flags"
\t@echo "  release  - Build with release flags"
\t@echo "  clean    - Remove build artifacts"
\t@echo "  install  - Install the binary"
\t@echo "  help     - Show this help"
"""

        # Write Makefile
        with open(makefile_path, 'w') as f:
            f.write(makefile_content)

        return makefile_path

    def generate_cmake_lists(self, output_dir: str = ".") -> str:
        """Generate CMakeLists.txt for the project"""
        cmake_path = os.path.join(output_dir, "CMakeLists.txt")

        # Prepare CMake content
        cmake_content = f"""# Generated CMakeLists.txt for {self.project_name}
cmake_minimum_required(VERSION 3.10)
project({self.project_name} C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Set build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
"""

        # Add compiler flags
        for flag in self.compiler_flags:
            cmake_content += f"add_compile_options({flag})\n"

        cmake_content += "\n# Include directories\n"
        for inc_dir in self.include_dirs:
            cmake_content += f"include_directories({inc_dir})\n"

        cmake_content += "\n# Link directories\n"
        for lib_dir in self.library_dirs:
            cmake_content += f"link_directories({lib_dir})\n"

        cmake_content += "\n# Source files\n"
        source_list = " ".join([os.path.basename(f) for f in self.source_files])
        cmake_content += f"set(SOURCES {source_list})\n\n"

        cmake_content += f"""# Create executable
add_executable(${{PROJECT_NAME}} ${{SOURCES}})

# Link libraries
"""
        for lib in self.libraries:
            cmake_content += f"target_link_libraries(${{PROJECT_NAME}} {lib})\n"

        # Write CMakeLists.txt
        with open(cmake_path, 'w') as f:
            f.write(cmake_content)

        return cmake_path

    def build_with_make(self, output_dir: str = ".", target: str = "all") -> bool:
        """Build the project using make"""
        makefile_path = self.generate_makefile(output_dir)

        try:
            # Run make
            result = subprocess.run(
                ["make", "-C", output_dir, target],
                capture_output=True,
                text=True,
                check=True
            )
            print("Build successful!")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Build failed: {e}")
            print(e.stderr)
            return False

    def build_with_cmake(self, output_dir: str = ".", build_dir: str = "build") -> bool:
        """Build the project using cmake"""
        cmake_path = self.generate_cmake_lists(output_dir)
        build_path = os.path.join(output_dir, build_dir)

        try:
            # Create build directory
            os.makedirs(build_path, exist_ok=True)

            # Configure
            result = subprocess.run(
                ["cmake", "-S", output_dir, "-B", build_path],
                capture_output=True,
                text=True,
                check=True
            )

            # Build
            result = subprocess.run(
                ["cmake", "--build", build_path],
                capture_output=True,
                text=True,
                check=True
            )

            print("CMake build successful!")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"CMake build failed: {e}")
            print(e.stderr)
            return False

    def run_executable(self, output_dir: str = ".", args: List[str] = None) -> bool:
        """Run the built executable"""
        executable_path = os.path.join(output_dir, self.project_name)

        if not os.path.exists(executable_path):
            print(f"Executable not found: {executable_path}")
            return False

        try:
            cmd = [executable_path]
            if args:
                cmd.extend(args)

            result = subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Execution failed: {e}")
            return False
        except FileNotFoundError:
            print(f"Executable not found: {executable_path}")
            return False


class KernelBuildSystem(CBuildSystem):
    """Build system for kernel modules and OS development"""

    def __init__(self, project_name: str = "agk_kernel_module"):
        super().__init__(project_name)
        self.kernel_version: str = ""
        self.kernel_source_dir: str = ""
        self.module_dependencies: List[str] = []
        self.is_kernel_module: bool = True

        # Kernel-specific flags
        self.compiler_flags.extend([
            "-DMODULE",
            "-DKERNEL",
            "-D__KERNEL__",
            "-no-pie"
        ])

    def set_kernel_source(self, kernel_source_dir: str):
        """Set the kernel source directory"""
        self.kernel_source_dir = kernel_source_dir

        if os.path.exists(kernel_source_dir):
            # Get kernel version
            version_file = os.path.join(kernel_source_dir, "include/linux/version.h")
            if os.path.exists(version_file):
                # Extract kernel version (simplified)
                self.kernel_version = "5.0.0"  # Placeholder

    def add_module_dependency(self, module: str):
        """Add a kernel module dependency"""
        self.module_dependencies.append(module)

    def generate_kernel_makefile(self, output_dir: str = ".") -> str:
        """Generate a Makefile for kernel module"""
        makefile_path = os.path.join(output_dir, "Makefile")

        makefile_content = f"""# Generated Kernel Module Makefile for {self.project_name}
obj-m += {self.project_name}.o

# Kernel source directory
KDIR := {self.kernel_source_dir or '/lib/modules/$(shell uname -r)/build'}

# Current directory
PWD := $(shell pwd)

# Module dependencies
"""

        if self.module_dependencies:
            makefile_content += f"{self.project_name}-y += {' '.join(self.module_dependencies)}\n"

        makefile_content += """
.PHONY: all clean install

all:
\tmake -C $(KDIR) M=$(PWD) modules

clean:
\tmake -C $(KDIR) M=$(PWD) clean

install:
\tmake -C $(KDIR) M=$(PWD) modules_install

help:
\t@echo "Available targets:"
\t@echo "  all      - Build the kernel module"
\t@echo "  clean    - Remove build artifacts"
\t@echo "  install  - Install the kernel module"
\t@echo "  help     - Show this help"
"""

        # Write Makefile
        with open(makefile_path, 'w') as f:
            f.write(makefile_content)

        return makefile_path


class BareMetalBuildSystem(CBuildSystem):
    """Build system for bare-metal and embedded systems"""

    def __init__(self, project_name: str = "agk_bare_metal"):
        super().__init__(project_name)
        self.linker_script: str = ""
        self.target_arch: str = "arm"  # Default to ARM
        self.bare_metal: bool = True

        # Bare-metal specific flags
        self.compiler_flags.extend([
            "-ffreestanding",
            "-nostdlib",
            "-nostartfiles",
            "-nodefaultlibs"
        ])

    def set_linker_script(self, script_path: str):
        """Set the linker script for bare-metal builds"""
        self.linker_script = script_path

    def set_target_arch(self, arch: str):
        """Set the target architecture"""
        self.target_arch = arch

        # Architecture-specific flags
        if arch == "arm":
            self.compiler_flags.extend([
                "-mcpu=cortex-m4",
                "-mthumb"
            ])
        elif arch == "arm64" or arch == "aarch64":
            self.compiler_flags.extend([
                "-mcpu=cortex-a53",
                "-march=armv8-a"
            ])
        elif arch == "x86":
            self.compiler_flags.extend([
                "-m32"
            ])
        elif arch == "x86_64":
            self.compiler_flags.extend([
                "-m64"
            ])


class MobileBuildSystem(CBuildSystem):
    """Build system for mobile applications (Android/iOS)"""

    def __init__(self, project_name: str = "agk_mobile_app"):
        super().__init__(project_name)
        self.target_platform: str = "android"  # android or ios
        self.target_arch: str = "arm64"  # arm, arm64, x86, x86_64
        self.api_level: int = 21  # Android API level
        self.ndk_path: str = ""
        self.sdk_path: str = ""
        self.mobile_specific: bool = True

        # Mobile-specific flags
        self.compiler_flags.extend([
            "-fPIC",
            "-fvisibility=hidden",
            "-DANDROID" if self.target_platform == "android" else "-DIOS"
        ])

    def set_target_platform(self, platform: str):
        """Set target mobile platform (android/ios)"""
        self.target_platform = platform.lower()
        if platform == "ios":
            self.compiler_flags = [flag for flag in self.compiler_flags if "ANDROID" not in flag]
            self.compiler_flags.append("-DIOS")
        else:
            self.compiler_flags = [flag for flag in self.compiler_flags if "IOS" not in flag]
            self.compiler_flags.append("-DANDROID")

    def set_target_arch(self, arch: str):
        """Set target architecture for mobile"""
        self.target_arch = arch

        # Architecture-specific flags for mobile
        if arch == "arm":
            self.compiler_flags.extend([
                "-march=armv7-a",
                "-mfloat-abi=softfp",
                "-mfpu=vfpv3-d16"
            ])
        elif arch == "arm64" or arch == "aarch64":
            self.compiler_flags.extend([
                "-march=armv8-a"
            ])
        elif arch == "x86":
            self.compiler_flags.extend([
                "-march=i686",
                "-m32"
            ])
        elif arch == "x86_64":
            self.compiler_flags.extend([
                "-march=x86-64",
                "-m64"
            ])

    def set_ndk_path(self, ndk_path: str):
        """Set Android NDK path"""
        self.ndk_path = ndk_path

    def set_sdk_path(self, sdk_path: str):
        """Set Android SDK path"""
        self.sdk_path = sdk_path

    def set_api_level(self, level: int):
        """Set Android API level"""
        self.api_level = level

    def get_mobile_compiler(self) -> str:
        """Get the appropriate compiler for mobile platform"""
        if self.target_platform == "android":
            if self.ndk_path:
                # Use NDK compiler
                arch_map = {
                    "arm": "armv7a-linux-androideabi",
                    "arm64": "aarch64-linux-android",
                    "x86": "i686-linux-android",
                    "x86_64": "x86_64-linux-android"
                }
                triple = arch_map.get(self.target_arch, "aarch64-linux-android")
                return f"{self.ndk_path}/toolchains/llvm/prebuilt/linux-x86_64/bin/{triple}{self.api_level}-clang"
            else:
                return "clang"  # Fallback
        elif self.target_platform == "ios":
            return "clang"  # iOS uses clang
        else:
            return "gcc"

    def generate_mobile_makefile(self, output_dir: str = ".") -> str:
        """Generate a Makefile for mobile builds"""
        makefile_path = os.path.join(output_dir, "Makefile")

        cc = self.get_mobile_compiler()
        cflags = " ".join(self.compiler_flags)
        ldflags = " ".join(self.linker_flags)

        # Add include directories
        for inc_dir in self.include_dirs:
            cflags += f" -I{inc_dir}"

        # Add library directories
        for lib_dir in self.library_dirs:
            ldflags += f" -L{lib_dir}"

        # Add libraries
        libs = " ".join([f"-l{lib}" for lib in self.libraries])

        if self.target_platform == "android":
            # Android-specific libraries
            libs += " -landroid -llog -lEGL -lGLESv3 -lOpenSLES"
            # Android-specific flags
            cflags += f" -D__ANDROID_API__={self.api_level}"
            if self.ndk_path:
                cflags += f" -I{self.ndk_path}/sysroot/usr/include"
                cflags += f" -I{self.ndk_path}/sysroot/usr/include/android"
        elif self.target_platform == "ios":
            # iOS-specific libraries
            libs += " -framework UIKit -framework Foundation -framework CoreGraphics -framework QuartzCore -framework OpenGLES"
            # iOS-specific flags
            cflags += " -fobjc-abi-version=2 -fobjc-arc"

        makefile_content = f"""# Generated Mobile Makefile for {self.project_name}
CC = {cc}
CFLAGS = {cflags}
LDFLAGS = {ldflags}
LIBS = {libs}

TARGET = {self.project_name}
SOURCES = {" ".join([os.path.basename(f) for f in self.source_files])}
OBJECTS = $(SOURCES:.c=.o)

# Platform-specific targets
.PHONY: all clean install apk ipa

all: $(TARGET)

$(TARGET): $(OBJECTS)
\t$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

%.o: %.c
\t$(CC) $(CFLAGS) -c $< -o $@

clean:
\trm -f $(OBJECTS) $(TARGET) $(TARGET).apk $(TARGET).ipa

apk: $(TARGET)
\t@echo "Building Android APK..."
\t@# Create APK structure
\t@mkdir -p apk/lib/{self.get_android_abi()}
\t@mkdir -p apk/assets
\t@mkdir -p apk/res
\t@# Copy native library
\t@cp $(TARGET) apk/lib/{self.get_android_abi()}/lib$(TARGET).so
\t@# Generate AndroidManifest.xml
\t@make android_manifest
\t@# Build APK using aapt/zipalign/apksigner (simplified)
\t@cd apk && zip -r ../$(TARGET).apk .
\t@echo "APK created: $(TARGET).apk"

ipa: $(TARGET)
\t@echo "Building iOS IPA..."
\t@# Create IPA structure
\t@mkdir -p ipa/Payload/{self.project_name}.app
\t@# Copy executable
\t@cp $(TARGET) ipa/Payload/{self.project_name}.app/
\t@# Generate Info.plist
\t@make ios_plist
\t@# Build IPA (simplified)
\t@cd ipa && zip -r ../$(TARGET).ipa Payload/
\t@echo "IPA created: $(TARGET).ipa"

android_manifest:
\t@echo "<?xml version=\\"1.0\\" encoding=\\"utf-8\\"?>" > apk/AndroidManifest.xml
\t@echo "<manifest xmlns:android=\\"http://schemas.android.com/apk/res/android\\"" >> apk/AndroidManifest.xml
\t@echo "    package=\\"{self.project_name}\\" android:versionCode=\\"1\\" android:versionName=\\"1.0\\">" >> apk/AndroidManifest.xml
\t@echo "    <uses-sdk android:minSdkVersion=\\"16\\" android:targetSdkVersion=\\"{self.api_level}\\" />" >> apk/AndroidManifest.xml
\t@echo "    <application android:label=\\"{self.project_name}\\" android:hasCode=\\"false\\">" >> apk/AndroidManifest.xml
\t@echo "        <activity android:name=\\"android.app.NativeActivity\\"" >> apk/AndroidManifest.xml
\t@echo "            android:label=\\"{self.project_name}\\" android:configChanges=\\"orientation|keyboardHidden\\">" >> apk/AndroidManifest.xml
\t@echo "            <meta-data android:name=\\"android.app.lib_name\\" android:value=\\"{self.project_name}\\" />" >> apk/AndroidManifest.xml
\t@echo "            <intent-filter>" >> apk/AndroidManifest.xml
\t@echo "                <action android:name=\\"android.intent.action.MAIN\\" />" >> apk/AndroidManifest.xml
\t@echo "                <category android:name=\\"android.intent.category.LAUNCHER\\" />" >> apk/AndroidManifest.xml
\t@echo "            </intent-filter>" >> apk/AndroidManifest.xml
\t@echo "        </activity>" >> apk/AndroidManifest.xml
\t@echo "    </application>" >> apk/AndroidManifest.xml
\t@echo "</manifest>" >> apk/AndroidManifest.xml

ios_plist:
\t@# Generate iOS Info.plist
\t@echo "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>" > ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "<!DOCTYPE plist PUBLIC \\"-//Apple//DTD PLIST 1.0//EN\\" \\"http://www.apple.com/DTDs/PropertyList-1.0.dtd\\">" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "<plist version=\\"1.0\\">" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "<dict>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "    <key>CFBundleExecutable</key>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "    <string>{self.project_name}</string>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "    <key>CFBundleIdentifier</key>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "    <string>com.agk.{self.project_name}</string>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "    <key>CFBundleName</key>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "    <string>{self.project_name}</string>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "    <key>CFBundleVersion</key>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "    <string>1.0</string>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "    <key>LSRequiresIPhoneOS</key>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "    <true/>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "</dict>" >> ipa/Payload/{self.project_name}.app/Info.plist
\t@echo "</plist>" >> ipa/Payload/{self.project_name}.app/Info.plist

install: $(TARGET)
\t@echo "Installing {self.project_name} for {self.target_platform}..."

help:
\t@echo "Available targets:"
\t@echo "  all      - Build the mobile app"
\t@echo "  apk      - Build Android APK"
\t@echo "  ipa      - Build iOS IPA"
\t@echo "  clean    - Remove build artifacts"
\t@echo "  install  - Install the app"
\t@echo "  help     - Show this help"
"""

        # Write Makefile
        with open(makefile_path, 'w') as f:
            f.write(makefile_content)

        return makefile_path

    def get_android_abi(self) -> str:
        """Get Android ABI for current target architecture"""
        abi_map = {
            "arm": "armeabi-v7a",
            "arm64": "arm64-v8a",
            "x86": "x86",
            "x86_64": "x86_64"
        }
        return abi_map.get(self.target_arch, "arm64-v8a")

    def generate_bare_metal_makefile(self, output_dir: str = ".") -> str:
        """Generate a Makefile for bare-metal builds"""
        makefile_path = os.path.join(output_dir, "Makefile")

        cc = f"{self.cross_compiler_prefix}gcc"
        ld = f"{self.cross_compiler_prefix}ld"
        objcopy = f"{self.cross_compiler_prefix}objcopy"

        cflags = " ".join(self.compiler_flags)
        ldflags = " ".join(self.linker_flags)

        if self.linker_script:
            ldflags += f" -T {self.linker_script}"

        makefile_content = f"""# Generated Bare-Metal Makefile for {self.project_name}
CC = {cc}
LD = {ld}
OBJCOPY = {objcopy}
CFLAGS = {cflags}
LDFLAGS = {ldflags}

TARGET = {self.project_name}
SOURCES = {" ".join([os.path.basename(f) for f in self.source_files])}
OBJECTS = $(SOURCES:.c=.o)

.PHONY: all clean flash

all: $(TARGET).bin

$(TARGET).elf: $(OBJECTS)
\t$(LD) $(LDFLAGS) -o $@ $^

$(TARGET).bin: $(TARGET).elf
\t$(OBJCOPY) -O binary $< $@

%.o: %.c
\t$(CC) $(CFLAGS) -c $< -o $@

clean:
\trm -f $(OBJECTS) $(TARGET).elf $(TARGET).bin

flash: $(TARGET).bin
\t@echo "Flashing $(TARGET).bin to device..."
\t# Add your flashing command here

help:
\t@echo "Available targets:"
\t@echo "  all      - Build the bare-metal binary"
\t@echo "  clean    - Remove build artifacts"
\t@echo "  flash    - Flash the binary to device"
\t@echo "  help     - Show this help"
"""

        # Write Makefile
        with open(makefile_path, 'w') as f:
            f.write(makefile_content)

        return makefile_path


def create_build_system(project_type: str = "application", **kwargs) -> CBuildSystem:
    """Factory function to create appropriate build system"""
    if project_type == "kernel":
        return KernelBuildSystem(**kwargs)
    elif project_type == "bare_metal":
        return BareMetalBuildSystem(**kwargs)
    elif project_type == "mobile":
        return MobileBuildSystem(**kwargs)
    else:
        return CBuildSystem(**kwargs)


# Example usage and testing
if __name__ == "__main__":
    # Create a sample build system
    build_sys = CBuildSystem("sample_app")
    build_sys.add_source_file("main.c")
    build_sys.add_include_dir("/usr/include")
    build_sys.add_library("m")

    # Generate build files
    build_sys.generate_makefile(".")
    build_sys.generate_cmake_lists(".")

    print("Build system files generated successfully!")