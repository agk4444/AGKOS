#!/usr/bin/env python3
"""
AGK Package Manager - Command Line Tool
Usage: agk-pkg [command] [options]
"""

import os
import sys
import json
import argparse
import tempfile
from pathlib import Path
from typing import List, Optional
import toml

from agk_package import PackageMetadata, PackageConfig, PackageBuilder, PackageInstaller
from agk_registry import PackageRegistry, RemoteRegistry, VersionResolver


class AGKPackageManager:
    """Main package manager class"""

    def __init__(self):
        self.local_registry = PackageRegistry()
        self.remote_registry = RemoteRegistry()
        self.install_dir = Path.home() / ".agk" / "packages"
        self.install_dir.mkdir(parents=True, exist_ok=True)

    def init_package(self, name: str = None, directory: str = "."):
        """Initialize a new package"""
        if name is None:
            # Use directory name
            name = Path(directory).name.lower().replace("-", "_").replace(" ", "_")

        config_path = Path(directory) / "agk.toml"

        if config_path.exists():
            print(f"Package already initialized at {config_path}")
            return

        # Create default package configuration
        metadata = PackageConfig.create_default_config(name)

        # Try to get user info from environment
        if os.environ.get('AGK_AUTHOR'):
            metadata.author = os.environ['AGK_AUTHOR']
        if os.environ.get('AGK_EMAIL'):
            metadata.email = os.environ['AGK_EMAIL']

        # Save configuration
        PackageConfig.save_to_file(metadata, str(config_path))

        # Create basic directory structure
        pkg_dir = Path(directory)
        (pkg_dir / "src").mkdir(exist_ok=True)
        (pkg_dir / "tests").mkdir(exist_ok=True)

        # Create README
        readme_path = pkg_dir / "README.md"
        if not readme_path.exists():
            with open(readme_path, 'w') as f:
                f.write(f"# {name}\n\n{metadata.description}\n\n## Installation\n\n```\nagk-pkg install {name}\n```\n")

        print(f"Package '{name}' initialized at {config_path}")
        print("\nNext steps:")
        print("1. Edit agk.toml to configure your package")
        print("2. Add your source files to the src/ directory")
        print("3. Run 'agk-pkg build' to build your package")
        print("4. Run 'agk-pkg publish' to publish to the registry")

    def build_package(self, source_dir: str = "."):
        """Build a package for distribution"""
        source_path = Path(source_dir)

        if not (source_path / "agk.toml").exists():
            print("Error: No agk.toml found. Run 'agk-pkg init' first.")
            return

        try:
            # Build package
            output_dir = source_path / "dist"
            output_dir.mkdir(exist_ok=True)

            package_path = PackageBuilder.build_package(str(source_path), str(output_dir))
            print(f"Package built successfully: {package_path}")

        except Exception as e:
            print(f"Error building package: {e}")

    def install_package(self, package_spec: str, version: str = None):
        """Install a package"""
        if "/" in package_spec or "\\" in package_spec:
            # Local package file
            self._install_local_package(package_spec)
        else:
            # Package from registry
            self._install_remote_package(package_spec, version)

    def _install_local_package(self, package_path: str):
        """Install package from local file"""
        try:
            # Install package
            metadata = PackageInstaller.install_package(package_path, str(self.install_dir))

            # Mark as installed in local registry
            package_dir = self.install_dir / metadata.name
            self.local_registry.mark_installed(metadata.name, metadata.version, str(package_dir))

            print(f"Successfully installed {metadata.name}@{metadata.version}")

        except Exception as e:
            print(f"Error installing package: {e}")

    def _install_remote_package(self, name: str, version: str = None):
        """Install package from remote registry"""
        try:
            # Get package info
            package_info = self.remote_registry.get_package(name)
            if not package_info:
                print(f"Package '{name}' not found in registry")
                return

            # Resolve version
            if version is None or version == "latest":
                version = package_info.latest_version

            if version not in package_info.versions:
                available_versions = list(package_info.versions.keys())
                version = VersionResolver.resolve_version(version, available_versions)

            # Check if already installed
            if self.local_registry.is_installed(name, version):
                print(f"Package {name}@{version} is already installed")
                return

            # Download package
            print(f"Downloading {name}@{version}...")
            with tempfile.NamedTemporaryFile(suffix='.agk-pkg', delete=False) as temp_file:
                temp_path = temp_file.name

            try:
                self.remote_registry.download_package(name, version, temp_path)
                print("Download complete, installing...")

                # Install package
                package_dir = self.install_dir / name
                metadata = PackageInstaller.install_package(temp_path, str(package_dir))

                # Mark as installed
                self.local_registry.mark_installed(name, version, str(package_dir))

                print(f"Successfully installed {name}@{version}")

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            print(f"Error installing package: {e}")

    def uninstall_package(self, name: str, version: str = None):
        """Uninstall a package"""
        try:
            if version is None:
                # Find installed version
                installed = self.local_registry.list_installed_packages()
                for pkg_name, pkg_version, install_path in installed:
                    if pkg_name == name:
                        version = pkg_version
                        break

            if not version:
                print(f"Package '{name}' is not installed")
                return

            # Remove package files
            package_dir = self.install_dir / name
            if package_dir.exists():
                import shutil
                shutil.rmtree(package_dir)

            # Mark as uninstalled
            self.local_registry.mark_uninstalled(name, version)

            print(f"Successfully uninstalled {name}@{version}")

        except Exception as e:
            print(f"Error uninstalling package: {e}")

    def search_packages(self, query: str, limit: int = 20):
        """Search for packages"""
        try:
            # Search local registry first
            local_results = self.local_registry.search_packages(query, limit)

            # Search remote registry
            remote_results = self.remote_registry.search_packages(query, limit)

            # Combine results, preferring remote results
            all_packages = {pkg.name: pkg for pkg in remote_results}
            for pkg in local_results:
                if pkg.name not in all_packages:
                    all_packages[pkg.name] = pkg

            results = list(all_packages.values())[:limit]

            if not results:
                print(f"No packages found matching '{query}'")
                return

            print(f"\nFound {len(results)} package(s):\n")

            for pkg in results:
                installed_marker = ""
                if self.local_registry.is_installed(pkg.name):
                    installed_marker = " [installed]"

                print(f"{pkg.name}@{pkg.latest_version}")
                print(f"  {pkg.description}")
                print(f"  by {pkg.author} ({pkg.email})")
                print(f"  {pkg.homepage}")
                print(f"  Keywords: {', '.join(pkg.keywords)}{installed_marker}")
                print()

        except Exception as e:
            print(f"Error searching packages: {e}")

    def list_installed(self):
        """List installed packages"""
        try:
            installed = self.local_registry.list_installed_packages()

            if not installed:
                print("No packages installed")
                return

            print("\nInstalled packages:\n")

            for name, version, install_path in installed:
                print(f"{name}@{version}")
                print(f"  Location: {install_path}")
                print()

        except Exception as e:
            print(f"Error listing installed packages: {e}")

    def show_package_info(self, name: str):
        """Show detailed package information"""
        try:
            # Try local registry first
            package_info = self.local_registry.get_package(name)

            if not package_info:
                # Try remote registry
                package_info = self.remote_registry.get_package(name)

            if not package_info:
                print(f"Package '{name}' not found")
                return

            print(f"\n{name}")
            print("=" * len(name))
            print(f"Description: {package_info.description}")
            print(f"Author: {package_info.author}")
            print(f"Email: {package_info.email}")
            print(f"License: {package_info.license}")
            print(f"Homepage: {package_info.homepage}")
            print(f"Repository: {package_info.repository}")
            print(f"Type: {package_info.package_type.value}")
            print(f"Keywords: {', '.join(package_info.keywords)}")
            print(f"Latest Version: {package_info.latest_version}")
            print(f"Created: {package_info.created_at}")
            print(f"Total Downloads: {package_info.total_downloads}")
            print(f"Verified: {'Yes' if package_info.verified else 'No'}")

            if package_info.versions:
                print("\nVersions:")
                for version, version_info in sorted(package_info.versions.items()):
                    print(f"  {version} ({version_info.uploaded_at})")
                    print(f"    Downloads: {version_info.downloads}")
                    print(f"    Size: {version_info.size} bytes")

            # Check if installed
            if self.local_registry.is_installed(name):
                print("\nStatus: Installed")
            else:
                print("\nStatus: Not installed")

        except Exception as e:
            print(f"Error showing package info: {e}")

    def publish_package(self, package_path: str = None):
        """Publish a package to the registry"""
        try:
            if package_path is None:
                # Look for package in dist/ directory
                dist_dir = Path("dist")
                if not dist_dir.exists():
                    print("Error: No dist/ directory found. Run 'agk-pkg build' first.")
                    return

                packages = list(dist_dir.glob("*.agk-pkg"))
                if not packages:
                    print("Error: No package files found in dist/ directory")
                    return

                if len(packages) > 1:
                    print("Multiple packages found:")
                    for i, pkg in enumerate(packages):
                        print(f"  {i + 1}. {pkg.name}")
                    choice = input("Select package to publish (1-n): ")
                    package_path = str(packages[int(choice) - 1])
                else:
                    package_path = str(packages[0])
            else:
                package_path = Path(package_path)

            # Get API key
            api_key = os.environ.get('AGK_REGISTRY_API_KEY')
            if not api_key:
                print("Error: AGK_REGISTRY_API_KEY environment variable not set")
                print("Please set your API key: export AGK_REGISTRY_API_KEY=your_key_here")
                return

            print(f"Publishing {package_path}...")

            # Publish to registry
            success = self.remote_registry.publish_package(str(package_path), api_key)

            if success:
                print("Package published successfully!")
            else:
                print("Failed to publish package")

        except Exception as e:
            print(f"Error publishing package: {e}")

    def validate_package(self, directory: str = "."):
        """Validate package configuration"""
        try:
            config_path = Path(directory) / "agk.toml"

            if not config_path.exists():
                print("Error: No agk.toml found")
                return

            # Load and validate configuration
            metadata = PackageConfig.load_from_file(str(config_path))

            print(f"Package: {metadata.name}")
            print(f"Version: {metadata.version}")
            print("Configuration is valid!")

            # Check for common issues
            issues = []

            if not metadata.description:
                issues.append("Missing description")

            if not metadata.author:
                issues.append("Missing author")

            if not metadata.keywords:
                issues.append("No keywords specified")

            if issues:
                print("\nSuggestions:")
                for issue in issues:
                    print(f"  - {issue}")

        except Exception as e:
            print(f"Error validating package: {e}")


