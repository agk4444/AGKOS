"""
AGK Package Registry System
Manages package storage, retrieval, and search functionality
"""

import os
import json
import sqlite3
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
import requests
from urllib.parse import urljoin, urlparse
import semver
from agk_package import PackageMetadata, PackageManifest, PackageType


@dataclass
class PackageVersion:
    """Represents a specific version of a package"""
    version: str
    metadata: PackageMetadata
    download_url: str
    checksum: str
    size: int
    uploaded_at: str = field(default_factory=lambda: datetime.now().isoformat())
    downloads: int = 0
    verified: bool = False


@dataclass
class PackageInfo:
    """Complete package information"""
    name: str
    description: str
    author: str
    email: str
    license: str
    homepage: str
    repository: str
    keywords: List[str]
    package_type: PackageType
    versions: Dict[str, PackageVersion] = field(default_factory=dict)
    latest_version: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    total_downloads: int = 0
    verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['package_type'] = self.package_type.value
        data['versions'] = {v: asdict(pv) for v, pv in self.versions.items()}
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackageInfo':
        """Create from dictionary"""
        data = data.copy()
        data['package_type'] = PackageType(data['package_type'])
        data['versions'] = {v: PackageVersion(**pv) for v, pv in data.get('versions', {}).items()}
        return cls(**data)


