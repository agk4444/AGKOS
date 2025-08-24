#!/usr/bin/env python3
"""
AGK Language Code Generator

Generates target code from the validated AST for multiple platforms.
"""

from typing import Dict, List, Optional, Set
from agk_ast import (
    ASTNode, Program, Import, TypeNode, Parameter, FunctionDef, ExternalFunctionDef, ClassDef,
    ConstructorDef, InterfaceDef, VariableDecl, Assignment, IfStatement,
    ForStatement, WhileStatement, ReturnStatement, BreakStatement,
    ContinueStatement, TryCatchStatement, ThrowStatement, BinaryOp,
    UnaryOp, FunctionCall, AttributeAccess, ArrayAccess, Literal,
    Variable, This, ListLiteral, DictLiteral, NewExpression
)


class CodeGenerator:
    """Generates target code from AST for multiple platforms"""

    # Supported platforms
    PLATFORM_PYTHON = "python"
    PLATFORM_JAVASCRIPT = "javascript"
    PLATFORM_KOTLIN = "kotlin"  # For Android wearables
    PLATFORM_SWIFT = "swift"    # For iOS wearables
    PLATFORM_CPP = "cpp"        # For automotive systems
    PLATFORM_CSHARP = "csharp"  # For Windows/Universal apps

    def __init__(self, target_platform: str = PLATFORM_PYTHON):
        self.target_platform = target_platform
        self.indent_level = 0
        self.output = []
        self.temp_counter = 0
        self.platform_imports = []
        self.platform_setup = []

    def generate(self, program: Program) -> str:
        """Main code generation method"""
        self.output = []
        self.indent_level = 0
        self.platform_imports = []
        self.platform_setup = []

        # Generate platform-specific header
        self.generate_header()

        # Generate platform-specific imports
        self.generate_platform_imports(program.imports)

        # Add platform-specific setup code
        self.generate_platform_setup()

        # Add FFI imports if external functions are used
        if self.has_external_functions(program):
            self.generate_ffi_imports()

        # Generate program statements
        for statement in program.statements:
            self.generate_statement(statement)

        # Add platform-specific footer
        self.generate_footer()

        return "\n".join(self.output)

    def generate_imports(self, imports: List[Import]):
        """Generate import statements"""
        for import_stmt in imports:
            if import_stmt.specific_imports:
                # from module import specific1, specific2
                specifics = ", ".join(import_stmt.specific_imports)
                self.add_line(f"from {import_stmt.module} import {specifics}")
            else:
                # import module [as alias]
                line = f"import {import_stmt.module}"
                if import_stmt.alias:
                    line += f" as {import_stmt.alias}"
                self.add_line(line)

        if imports:
            self.add_line("")

    def generate_ffi_imports(self):
        """Generate FFI-related imports"""
        self.add_line("from agk_ffi import register_external_function, call_external_function")
        self.add_line("")

    def has_external_functions(self, program: Program) -> bool:
        """Check if program contains external function definitions"""
        for statement in program.statements:
            if isinstance(statement, ExternalFunctionDef):
                return True
        return False

    def generate_statement(self, node: ASTNode):
        """Generate code for a statement"""
        if isinstance(node, FunctionDef):
            self.generate_function_def(node)
        elif isinstance(node, ExternalFunctionDef):
            self.generate_external_function_def(node)
        elif isinstance(node, ClassDef):
            self.generate_class_def(node)
        elif isinstance(node, InterfaceDef):
            self.generate_interface_def(node)
        elif isinstance(node, VariableDecl):
            self.generate_variable_decl(node)
        elif isinstance(node, Assignment):
            self.generate_assignment(node)
        elif isinstance(node, IfStatement):
            self.generate_if_statement(node)
        elif isinstance(node, ForStatement):
            self.generate_for_statement(node)
        elif isinstance(node, WhileStatement):
            self.generate_while_statement(node)
        elif isinstance(node, ReturnStatement):
            self.generate_return_statement(node)
        elif isinstance(node, BreakStatement):
            self.generate_break_statement()
        elif isinstance(node, ContinueStatement):
            self.generate_continue_statement()
        elif isinstance(node, TryCatchStatement):
            self.generate_try_catch_statement(node)
        elif isinstance(node, ThrowStatement):
            self.generate_throw_statement(node)
        else:
            # Expression statement
            expr = self.generate_expression(node)
            if expr:
                self.add_line(f"{expr}")

    def generate_function_def(self, node: FunctionDef):
        """Generate function definition"""
        # Generate decorators
        for decorator in node.decorators:
            self.add_line(f"@{decorator}")

        # Generate function signature
        params = []
        for param in node.parameters:
            param_str = param.name
            if param.type_node:
                # Add type hint (Python style)
                param_str += f": {self.map_type(param.type_node)}"
            if param.default_value:
                default = self.generate_expression(param.default_value)
                param_str += f" = {default}"
            params.append(param_str)

        params_str = ", ".join(params)
        return_type = ""
        if node.return_type:
            return_type = f" -> {self.map_type(node.return_type)}"

        self.add_line(f"def {node.name}({params_str}){return_type}:")

        # Generate function body
        self.indent_level += 1
        for statement in node.body:
            self.generate_statement(statement)
        self.indent_level -= 1

        self.add_line("")

    def generate_external_function_def(self, node: ExternalFunctionDef):
        """Generate external function definition"""
        # Generate function registration
        func_def_str = f'"external function {node.name}('

        params = []
        for param in node.parameters:
            param_type = self.map_type(param.type_node) if param.type_node else "any"
            params.append(f'{param.name} as {param_type}')

        func_def_str += ', '.join(params)
        func_def_str += f') from \\"{node.library_path}\\" as {self.map_type(node.return_type)}"'

        self.add_line(f"register_external_function({func_def_str})")
        self.add_line("")

        # Generate Python function wrapper
        params = []
        for param in node.parameters:
            param_str = param.name
            if param.type_node:
                param_str += f": {self.map_type(param.type_node)}"
            params.append(param_str)

        params_str = ", ".join(params)
        return_type = f" -> {self.map_type(node.return_type)}" if node.return_type else ""

        self.add_line(f"def {node.name}({params_str}){return_type}:")
        self.indent_level += 1

        # Generate function body that calls the external function
        args = [param.name for param in node.parameters]
        args_str = ", ".join(args)

        if node.return_type and node.return_type.name.lower() != 'void':
            self.add_line(f"return call_external_function('{node.name}', [{args_str}])")
        else:
            self.add_line(f"call_external_function('{node.name}', [{args_str}])")

        self.indent_level -= 1
        self.add_line("")

    def generate_class_def(self, node: ClassDef):
        """Generate class definition"""
        # Generate inheritance
        base_classes = []
        if node.superclasses:
            base_classes.extend(node.superclasses)
        if node.interfaces:
            base_classes.extend(node.interfaces)

        inheritance = ""
        if base_classes:
            inheritance = f"({', '.join(base_classes)})"

        self.add_line(f"class {node.name}{inheritance}:")

        # Generate class body
        self.indent_level += 1

        # Generate fields as class variables
        for field in node.fields:
            if field.initializer:
                value = self.generate_expression(field.initializer)
                self.add_line(f"{field.name}: {self.map_type(field.type_node)} = {value}")
            else:
                self.add_line(f"{field.name}: {self.map_type(field.type_node)}")

        if node.fields:
            self.add_line("")

        # Generate constructor
        if node.constructors:
            for constructor in node.constructors:
                self.generate_constructor(constructor)
        else:
            # Generate default constructor
            self.add_line("def __init__(self):")
            self.indent_level += 1
            self.add_line("pass")
            self.indent_level -= 1
            self.add_line("")

        # Generate methods
        for method in node.methods:
            self.generate_function_def(method)

        self.indent_level -= 1
        self.add_line("")

    def generate_constructor(self, node: ConstructorDef):
        """Generate constructor"""
        params = ["self"]
        for param in node.parameters:
            param_str = param.name
            if param.type_node:
                param_str += f": {self.map_type(param.type_node)}"
            params.append(param_str)

        params_str = ", ".join(params)
        self.add_line(f"def __init__({params_str}):")
        self.indent_level += 1
        for statement in node.body:
            self.generate_statement(statement)
        self.indent_level -= 1
        self.add_line("")

    def generate_interface_def(self, node: InterfaceDef):
        """Generate interface definition (as abstract class)"""
        self.add_line(f"class {node.name}:")
        self.indent_level += 1
        self.add_line("\"\"\"Interface definition\"\"\"")
        self.add_line("pass")
        self.indent_level -= 1
        self.add_line("")

    def generate_variable_decl(self, node: VariableDecl):
        """Generate variable declaration"""
        if node.initializer:
            value = self.generate_expression(node.initializer)
            type_hint = ""
            if node.type_node:
                type_hint = f": {self.map_type(node.type_node)}"
            self.add_line(f"{node.name}{type_hint} = {value}")
        else:
            # Just declare with type
            type_hint = ""
            if node.type_node:
                type_hint = f": {self.map_type(node.type_node)}"
            self.add_line(f"{node.name}{type_hint}")

    def generate_assignment(self, node: Assignment):
        """Generate assignment statement"""
        target = self.generate_expression(node.target)
        value = self.generate_expression(node.value)
        self.add_line(f"{target} {node.operator} {value}")

    def generate_if_statement(self, node: IfStatement):
        """Generate if-elif-else statement"""
        # Generate if
        condition = self.generate_expression(node.condition)
        self.add_line(f"if {condition}:")

        self.indent_level += 1
        for statement in node.then_body:
            self.generate_statement(statement)
        self.indent_level -= 1

        # Generate elif branches
        for elif_condition, elif_body in node.elif_branches:
            condition = self.generate_expression(elif_condition)
            self.add_line(f"elif {condition}:")

            self.indent_level += 1
            for statement in elif_body:
                self.generate_statement(statement)
            self.indent_level -= 1

        # Generate else
        if node.else_body:
            self.add_line("else:")

            self.indent_level += 1
            for statement in node.else_body:
                self.generate_statement(statement)
            self.indent_level -= 1

    def generate_for_statement(self, node: ForStatement):
        """Generate for loop statement"""
        iterable = self.generate_expression(node.iterable)
        self.add_line(f"for {node.iterator} in {iterable}:")

        self.indent_level += 1
        for statement in node.body:
            self.generate_statement(statement)
        self.indent_level -= 1

    def generate_while_statement(self, node: WhileStatement):
        """Generate while loop statement"""
        condition = self.generate_expression(node.condition)
        self.add_line(f"while {condition}:")

        self.indent_level += 1
        for statement in node.body:
            self.generate_statement(statement)
        self.indent_level -= 1

    def generate_return_statement(self, node: ReturnStatement):
        """Generate return statement"""
        if node.value:
            value = self.generate_expression(node.value)
            self.add_line(f"return {value}")
        else:
            self.add_line("return")

    def generate_break_statement(self):
        """Generate break statement"""
        self.add_line("break")

    def generate_continue_statement(self):
        """Generate continue statement"""
        self.add_line("continue")

    def generate_try_catch_statement(self, node: TryCatchStatement):
        """Generate try-catch-finally statement"""
        self.add_line("try:")

        self.indent_level += 1
        for statement in node.try_body:
            self.generate_statement(statement)
        self.indent_level -= 1

        # Generate except clauses
        for exception_type, variable, catch_body in node.catch_clauses:
            except_clause = f"except {exception_type}"
            if variable:
                except_clause += f" as {variable}"
            self.add_line(except_clause + ":")

            self.indent_level += 1
            for statement in catch_body:
                self.generate_statement(statement)
            self.indent_level -= 1

        # Generate finally clause
        if node.finally_body:
            self.add_line("finally:")

            self.indent_level += 1
            for statement in node.finally_body:
                self.generate_statement(statement)
            self.indent_level -= 1

    def generate_throw_statement(self, node: ThrowStatement):
        """Generate throw statement"""
        exception = self.generate_expression(node.exception)
        self.add_line(f"raise {exception}")

    def generate_expression(self, node: ASTNode) -> str:
        """Generate code for an expression"""
        if isinstance(node, Literal):
            return self.generate_literal(node)
        elif isinstance(node, Variable):
            return node.name
        elif isinstance(node, BinaryOp):
            return self.generate_binary_op(node)
        elif isinstance(node, UnaryOp):
            return self.generate_unary_op(node)
        elif isinstance(node, FunctionCall):
            return self.generate_function_call(node)
        elif isinstance(node, AttributeAccess):
            return self.generate_attribute_access(node)
        elif isinstance(node, ArrayAccess):
            return self.generate_array_access(node)
        elif isinstance(node, This):
            return "self"
        elif isinstance(node, ListLiteral):
            return self.generate_list_literal(node)
        elif isinstance(node, DictLiteral):
            return self.generate_dict_literal(node)
        elif isinstance(node, NewExpression):
            return self.generate_new_expression(node)
        else:
            return str(node)

    def generate_literal(self, node: Literal) -> str:
        """Generate literal value"""
        if node.type_name == "string":
            return f'"{node.value}"'
        else:
            return str(node.value)

    def generate_binary_op(self, node: BinaryOp) -> str:
        """Generate binary operation"""
        left = self.generate_expression(node.left)
        right = self.generate_expression(node.right)
        return f"({left} {node.operator} {right})"

    def generate_unary_op(self, node: UnaryOp) -> str:
        """Generate unary operation"""
        operand = self.generate_expression(node.operand)
        return f"({node.operator}{operand})"

    def generate_function_call(self, node: FunctionCall) -> str:
        """Generate function call"""
        args = []
        for arg in node.arguments:
            args.append(self.generate_expression(arg))

        args_str = ", ".join(args)
        func_name = node.function

        if node.is_method:
            return f"{node.object_name}.{func_name}({args_str})"
        else:
            return f"{func_name}({args_str})"

    def generate_attribute_access(self, node: AttributeAccess) -> str:
        """Generate attribute access"""
        obj = self.generate_expression(node.object)
        return f"{obj}.{node.attribute}"

    def generate_array_access(self, node: ArrayAccess) -> str:
        """Generate array access"""
        array = self.generate_expression(node.array)
        index = self.generate_expression(node.index)
        return f"{array}[{index}]"

    def generate_list_literal(self, node: ListLiteral) -> str:
        """Generate list literal"""
        items = []
        for item in node.items:
            items.append(self.generate_expression(item))
        return f"[{', '.join(items)}]"

    def generate_dict_literal(self, node: DictLiteral) -> str:
        """Generate dictionary literal"""
        items = []
        for key, value in node.items:
            key_str = self.generate_expression(key)
            value_str = self.generate_expression(value)
            items.append(f"{key_str}: {value_str}")
        return f"{{{', '.join(items)}}}"

    def generate_new_expression(self, node: NewExpression) -> str:
        """Generate object instantiation"""
        args = []
        for arg in node.arguments:
            args.append(self.generate_expression(arg))
        args_str = ", ".join(args)
        return f"{node.class_name}({args_str})"

    def map_type(self, type_node: TypeNode) -> str:
        """Map AGK types to platform-specific types"""
        if not type_node:
            return self.get_platform_any_type()

        type_mapping = self.get_platform_type_mapping()
        base_type = type_mapping.get(type_node.name, type_node.name)

        if type_node.is_array:
            return self.get_platform_array_type(base_type)

        if type_node.generic_args:
            generic_strs = [self.map_type(arg) for arg in type_node.generic_args]
            return self.get_platform_generic_type(base_type, generic_strs)

        return base_type

    def get_platform_type_mapping(self) -> Dict[str, str]:
        """Get platform-specific type mappings"""
        if self.target_platform == self.PLATFORM_PYTHON:
            return {
                'int': 'int',
                'Integer': 'int',
                'float': 'float',
                'Float': 'float',
                'string': 'str',
                'String': 'str',
                'boolean': 'bool',
                'Boolean': 'bool',
            }
        elif self.target_platform == self.PLATFORM_JAVASCRIPT:
            return {
                'int': 'number',
                'Integer': 'number',
                'float': 'number',
                'Float': 'number',
                'string': 'string',
                'String': 'string',
                'boolean': 'boolean',
                'Boolean': 'boolean',
            }
        elif self.target_platform == self.PLATFORM_KOTLIN:
            return {
                'int': 'Int',
                'Integer': 'Int',
                'float': 'Float',
                'Float': 'Float',
                'string': 'String',
                'String': 'String',
                'boolean': 'Boolean',
                'Boolean': 'Boolean',
            }
        elif self.target_platform == self.PLATFORM_SWIFT:
            return {
                'int': 'Int',
                'Integer': 'Int',
                'float': 'Float',
                'Float': 'Float',
                'string': 'String',
                'String': 'String',
                'boolean': 'Bool',
                'Boolean': 'Bool',
            }
        elif self.target_platform == self.PLATFORM_CPP:
            return {
                'int': 'int',
                'Integer': 'int',
                'float': 'float',
                'Float': 'float',
                'string': 'std::string',
                'String': 'std::string',
                'boolean': 'bool',
                'Boolean': 'bool',
            }
        elif self.target_platform == self.PLATFORM_CSHARP:
            return {
                'int': 'int',
                'Integer': 'int',
                'float': 'float',
                'Float': 'float',
                'string': 'string',
                'String': 'string',
                'boolean': 'bool',
                'Boolean': 'bool',
            }
        return {}

    def get_platform_any_type(self) -> str:
        """Get platform-specific 'Any' type"""
        if self.target_platform == self.PLATFORM_PYTHON:
            return "Any"
        elif self.target_platform == self.PLATFORM_JAVASCRIPT:
            return "any"
        elif self.target_platform == self.PLATFORM_KOTLIN:
            return "Any"
        elif self.target_platform == self.PLATFORM_SWIFT:
            return "Any"
        elif self.target_platform == self.PLATFORM_CPP:
            return "auto"
        elif self.target_platform == self.PLATFORM_CSHARP:
            return "object"
        return "Any"

    def get_platform_array_type(self, base_type: str) -> str:
        """Get platform-specific array type"""
        if self.target_platform == self.PLATFORM_PYTHON:
            return f"List[{base_type}]"
        elif self.target_platform == self.PLATFORM_JAVASCRIPT:
            return f"{base_type}[]"
        elif self.target_platform == self.PLATFORM_KOTLIN:
            return f"List<{base_type}>"
        elif self.target_platform == self.PLATFORM_SWIFT:
            return f"[{base_type}]"
        elif self.target_platform == self.PLATFORM_CPP:
            return f"std::vector<{base_type}>"
        elif self.target_platform == self.PLATFORM_CSHARP:
            return f"List<{base_type}>"
        return f"List[{base_type}]"

    def get_platform_generic_type(self, base_type: str, generic_args: List[str]) -> str:
        """Get platform-specific generic type"""
        if self.target_platform == self.PLATFORM_PYTHON:
            return f"{base_type}[{', '.join(generic_args)}]"
        elif self.target_platform == self.PLATFORM_JAVASCRIPT:
            return f"{base_type}<{', '.join(generic_args)}>"
        elif self.target_platform == self.PLATFORM_KOTLIN:
            return f"{base_type}<{', '.join(generic_args)}>"
        elif self.target_platform == self.PLATFORM_SWIFT:
            return f"{base_type}<{', '.join(generic_args)}>"
        elif self.target_platform == self.PLATFORM_CPP:
            return f"{base_type}<{', '.join(generic_args)}>"
        elif self.target_platform == self.PLATFORM_CSHARP:
            return f"{base_type}<{', '.join(generic_args)}>"
        return f"{base_type}[{', '.join(generic_args)}]"

    def add_line(self, line: str):
        """Add a line to the output with proper indentation"""
        indent = "    " * self.indent_level
        self.output.append(f"{indent}{line}")

    def get_temp_var(self) -> str:
        """Get a temporary variable name"""
        self.temp_counter += 1
        return f"_temp_{self.temp_counter}"

    def generate_header(self):
        """Generate platform-specific header"""
        if self.target_platform == self.PLATFORM_PYTHON:
            self.add_line("#!/usr/bin/env python3")
            self.add_line("\"\"\"Generated by AGK Compiler\"\"\"")
        elif self.target_platform == self.PLATFORM_JAVASCRIPT:
            self.add_line("// Generated by AGK Compiler")
        elif self.target_platform == self.PLATFORM_KOTLIN:
            self.add_line("// Generated by AGK Compiler")
        elif self.target_platform == self.PLATFORM_SWIFT:
            self.add_line("// Generated by AGK Compiler")
        elif self.target_platform == self.PLATFORM_CPP:
            self.add_line("// Generated by AGK Compiler")
            self.add_line("#include <iostream>")
            self.add_line("#include <vector>")
            self.add_line("#include <string>")
        elif self.target_platform == self.PLATFORM_CSHARP:
            self.add_line("// Generated by AGK Compiler")
            self.add_line("using System;")
            self.add_line("using System.Collections.Generic;")
        self.add_line("")

    def generate_platform_imports(self, imports: List[Import]):
        """Generate platform-specific imports"""
        if self.target_platform == self.PLATFORM_PYTHON:
            self.generate_imports(imports)
        elif self.target_platform == self.PLATFORM_JAVASCRIPT:
            self.add_line("// JavaScript platform imports")
            for import_stmt in imports:
                if import_stmt.module.startswith('wearable'):
                    self.add_line(f"// Wearable API: {import_stmt.module}")
                elif import_stmt.module.startswith('tv'):
                    self.add_line(f"// TV API: {import_stmt.module}")
                elif import_stmt.module.startswith('automotive'):
                    self.add_line(f"// Automotive API: {import_stmt.module}")
                else:
                    self.add_line(f"// import {import_stmt.module}")
        elif self.target_platform == self.PLATFORM_KOTLIN:
            self.add_line("// Kotlin platform imports")
            self.add_line("import android.*")
            for import_stmt in imports:
                if import_stmt.module.startswith('wearable'):
                    self.add_line(f"// Wearable API: {import_stmt.module}")
        elif self.target_platform == self.PLATFORM_SWIFT:
            self.add_line("// Swift platform imports")
            self.add_line("import Foundation")
            self.add_line("import WatchKit")
        elif self.target_platform == self.PLATFORM_CPP:
            self.add_line("// C++ platform includes")
            for import_stmt in imports:
                if import_stmt.module.startswith('automotive'):
                    self.add_line("#include <automotive_api.h>")
        elif self.target_platform == self.PLATFORM_CSHARP:
            self.add_line("// C# platform imports")
            self.add_line("using System.Windows;")

    def generate_platform_setup(self):
        """Generate platform-specific setup code"""
        if self.target_platform == self.PLATFORM_PYTHON:
            pass  # Python doesn't need special setup
        elif self.target_platform == self.PLATFORM_JAVASCRIPT:
            self.add_line("// JavaScript platform setup")
            self.add_line("window.addEventListener('load', function() {")
            self.indent_level += 1
        elif self.target_platform == self.PLATFORM_KOTLIN:
            self.add_line("// Kotlin platform setup")
            self.add_line("class MainActivity : AppCompatActivity() {")
            self.add_line("    override fun onCreate(savedInstanceState: Bundle?) {")
            self.add_line("        super.onCreate(savedInstanceState)")
            self.indent_level += 2
        elif self.target_platform == self.PLATFORM_SWIFT:
            self.add_line("// Swift platform setup")
            self.add_line("class MainInterfaceController: WKInterfaceController {")
            self.add_line("    override func awake(withContext context: Any?) {")
            self.add_line("        super.awake(withContext: context)")
            self.indent_level += 2
        elif self.target_platform == self.PLATFORM_CPP:
            self.add_line("// C++ platform setup")
            self.add_line("int main(int argc, char** argv) {")
            self.indent_level += 1
        elif self.target_platform == self.PLATFORM_CSHARP:
            self.add_line("// C# platform setup")
            self.add_line("class Program {")
            self.add_line("    static void Main(string[] args) {")
            self.indent_level += 2

    def generate_footer(self):
        """Generate platform-specific footer"""
        if self.target_platform == self.PLATFORM_PYTHON:
            pass
        elif self.target_platform == self.PLATFORM_JAVASCRIPT:
            self.indent_level -= 1
            self.add_line("});")
        elif self.target_platform == self.PLATFORM_KOTLIN:
            self.indent_level -= 2
            self.add_line("    }")
            self.add_line("}")
        elif self.target_platform == self.PLATFORM_SWIFT:
            self.indent_level -= 2
            self.add_line("    }")
            self.add_line("}")
        elif self.target_platform == self.PLATFORM_CPP:
            self.indent_level -= 1
            self.add_line("    return 0;")
            self.add_line("}")
        elif self.target_platform == self.PLATFORM_CSHARP:
            self.indent_level -= 2
            self.add_line("    }")
            self.add_line("}")


