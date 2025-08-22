#!/usr/bin/env python3
"""
AGK Language REPL (Read-Eval-Print Loop)

Interactive shell for AGK programming language experimentation.
"""

import sys
import os
from typing import Optional
from agk_lexer import AGKLexer
from agk_parser import AGKParser
from agk_semantic import SemanticAnalyzer
from agk_codegen import CodeGenerator
from agk_error_handler import ErrorHandler, ErrorSeverity


class AGKREPL:
    """Interactive REPL for AGK language"""

    def __init__(self):
        self.compiler = None
        self.error_handler = ErrorHandler()
        self.history = []
        self.session_count = 0

    def start(self):
        """Start the REPL session"""
        print("AGK Language Interactive Shell")
        print("=====================================")
        print("Type 'help' for commands, 'quit' to exit")
        print("Write natural language code and see Python output!")
        print("=====================================")

        while True:
            try:
                # Get user input
                user_input = self.get_input()

                if not user_input:
                    continue

                # Process special commands
                if self.handle_special_commands(user_input):
                    continue

                # Compile and execute
                self.compile_and_execute(user_input)

            except KeyboardInterrupt:
                print("\n\nExiting AGK REPL...")
                break
            except EOFError:
                print("\n\nExiting AGK REPL...")
                break
            except Exception as e:
                print(f"\nREPL Error: {e}")
                continue

    def get_input(self) -> str:
        """Get user input with session counter"""
        self.session_count += 1
        try:
            return input(f"agk[{self.session_count}]> ").strip()
        except (EOFError, KeyboardInterrupt):
            return "quit"

    def handle_special_commands(self, command: str) -> bool:
        """Handle special REPL commands"""
        command_lower = command.lower()

        if command_lower in ['quit', 'exit', 'q']:
            print("Goodbye! Thanks for using AGK!")
            sys.exit(0)
            return True

        elif command_lower in ['help', 'h']:
            self.show_help()
            return True

        elif command_lower in ['clear', 'cls']:
            os.system('clear' if os.name != 'nt' else 'cls')
            return True

        elif command_lower == 'history':
            self.show_history()
            return True

        elif command_lower.startswith('load '):
            filename = command[5:].strip()
            return self.load_file(filename)

        return False

    def show_help(self):
        """Show help information"""
        help_text = """
AGK Language REPL - Help
========================

COMMANDS:
  help, h     - Show this help
  quit, exit  - Exit the REPL
  clear, cls  - Clear the screen
  history     - Show command history
  load <file> - Load and execute an AGK file

AGK SYNTAX EXAMPLES:
  Basic:
    create x as Integer
    set x to 42
    return x + 10

  With imports:
    import math
    create result as Float
    set result to math.sqrt(16.0)

  Functions:
    define function greet that takes name as String and returns String:
        return "Hello, " + name + "!"

  Conditionals:
    if x is greater than 10:
        return "Big number!"
    else:
        return "Small number!"

LIBRARIES AVAILABLE:
  Core: math, string, list, io
  Advanced: llm (AI), gto (game theory), web (full-stack)
  Business: date (time), finance (calculations)

The REPL will compile your AGK code to Python and show the result!
"""
        print(help_text)

    def show_history(self):
        """Show command history"""
        if not self.history:
            print("No history available")
            return

        print("Command History:")
        print("================")
        for i, cmd in enumerate(self.history[-10:], 1):  # Show last 10
            print("2d")

    def load_file(self, filename: str) -> bool:
        """Load and execute an AGK file"""
        try:
            with open(filename, 'r') as f:
                content = f.read()

            print(f"Loading file: {filename}")
            print("=" * 50)
            print(content)
            print("=" * 50)

            self.compile_and_execute(content)
            return True

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
        except Exception as e:
            print(f"Error loading file: {e}")

        return True

    def compile_and_execute(self, source_code: str):
        """Compile and execute AGK code"""
        try:
            # Clear previous errors
            self.error_handler.clear()

            # Add to history
            self.history.append(source_code)

            # Special handling for single expressions
            if not source_code.startswith('define') and '=' not in source_code:
                # Wrap simple expressions in a function
                source_code = f"""
define function temp_result:
    {source_code}
"""

            print("Compiling...")
            print("-" * 30)

            # Phase 1: Lexical Analysis
            lexer = AGKLexer(source_code)
            tokens = lexer.tokenize()

            # Phase 2: Parsing
            parser = AGKParser(tokens)
            ast = parser.parse()

            # Phase 3: Semantic Analysis
            analyzer = SemanticAnalyzer()
            success = analyzer.analyze(ast)

            if not success:
                print("SEMANTIC ERRORS:")
                for error in analyzer.get_errors():
                    print(f"  ERROR: {error}")
                for warning in analyzer.get_warnings():
                    print(f"  WARNING: {warning}")
                return

            # Phase 4: Code Generation
            generator = CodeGenerator()
            generated_code = generator.generate(ast)

            print("Generated Python Code:")
            print("-" * 30)
            print(generated_code)

            # Try to execute the generated code safely
            if self.should_execute(generated_code):
                print("-" * 30)
                print("Execution Result:")
                self.execute_python_code(generated_code)

        except Exception as e:
            print(f"COMPILATION ERROR: {e}")

    def should_execute(self, python_code: str) -> bool:
        """Determine if the generated code should be executed"""
        # Don't execute code with imports or complex structures
        dangerous_patterns = [
            'import ', 'from ', 'class ', 'def ',
            'open(', 'exec(', 'eval(', 'system(',
            'subprocess', 'os.', 'sys.'
        ]

        for pattern in dangerous_patterns:
            if pattern in python_code:
                return False

        return True

    def execute_python_code(self, python_code: str):
        """Safely execute generated Python code"""
        try:
            # Create a safe execution environment
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'abs': abs,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                }
            }

            # Execute the code
            exec(python_code, safe_globals)

            # Look for function results
            if 'temp_result' in safe_globals:
                result = safe_globals['temp_result']()
                print(f"Result: {result}")
            elif 'result' in safe_globals:
                print(f"Result: {safe_globals['result']}")

        except Exception as e:
            print(f"Execution error: {e}")


