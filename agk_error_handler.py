#!/usr/bin/env python3
"""
AGK Language Error Handler

Comprehensive error handling and reporting system for the AGK compiler.
"""

from typing import List, Optional, Dict
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class ErrorType(Enum):
    """Types of errors that can occur"""
    LEXICAL = "Lexical Error"
    SYNTAX = "Syntax Error"
    SEMANTIC = "Semantic Error"
    TYPE = "Type Error"
    RUNTIME = "Runtime Error"
    IMPORT = "Import Error"
    LIBRARY = "Library Error"
    COMPILATION = "Compilation Error"


class SourceLocation:
    """Represents a location in source code"""
    def __init__(self, filename: str, line: int, column: int):
        self.filename = filename
        self.line = line
        self.column = column

    def __str__(self):
        return f"{self.filename}:{self.line}:{self.column}"


class AGKError:
    """Represents an error in the AGK compilation process"""

    def __init__(self,
                 error_type: ErrorType,
                 severity: ErrorSeverity,
                 message: str,
                 location: Optional[SourceLocation] = None,
                 context: Optional[str] = None,
                 suggestion: Optional[str] = None):
        self.error_type = error_type
        self.severity = severity
        self.message = message
        self.location = location
        self.context = context
        self.suggestion = suggestion
        self.timestamp = None  # Could add timestamp if needed

    def __str__(self):
        """String representation of the error"""
        parts = []

        # Severity and type
        parts.append(f"[{self.severity.value}] {self.error_type.value}")

        # Location
        if self.location:
            parts.append(f"at {self.location}")

        # Message
        parts.append(f": {self.message}")

        # Context
        if self.context:
            parts.append(f"\nContext: {self.context}")

        # Suggestion
        if self.suggestion:
            parts.append(f"\nSuggestion: {self.suggestion}")

        return "".join(parts)

    def to_dict(self) -> Dict:
        """Convert error to dictionary representation"""
        return {
            'type': self.error_type.value,
            'severity': self.severity.value,
            'message': self.message,
            'location': str(self.location) if self.location else None,
            'context': self.context,
            'suggestion': self.suggestion
        }