class PackageRegistry:
    """Local package registry for managing installed packages"""

    def __init__(self, registry_path: str = None):
        if registry_path is None:
            registry_path = os.path.join(os.path.expanduser("~"), ".agk", "registry")

        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.registry_path / "registry.db"
        self.packages_path = self.registry_path / "packages"
        self.packages_path.mkdir(exist_ok=True)

        self._lock = threading.RLock()
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS packages (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    author TEXT,
                    email TEXT,
                    license TEXT,
                    homepage TEXT,
                    repository TEXT,
                    keywords TEXT,
                    package_type TEXT,
                    latest_version TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    total_downloads INTEGER DEFAULT 0,
                    verified BOOLEAN DEFAULT 0
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    package_name TEXT,
                    version TEXT,
                    download_url TEXT,
                    checksum TEXT,
                    size INTEGER,
                    uploaded_at TEXT,
                    downloads INTEGER DEFAULT 0,
                    verified BOOLEAN DEFAULT 0,
                    PRIMARY KEY (package_name, version),
                    FOREIGN KEY (package_name) REFERENCES packages (name)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS installed (
                    package_name TEXT,
                    version TEXT,
                    install_path TEXT,
                    installed_at TEXT,
                    PRIMARY KEY (package_name, version)
                )
            """)

            conn.commit()

    def add_package(self, package_info: PackageInfo):
        """Add or update package information"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Insert/update package info
                conn.execute("""
                    INSERT OR REPLACE INTO packages
                    (name, description, author, email, license, homepage, repository,
                     keywords, package_type, latest_version, created_at, updated_at,
                     total_downloads, verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    package_info.name,
                    package_info.description,
                    package_info.author,
                    package_info.email,
                    package_info.license,
                    package_info.homepage,
                    package_info.repository,
                    json.dumps(package_info.keywords),
                    package_info.package_type.value,
                    package_info.latest_version,
                    package_info.created_at,
                    package_info.updated_at,
                    package_info.total_downloads,
                    package_info.verified
                ))

                # Insert versions
                for version, version_info in package_info.versions.items():
                    conn.execute("""
                        INSERT OR REPLACE INTO versions
                        (package_name, version, download_url, checksum, size,
                         uploaded_at, downloads, verified)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        package_info.name,
                        version,
                        version_info.download_url,
                        version_info.checksum,
                        version_info.size,
                        version_info.uploaded_at,
                        version_info.downloads,
                        version_info.verified
                    ))

                conn.commit()

    def get_package(self, name: str) -> Optional[PackageInfo]:
        """Get package information"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Get package info
                cursor = conn.execute("""
                    SELECT * FROM packages WHERE name = ?
                """, (name,))

                row = cursor.fetchone()
                if not row:
                    return None

                # Get versions
                cursor = conn.execute("""
                    SELECT * FROM versions WHERE package_name = ?
                """, (name,))

                versions = {}
                for v_row in cursor.fetchall():
                    versions[v_row[1]] = PackageVersion(
                        version=v_row[1],
                        download_url=v_row[2],
                        checksum=v_row[3],
                        size=v_row[4],
                        uploaded_at=v_row[5],
                        downloads=v_row[6],
                        verified=bool(v_row[7])
                    )

                return PackageInfo(
                    name=row[0],
                    description=row[1],
                    author=row[2],
                    email=row[3],
                    license=row[4],
                    homepage=row[5],
                    repository=row[6],
                    keywords=json.loads(row[7]) if row[7] else [],
                    package_type=PackageType(row[8]),
                    latest_version=row[9],
                    created_at=row[10],
                    updated_at=row[11],
                    total_downloads=row[12],
                    verified=bool(row[13]),
                    versions=versions
                )

    def search_packages(self, query: str, limit: int = 20) -> List[PackageInfo]:
        """Search packages by name, description, or keywords"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Simple search - could be enhanced with FTS
                search_term = f"%{query}%"
                cursor = conn.execute("""
                    SELECT * FROM packages
                    WHERE name LIKE ? OR description LIKE ? OR keywords LIKE ?
                    ORDER BY total_downloads DESC
                    LIMIT ?
                """, (search_term, search_term, search_term, limit))

                packages = []
                for row in cursor.fetchall():
                    packages.append(PackageInfo(
                        name=row[0],
                        description=row[1],
                        author=row[2],
                        email=row[3],
                        license=row[4],
                        homepage=row[5],
                        repository=row[6],
                        keywords=json.loads(row[7]) if row[7] else [],
                        package_type=PackageType(row[8]),
                        latest_version=row[9],
                        created_at=row[10],
                        updated_at=row[11],
                        total_downloads=row[12],
                        verified=bool(row[13])
                    ))

                return packages

    def list_installed_packages(self) -> List[Tuple[str, str, str]]:
        """List installed packages"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT package_name, version, install_path
                    FROM installed
                    ORDER BY package_name
                """)
                return cursor.fetchall()

    def mark_installed(self, name: str, version: str, install_path: str):
        """Mark package as installed"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO installed
                    (package_name, version, install_path, installed_at)
                    VALUES (?, ?, ?, ?)
                """, (name, version, install_path, datetime.now().isoformat()))
                conn.commit()

    def mark_uninstalled(self, name: str, version: str):
        """Mark package as uninstalled"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    DELETE FROM installed
                    WHERE package_name = ? AND version = ?
                """, (name, version))
                conn.commit()

    def is_installed(self, name: str, version: str = None) -> bool:
        """Check if package is installed"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                if version:
                    cursor = conn.execute("""
                        SELECT 1 FROM installed
                        WHERE package_name = ? AND version = ?
                    """, (name, version))
                else:
                    cursor = conn.execute("""
                        SELECT 1 FROM installed
                        WHERE package_name = ?
                    """, (name,))
                return cursor.fetchone() is not None


class RemoteRegistry:
    """Client for remote package registries"""

    def __init__(self, base_url: str = "https://registry.agk-lang.org"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AGK-Package-Manager/1.0'
        })

    def search_packages(self, query: str, limit: int = 20) -> List[PackageInfo]:
        """Search packages in remote registry"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/search",
                params={'q': query, 'limit': limit},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            packages = []
            for pkg_data in data.get('packages', []):
                packages.append(PackageInfo.from_dict(pkg_data))
            return packages

        except Exception as e:
            print(f"Error searching remote registry: {e}")
            return []

    def get_package(self, name: str) -> Optional[PackageInfo]:
        """Get package information from remote registry"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/packages/{name}",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return PackageInfo.from_dict(data)

        except Exception as e:
            print(f"Error fetching package {name}: {e}")
            return None

    def get_package_version(self, name: str, version: str) -> Optional[PackageVersion]:
        """Get specific package version"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/packages/{name}/{version}",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return PackageVersion(**data)

        except Exception as e:
            print(f"Error fetching package {name}@{version}: {e}")
            return None

    def download_package(self, name: str, version: str, download_path: str):
        """Download package archive"""
        package_version = self.get_package_version(name, version)
        if not package_version:
            raise ValueError(f"Package {name}@{version} not found")

        response = self.session.get(package_version.download_url, stream=True, timeout=300)
        response.raise_for_status()

        Path(download_path).parent.mkdir(parents=True, exist_ok=True)
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Verify checksum
        with open(download_path, 'rb') as f:
            file_hash = hashlib.sha256()
            for chunk in iter(lambda: f.read(4096), b""):
                file_hash.update(chunk)

        if file_hash.hexdigest() != package_version.checksum:
            os.remove(download_path)
            raise ValueError("Package checksum verification failed")

    def publish_package(self, package_path: str, api_key: str) -> bool:
        """Publish package to remote registry"""
        try:
            with open(package_path, 'rb') as f:
                files = {'package': f}
                headers = {'Authorization': f'Bearer {api_key}'}

                response = self.session.post(
                    f"{self.base_url}/api/packages",
                    files=files,
                    headers=headers,
                    timeout=300
                )
                response.raise_for_status()
                return True

        except Exception as e:
            print(f"Error publishing package: {e}")
            return False


