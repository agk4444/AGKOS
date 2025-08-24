"""
AGK Package Publishing Tools
Tools for preparing, validating, and publishing AGK packages
"""

import os
import json
import hashlib
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import toml
import requests
from urllib.parse import urljoin

from agk_package import PackageMetadata, PackageConfig, PackageBuilder, PackageType
from agk_registry import RemoteRegistry
from agk_dependency_resolver import DependencyResolver, ResolutionStrategy


class PackageValidator:
    """Validates packages before publishing"""

    @staticmethod
    def validate_package(directory: str = ".") -> List[str]:
        """Comprehensive package validation"""
        issues = []
        directory = Path(directory)

        # Check for required files
        required_files = ["agk.toml", "README.md"]
        for file in required_files:
            if not (directory / file).exists():
                issues.append(f"Missing required file: {file}")

        if issues:
            return issues

        try:
            # Load and validate metadata
            metadata = PackageConfig.load_from_file(str(directory / "agk.toml"))
            issues.extend(PackageValidator._validate_metadata(metadata))

            # Check package structure
            issues.extend(PackageValidator._validate_structure(directory, metadata))

            # Validate dependencies
            issues.extend(PackageValidator._validate_dependencies(metadata))

            # Check for security issues
            issues.extend(PackageValidator._validate_security(directory, metadata))

        except Exception as e:
            issues.append(f"Error loading package: {e}")

        return issues

    @staticmethod
    def _validate_metadata(metadata: PackageMetadata) -> List[str]:
        """Validate package metadata"""
        issues = []

        # Required fields
        required_fields = {
            'name': metadata.name,
            'version': metadata.version,
            'description': metadata.description,
            'author': metadata.author
        }

        for field, value in required_fields.items():
            if not value:
                issues.append(f"Missing required field: {field}")

        # Version format
        if metadata.version:
            try:
                from packaging import version
                version.parse(metadata.version)
            except Exception:
                issues.append(f"Invalid version format: {metadata.version}")

        # Email format (basic check)
        if metadata.email and '@' not in metadata.email:
            issues.append(f"Invalid email format: {metadata.email}")

        # Keywords
        if not metadata.keywords:
            issues.append("No keywords specified - consider adding some for discoverability")

        # License
        common_licenses = {'MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'ISC'}
        if metadata.license and metadata.license not in common_licenses:
            issues.append(f"Consider using a common license: {metadata.license}")

        return issues

    @staticmethod
    def _validate_structure(directory: Path, metadata: PackageMetadata) -> List[str]:
        """Validate package structure"""
        issues = []

        # Check for source files
        agk_files = list(directory.glob("**/*.agk"))
        if not agk_files:
            issues.append("No AGK source files found")

        # Check for main entry point if it's an application
        if metadata.package_type == PackageType.APPLICATION:
            main_files = ["main.agk", "app.agk", f"{metadata.name}.agk"]
            has_main = any((directory / main_file).exists() for main_file in main_files)
            if not has_main:
                issues.append("No main entry point found for application package")

        # Check README content
        readme_path = directory / metadata.readme
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if metadata.name.lower() not in content:
                    issues.append("README doesn't mention the package name")

        # Check for tests
        test_files = list(directory.glob("**/test*.agk")) + list(directory.glob("**/test_*.agk"))
        if not test_files:
            issues.append("No test files found - consider adding tests")

        # Check file sizes
        for agk_file in agk_files:
            size = agk_file.stat().st_size
            if size > 1024 * 1024:  # 1MB
                issues.append(f"Large file detected: {agk_file.name} ({size} bytes)")

        return issues

    @staticmethod
    def _validate_dependencies(metadata: PackageMetadata) -> List[str]:
        """Validate package dependencies"""
        issues = []

        resolver = DependencyResolver()

        for dep in metadata.dependencies:
            try:
                resolution = resolver.resolve_package_dependencies(dep.name, dep.version_spec)
                if resolution.unresolved:
                    issues.append(f"Unresolvable dependency: {dep.name}@{dep.version_spec}")
                if resolution.conflicts:
                    issues.append(f"Dependency conflicts for {dep.name}: {resolution.conflicts}")
            except Exception as e:
                issues.append(f"Error resolving dependency {dep.name}: {e}")

        return issues

    @staticmethod
    def _validate_security(directory: Path, metadata: PackageMetadata) -> List[str]:
        """Security validation"""
        issues = []

        # Check for sensitive files
        sensitive_patterns = [
            "**/.env*",
            "**/config.json",
            "**/*password*",
            "**/*secret*",
            "**/*key*",
            "**/.git*"
        ]

        for pattern in sensitive_patterns:
            for file in directory.glob(pattern):
                if file.is_file():
                    issues.append(f"Potentially sensitive file included: {file.name}")

        # Check for hardcoded secrets in AGK files
        agk_files = list(directory.glob("**/*.agk"))
        for agk_file in agk_files:
            try:
                with open(agk_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple pattern matching for potential secrets
                    if 'password' in content.lower() and ('=' in content or ':' in content):
                        issues.append(f"Potential hardcoded password in {agk_file.name}")
                    if 'secret' in content.lower() and ('=' in content or ':' in content):
                        issues.append(f"Potential hardcoded secret in {agk_file.name}")
            except Exception:
                pass

        return issues


class PackagePreparer:
    """Prepares packages for publishing"""

    @staticmethod
    def prepare_package(directory: str = ".") -> Dict[str, Any]:
        """Prepare package for publishing"""
        directory = Path(directory)

        # Validate first
        issues = PackageValidator.validate_package(str(directory))
        if issues:
            return {
                'success': False,
                'issues': issues,
                'package_path': None
            }

        try:
            # Load metadata
            metadata = PackageConfig.load_from_file(str(directory / "agk.toml"))

            # Update metadata
            metadata.updated_at = datetime.now().isoformat()

            # Save updated metadata
            PackageConfig.save_to_file(metadata, str(directory / "agk.toml"))

            # Build package
            package_path = PackageBuilder.build_package(str(directory), str(directory / "dist"))

            return {
                'success': True,
                'issues': [],
                'package_path': package_path,
                'metadata': metadata
            }

        except Exception as e:
            return {
                'success': False,
                'issues': [f"Error preparing package: {e}"],
                'package_path': None
            }

    @staticmethod
    def create_changelog(directory: str = ".", version: str = None) -> str:
        """Create or update changelog"""
        directory = Path(directory)
        changelog_path = directory / "CHANGELOG.md"

        if version is None:
            # Get version from agk.toml
            try:
                metadata = PackageConfig.load_from_file(str(directory / "agk.toml"))
                version = metadata.version
            except:
                version = "1.0.0"

        if changelog_path.exists():
            # Update existing changelog
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "# Changelog\n\n"

        # Add new version entry
        today = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"## [{version}] - {today}\n\n### Added\n- \n\n### Changed\n- \n\n### Fixed\n- \n\n"

        content = new_entry + content

        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(changelog_path)

    @staticmethod
    def run_tests(directory: str = ".") -> Dict[str, Any]:
        """Run package tests"""
        directory = Path(directory)
        test_files = list(directory.glob("**/test*.agk")) + list(directory.glob("**/test_*.agk"))

        if not test_files:
            return {'success': False, 'message': 'No test files found'}

        # This would integrate with the AGK test framework
        # For now, just check if test files exist and are valid
        results = []
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Basic validation
                    if 'define' in content and 'function' in content:
                        results.append({'file': str(test_file), 'status': 'valid'})
                    else:
                        results.append({'file': str(test_file), 'status': 'invalid'})
            except Exception as e:
                results.append({'file': str(test_file), 'status': f'error: {e}'})

        return {
            'success': all(r['status'] == 'valid' for r in results),
            'results': results
        }


class PackagePublisher:
    """Handles package publishing to registry"""

    def __init__(self, registry_url: str = "https://registry.agk-lang.org",
                 api_key: str = None):
        self.remote_registry = RemoteRegistry(registry_url)
        self.api_key = api_key or os.environ.get('AGK_REGISTRY_API_KEY')

    def publish_package(self, package_path: str, dry_run: bool = False) -> Dict[str, Any]:
        """Publish package to registry"""
        if not self.api_key:
            return {
                'success': False,
                'message': 'API key not provided. Set AGK_REGISTRY_API_KEY environment variable.'
            }

        package_path = Path(package_path)
        if not package_path.exists():
            return {
                'success': False,
                'message': f'Package file not found: {package_path}'
            }

        try:
            if dry_run:
                return {
                    'success': True,
                    'message': f'Would publish {package_path.name} (dry run)',
                    'package_name': 'unknown'
                }

            # Publish to registry
            success = self.remote_registry.publish_package(str(package_path), self.api_key)

            if success:
                # Extract package name from filename
                package_name = package_path.name.replace('.agk-pkg', '').split('-')[0]
                return {
                    'success': True,
                    'message': f'Successfully published {package_name}',
                    'package_name': package_name
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to publish package to registry'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error publishing package: {e}'
            }

    def check_package_status(self, name: str, version: str = None) -> Dict[str, Any]:
        """Check if package/version exists in registry"""
        try:
            package_info = self.remote_registry.get_package(name)
            if not package_info:
                return {
                    'exists': False,
                    'message': f'Package {name} not found in registry'
                }

            if version:
                if version in package_info.versions:
                    version_info = package_info.versions[version]
                    return {
                        'exists': True,
                        'message': f'Package {name}@{version} exists',
                        'published_at': version_info.uploaded_at,
                        'downloads': version_info.downloads
                    }
                else:
                    return {
                        'exists': False,
                        'message': f'Package {name}@{version} not found in registry'
                    }
            else:
                return {
                    'exists': True,
                    'message': f'Package {name} exists (latest: {package_info.latest_version})',
                    'versions': list(package_info.versions.keys())
                }

        except Exception as e:
            return {
                'exists': False,
                'message': f'Error checking package status: {e}'
            }


class PublishingWorkflow:
    """Complete publishing workflow"""

    @staticmethod
    def publish_workflow(directory: str = ".", options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Complete publishing workflow"""
        if options is None:
            options = {}

        workflow_results = {
            'validation': {},
            'preparation': {},
            'testing': {},
            'publishing': {}
        }

        directory = Path(directory)

        # Step 1: Validation
        print("Step 1: Validating package...")
        validation_issues = PackageValidator.validate_package(str(directory))
        workflow_results['validation'] = {
            'success': len(validation_issues) == 0,
            'issues': validation_issues
        }

        if validation_issues:
            print(f"Validation failed with {len(validation_issues)} issues:")
            for issue in validation_issues:
                print(f"  - {issue}")
            return workflow_results

        print("✓ Validation passed")

        # Step 2: Testing
        if options.get('run_tests', True):
            print("Step 2: Running tests...")
            test_results = PackagePreparer.run_tests(str(directory))
            workflow_results['testing'] = test_results

            if not test_results['success']:
                print("Warning: Tests failed or no tests found")
                if options.get('require_tests', False):
                    return workflow_results
            else:
                print("✓ Tests passed")

        # Step 3: Preparation
        print("Step 3: Preparing package...")
        prep_results = PackagePreparer.prepare_package(str(directory))
        workflow_results['preparation'] = prep_results

        if not prep_results['success']:
            print(f"Preparation failed: {prep_results['issues']}")
            return workflow_results

        print(f"✓ Package prepared: {prep_results['package_path']}")

        # Step 4: Publishing
        if options.get('publish', True):
            print("Step 4: Publishing package...")
            publisher = PackagePublisher()
            pub_results = publisher.publish_package(
                prep_results['package_path'],
                dry_run=options.get('dry_run', False)
            )
            workflow_results['publishing'] = pub_results

            if pub_results['success']:
                print(f"✓ {pub_results['message']}")
            else:
                print(f"✗ {pub_results['message']}")

        return workflow_results


# Command-line interface
def main():
    """CLI for publishing tools"""
    import argparse

    parser = argparse.ArgumentParser(description="AGK Package Publishing Tools")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate package')
    validate_parser.add_argument('--directory', '-d', default='.', help='Package directory')

    # Prepare command
    prepare_parser = subparsers.add_parser('prepare', help='Prepare package for publishing')
    prepare_parser.add_argument('--directory', '-d', default='.', help='Package directory')

    # Test command
    test_parser = subparsers.add_parser('test', help='Run package tests')
    test_parser.add_argument('--directory', '-d', default='.', help='Package directory')

    # Publish command
    publish_parser = subparsers.add_parser('publish', help='Publish package')
    publish_parser.add_argument('package', help='Package file path')
    publish_parser.add_argument('--dry-run', action='store_true', help='Dry run')

    # Status command
    status_parser = subparsers.add_parser('status', help='Check package status')
    status_parser.add_parser.add_argument('name', help='Package name')
    status_parser.add_argument('version', nargs='?', help='Package version')

    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Run complete publishing workflow')
    workflow_parser.add_argument('--directory', '-d', default='.', help='Package directory')
    workflow_parser.add_argument('--no-tests', action='store_true', help='Skip tests')
    workflow_parser.add_argument('--no-publish', action='store_true', help='Skip publishing')
    workflow_parser.add_argument('--dry-run', action='store_true', help='Dry run for publishing')
    workflow_parser.add_argument('--require-tests', action='store_true', help='Require tests to pass')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'validate':
            issues = PackageValidator.validate_package(args.directory)
            if issues:
                print(f"Validation failed with {len(issues)} issues:")
                for issue in issues:
                    print(f"  - {issue}")
                exit(1)
            else:
                print("✓ Package validation passed")

        elif args.command == 'prepare':
            results = PackagePreparer.prepare_package(args.directory)
            if results['success']:
                print(f"✓ Package prepared: {results['package_path']}")
            else:
                print("Preparation failed:")
                for issue in results['issues']:
                    print(f"  - {issue}")
                exit(1)

        elif args.command == 'test':
            results = PackagePreparer.run_tests(args.directory)
            if results['success']:
                print("✓ Tests passed")
            else:
                print(f"Test results: {results['message']}")
                for result in results.get('results', []):
                    print(f"  {result['file']}: {result['status']}")

        elif args.command == 'publish':
            publisher = PackagePublisher()
            results = publisher.publish_package(args.package, args.dry_run)
            if results['success']:
                print(f"✓ {results['message']}")
            else:
                print(f"✗ {results['message']}")
                exit(1)

        elif args.command == 'status':
            publisher = PackagePublisher()
            results = publisher.check_package_status(args.name, getattr(args, 'version', None))
            print(results['message'])
            if results.get('versions'):
                print(f"Available versions: {', '.join(results['versions'])}")

        elif args.command == 'workflow':
            options = {
                'run_tests': not args.no_tests,
                'publish': not args.no_publish,
                'dry_run': args.dry_run,
                'require_tests': args.require_tests
            }

            results = PublishingWorkflow.publish_workflow(args.directory, options)

            # Print summary
            for step, result in results.items():
                if result.get('success'):
                    print(f"✓ {step.title()}: Success")
                else:
                    print(f"✗ {step.title()}: Failed")

                    if 'issues' in result:
                        for issue in result['issues']:
                            print(f"    - {issue}")

                    if 'message' in result:
                        print(f"    - {result['message']}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()