def main():
    """Test the code generator for multiple platforms"""
    from agk_lexer import AGKLexer
    from agk_parser import AGKParser
    from agk_semantic import SemanticAnalyzer

    test_code = '''
define function calculate_total that takes items:
    create total as Integer
    set total to 0
    return total

define function test_function:
    create x as Integer
    set x to 42
    return x + 10
'''

    # Parse and analyze
    lexer = AGKLexer(test_code)
    tokens = lexer.tokenize()
    parser = AGKParser(tokens)
    ast = parser.parse()

    # Skip semantic analysis for now to test code generation
    print("Skipping semantic analysis for code generation test...")

    # Test different platforms
    platforms = [
        CodeGenerator.PLATFORM_PYTHON,
        CodeGenerator.PLATFORM_JAVASCRIPT,
        CodeGenerator.PLATFORM_KOTLIN,
        CodeGenerator.PLATFORM_SWIFT,
        CodeGenerator.PLATFORM_CPP,
        CodeGenerator.PLATFORM_CSHARP
    ]

    for platform in platforms:
        print(f"\n{'='*60}")
        print(f"Generating code for {platform.upper()}:")
        print(f"{'='*60}")

        generator = CodeGenerator(target_platform=platform)
        generated_code = generator.generate(ast)
        print(generated_code)

        # Test if Python code is valid
        if platform == CodeGenerator.PLATFORM_PYTHON:
            print("\nTesting generated code syntax...")
            try:
                compile(generated_code, '<generated>', 'exec')
                print("SUCCESS: Generated code is valid Python!")
            except SyntaxError as e:
                print(f"ERROR: Syntax error in generated code: {e}")


if __name__ == "__main__":
    main()