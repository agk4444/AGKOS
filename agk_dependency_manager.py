"""
Library Dependency Management for AGK Language Compiler
Automatically resolves and loads library dependencies
"""

import os
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class DependencyType(Enum):
    """Types of dependencies"""
    STANDARD_LIBRARY = "standard"
    EXTERNAL_LIBRARY = "external"
    USER_LIBRARY = "user"
    SYSTEM_LIBRARY = "system"


@dataclass
class LibraryDependency:
    """Represents a library dependency"""
    name: str
    version: str = "latest"
    type: DependencyType = DependencyType.STANDARD_LIBRARY
    dependencies: List['LibraryDependency'] = field(default_factory=list)
    description: str = ""
    loaded: bool = False
    load_order: int = 0


@dataclass
class DependencyGraph:
    """Represents the dependency graph"""
    nodes: Dict[str, LibraryDependency] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)
    resolution_order: List[str] = field(default_factory=list)


class DependencyResolutionError(Exception):
    """Exception raised for dependency resolution errors"""
    pass


class CircularDependencyError(DependencyResolutionError):
    """Exception raised for circular dependencies"""
    pass


class MissingDependencyError(DependencyResolutionError):
    """Exception raised for missing dependencies"""
    pass


class VersionConflictError(DependencyResolutionError):
    """Exception raised for version conflicts"""
    pass


