"""
Enhanced Dependency Resolution System for AGK Package Manager
Handles complex dependency resolution for external packages
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx
from urllib.parse import urljoin

from agk_package import PackageMetadata, PackageDependency, DependencyType
from agk_registry import PackageRegistry, RemoteRegistry, VersionResolver, PackageInfo
from agk_dependency_manager import (
    DependencyGraph, LibraryDependency, DependencyType as InternalDepType,
    CircularDependencyError, MissingDependencyError, VersionConflictError
)


class ResolutionStrategy(Enum):
    """Dependency resolution strategies"""
    FAST = "fast"  # Fast resolution, may not be optimal
    COMPATIBLE = "compatible"  # Maximize compatibility
    LATEST = "latest"  # Use latest versions
    CONSERVATIVE = "conservative"  # Minimize changes


@dataclass
class ResolvedDependency:
    """Represents a resolved dependency"""
    name: str
    version: str
    source: str = "registry"  # registry, local, git, etc.
    dependencies: List['ResolvedDependency'] = field(default_factory=list)
    metadata: Optional[PackageMetadata] = None
    resolved_at: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())


@dataclass
class DependencyResolution:
    """Complete dependency resolution result"""
    root_package: str
    resolved_dependencies: Dict[str, ResolvedDependency] = field(default_factory=dict)
    conflicts: List[str] = field(default_factory=list)
    unresolved: List[str] = field(default_factory=list)
    resolution_time: float = 0.0
    strategy: ResolutionStrategy = ResolutionStrategy.COMPATIBLE


class DependencyResolver:
    """Advanced dependency resolver for AGK packages"""

    def __init__(self, local_registry: PackageRegistry = None,
                 remote_registry: RemoteRegistry = None,
                 install_dir: str = None):
        self.local_registry = local_registry or PackageRegistry()
        self.remote_registry = remote_registry or RemoteRegistry()
        self.install_dir = Path(install_dir) if install_dir else Path.home() / ".agk" / "packages"

        # Resolution cache
        self._resolution_cache: Dict[str, DependencyResolution] = {}
        self._package_cache: Dict[str, PackageInfo] = {}

        # Conflict resolution preferences
        self.strategy = ResolutionStrategy.COMPATIBLE

    def resolve_package_dependencies(self, package_name: str,
                                   version_spec: str = "*",
                                   strategy: ResolutionStrategy = None) -> DependencyResolution:
        """Resolve all dependencies for a package"""
        if strategy:
            self.strategy = strategy

        cache_key = f"{package_name}@{version_spec}"
        if cache_key in self._resolution_cache:
            return self._resolution_cache[cache_key]

        start_time = __import__('time').time()

        try:
            resolution = self._resolve_dependencies_recursive(package_name, version_spec)
            resolution.resolution_time = __import__('time').time() - start_time
            resolution.strategy = self.strategy

            # Cache result
            self._resolution_cache[cache_key] = resolution
            return resolution

        except Exception as e:
            # Return partial resolution on error
            resolution = DependencyResolution(package_name)
            resolution.unresolved = [package_name]
            resolution.conflicts = [str(e)]
            return resolution

    def _resolve_dependencies_recursive(self, package_name: str,
                                      version_spec: str,
                                      visited: Set[str] = None,
                                      depth: int = 0) -> DependencyResolution:
        """Recursively resolve dependencies"""
        if visited is None:
            visited = set()

        if depth > 50:  # Prevent infinite recursion
            raise RecursionError(f"Maximum dependency depth exceeded for {package_name}")

        resolution = DependencyResolution(package_name)

        # Check for circular dependencies
        if package_name in visited:
            resolution.conflicts.append(f"Circular dependency detected: {package_name}")
            return resolution

        visited.add(package_name)

        try:
            # Get package info
            package_info = self._get_package_info(package_name)
            if not package_info:
                resolution.unresolved.append(package_name)
                return resolution

            # Resolve version
            available_versions = list(package_info.versions.keys())
            resolved_version = VersionResolver.resolve_version(version_spec, available_versions)

            # Create resolved dependency
            resolved_dep = ResolvedDependency(
                name=package_name,
                version=resolved_version,
                metadata=package_info.versions[resolved_version].metadata if resolved_version in package_info.versions else None
            )

            resolution.resolved_dependencies[package_name] = resolved_dep

            # Resolve sub-dependencies
            if resolved_version in package_info.versions:
                version_info = package_info.versions[resolved_version]
                if version_info.metadata:
                    for dep in version_info.metadata.dependencies:
                        if dep.type == DependencyType.REQUIRED:
                            sub_resolution = self._resolve_dependencies_recursive(
                                dep.name, dep.version_spec, visited.copy(), depth + 1
                            )

                            # Merge results
                            resolved_dep.dependencies.extend([
                                sub_resolution.resolved_dependencies[dep_name]
                                for dep_name in sub_resolution.resolved_dependencies
                            ])
                            resolution.conflicts.extend(sub_resolution.conflicts)
                            resolution.unresolved.extend(sub_resolution.unresolved)

                            # Update main resolution
                            resolution.resolved_dependencies.update(sub_resolution.resolved_dependencies)

        except Exception as e:
            resolution.conflicts.append(f"Error resolving {package_name}: {e}")

        finally:
            visited.remove(package_name)

        return resolution

    def _get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """Get package information from cache or registry"""
        if package_name in self._package_cache:
            return self._package_cache[package_name]

        # Try local registry first
        package_info = self.local_registry.get_package(package_name)
        if not package_info:
            # Try remote registry
            package_info = self.remote_registry.get_package(package_name)

        if package_info:
            self._package_cache[package_name] = package_info

        return package_info

    def resolve_from_agk_toml(self, toml_path: str,
                            strategy: ResolutionStrategy = None) -> DependencyResolution:
        """Resolve dependencies from agk.toml file"""
        try:
            from agk_package import PackageConfig
            metadata = PackageConfig.load_from_file(toml_path)

            # Create a mock root dependency
            root_dep = ResolvedDependency(
                name=metadata.name,
                version=metadata.version,
                source="local",
                metadata=metadata
            )

            resolution = DependencyResolution(metadata.name)
            resolution.resolved_dependencies[metadata.name] = root_dep

            # Resolve each dependency
            visited = {metadata.name}
            for dep in metadata.dependencies:
                if dep.type == DependencyType.REQUIRED:
                    sub_resolution = self._resolve_dependencies_recursive(
                        dep.name, dep.version_spec, visited.copy(), 1
                    )

                    root_dep.dependencies.extend([
                        sub_resolution.resolved_dependencies[dep_name]
                        for dep_name in sub_resolution.resolved_dependencies
                    ])
                    resolution.conflicts.extend(sub_resolution.conflicts)
                    resolution.unresolved.extend(sub_resolution.unresolved)
                    resolution.resolved_dependencies.update(sub_resolution.resolved_dependencies)

            resolution.resolution_time = 0.0  # Not measuring time for this method
            resolution.strategy = strategy or self.strategy

            return resolution

        except Exception as e:
            resolution = DependencyResolution("unknown")
            resolution.conflicts = [str(e)]
            return resolution

    def install_resolved_dependencies(self, resolution: DependencyResolution,
                                    dry_run: bool = False) -> List[str]:
        """Install resolved dependencies"""
        installed = []
        failed = []

        # Sort dependencies by depth (install dependencies first)
        def get_depth(dep: ResolvedDependency, visited: Set[str] = None) -> int:
            if visited is None:
                visited = set()
            if dep.name in visited:
                return 0
            visited.add(dep.name)
            if not dep.dependencies:
                return 0
            return 1 + max(get_depth(subdep, visited.copy()) for subdep in dep.dependencies)

        # Get root dependencies (skip the main package)
        root_deps = [dep for dep in resolution.resolved_dependencies.values()
                    if dep.name != resolution.root_package]

        # Sort by installation order
        sorted_deps = sorted(root_deps, key=lambda d: get_depth(d))

        for dep in sorted_deps:
            try:
                if not self.local_registry.is_installed(dep.name, dep.version):
                    if not dry_run:
                        # Install the dependency
                        self._install_dependency(dep)
                    installed.append(f"{dep.name}@{dep.version}")
                else:
                    installed.append(f"{dep.name}@{dep.version} (already installed)")

            except Exception as e:
                failed.append(f"{dep.name}@{dep.version}: {e}")

        return installed if not failed else failed

    def _install_dependency(self, dependency: ResolvedDependency):
        """Install a single dependency"""
        try:
            # Download package
            with tempfile.NamedTemporaryFile(suffix='.agk-pkg', delete=False) as temp_file:
                temp_path = temp_file.name

            try:
                self.remote_registry.download_package(dependency.name, dependency.version, temp_path)

                # Install package
                from agk_package import PackageInstaller
                package_dir = self.install_dir / dependency.name
                metadata = PackageInstaller.install_package(temp_path, str(package_dir))

                # Mark as installed
                self.local_registry.mark_installed(dependency.name, dependency.version, str(package_dir))

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            raise Exception(f"Failed to install {dependency.name}@{dependency.version}: {e}")

    def check_conflicts(self, resolution: DependencyResolution) -> List[str]:
        """Check for version conflicts in resolution"""
        conflicts = []
        version_map = {}

        def collect_versions(dep: ResolvedDependency):
            if dep.name in version_map and version_map[dep.name] != dep.version:
                conflicts.append(f"Version conflict for {dep.name}: {version_map[dep.name]} vs {dep.version}")
            version_map[dep.name] = dep.version

            for subdep in dep.dependencies:
                collect_versions(subdep)

        for dep in resolution.resolved_dependencies.values():
            collect_versions(dep)

        return conflicts

    def get_dependency_tree(self, resolution: DependencyResolution,
                           indent: int = 0) -> str:
        """Generate dependency tree string"""
        def build_tree(dep: ResolvedDependency, level: int = 0) -> str:
            tree_str = "  " * level + f"{dep.name}@{dep.version}"
            if dep.dependencies:
                tree_str += "\n"
                for subdep in dep.dependencies:
                    tree_str += build_tree(subdep, level + 1) + "\n"
            return tree_str.rstrip()

        # Find root dependency
        root_dep = resolution.resolved_dependencies.get(resolution.root_package)
        if not root_dep:
            return "No dependencies resolved"

        return build_tree(root_dep)

    def export_resolution(self, resolution: DependencyResolution,
                         output_file: str):
        """Export dependency resolution to file"""
        data = {
            'root_package': resolution.root_package,
            'strategy': resolution.strategy.value,
            'resolved_dependencies': {
                name: {
                    'name': dep.name,
                    'version': dep.version,
                    'source': dep.source,
                    'dependencies': [d.name for d in dep.dependencies]
                }
                for name, dep in resolution.resolved_dependencies.items()
            },
            'conflicts': resolution.conflicts,
            'unresolved': resolution.unresolved,
            'resolution_time': resolution.resolution_time
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

    def clear_cache(self):
        """Clear resolution and package caches"""
        self._resolution_cache.clear()
        self._package_cache.clear()


# Integration with existing dependency manager
class IntegratedDependencyManager:
    """Integrates old and new dependency systems"""

    def __init__(self, local_registry: PackageRegistry = None):
        from agk_dependency_manager import AGKDependencyManager
        self.old_manager = AGKDependencyManager()
        self.new_resolver = DependencyResolver(local_registry)
        self.local_registry = local_registry or PackageRegistry()

    def resolve_all_dependencies(self, requested_libraries: List[str],
                               package_dependencies: List[PackageDependency] = None) -> Dict[str, Any]:
        """Resolve both internal and external dependencies"""
        result = {
            'internal': [],
            'external': DependencyResolution("combined"),
            'conflicts': [],
            'unresolved': []
        }

        # Resolve internal dependencies
        try:
            internal_deps = self.old_manager.resolve_dependencies(requested_libraries)
            result['internal'] = internal_deps
        except Exception as e:
            result['conflicts'].append(f"Internal dependency error: {e}")

        # Resolve external dependencies
        if package_dependencies:
            for dep in package_dependencies:
                if dep.type == DependencyType.REQUIRED:
                    ext_resolution = self.new_resolver.resolve_package_dependencies(
                        dep.name, dep.version_spec
                    )

                    # Merge external dependencies
                    result['external'].resolved_dependencies.update(ext_resolution.resolved_dependencies)
                    result['external'].conflicts.extend(ext_resolution.conflicts)
                    result['external'].unresolved.extend(ext_resolution.unresolved)

        # Check for conflicts between internal and external
        internal_names = set(result['internal'])
        external_names = set(result['external'].resolved_dependencies.keys())

        overlap = internal_names & external_names
        if overlap:
            result['conflicts'].append(f"Name conflicts between internal and external dependencies: {overlap}")

        return result


# Command-line interface for dependency resolution
def resolve_dependencies_cli():
    """CLI interface for dependency resolution"""
    import argparse

    parser = argparse.ArgumentParser(description="AGK Dependency Resolver")
    parser.add_argument('package', help='Package name or agk.toml file')
    parser.add_argument('--version', help='Package version specification')
    parser.add_argument('--strategy', choices=['fast', 'compatible', 'latest', 'conservative'],
                       default='compatible', help='Resolution strategy')
    parser.add_argument('--install', action='store_true', help='Install resolved dependencies')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be installed')
    parser.add_argument('--export', help='Export resolution to file')

    args = parser.parse_args()

    resolver = DependencyResolver()

    # Determine strategy
    strategy_map = {
        'fast': ResolutionStrategy.FAST,
        'compatible': ResolutionStrategy.COMPATIBLE,
        'latest': ResolutionStrategy.LATEST,
        'conservative': ResolutionStrategy.CONSERVATIVE
    }
    strategy = strategy_map[args.strategy]

    if args.package.endswith('.toml'):
        # Resolve from agk.toml
        resolution = resolver.resolve_from_agk_toml(args.package, strategy)
    else:
        # Resolve package from registry
        version_spec = args.version or "*"
        resolution = resolver.resolve_package_dependencies(args.package, version_spec, strategy)

    print(f"Dependency Resolution for {args.package}")
    print("=" * 40)

    if resolution.resolved_dependencies:
        print(f"\nResolved Dependencies ({len(resolution.resolved_dependencies)}):")
        for name, dep in resolution.resolved_dependencies.items():
            print(f"  {name}@{dep.version}")

        print(f"\nDependency Tree:\n{resolver.get_dependency_tree(resolution)}")

    if resolution.conflicts:
        print(f"\nConflicts ({len(resolution.conflicts)}):")
        for conflict in resolution.conflicts:
            print(f"  ERROR: {conflict}")

    if resolution.unresolved:
        print(f"\nUnresolved ({len(resolution.unresolved)}):")
        for unresolved in resolution.unresolved:
            print(f"  WARNING: {unresolved}")

    print(f"Resolution time: {resolution.resolution_time:.3f}s")

    if args.install or args.dry_run:
        print(f"\nInstallation ({'DRY RUN' if args.dry_run else 'LIVE'}):")
        installed = resolver.install_resolved_dependencies(resolution, dry_run=args.dry_run)

        for item in installed:
            print(f"  {item}")

    if args.export:
        resolver.export_resolution(resolution, args.export)
        print(f"\nResolution exported to: {args.export}")


if __name__ == "__main__":
    resolve_dependencies_cli()