class VersionResolver:
    """Handles version resolution and compatibility"""

    @staticmethod
    def resolve_version(version_spec: str, available_versions: List[str]) -> str:
        """Resolve version specification to concrete version"""
        if version_spec == "latest":
            return max(available_versions, key=lambda v: semver.VersionInfo.parse(v))

        if version_spec.startswith("^"):
            base_version = version_spec[1:]
            base_ver = semver.VersionInfo.parse(base_version)
            compatible = [
                v for v in available_versions
                if semver.VersionInfo.parse(v).major == base_ver.major
            ]
            return max(compatible, key=lambda v: semver.VersionInfo.parse(v))

        if version_spec.startswith("~"):
            base_version = version_spec[1:]
            base_ver = semver.VersionInfo.parse(base_version)
            compatible = [
                v for v in available_versions
                if semver.VersionInfo.parse(v).major == base_ver.major and
                semver.VersionInfo.parse(v).minor == base_ver.minor
            ]
            return max(compatible, key=lambda v: semver.VersionInfo.parse(v))

        # Exact version match
        if version_spec in available_versions:
            return version_spec

        # Try to parse as semantic version range
        try:
            spec = semver.NpmSpec(version_spec)
            for version in available_versions:
                if spec.match(semver.VersionInfo.parse(version)):
                    return version
        except:
            pass

        raise ValueError(f"No compatible version found for {version_spec}")

    @staticmethod
    def satisfies_version(version: str, version_spec: str) -> bool:
        """Check if version satisfies specification"""
        try:
            ver = semver.VersionInfo.parse(version)
            spec = semver.NpmSpec(version_spec)
            return spec.match(ver)
        except:
            return version == version_spec

    @staticmethod
    def get_latest_version(versions: List[str]) -> str:
        """Get latest version from list"""
        return max(versions, key=lambda v: semver.VersionInfo.parse(v))


# Example usage and testing
if __name__ == "__main__":
    # Test local registry
    registry = PackageRegistry()

    # Create sample package info
    metadata = PackageMetadata(
        name="sample-package",
        version="1.0.0",
        description="A sample AGK package",
        author="Test Author",
        keywords=["sample", "test"]
    )

    package_info = PackageInfo(
        name="sample-package",
        description="A sample AGK package",
        author="Test Author",
        email="test@example.com",
        license="MIT",
        homepage="https://example.com",
        repository="https://github.com/example/sample-package",
        keywords=["sample", "test"],
        package_type=PackageType.LIBRARY,
        latest_version="1.0.0"
    )

    # Add package
    registry.add_package(package_info)

    # Search packages
    results = registry.search_packages("sample")
    print(f"Found {len(results)} packages")

    # Get package
    pkg = registry.get_package("sample-package")
    if pkg:
        print(f"Package: {pkg.name} v{pkg.latest_version}")