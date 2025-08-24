"""
AGK Package Management System
Handles package metadata, installation, and distribution
"""

import os
import json
import hashlib
import tarfile
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field, asdict
import toml
from enum import Enum


class PackageType(Enum):
    """Types of AGK packages"""
    LIBRARY = "library"
    APPLICATION = "application"
    TEMPLATE = "template"
    TOOL = "tool"


class DependencyType(Enum):
    """Types of package dependencies"""
    REQUIRED = "required"
    OPTIONAL = "optional"
    DEVELOPMENT = "development"
    PEER = "peer"


@dataclass
class PackageDependency:
    """Represents a package dependency"""
    name: str
    version_spec: str = "*"
    type: DependencyType = DependencyType.REQUIRED
    description: str = ""
    repository: str = ""


@dataclass
class PackageMetadata:
    """Complete package metadata"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    email: str = ""
    license: str = "MIT"
    homepage: str = ""
    repository: str = ""
    keywords: List[str] = field(default_factory=list)
    package_type: PackageType = PackageType.LIBRARY
    dependencies: List[PackageDependency] = field(default_factory=list)
    dev_dependencies: List[PackageDependency] = field(default_factory=list)
    peer_dependencies: List[PackageDependency] = field(default_factory=list)
    agk_version: str = ">=1.0.0"
    python_version: str = ">=3.8"
    readme: str = "README.md"
    entry_points: Dict[str, str] = field(default_factory=dict)
    files: List[str] = field(default_factory=list)
    exclude_files: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        data = asdict(self)
        data['package_type'] = self.package_type.value
        data['dependencies'] = [asdict(dep) for dep in self.dependencies]
        data['dev_dependencies'] = [asdict(dep) for dep in self.dev_dependencies]
        data['peer_dependencies'] = [asdict(dep) for dep in self.peer_dependencies]
        for dep_list in data['dependencies'] + data['dev_dependencies'] + data['peer_dependencies']:
            dep_list['type'] = dep_list['type'].value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackageMetadata':
        """Create metadata from dictionary"""
        data = data.copy()
        data['package_type'] = PackageType(data['package_type'])
        data['dependencies'] = [PackageDependency(**dep) for dep in data.get('dependencies', [])]
        data['dev_dependencies'] = [PackageDependency(**dep) for dep in data.get('dev_dependencies', [])]
        data['peer_dependencies'] = [PackageDependency(**dep) for dep in data.get('peer_dependencies', [])]
        for dep in data['dependencies'] + data['dev_dependencies'] + data['peer_dependencies']:
            dep['type'] = DependencyType(dep['type'])
        return cls(**data)


@dataclass
class PackageFile:
    """Represents a file in a package"""
    path: str
    size: int
    sha256: str
    content_type: str = "text/plain"


@dataclass
class PackageManifest:
    """Package manifest for distribution"""
    metadata: PackageMetadata
    files: List[PackageFile] = field(default_factory=list)
    total_size: int = 0
    checksum: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary"""
        return {
            'metadata': self.metadata.to_dict(),
            'files': [asdict(f) for f in self.files],
            'total_size': self.total_size,
            'checksum': self.checksum
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackageManifest':
        """Create manifest from dictionary"""
        return cls(
            metadata=PackageMetadata.from_dict(data['metadata']),
            files=[PackageFile(**f) for f in data.get('files', [])],
            total_size=data.get('total_size', 0),
            checksum=data.get('checksum', '')
        )


class PackageConfig:
    """Handles package configuration files (agk.toml)"""

    @staticmethod
    def load_from_file(path: str) -> PackageMetadata:
        """Load package metadata from agk.toml file"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Package config not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = toml.load(f)

        return PackageConfig._parse_toml_data(data)

    @staticmethod
    def save_to_file(metadata: PackageMetadata, path: str):
        """Save package metadata to agk.toml file"""
        data = PackageConfig._metadata_to_toml(metadata)

        with open(path, 'w', encoding='utf-8') as f:
            toml.dump(data, f)

    @staticmethod
    def _parse_toml_data(data: Dict[str, Any]) -> PackageMetadata:
        """Parse TOML data into PackageMetadata"""
        package_data = data.get('package', {})

        # Parse dependencies
        dependencies = []
        if 'dependencies' in data:
            for name, version_spec in data['dependencies'].items():
                if isinstance(version_spec, str):
                    dependencies.append(PackageDependency(name=name, version_spec=version_spec))
                elif isinstance(version_spec, dict):
                    dependencies.append(PackageDependency(
                        name=name,
                        **version_spec
                    ))

        # Parse dev dependencies
        dev_dependencies = []
        if 'dev-dependencies' in data:
            for name, version_spec in data['dev-dependencies'].items():
                if isinstance(version_spec, str):
                    dev_dependencies.append(PackageDependency(
                        name=name,
                        version_spec=version_spec,
                        type=DependencyType.DEVELOPMENT
                    ))
                elif isinstance(version_spec, dict):
                    dep_data = version_spec.copy()
                    dep_data['type'] = DependencyType.DEVELOPMENT
                    dev_dependencies.append(PackageDependency(name=name, **dep_data))

        return PackageMetadata(
            name=package_data.get('name', ''),
            version=package_data.get('version', '1.0.0'),
            description=package_data.get('description', ''),
            author=package_data.get('author', ''),
            email=package_data.get('email', ''),
            license=package_data.get('license', 'MIT'),
            homepage=package_data.get('homepage', ''),
            repository=package_data.get('repository', ''),
            keywords=package_data.get('keywords', []),
            package_type=PackageType(package_data.get('type', 'library')),
            dependencies=dependencies,
            dev_dependencies=dev_dependencies,
            agk_version=package_data.get('agk-version', '>=1.0.0'),
            python_version=package_data.get('python-version', '>=3.8'),
            readme=package_data.get('readme', 'README.md'),
            entry_points=data.get('entry-points', {}),
            files=data.get('files', []),
            exclude_files=data.get('exclude', [])
        )

    @staticmethod
    def _metadata_to_toml(metadata: PackageMetadata) -> Dict[str, Any]:
        """Convert PackageMetadata to TOML data"""
        data = {
            'package': {
                'name': metadata.name,
                'version': metadata.version,
                'description': metadata.description,
                'author': metadata.author,
                'email': metadata.email,
                'license': metadata.license,
                'homepage': metadata.homepage,
                'repository': metadata.repository,
                'keywords': metadata.keywords,
                'type': metadata.package_type.value,
                'agk-version': metadata.agk_version,
                'python-version': metadata.python_version,
                'readme': metadata.readme
            },
            'entry-points': metadata.entry_points,
            'files': metadata.files,
            'exclude': metadata.exclude_files
        }

        # Add dependencies
        if metadata.dependencies:
            data['dependencies'] = {}
            for dep in metadata.dependencies:
                if dep.type == DependencyType.REQUIRED:
                    data['dependencies'][dep.name] = dep.version_spec

        if metadata.dev_dependencies:
            data['dev-dependencies'] = {}
            for dep in metadata.dev_dependencies:
                data['dev-dependencies'][dep.name] = dep.version_spec

        return data

    @staticmethod
    def create_default_config(name: str) -> PackageMetadata:
        """Create a default package configuration"""
        return PackageMetadata(
            name=name,
            description=f"AGK package: {name}",
            author="Your Name",
            email="your.email@example.com",
            license="MIT",
            keywords=["agk", "library"],
            agk_version=">=1.0.0",
            python_version=">=3.8"
        )


class PackageBuilder:
    """Builds packages for distribution"""

    @staticmethod
    def build_package(source_path: str, output_path: str) -> str:
        """Build a package from source directory"""
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source path not found: {source_path}")

        # Find package config
        config_path = source_path / "agk.toml"
        if not config_path.exists():
            raise FileNotFoundError(f"Package config not found: {config_path}")

        # Load metadata
        metadata = PackageConfig.load_from_file(str(config_path))

        # Create temporary build directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Copy package files
            PackageBuilder._copy_package_files(source_path, temp_path, metadata)

            # Create manifest
            manifest = PackageBuilder._create_manifest(temp_path, metadata)

            # Save manifest
            manifest_path = temp_path / "agk-package.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest.to_dict(), f, indent=2)

            # Create package archive
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            package_name = f"{metadata.name}-{metadata.version}.agk-pkg"
            package_path = output_path / package_name

            with tarfile.open(package_path, "w:gz") as tar:
                for file_path in temp_path.rglob("*"):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(temp_path))
                        tar.add(file_path, arcname=arcname)

            return str(package_path)

    @staticmethod
    def _copy_package_files(source_path: Path, dest_path: Path, metadata: PackageMetadata):
        """Copy package files to build directory"""
        # Default files to include
        include_patterns = ["**/*.agk", "**/*.py", "**/*.toml", "**/*.md", "**/*.txt", "**/*.json"]

        # Add custom include patterns
        for pattern in metadata.files:
            if pattern not in include_patterns:
                include_patterns.append(pattern)

        # Copy files
        for pattern in include_patterns:
            for file_path in source_path.glob(pattern):
                if file_path.is_file():
                    # Check if file should be excluded
                    relative_path = file_path.relative_to(source_path)
                    if any(relative_path.match(exclude) for exclude in metadata.exclude_files):
                        continue

                    dest_file = dest_path / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_file)

    @staticmethod
    def _create_manifest(package_path: Path, metadata: PackageMetadata) -> PackageManifest:
        """Create package manifest"""
        files = []
        total_size = 0

        for file_path in package_path.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                sha256 = PackageBuilder._calculate_sha256(file_path)
                content_type = PackageBuilder._guess_content_type(file_path)

                relative_path = str(file_path.relative_to(package_path))
                files.append(PackageFile(
                    path=relative_path,
                    size=size,
                    sha256=sha256,
                    content_type=content_type
                ))
                total_size += size

        # Calculate package checksum
        checksum = PackageBuilder._calculate_package_checksum(files)

        return PackageManifest(
            metadata=metadata,
            files=files,
            total_size=total_size,
            checksum=checksum
        )

    @staticmethod
    def _calculate_sha256(file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def _guess_content_type(file_path: Path) -> str:
        """Guess content type of a file"""
        suffix = file_path.suffix.lower()
        content_types = {
            '.agk': 'text/x-agk',
            '.py': 'text/x-python',
            '.toml': 'application/toml',
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript'
        }
        return content_types.get(suffix, 'application/octet-stream')

    @staticmethod
    def _calculate_package_checksum(files: List[PackageFile]) -> str:
        """Calculate overall package checksum"""
        sha256_hash = hashlib.sha256()
        for file in sorted(files, key=lambda f: f.path):
            sha256_hash.update(file.sha256.encode())
        return sha256_hash.hexdigest()


class PackageInstaller:
    """Handles package installation"""

    @staticmethod
    def install_package(package_path: str, install_dir: str):
        """Install a package from archive"""
        install_path = Path(install_dir)
        install_path.mkdir(parents=True, exist_ok=True)

        # Extract package
        with tarfile.open(package_path, "r:gz") as tar:
            tar.extractall(install_path)

        # Load and validate manifest
        manifest_path = install_path / "agk-package.json"
        if not manifest_path.exists():
            raise ValueError("Invalid package: missing manifest")

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)

        manifest = PackageManifest.from_dict(manifest_data)

        # Validate package integrity
        PackageInstaller._validate_package(manifest, install_path)

        # Remove manifest file
        manifest_path.unlink()

        return manifest.metadata

    @staticmethod
    def _validate_package(manifest: PackageManifest, install_path: Path):
        """Validate package integrity"""
        # Check file count
        actual_files = list(install_path.rglob("*"))
        actual_files = [f for f in actual_files if f.is_file() and f.name != "agk-package.json"]

        if len(actual_files) != len(manifest.files):
            raise ValueError("Package file count mismatch")

        # Check file hashes
        for package_file in manifest.files:
            file_path = install_path / package_file.path
            if not file_path.exists():
                raise ValueError(f"Missing file: {package_file.path}")

            actual_sha256 = PackageBuilder._calculate_sha256(file_path)
            if actual_sha256 != package_file.sha256:
                raise ValueError(f"File corruption detected: {package_file.path}")

        # Verify package checksum
        calculated_checksum = PackageBuilder._calculate_package_checksum(manifest.files)
        if calculated_checksum != manifest.checksum:
            raise ValueError("Package checksum verification failed")


# Example usage and testing
if __name__ == "__main__":
    # Create a sample package
    metadata = PackageConfig.create_default_config("sample-package")
    metadata.description = "A sample AGK package"
    metadata.keywords = ["sample", "demo"]

    print("Package metadata:")
    print(json.dumps(metadata.to_dict(), indent=2))