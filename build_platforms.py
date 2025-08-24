#!/usr/bin/env python3
"""
AGK Cross-Platform Build Script

Compiles AGK source files for multiple target platforms simultaneously.
"""

import os
import sys
import subprocess
from pathlib import Path

class PlatformBuilder:
    """Builds AGK applications for multiple platforms"""

    # Platform configurations
    PLATFORMS = {
        "python": {
            "name": "Python",
            "extension": ".py",
            "description": "Standard Python application"
        },
        "javascript": {
            "name": "JavaScript",
            "extension": ".js",
            "description": "Web browser application"
        },
        "kotlin": {
            "name": "Kotlin",
            "extension": ".kt",
            "description": "Android/Kotlin application"
        },
        "swift": {
            "name": "Swift",
            "extension": ".swift",
            "description": "iOS/Swift application"
        },
        "cpp": {
            "name": "C++",
            "extension": ".cpp",
            "description": "C++ application"
        },
        "csharp": {
            "name": "C#",
            "extension": ".cs",
            "description": "C#/.NET application"
        },
        "wearable": {
            "name": "Wearable",
            "extension": ".py",
            "description": "Wearable device application"
        },
        "tv": {
            "name": "TV",
            "extension": ".py",
            "description": "Smart TV application"
        },
        "automotive": {
            "name": "Automotive",
            "extension": ".py",
            "description": "Automotive infotainment application"
        }
    }

    def __init__(self):
        self.compiler_path = "agk_compiler.py"
        self.output_dir = "build"

    def build_all_platforms(self, source_file: str, output_prefix: str = None):
        """Build for all available platforms"""
        if not os.path.exists(source_file):
            print(f"ERROR: Source file '{source_file}' not found")
            return False

        if output_prefix is None:
            output_prefix = Path(source_file).stem

        print(f"Building {source_file} for all platforms...")
        print("=" * 60)

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        success_count = 0
        total_count = len(self.PLATFORMS)

        for platform, config in self.PLATFORMS.items():
            print(f"\nBuilding for {config['name']} ({platform})...")

            output_file = f"{self.output_dir}/{output_prefix}_{platform}{config['extension']}"

            if self.build_platform(source_file, platform, output_file):
                success_count += 1
                print(f"✅ {config['name']} build successful")
            else:
                print(f"❌ {config['name']} build failed")

        print(f"\n{'='*60}")
        print(f"Build Summary: {success_count}/{total_count} platforms successful")

        if success_count == total_count:
            print("🎉 All platforms built successfully!")
        elif success_count > 0:
            print(f"⚠️  Partial success: {success_count} platforms built")
        else:
            print("💥 All builds failed")

        return success_count > 0

    def build_platform(self, source_file: str, platform: str, output_file: str = None):
        """Build for a specific platform"""
        if platform not in self.PLATFORMS:
            print(f"ERROR: Unknown platform '{platform}'")
            return False

        if output_file is None:
            output_file = f"{Path(source_file).stem}_{platform}{self.PLATFORMS[platform]['extension']}"

        try:
            # Run the AGK compiler with platform flag
            cmd = [
                sys.executable,
                self.compiler_path,
                source_file,
                output_file,
                "--platform",
                platform
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True
            else:
                print(f"Build failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"Build timeout for platform {platform}")
            return False
        except Exception as e:
            print(f"Build error: {e}")
            return False

    def list_platforms(self):
        """List all available platforms"""
        print("Available Platforms:")
        print("=" * 40)

        for platform, config in self.PLATFORMS.items():
            print(f"{platform:12} - {config['name']:15} ({config['description']})")

    def clean_builds(self):
        """Clean build directory"""
        if os.path.exists(self.output_dir):
            import shutil
            shutil.rmtree(self.output_dir)
            print(f"Cleaned build directory: {self.output_dir}")
        else:
            print("Build directory already clean")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python build_platforms.py <command> [args...]")
        print("Commands:")
        print("  build <source_file> [output_prefix]  - Build for all platforms")
        print("  platform <source_file> <platform>   - Build for specific platform")
        print("  list                                 - List available platforms")
        print("  clean                                - Clean build directory")
        sys.exit(1)

    builder = PlatformBuilder()
    command = sys.argv[1]

    if command == "build":
        if len(sys.argv) < 3:
            print("ERROR: build command requires source file")
            sys.exit(1)

        source_file = sys.argv[2]
        output_prefix = sys.argv[3] if len(sys.argv) > 3 else None

        success = builder.build_all_platforms(source_file, output_prefix)
        sys.exit(0 if success else 1)

    elif command == "platform":
        if len(sys.argv) < 4:
            print("ERROR: platform command requires source file and platform")
            sys.exit(1)

        source_file = sys.argv[2]
        platform = sys.argv[3]

        success = builder.build_platform(source_file, platform)
        sys.exit(0 if success else 1)

    elif command == "list":
        builder.list_platforms()

    elif command == "clean":
        builder.clean_builds()

    else:
        print(f"ERROR: Unknown command '{command}'")
        sys.exit(1)

if __name__ == "__main__":
    main()