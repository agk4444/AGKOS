#!/usr/bin/env python3
"""
AGK Language Compiler

Main compiler that combines all components: lexer, parser, semantic analyzer, and code generator.
"""

import sys
from typing import Optional
from agk_lexer import AGKLexer
from agk_parser import AGKParser
from agk_semantic import SemanticAnalyzer
from agk_codegen import CodeGenerator


class AGKCompiler:
    """Main AGK compiler class"""

    def __init__(self, target_platform: str = "python"):
        self.target_platform = target_platform
        self.lexer = None
        self.parser = None
        self.analyzer = None
        self.generator = None
        self.errors = []
        self.warnings = []

    def compile(self, source_code: str, output_file: Optional[str] = None) -> bool:
        """
        Compile AGK source code to target language

        Args:
            source_code: The AGK source code to compile
            output_file: Optional output file path

        Returns:
            bool: True if compilation successful, False otherwise
        """
        self.errors = []
        self.warnings = []

        try:
            # Phase 1: Lexical Analysis
            print("Phase 1: Lexical Analysis...")
            self.lexer = AGKLexer(source_code)
            tokens = self.lexer.tokenize()

            # Phase 2: Parsing
            print("Phase 2: Parsing...")
            self.parser = AGKParser(tokens)
            ast = self.parser.parse()

            # Phase 3: Semantic Analysis
            print("Phase 3: Semantic Analysis...")
            self.analyzer = SemanticAnalyzer()
            semantic_success = self.analyzer.analyze(ast)

            if not semantic_success:
                self.errors.extend(self.analyzer.get_errors())

            self.warnings.extend(self.analyzer.get_warnings())

            # Phase 4: Code Generation
            print("Phase 4: Code Generation...")
            print(f"Target platform: {self.target_platform}")
            self.generator = CodeGenerator(self.target_platform)
            generated_code = self.generator.generate(ast)

            # Output results
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(generated_code)
                print(f"SUCCESS: Compilation successful! Output written to {output_file}")
            else:
                print("Generated Code:")
                print("=" * 50)
                print(generated_code)

            # Report warnings
            if self.warnings:
                print(f"\nWarnings ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(f"  WARNING: {warning}")

            # Report errors (but don't fail if only warnings)
            if self.errors:
                print(f"\nErrors ({len(self.errors)}):")
                for error in self.errors:
                    print(f"  ERROR: {error}")
                return False

            return True

        except Exception as e:
            self.errors.append(f"Compilation error: {e}")
            print(f"ERROR: Compilation failed: {e}")
            return False

    def get_errors(self) -> list:
        """Get compilation errors"""
        return self.errors

    def get_warnings(self) -> list:
        """Get compilation warnings"""
        return self.warnings


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python agk_compiler.py <source_file> [output_file] [--platform <platform>]")
        print("       python agk_compiler.py --repl [--platform <platform>]")
        print("Platforms: python, javascript, kotlin, swift, cpp, csharp")
        print("          wearable, tv, automotive")
        sys.exit(1)

    # Parse platform argument
    target_platform = "python"  # default
    args = sys.argv[1:]

    if "--platform" in args:
        platform_index = args.index("--platform")
        if platform_index + 1 < len(args):
            target_platform = args[platform_index + 1]
            # Remove platform args from list
            args = args[:platform_index] + args[platform_index + 2:]
        else:
            print("ERROR: --platform requires a value")
            sys.exit(1)

    if len(args) == 0:
        print("ERROR: No source file specified")
        sys.exit(1)

    if args[0] == "--repl":
        run_repl(target_platform)
        return

    source_file = args[0]
    output_file = args[1] if len(args) > 1 else None

    try:
        with open(source_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"ERROR: Source file '{source_file}' not found")
        sys.exit(1)

    print(f"Compiling AGK source file: {source_file}")
    print(f"Target platform: {target_platform}")
    print("=" * 50)

    compiler = AGKCompiler(target_platform)
    success = compiler.compile(source_code, output_file)

    if success:
        print("\nSUCCESS: Compilation completed successfully!")
    else:
        print(f"\nERROR: Compilation failed with {len(compiler.get_errors())} errors")
        sys.exit(1)


def run_repl(target_platform: str = "python"):
    """Run interactive REPL mode"""
    print("AGK Language REPL")
    print(f"Target platform: {target_platform}")
    print("Type 'quit' or 'exit' to exit")
    print("=" * 30)

    compiler = AGKCompiler(target_platform)

    while True:
        try:
            source = input("agk> ").strip()

            if source.lower() in ['quit', 'exit', 'q']:
                break
            elif source.lower() in ['help', 'h']:
                print("AGK Language Help:")
                print("  - Use natural language syntax")
                print("  - Examples:")
                print("    define function hello: return 'Hello World'")
                print("    create x as Integer")
                print("    set x to 42")
                continue
            elif not source:
                continue

            # Add proper structure for single expressions
            if not source.startswith('define') and '=' not in source:
                source = f"define function temp: {source}"

            print("Compiling...")
            success = compiler.compile(source)

            if success:
                print("SUCCESS")
            else:
                for error in compiler.get_errors():
                    print(f"ERROR: {error}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()