class AGKDependencyManager:
    """Manages library dependencies for AGK"""

    def __init__(self):
        self.dependency_graph = DependencyGraph()
        self.library_paths = [
            "stdlib/",
            "lib/",
            "libs/",
            "libraries/",
            "external/"
        ]
        self.loaded_libraries: Set[str] = set()
        self.library_registry: Dict[str, dict] = {}
        self.version_constraints: Dict[str, str] = {}

        # Initialize standard library dependencies
        self._initialize_standard_libraries()

    def _initialize_standard_libraries(self):
        """Initialize standard library dependency information"""
        standard_libs = {
            "math": LibraryDependency(
                name="math",
                type=DependencyType.STANDARD_LIBRARY,
                description="Mathematical functions and constants"
            ),
            "string": LibraryDependency(
                name="string",
                type=DependencyType.STANDARD_LIBRARY,
                description="String manipulation functions"
            ),
            "list": LibraryDependency(
                name="list",
                type=DependencyType.STANDARD_LIBRARY,
                description="List and collection operations"
            ),
            "io": LibraryDependency(
                name="io",
                type=DependencyType.STANDARD_LIBRARY,
                description="Input/Output operations"
            ),
            "llm": LibraryDependency(
                name="llm",
                type=DependencyType.STANDARD_LIBRARY,
                dependencies=[
                    LibraryDependency(name="string", type=DependencyType.STANDARD_LIBRARY),
                    LibraryDependency(name="io", type=DependencyType.STANDARD_LIBRARY)
                ],
                description="Large Language Model integration"
            ),
            "gto": LibraryDependency(
                name="gto",
                type=DependencyType.STANDARD_LIBRARY,
                dependencies=[
                    LibraryDependency(name="math", type=DependencyType.STANDARD_LIBRARY)
                ],
                description="Game Theory Operations"
            ),
            "web": LibraryDependency(
                name="web",
                type=DependencyType.STANDARD_LIBRARY,
                dependencies=[
                    LibraryDependency(name="string", type=DependencyType.STANDARD_LIBRARY),
                    LibraryDependency(name="io", type=DependencyType.STANDARD_LIBRARY)
                ],
                description="Web development and HTTP operations"
            ),
            "date": LibraryDependency(
                name="date",
                type=DependencyType.STANDARD_LIBRARY,
                description="Date and time manipulation"
            ),
            "finance": LibraryDependency(
                name="finance",
                type=DependencyType.STANDARD_LIBRARY,
                dependencies=[
                    LibraryDependency(name="math", type=DependencyType.STANDARD_LIBRARY)
                ],
                description="Financial calculations and investment analysis"
            ),
            "crypto": LibraryDependency(
                name="crypto",
                type=DependencyType.STANDARD_LIBRARY,
                description="Cryptographic functions for security and data protection"
            ),
            "graphics": LibraryDependency(
                name="graphics",
                type=DependencyType.STANDARD_LIBRARY,
                description="2D and 3D graphics capabilities"
            )
        }

        for lib in standard_libs.values():
            self.dependency_graph.nodes[lib.name] = lib

    def add_library_dependency(self, library_name: str, dependencies: List[str],
                             lib_type: DependencyType = DependencyType.USER_LIBRARY):
        """Add a user library with its dependencies"""
        if library_name in self.dependency_graph.nodes:
            return  # Already exists

        # Convert string dependencies to LibraryDependency objects
        dep_objects = []
        for dep in dependencies:
            if dep in self.dependency_graph.nodes:
                dep_objects.append(self.dependency_graph.nodes[dep])
            else:
                # Create new dependency
                dep_objects.append(LibraryDependency(
                    name=dep,
                    type=DependencyType.USER_LIBRARY
                ))

        library = LibraryDependency(
            name=library_name,
            type=lib_type,
            dependencies=dep_objects
        )

        self.dependency_graph.nodes[library_name] = library

        # Update edges
        self.dependency_graph.edges[library_name] = [dep.name for dep in dep_objects]

    def resolve_dependencies(self, requested_libraries: List[str]) -> List[str]:
        """
        Resolve dependencies for the requested libraries
        Returns a list of libraries in the correct load order
        """
        try:
            # Build dependency graph for requested libraries
            visited = set()
            temp_visited = set()  # For cycle detection
            load_order = []

            for lib in requested_libraries:
                if lib not in visited:
                    self._resolve_library_dependencies(lib, visited, temp_visited, load_order)

            # Reverse the order for correct loading (dependencies first)
            load_order.reverse()
            self.dependency_graph.resolution_order = load_order

            return load_order

        except RecursionError:
            raise CircularDependencyError("Circular dependency detected in library dependencies")

    def _resolve_library_dependencies(self, library_name: str, visited: Set[str],
                                    temp_visited: Set[str], load_order: List[str]):
        """Recursively resolve dependencies using DFS"""
        if library_name in temp_visited:
            raise CircularDependencyError(f"Circular dependency detected: {library_name}")

        if library_name in visited:
            return

        if library_name not in self.dependency_graph.nodes:
            raise MissingDependencyError(f"Library '{library_name}' not found")

        temp_visited.add(library_name)

        # Resolve all dependencies first
        library = self.dependency_graph.nodes[library_name]
        for dependency in library.dependencies:
            self._resolve_library_dependencies(dependency.name, visited, temp_visited, load_order)

        temp_visited.remove(library_name)
        visited.add(library_name)
        load_order.append(library_name)

    def validate_dependencies(self) -> List[str]:
        """Validate that all dependencies are satisfied"""
        errors = []

        for lib_name, library in self.dependency_graph.nodes.items():
            for dependency in library.dependencies:
                if dependency.name not in self.dependency_graph.nodes:
                    errors.append(f"Missing dependency '{dependency.name}' required by '{lib_name}'")

        return errors

    def get_dependency_tree(self, library_name: str, indent: int = 0) -> str:
        """Get a string representation of the dependency tree"""
        if library_name not in self.dependency_graph.nodes:
            return f"{'  ' * indent}{library_name} (NOT FOUND)"

        library = self.dependency_graph.nodes[library_name]
        result = f"{'  ' * indent}{library_name} ({library.type.value})"

        if library.dependencies:
            result += "\n"
            for dep in library.dependencies:
                result += self.get_dependency_tree(dep.name, indent + 1) + "\n"

        return result.rstrip()

    def load_library_file(self, library_name: str) -> Optional[str]:
        """Load a library file from the filesystem"""
        if library_name in self.loaded_libraries:
            return None  # Already loaded

        # Try different file extensions and paths
        search_patterns = [
            f"{library_name}.agk",
            f"{library_name}.py",
            f"lib{library_name}.agk",
            f"{library_name}_lib.agk"
        ]

        for path in self.library_paths:
            for pattern in search_patterns:
                full_path = os.path.join(path, pattern)
                if os.path.exists(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self.loaded_libraries.add(library_name)
                        return content
                    except Exception as e:
                        continue

        return None

    def check_version_compatibility(self, library_name: str, required_version: str) -> bool:
        """Check if a library version is compatible with requirements"""
        # Simple version checking - in a real implementation this would be more sophisticated
        if required_version == "latest":
            return True

        # For now, assume all specific versions are compatible
        return True

    def get_load_order(self) -> List[str]:
        """Get the current dependency resolution order"""
        return self.dependency_graph.resolution_order

    def clear_cache(self):
        """Clear the dependency cache"""
        self.loaded_libraries.clear()
        self.dependency_graph.resolution_order.clear()

    def export_dependency_graph(self, filename: str):
        """Export the dependency graph to a JSON file"""
        graph_data = {
            "libraries": {},
            "resolution_order": self.dependency_graph.resolution_order
        }

        for name, library in self.dependency_graph.nodes.items():
            graph_data["libraries"][name] = {
                "name": library.name,
                "version": library.version,
                "type": library.type.value,
                "dependencies": [dep.name for dep in library.dependencies],
                "description": library.description
            }

        try:
            with open(filename, 'w') as f:
                json.dump(graph_data, f, indent=2)
        except Exception as e:
            raise DependencyResolutionError(f"Failed to export dependency graph: {e}")

    def import_dependency_graph(self, filename: str):
        """Import dependency graph from a JSON file"""
        try:
            with open(filename, 'r') as f:
                graph_data = json.load(f)

            # Clear existing data
            self.dependency_graph = DependencyGraph()

            # Import libraries
            for name, lib_data in graph_data.get("libraries", {}).items():
                library = LibraryDependency(
                    name=lib_data["name"],
                    version=lib_data["version"],
                    type=DependencyType(lib_data["type"]),
                    description=lib_data["description"]
                )
                self.dependency_graph.nodes[name] = library

            # Import dependencies
            for name, lib_data in graph_data.get("libraries", {}).items():
                dependencies = []
                for dep_name in lib_data.get("dependencies", []):
                    if dep_name in self.dependency_graph.nodes:
                        dependencies.append(self.dependency_graph.nodes[dep_name])
                self.dependency_graph.nodes[name].dependencies = dependencies
                self.dependency_graph.edges[name] = [dep.name for dep in dependencies]

            # Import resolution order
            self.dependency_graph.resolution_order = graph_data.get("resolution_order", [])

        except Exception as e:
            raise DependencyResolutionError(f"Failed to import dependency graph: {e}")


# Global dependency manager instance
dependency_manager = AGKDependencyManager()

# Convenience functions for use in the compiler
def resolve_dependencies(requested_libraries: List[str]) -> List[str]:
    """Resolve dependencies for the given libraries"""
    return dependency_manager.resolve_dependencies(requested_libraries)

def get_dependency_tree(library_name: str) -> str:
    """Get dependency tree as string"""
    return dependency_manager.get_dependency_tree(library_name)

def validate_dependencies() -> List[str]:
    """Validate all dependencies"""
    return dependency_manager.validate_dependencies()

def add_user_library(name: str, dependencies: List[str]):
    """Add a user library with dependencies"""
    dependency_manager.add_library_dependency(name, dependencies)

# Example usage and testing
if __name__ == "__main__":
    # Test the dependency manager
    try:
        # Add some user libraries
        dependency_manager.add_library_dependency("mylib", ["math", "string", "io"])
        dependency_manager.add_library_dependency("advanced", ["mylib", "llm", "web"])

        # Resolve dependencies
        load_order = dependency_manager.resolve_dependencies(["advanced"])
        print("Load order:", load_order)

        # Print dependency tree
        print("\nDependency tree for 'advanced':")
        print(dependency_manager.get_dependency_tree("advanced"))

        # Validate dependencies
        errors = dependency_manager.validate_dependencies()
        if errors:
            print("\nValidation errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("\nAll dependencies validated successfully!")

    except Exception as e:
        print(f"Error: {e}")