def create_argument_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="AGK Package Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agk-pkg init my-package           # Initialize new package
  agk-pkg build                     # Build package
  agk-pkg install my-package        # Install package
  agk-pkg install my-package@1.0.0  # Install specific version
  agk-pkg search web                # Search for packages
  agk-pkg list                      # List installed packages
  agk-pkg info my-package           # Show package info
  agk-pkg uninstall my-package      # Uninstall package
  agk-pkg publish                   # Publish package
  agk-pkg validate                  # Validate package config
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new package')
    init_parser.add_argument('name', nargs='?', help='Package name')
    init_parser.add_argument('--directory', '-d', default='.', help='Target directory')

    # Build command
    build_parser = subparsers.add_parser('build', help='Build package for distribution')
    build_parser.add_argument('--source-dir', '-s', default='.', help='Source directory')

    # Install command
    install_parser = subparsers.add_parser('install', help='Install a package')
    install_parser.add_argument('package', help='Package name or path')
    install_parser.add_argument('version', nargs='?', help='Package version')

    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a package')
    uninstall_parser.add_argument('package', help='Package name')
    uninstall_parser.add_argument('version', nargs='?', help='Package version')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for packages')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', '-l', type=int, default=20, help='Maximum results')

    # List command
    subparsers.add_parser('list', help='List installed packages')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show package information')
    info_parser.add_argument('package', help='Package name')

    # Publish command
    publish_parser = subparsers.add_parser('publish', help='Publish package to registry')
    publish_parser.add_argument('package', nargs='?', help='Package file path')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate package configuration')
    validate_parser.add_argument('--directory', '-d', default='.', help='Package directory')

    return parser


def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Create package manager
    pkg_manager = AGKPackageManager()

    try:
        if args.command == 'init':
            pkg_manager.init_package(args.name, args.directory)

        elif args.command == 'build':
            pkg_manager.build_package(args.source_dir)

        elif args.command == 'install':
            # Handle version specification in package name
            package_spec = args.package
            version = args.version

            if '@' in package_spec and version is None:
                package_spec, version = package_spec.split('@', 1)

            pkg_manager.install_package(package_spec, version)

        elif args.command == 'uninstall':
            pkg_manager.uninstall_package(args.package, args.version)

        elif args.command == 'search':
            pkg_manager.search_packages(args.query, args.limit)

        elif args.command == 'list':
            pkg_manager.list_installed()

        elif args.command == 'info':
            pkg_manager.show_package_info(args.package)

        elif args.command == 'publish':
            pkg_manager.publish_package(args.package)

        elif args.command == 'validate':
            pkg_manager.validate_package(args.directory)

    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()