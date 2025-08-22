#!/usr/bin/env python3
"""
AGK Language Test Framework

Simple testing framework for AGK compiler and libraries.
"""

import os
import sys
import subprocess
from typing import List, Dict, Tuple
from agk_error_handler import ErrorHandler, ErrorType, ErrorSeverity, SourceLocation


class TestResult:
    """Result of a single test"""

    def __init__(self, test_name: str, passed: bool, message: str = "", execution_time: float = 0.0):
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.execution_time = execution_time

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"{status} {self.test_name}: {self.message}"


class TestSuite:
    """Collection of tests"""

    def __init__(self, name: str):
        self.name = name
        self.tests: List[TestResult] = []
        self.start_time = 0
        self.end_time = 0

    def add_test(self, result: TestResult):
        """Add a test result"""
        self.tests.append(result)

    def get_passed_count(self) -> int:
        """Get number of passed tests"""
        return len([t for t in self.tests if t.passed])

    def get_failed_count(self) -> int:
        """Get number of failed tests"""
        return len([t for t in self.tests if not t.passed])

    def get_total_count(self) -> int:
        """Get total number of tests"""
        return len(self.tests)

    def print_results(self):
        """Print test results"""
        print(f"\n{'='*60}")
        print(f"TEST SUITE: {self.name}")
        print(f"{'='*60}")

        if not self.tests:
            print("No tests found!")
            return

        for test in self.tests:
            print(f"  {test}")

        print(f"{'='*60}")
        passed = self.get_passed_count()
        failed = self.get_failed_count()
        total = self.get_total_count()

        if failed == 0:
            print(f"SUCCESS: ALL TESTS PASSED! ({passed}/{total})")
        else:
            print(f"WARNING: {passed}/{total} tests passed, {failed} failed")

        print(f"{'='*60}")


class AGKTestFramework:
    """Test framework for AGK compiler"""

    def __init__(self):
        self.test_suites: Dict[str, TestSuite] = {}

    def create_suite(self, name: str) -> TestSuite:
        """Create a new test suite"""
        suite = TestSuite(name)
        self.test_suites[name] = suite
        return suite

    def test_compilation(self, suite: TestSuite, test_name: str, agk_code: str, should_pass: bool = True) -> TestResult:
        """Test compilation of AGK code"""

        # Write test code to temporary file
        temp_file = f"temp_test_{test_name}.agk"
        try:
            with open(temp_file, 'w') as f:
                f.write(agk_code)

            # Try to compile
            result = subprocess.run([
                sys.executable, "agk_compiler.py", temp_file
            ], capture_output=True, text=True, timeout=10)

            # Check if compilation result matches expectation
            if should_pass:
                passed = result.returncode == 0
                message = "Compilation succeeded" if passed else f"Compilation failed: {result.stderr}"
            else:
                passed = result.returncode != 0
                message = "Compilation correctly failed" if passed else "Compilation should have failed"

        except subprocess.TimeoutExpired:
            passed = False
            message = "Compilation timed out"
        except Exception as e:
            passed = False
            message = f"Test error: {e}"
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)

        result = TestResult(test_name, passed, message)
        suite.add_test(result)
        return result

    def test_library_import(self, suite: TestSuite, test_name: str, library_name: str) -> TestResult:
        """Test importing a library"""

        agk_code = f"""
import {library_name}

define function test_{library_name}_import:
    return "Import test for {library_name}"
"""

        return self.test_compilation(suite, test_name, agk_code, should_pass=True)

    def test_library_function(self, suite: TestSuite, test_name: str, library_code: str) -> TestResult:
        """Test a library function"""

        agk_code = f"""
{library_code}

define function test_function:
    return "Library function test"
"""

        return self.test_compilation(suite, test_name, agk_code, should_pass=True)

    def test_syntax_error(self, suite: TestSuite, test_name: str, invalid_code: str) -> TestResult:
        """Test that invalid syntax is properly caught"""

        return self.test_compilation(suite, test_name, invalid_code, should_pass=False)

    def test_semantic_error(self, suite: TestSuite, test_name: str, code_with_error: str) -> TestResult:
        """Test that semantic errors are properly caught"""

        return self.test_compilation(suite, test_name, code_with_error, should_pass=False)

    def run_all_tests(self):
        """Run all test suites"""
        print("AGK Language Test Framework")
        print("=" * 60)

        for suite_name, suite in self.test_suites.items():
            suite.print_results()

        # Print summary
        total_passed = sum(suite.get_passed_count() for suite in self.test_suites.values())
        total_failed = sum(suite.get_failed_count() for suite in self.test_suites.values())
        total_tests = sum(suite.get_total_count() for suite in self.test_suites.values())

        print(f"\nOVERALL SUMMARY")
        print(f"{'='*60}")
        print(f"Total test suites: {len(self.test_suites)}")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")

        if total_failed == 0:
            print("SUCCESS: All tests passed!")
        else:
            print(f"WARNING: {total_failed} test(s) failed")

        print(f"{'='*60}")