class ErrorHandler:
    """Central error handling system for AGK compiler"""

    def __init__(self):
        self.errors: List[AGKError] = []
        self.warnings: List[AGKError] = []
        self.max_errors = 100  # Prevent memory issues with too many errors

    def add_error(self,
                  error_type: ErrorType,
                  message: str,
                  location: Optional[SourceLocation] = None,
                  context: Optional[str] = None,
                  suggestion: Optional[str] = None) -> None:
        """Add an error to the error list"""

        if len(self.errors) >= self.max_errors:
            return  # Don't add more errors if we've hit the limit

        error = AGKError(error_type, ErrorSeverity.ERROR, message, location, context, suggestion)
        self.errors.append(error)

    def add_warning(self,
                    error_type: ErrorType,
                    message: str,
                    location: Optional[SourceLocation] = None,
                    context: Optional[str] = None,
                    suggestion: Optional[str] = None) -> None:
        """Add a warning to the warning list"""

        warning = AGKError(error_type, ErrorSeverity.WARNING, message, location, context, suggestion)
        self.warnings.append(warning)

    def add_info(self,
                 error_type: ErrorType,
                 message: str,
                 location: Optional[SourceLocation] = None,
                 context: Optional[str] = None) -> None:
        """Add an info message"""

        info = AGKError(error_type, ErrorSeverity.INFO, message, location, context)
        self.warnings.append(info)  # Info messages go in warnings list

    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0

    def get_error_count(self) -> int:
        """Get the number of errors"""
        return len(self.errors)

    def get_warning_count(self) -> int:
        """Get the number of warnings"""
        return len(self.warnings)

    def clear(self) -> None:
        """Clear all errors and warnings"""
        self.errors.clear()
        self.warnings.clear()

    def get_all_messages(self) -> List[AGKError]:
        """Get all errors and warnings combined"""
        return self.errors + self.warnings

    def get_errors_by_type(self, error_type: ErrorType) -> List[AGKError]:
        """Get errors of a specific type"""
        return [error for error in self.errors if error.error_type == error_type]

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[AGKError]:
        """Get errors of a specific severity"""
        return [error for error in (self.errors + self.warnings) if error.severity == severity]

    def print_errors(self, show_warnings: bool = True) -> None:
        """Print all errors and optionally warnings"""
        if not self.errors and not (show_warnings and self.warnings):
            return

        print("\n" + "="*60)
        print("AGK COMPILER MESSAGES")
        print("="*60)

        # Print errors
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            print("-" * 40)
            for i, error in enumerate(self.errors, 1):
                print(f"{i:2d}. {error}")

        # Print warnings
        if show_warnings and self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            print("-" * 40)
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i:2d}. {warning}")

        print("="*60)

    def print_summary(self) -> None:
        """Print a summary of errors and warnings"""
        if not self.errors and not self.warnings:
            print("✅ Compilation successful - no errors or warnings!")
            return

        error_count = len(self.errors)
        warning_count = len(self.warnings)

        if error_count > 0:
            print(f"❌ Compilation failed with {error_count} error(s)" +
                  (f" and {warning_count} warning(s)" if warning_count > 0 else ""))
        elif warning_count > 0:
            print(f"⚠️  Compilation successful with {warning_count} warning(s)")

    def get_error_report(self) -> str:
        """Generate a detailed error report as a string"""
        report_lines = []
        report_lines.append("AGK Compiler Error Report")
        report_lines.append("=" * 50)

        if self.errors:
            report_lines.append(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                report_lines.append(f"  - {error}")

        if self.warnings:
            report_lines.append(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                report_lines.append(f"  - {warning}")

        return "\n".join(report_lines)


# Predefined error messages and suggestions
class ErrorMessages:
    """Common error messages and suggestions"""

    @staticmethod
    def undefined_variable(name: str) -> tuple:
        return (
            f"Variable '{name}' not declared",
            f"Make sure to declare '{name}' with 'create {name} as Type' before using it"
        )

    @staticmethod
    def undefined_function(name: str) -> tuple:
        return (
            f"Function '{name}' not declared",
            f"Define function '{name}' with 'define function {name} that takes ...' or import it"
        )

    @staticmethod
    def type_mismatch(expected: str, actual: str) -> tuple:
        return (
            f"Type mismatch: expected {expected}, got {actual}",
            "Check the types of your variables and function return values"
        )

    @staticmethod
    def import_error(module: str) -> tuple:
        return (
            f"Cannot import module '{module}'",
            f"Make sure '{module}.agk' exists in the stdlib/ directory"
        )

    @staticmethod
    def syntax_error(token: str) -> tuple:
        return (
            f"Syntax error near '{token}'",
            "Check your AGK syntax and make sure all statements are properly formed"
        )

    @staticmethod
    def indentation_error() -> tuple:
        return (
            "Indentation error",
            "AGK uses indentation to define code blocks - make sure your indentation is consistent"
        )


# Integration with existing compiler components
def create_location(filename: str, line: int, column: int) -> SourceLocation:
    """Helper function to create a SourceLocation"""
    return SourceLocation(filename, line, column)


def report_lexical_error(handler: ErrorHandler, message: str, location: SourceLocation):
    """Report a lexical error"""
    handler.add_error(
        ErrorType.LEXICAL,
        message,
        location,
        suggestion="Check your syntax and make sure all tokens are valid"
    )


def report_syntax_error(handler: ErrorHandler, message: str, location: SourceLocation):
    """Report a syntax error"""
    handler.add_error(
        ErrorType.SYNTAX,
        message,
        location,
        suggestion="Review your AGK syntax and ensure all statements are properly formed"
    )


def report_semantic_error(handler: ErrorHandler, message: str, location: Optional[SourceLocation] = None, suggestion: str = ""):
    """Report a semantic error"""
    handler.add_error(
        ErrorType.SEMANTIC,
        message,
        location,
        suggestion=suggestion
    )


def report_type_error(handler: ErrorHandler, message: str, location: Optional[SourceLocation] = None):
    """Report a type error"""
    handler.add_error(
        ErrorType.TYPE,
        message,
        location,
        suggestion="Check variable types and ensure type compatibility"
    )


def report_import_error(handler: ErrorHandler, module: str, location: Optional[SourceLocation] = None):
    """Report an import error"""
    message, suggestion = ErrorMessages.import_error(module)
    handler.add_error(
        ErrorType.IMPORT,
        message,
        location,
        suggestion=suggestion
    )