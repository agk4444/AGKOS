"""
Foreign Function Interface (FFI) for AGK Language Compiler
Enables calling functions from external shared libraries (DLLs, SO files)
"""

import ctypes
import platform
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from agk_error_handler import AGKError, ErrorSeverity, ErrorCategory

@dataclass
class ExternalFunction:
    """Represents an external function declaration"""
    name: str
    parameters: List[str]
    return_type: str
    library_path: str
    library_handle: Optional[ctypes.CDLL] = None
    function_handle: Optional[ctypes.CDLL._FuncPtr] = None

class FFIError(Exception):
    """Custom exception for FFI-related errors"""
    pass

class AGKFFIManager:
    """Manages foreign function interface operations"""

    def __init__(self):
        self.loaded_libraries: Dict[str, ctypes.CDLL] = {}
        self.external_functions: Dict[str, ExternalFunction] = {}
        self.type_mappings = {
            'int': ctypes.c_int,
            'float': ctypes.c_float,
            'double': ctypes.c_double,
            'string': ctypes.c_char_p,
            'bool': ctypes.c_bool,
            'void': None,
            'char': ctypes.c_char,
            'long': ctypes.c_long,
            'short': ctypes.c_short
        }

    def load_library(self, lib_path: str) -> ctypes.CDLL:
        """
        Load a shared library (DLL or SO file)
        Handles platform-specific library naming conventions
        """
        if lib_path in self.loaded_libraries:
            return self.loaded_libraries[lib_path]

        # Handle platform-specific library extensions
        original_path = lib_path
        if not any(lib_path.endswith(ext) for ext in ['.dll', '.so', '.dylib']):
            if platform.system() == 'Windows':
                lib_path += '.dll'
            elif platform.system() == 'Darwin':
                lib_path += '.dylib'
            else:  # Linux and other Unix-like systems
                lib_path += '.so'

        # Try to find the library in common locations
        search_paths = [
            lib_path,
            os.path.join(os.getcwd(), lib_path),
            os.path.join(os.getcwd(), 'lib', lib_path),
            os.path.join(os.getcwd(), 'libs', lib_path)
        ]

        loaded_lib = None
        for path in search_paths:
            try:
                loaded_lib = ctypes.CDLL(path)
                self.loaded_libraries[original_path] = loaded_lib
                print(f"Successfully loaded library: {path}")
                break
            except OSError as e:
                continue

        if loaded_lib is None:
            raise FFIError(f"Could not load library '{original_path}'. Searched paths: {search_paths}")

        return loaded_lib

    def register_external_function(self, func_def: str) -> ExternalFunction:
        """
        Parse and register an external function declaration
        Expected format: "external function name(params) from 'lib' as return_type"
        """
        try:
            # Parse the function declaration
            parts = func_def.replace('external function', '').strip().split('from')
            if len(parts) != 2:
                raise FFIError("Invalid external function declaration format")

            func_signature = parts[0].strip()
            lib_and_return = parts[1].strip().split('as')
            if len(lib_and_return) != 2:
                raise FFIError("Missing return type specification")

            lib_path = lib_and_return[0].strip().strip('"').strip("'")
            return_type = lib_and_return[1].strip()

            # Parse function name and parameters
            func_name_end = func_signature.find('(')
            if func_name_end == -1:
                raise FFIError("Missing parameter list in function declaration")

            func_name = func_signature[:func_name_end].strip()
            params_str = func_signature[func_name_end:].strip('()')

            # Parse parameters
            parameters = []
            if params_str.strip():
                param_list = [p.strip() for p in params_str.split(',')]
                for param in param_list:
                    if ' as ' in param:
                        param_name = param.split(' as ')[0].strip()
                        parameters.append(param_name)
                    else:
                        parameters.append(param.strip())

            # Create external function object
            ext_func = ExternalFunction(
                name=func_name,
                parameters=parameters,
                return_type=return_type,
                library_path=lib_path
            )

            # Load the library
            ext_func.library_handle = self.load_library(lib_path)

            # Get function handle
            try:
                ext_func.function_handle = getattr(ext_func.library_handle, func_name)
            except AttributeError:
                raise FFIError(f"Function '{func_name}' not found in library '{lib_path}'")

            # Set return type
            if return_type.lower() != 'void':
                if return_type in self.type_mappings:
                    ext_func.function_handle.restype = self.type_mappings[return_type]
                else:
                    raise FFIError(f"Unsupported return type: {return_type}")

            # Set argument types (simplified - assuming all params are strings for now)
            if parameters:
                ext_func.function_handle.argtypes = [ctypes.c_char_p] * len(parameters)

            self.external_functions[func_name] = ext_func
            return ext_func

        except Exception as e:
            raise FFIError(f"Error registering external function: {str(e)}")

    def call_external_function(self, func_name: str, args: List[Any]) -> Any:
        """
        Call an external function with the given arguments
        """
        if func_name not in self.external_functions:
            raise FFIError(f"External function '{func_name}' not registered")

        ext_func = self.external_functions[func_name]

        if len(args) != len(ext_func.parameters):
            raise FFIError(f"Function '{func_name}' expects {len(ext_func.parameters)} arguments, got {len(args)}")

        # Convert arguments to appropriate types
        converted_args = []
        for arg in args:
            if isinstance(arg, str):
                converted_args.append(arg.encode('utf-8'))
            elif isinstance(arg, (int, float, bool)):
                converted_args.append(arg)
            else:
                converted_args.append(str(arg).encode('utf-8'))

        try:
            result = ext_func.function_handle(*converted_args)

            # Handle return value conversion
            if ext_func.return_type.lower() == 'string':
                if isinstance(result, bytes):
                    return result.decode('utf-8')
                return str(result)
            elif ext_func.return_type.lower() in ['int', 'float', 'double', 'bool']:
                return result
            else:
                return result

        except Exception as e:
            raise FFIError(f"Error calling external function '{func_name}': {str(e)}")

    def get_external_function_info(self, func_name: str) -> Optional[ExternalFunction]:
        """Get information about a registered external function"""
        return self.external_functions.get(func_name)

    def list_external_functions(self) -> List[str]:
        """Get list of all registered external function names"""
        return list(self.external_functions.keys())

    def unload_library(self, lib_path: str) -> bool:
        """
        Unload a library and remove all its functions
        Note: This is mainly for cleanup - Python's ctypes doesn't always
        allow unloading libraries on all platforms
        """
        if lib_path in self.loaded_libraries:
            # Remove all functions from this library
            functions_to_remove = [
                name for name, func in self.external_functions.items()
                if func.library_path == lib_path
            ]

            for func_name in functions_to_remove:
                del self.external_functions[func_name]

            del self.loaded_libraries[lib_path]
            return True
        return False

# Global FFI manager instance
ffi_manager = AGKFFIManager()

# Convenience functions for use in generated code
def register_external_function(func_def: str) -> ExternalFunction:
    """Register an external function (for use in generated Python code)"""
    return ffi_manager.register_external_function(func_def)

def call_external_function(func_name: str, args: List[Any]) -> Any:
    """Call an external function (for use in generated Python code)"""
    return ffi_manager.call_external_function(func_name, args)

def get_external_function_info(func_name: str) -> Optional[ExternalFunction]:
    """Get external function info (for use in generated Python code)"""
    return ffi_manager.get_external_function_info(func_name)

# Example external library for testing (if available)
def create_example_library():
    """Create a simple example shared library for testing"""
    # This would normally be a compiled C library
    # For demonstration, we'll create a mock
    pass