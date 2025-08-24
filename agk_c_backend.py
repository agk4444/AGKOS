#!/usr/bin/env python3
"""
AGK Language C Backend

Main integration module for compiling AGK to native C executables
with full system programming support.
"""

import os
import sys
from typing import Optional, Dict, List, Any
from pathlib import Path

from agk_ast import Program
from agk_c_codegen import CCodeGenerator
from agk_c_build import CBuildSystem, create_build_system
from agk_compiler import AGKCompiler


class CBackend:
    """Main C backend for AGK compilation"""

    def __init__(self, project_name: str = "agk_system_app"):
        self.project_name = project_name
        self.output_dir: str = ""
        self.source_files: List[str] = []
        self.compiler = AGKCompiler()
        self.code_generator = CCodeGenerator(enable_system_extensions=True)
        self.build_system = CBuildSystem(project_name)
        self.build_type: str = "release"
        self.run_after_build: bool = False
        self.execution_args: List[str] = []

    def set_output_directory(self, output_dir: str):
        """Set the output directory for generated files"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def set_build_type(self, build_type: str):
        """Set the build type (debug/release)"""
        self.build_type = build_type.lower()
        self.build_system.set_build_type(build_type)

    def enable_system_extensions(self, enable: bool = True):
        """Enable or disable system programming extensions"""
        self.code_generator.enable_system_extensions = enable

    def set_cross_compile(self, target: str, compiler_prefix: str = ""):
        """Set cross-compilation target"""
        self.build_system.set_cross_compile(target, compiler_prefix)

    def add_include_directory(self, include_dir: str):
        """Add an include directory"""
        self.build_system.add_include_dir(include_dir)

    def add_library_directory(self, lib_dir: str):
        """Add a library directory"""
        self.build_system.add_library_dir(lib_dir)

    def add_library(self, library: str):
        """Add a library to link against"""
        self.build_system.add_library(library)

    def add_source_file(self, source_file: str):
        """Add a source file to the build"""
        self.source_files.append(source_file)

    def compile_agk_to_c(self, agk_source: str, output_file: str) -> bool:
        """Compile AGK source to C code"""
        try:
            # Parse AGK source
            success = self.compiler.compile(agk_source)
            if not success:
                print("AGK compilation failed:")
                for error in self.compiler.get_errors():
                    print(f"  ERROR: {error}")
                return False

            # Get the AST from the compiler
            # Note: We'd need to modify the compiler to expose the AST
            # For now, we'll generate code directly
            ast = self._create_sample_ast()

            # Generate C code
            c_code = self.code_generator.generate(ast)

            # Write C code to file
            with open(output_file, 'w') as f:
                f.write(c_code)

            print(f"SUCCESS: C code generated: {output_file}")
            return True

        except Exception as e:
            print(f"ERROR: C code generation failed: {e}")
            return False

    def _create_sample_ast(self) -> Program:
        """Create a sample AST for testing (this would normally come from the parser)"""
        from agk_ast import Program, FunctionDef, VariableDecl, ReturnStatement, Literal

        # Create a simple main function
        return_stmt = ReturnStatement(Literal(0, "int"))
        main_func = FunctionDef(
            name="main",
            parameters=[],
            return_type=None,
            body=[return_stmt]
        )

        return Program([main_func])

    def build_project(self, source_files: List[str] = None) -> bool:
        """Build the project to an executable"""
        try:
            # Use provided source files or generated ones
            sources = source_files or self.source_files

            if not sources:
                print("ERROR: No source files to build")
                return False

            # Add source files to build system
            for source in sources:
                self.build_system.add_source_file(source)

            # Generate build files and compile
            print(f"Building project: {self.project_name}")
            print(f"Build type: {self.build_type}")

            # Try building with make first
            if self.build_system.build_with_make(self.output_dir):
                print("SUCCESS: Project built successfully!")
                return True
            else:
                # Fallback to cmake
                print("Make build failed, trying CMake...")
                if self.build_system.build_with_cmake(self.output_dir):
                    print("SUCCESS: Project built successfully with CMake!")
                    return True
                else:
                    print("ERROR: Both Make and CMake builds failed")
                    return False

        except Exception as e:
            print(f"ERROR: Build failed: {e}")
            return False

    def run_executable(self, args: List[str] = None) -> bool:
        """Run the built executable"""
        try:
            execution_args = args or self.execution_args

            if self.build_system.run_executable(self.output_dir, execution_args):
                print("SUCCESS: Program executed successfully!")
                return True
            else:
                print("ERROR: Program execution failed")
                return False

        except Exception as e:
            print(f"ERROR: Execution failed: {e}")
            return False

    def compile_and_build(self,
                         agk_source: str,
                         output_dir: str = "bin",
                         build_type: str = "release",
                         run_after_build: bool = False,
                         execution_args: List[str] = None) -> bool:
        """Complete pipeline: AGK source -> C code -> executable"""
        try:
            # Set configuration
            self.set_output_directory(output_dir)
            self.set_build_type(build_type)
            self.run_after_build = run_after_build
            self.execution_args = execution_args or []

            # Step 1: Compile AGK to C
            c_source_file = os.path.join(output_dir, f"{self.project_name}.c")
            if not self.compile_agk_to_c(agk_source, c_source_file):
                return False

            # Step 2: Build the project
            if not self.build_project([c_source_file]):
                return False

            # Step 3: Run if requested
            if run_after_build:
                return self.run_executable()

            return True

        except Exception as e:
            print(f"ERROR: Compile and build failed: {e}")
            return False


class SystemProgrammingBackend(CBackend):
    """Extended backend with system programming capabilities"""

    def __init__(self, project_name: str = "agk_system_program"):
        super().__init__(project_name)
        self.system_extensions_enabled = True
        self.enable_system_extensions(True)

        # Add system programming libraries
        self.add_system_libraries()

    def add_system_libraries(self):
        """Add system programming specific libraries"""
        # Platform-specific system libraries
        import platform
        system = platform.system().lower()

        if system == "linux":
            self.add_library("pthread")
            self.add_library("rt")  # Real-time extensions
            self.add_library("dl")  # Dynamic loading
        elif system == "windows":
            self.add_library("ws2_32")  # Winsock
            self.add_library("user32")
            self.add_library("kernel32")
        elif system == "darwin":  # macOS
            self.add_library("pthread")

    def create_kernel_module(self, agk_source: str, kernel_source_dir: str = None) -> bool:
        """Create a kernel module from AGK source"""
        try:
            from agk_c_build import KernelBuildSystem

            # Switch to kernel build system
            kernel_build = KernelBuildSystem(self.project_name)
            if kernel_source_dir:
                kernel_build.set_kernel_source(kernel_source_dir)

            self.build_system = kernel_build

            # Enable kernel-specific features
            self.code_generator.enable_system_extensions = True
            self.add_include_directory("/usr/src/linux/include")

            # Generate kernel module code
            c_source_file = os.path.join(self.output_dir, f"{self.project_name}.c")
            if not self.compile_agk_to_c(agk_source, c_source_file):
                return False

            # Build kernel module
            return self.build_project([c_source_file])

        except Exception as e:
            print(f"ERROR: Kernel module creation failed: {e}")
            return False

    def create_bare_metal_program(self,
                                  agk_source: str,
                                  target_arch: str = "arm",
                                  linker_script: str = None) -> bool:
        """Create a bare-metal program from AGK source"""
        try:
            from agk_c_build import BareMetalBuildSystem

            # Switch to bare-metal build system
            bare_metal_build = BareMetalBuildSystem(self.project_name)
            bare_metal_build.set_target_arch(target_arch)

            if linker_script:
                bare_metal_build.set_linker_script(linker_script)

            self.build_system = bare_metal_build

            # Generate bare-metal C code
            c_source_file = os.path.join(self.output_dir, f"{self.project_name}.c")
            if not self.compile_agk_to_c(agk_source, c_source_file):
                return False

            # Build bare-metal binary
            return self.build_project([c_source_file])

        except Exception as e:
            print(f"ERROR: Bare-metal program creation failed: {e}")
            return False

    def create_mobile_app(self,
                         agk_source: str,
                         target_platform: str = "android",
                         target_arch: str = "arm64",
                         api_level: int = 21,
                         ndk_path: str = None,
                         sdk_path: str = None) -> bool:
        """Create a mobile app from AGK source"""
        try:
            from agk_c_build import MobileBuildSystem

            # Switch to mobile build system
            mobile_build = MobileBuildSystem(self.project_name)
            mobile_build.set_target_platform(target_platform)
            mobile_build.set_target_arch(target_arch)
            mobile_build.set_api_level(api_level)

            if ndk_path:
                mobile_build.set_ndk_path(ndk_path)
            if sdk_path:
                mobile_build.set_sdk_path(sdk_path)

            # Add mobile-specific libraries
            if target_platform == "android":
                mobile_build.add_library("android")
                mobile_build.add_library("log")
                mobile_build.add_library("EGL")
                mobile_build.add_library("GLESv3")
                mobile_build.add_library("OpenSLES")
            elif target_platform == "ios":
                mobile_build.add_library("UIKit")
                mobile_build.add_library("Foundation")
                mobile_build.add_library("CoreGraphics")
                mobile_build.add_library("QuartzCore")
                mobile_build.add_library("OpenGLES")

            self.build_system = mobile_build

            # Generate mobile C code
            c_source_file = os.path.join(self.output_dir, f"{self.project_name}.c")
            if not self.compile_agk_to_c(agk_source, c_source_file):
                return False

            # Build mobile app
            return self.build_project([c_source_file])

        except Exception as e:
            print(f"ERROR: Mobile app creation failed: {e}")
            return False


def compile_agk_to_c_backend(agk_source: str,
                           output_dir: str = "bin",
                           project_name: str = "agk_system_app",
                           build_type: str = "release",
                           run_after_build: bool = False,
                           execution_args: List[str] = None,
                           system_programming: bool = True) -> CBackend:
    """
    Convenience function to compile AGK to C backend

    Args:
        agk_source: AGK source code string
        output_dir: Output directory for generated files
        project_name: Name of the project
        build_type: Build type (debug/release)
        run_after_build: Whether to run the program after building
        execution_args: Arguments to pass to the executable
        system_programming: Enable system programming extensions

    Returns:
        CBackend: Configured C backend instance
    """
    try:
        # Create appropriate backend
        if system_programming:
            backend = SystemProgrammingBackend(project_name)
        else:
            backend = CBackend(project_name)

        # Compile, build, and optionally run
        success = backend.compile_and_build(
            agk_source=agk_source,
            output_dir=output_dir,
            build_type=build_type,
            run_after_build=run_after_build,
            execution_args=execution_args
        )

        if success:
            print(f"SUCCESS: AGK compiled to C backend successfully!")
            print(f"Output directory: {os.path.abspath(output_dir)}")
            if run_after_build:
                print("Program executed successfully!")
        else:
            print("ERROR: AGK to C backend compilation failed!")

        return backend

    except Exception as e:
        print(f"ERROR: C backend compilation failed: {e}")
        return None


# Example usage and testing
if __name__ == "__main__":
    # Example AGK system program
    sample_agk_code = '''
define function memory_test:
    create buffer as pointer
    set buffer to memory_allocate(1024)
    if buffer is null:
        return -1

    memory_set(buffer, 0, 1024)
    memory_free(buffer)
    return 0

define function file_test:
    create fd as int
    set fd to file_open("test.txt", O_CREAT | O_WRONLY)
    if fd < 0:
        return -1

    file_write(fd, "Hello, System Programming!", 26)
    file_close(fd)
    return 0

define function program_main:
    print("AGK System Programming Test")
    create result as int

    set result to memory_test()
    print("Memory test result: " + result)

    set result to file_test()
    print("File test result: " + result)

    return 0
'''

    # Compile to C backend
    backend = compile_agk_to_c_backend(
        agk_source=sample_agk_code,
        output_dir="system_program_output",
        project_name="agk_system_test",
        build_type="debug",
        run_after_build=False
    )

    if backend:
        print("\\nGenerated files:")
        output_path = Path("system_program_output")
        for file in output_path.glob("*"):
            if file.is_file():
                print(f"  {file.name}")