def create_api_key_manager():
    """Create API key management system"""
    api_keys = {}

    def set_api_key(service: str, key: str):
        """Set API key for a service"""
        api_keys[service.lower()] = key
        print(f"API key set for {service}")

    def get_api_key(service: str) -> Optional[str]:
        """Get API key for a service"""
        return api_keys.get(service.lower())

    def list_services():
        """List available services"""
        return list(api_keys.keys())

    def remove_api_key(service: str):
        """Remove API key for a service"""
        if service.lower() in api_keys:
            del api_keys[service.lower()]
            print(f"API key removed for {service}")

    return {
        'set': set_api_key,
        'get': get_api_key,
        'list': list_services,
        'remove': remove_api_key
    }


# Global API key manager
api_key_manager = create_api_key_manager()


def enhanced_repl():
    """Enhanced REPL with API key management"""
    print("AGK Language Enhanced REPL")
    print("==========================")
    print("Commands:")
    print("  help, h           - Show help")
    print("  quit, exit        - Exit REPL")
    print("  api set <svc> <key> - Set API key")
    print("  api get <svc>     - Get API key")
    print("  api list          - List services")
    print("  api remove <svc>  - Remove API key")
    print("==========================")

    repl = AGKREPL()

    while True:
        try:
            user_input = repl.get_input()

            if not user_input:
                continue

            # Handle API key commands
            if user_input.startswith('api '):
                parts = user_input.split()
                if len(parts) >= 2:
                    command = parts[1]

                    if command == 'set' and len(parts) >= 4:
                        service = parts[2]
                        key = parts[3]
                        api_key_manager['set'](service, key)
                    elif command == 'get' and len(parts) >= 3:
                        service = parts[2]
                        key = api_key_manager['get'](service)
                        if key:
                            print(f"API key for {service}: {key[:8]}...")
                        else:
                            print(f"No API key set for {service}")
                    elif command == 'list':
                        services = api_key_manager['list']()
                        if services:
                            print("Available services:", ', '.join(services))
                        else:
                            print("No API keys set")
                    elif command == 'remove' and len(parts) >= 3:
                        service = parts[2]
                        api_key_manager['remove'](service)
                continue

            # Handle other special commands
            if repl.handle_special_commands(user_input):
                continue

            # Compile and execute AGK code
            repl.compile_and_execute(user_input)

        except KeyboardInterrupt:
            print("\n\nExiting AGK REPL...")
            break
        except EOFError:
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--enhanced":
        enhanced_repl()
    else:
        repl = AGKREPL()
        repl.start()