def run_basic_tests():
    """Run basic compiler tests"""

    framework = AGKTestFramework()

    # Test basic functionality
    basic_suite = framework.create_suite("Basic Compiler Tests")

    # Test 1: Simple function
    framework.test_compilation(basic_suite, "simple_function",
        """
        define function hello:
            return "Hello World"
        """)

    # Test 2: Variable declarations
    framework.test_compilation(basic_suite, "variable_declaration",
        """
        define function test_vars:
            create x as Integer
            set x to 42
            return x
        """)

    # Test 3: Function with parameters
    framework.test_compilation(basic_suite, "function_parameters",
        """
        define function add that takes a as Integer, b as Integer and returns Integer:
            return a + b
        """)

    # Test library imports
    library_suite = framework.create_suite("Library Import Tests")

    # Test standard libraries
    libraries = ["math", "string", "list", "io"]
    for lib in libraries:
        framework.test_library_import(library_suite, f"import_{lib}", lib)

    # Test advanced libraries
    advanced_libs = ["date", "finance", "llm", "gto", "web"]
    for lib in advanced_libs:
        framework.test_library_import(library_suite, f"import_{lib}", lib)

    # Test error handling
    error_suite = framework.create_suite("Error Handling Tests")

    # Test syntax errors
    framework.test_syntax_error(error_suite, "invalid_syntax",
        """
        define function broken(
            return "missing colon"
        """)

    # Test undefined variable
    framework.test_semantic_error(error_suite, "undefined_variable",
        """
        define function test:
            set x to 42
            return x
        """)

    # Test library functions
    lib_func_suite = framework.create_suite("Library Function Tests")

    # Test math functions
    framework.test_library_function(lib_func_suite, "math_sqrt",
        """
        import math
        define function test_sqrt:
            create result as Float
            set result to math.sqrt(16.0)
            return result
        """)

    # Test string functions
    framework.test_library_function(lib_func_suite, "string_uppercase",
        """
        import string
        define function test_uppercase:
            create result as String
            set result to string.uppercase("hello")
            return result
        """)

    # Test date functions
    framework.test_library_function(lib_func_suite, "date_today",
        """
        import date
        define function test_date:
            create today as Date
            set today to date.today()
            return "Date test completed"
        """)

    # Test finance functions
    framework.test_library_function(lib_func_suite, "finance_compound",
        """
        import finance
        define function test_finance:
            create result as Float
            set result to finance.compound_interest(1000.0, 0.05, 5.0, 12)
            return result
        """)

    # Run all tests
    framework.run_all_tests()


def run_library_documentation_tests():
    """Test that all libraries are properly documented"""

    framework = AGKTestFramework()
    doc_suite = framework.create_suite("Library Documentation Tests")

    # Check if all library files exist and are non-empty
    libraries = {
        "math": "Mathematical functions and constants",
        "string": "String manipulation functions",
        "list": "List operations and utilities",
        "io": "Input/output functions",
        "date": "Date and time manipulation functions",
        "finance": "Financial calculations and investment analysis",
        "llm": "Large Language Model integration",
        "gto": "Game Theory Optimization algorithms",
        "web": "Web interface and HTTP capabilities"
    }

    for lib_name, description in libraries.items():
        lib_file = f"stdlib/{lib_name}.agk"

        if os.path.exists(lib_file):
            with open(lib_file, 'r') as f:
                content = f.read()
                if len(content.strip()) > 0:
                    framework.test_compilation(doc_suite, f"{lib_name}_documentation",
                        f"import {lib_name}\ndefine function test: return '{lib_name} imported successfully'")
                else:
                    result = TestResult(f"{lib_name}_documentation", False, "Library file is empty")
                    doc_suite.add_test(result)
        else:
            result = TestResult(f"{lib_name}_documentation", False, f"Library file {lib_file} not found")
            doc_suite.add_test(result)

    doc_suite.print_results()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--doc":
        run_library_documentation_tests()
    else:
        run_basic_tests()