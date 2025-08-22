#!/usr/bin/env python3
"""
AGK Language Semantic Analyzer

Performs type checking, variable validation, and semantic analysis on the AST.
"""

from typing import Dict, List, Optional, Set
from agk_ast import (
    ASTNode, Program, Import, TypeNode, Parameter, FunctionDef, ClassDef,
    ConstructorDef, InterfaceDef, VariableDecl, Assignment, IfStatement,
    ForStatement, WhileStatement, ReturnStatement, BreakStatement,
    ContinueStatement, TryCatchStatement, ThrowStatement, BinaryOp,
    UnaryOp, FunctionCall, AttributeAccess, ArrayAccess, Literal,
    Variable, This, ListLiteral, DictLiteral, NewExpression
)


class SymbolInfo:
    """Information about a symbol in the symbol table"""
    def __init__(self, name: str, type_node: Optional[TypeNode] = None,
                 is_function: bool = False, is_class: bool = False,
                 is_variable: bool = True, is_constant: bool = False,
                 visibility: str = "public"):
        self.name = name
        self.type_node = type_node
        self.is_function = is_function
        self.is_class = is_class
        self.is_variable = is_variable
        self.is_constant = is_constant
        self.visibility = visibility
        self.is_initialized = False
        self.is_used = False


class Scope:
    """Represents a scope in the symbol table"""
    def __init__(self, parent: Optional['Scope'] = None, name: str = "global"):
        self.parent = parent
        self.name = name
        self.symbols: Dict[str, SymbolInfo] = {}
        self.children: List['Scope'] = []

    def declare(self, name: str, info: SymbolInfo) -> bool:
        """Declare a symbol in this scope"""
        if name in self.symbols:
            return False  # Already declared in this scope
        self.symbols[name] = info
        return True

    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """Look up a symbol, searching parent scopes if necessary"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def lookup_current_scope(self, name: str) -> Optional[SymbolInfo]:
        """Look up a symbol only in the current scope"""
        return self.symbols.get(name)


class SemanticError(Exception):
    """Exception raised for semantic errors"""
    def __init__(self, message: str, node: ASTNode = None):
        self.message = message
        self.node = node
        super().__init__(message)


class TypeChecker:
    """Performs type checking and compatibility analysis"""

    # Basic type compatibility matrix
    TYPE_COMPATIBILITY = {
        'int': {'float', 'string'},
        'float': {'string'},
        'string': set(),
        'boolean': set(),
    }

    def is_compatible(self, from_type: str, to_type: str) -> bool:
        """Check if from_type can be converted to to_type"""
        if from_type == to_type:
            return True
        return to_type in self.TYPE_COMPATIBILITY.get(from_type, set())

    def get_common_type(self, type1: str, type2: str) -> Optional[str]:
        """Get the common type for binary operations"""
        if type1 == type2:
            return type1
        if 'float' in (type1, type2) and 'int' in (type1, type2):
            return 'float'
        if 'string' in (type1, type2):
            return 'string'
        return None

    def check_binary_op(self, left_type: str, operator: str, right_type: str) -> Optional[str]:
        """Check if a binary operation is valid and return result type"""
        # Arithmetic operations
        if operator in ['+', '-', '*', '/']:
            if left_type in ('int', 'float') and right_type in ('int', 'float'):
                return self.get_common_type(left_type, right_type)
            elif operator == '+' and ('string' in (left_type, right_type)):
                return 'string'

        # Comparison operations
        elif operator in ['==', '!=', '<', '>', '<=', '>=']:
            if self.is_compatible(left_type, right_type) or self.is_compatible(right_type, left_type):
                return 'boolean'

        # Logical operations
        elif operator in ['&&', '||']:
            if left_type == 'boolean' and right_type == 'boolean':
                return 'boolean'

        return None


class SemanticAnalyzer:
    """Main semantic analyzer class"""

    def __init__(self):
        self.global_scope = Scope(name="global")
        self.current_scope = self.global_scope
        self.type_checker = TypeChecker()
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def analyze(self, program: Program) -> bool:
        """Main analysis method"""
        try:
            self.visit_program(program)
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(f"Analysis error: {e}")
            return False

    def visit_program(self, node: Program):
        """Analyze a program"""
        # First pass: collect all declarations
        for statement in node.statements:
            if isinstance(statement, (FunctionDef, ClassDef, InterfaceDef)):
                self.collect_declaration(statement)

        # Second pass: analyze all statements
        for statement in node.statements:
            statement.accept(self)

    def collect_declaration(self, node: ASTNode):
        """Collect declarations in a first pass"""
        if isinstance(node, FunctionDef):
            info = SymbolInfo(node.name, node.return_type, is_function=True)
            self.current_scope.declare(node.name, info)
        elif isinstance(node, ClassDef):
            info = SymbolInfo(node.name, is_class=True)
            self.current_scope.declare(node.name, info)
        elif isinstance(node, InterfaceDef):
            info = SymbolInfo(node.name, is_class=True)  # Treat interfaces as classes for now
            self.current_scope.declare(node.name, info)

    def visit_functiondef(self, node: FunctionDef):
        """Analyze a function definition"""
        # Create new scope for function
        func_scope = Scope(self.current_scope, f"function_{node.name}")
        self.current_scope = func_scope

        try:
            # Add parameters to scope
            for param in node.parameters:
                param_info = SymbolInfo(param.name, param.type_node, is_variable=True)
                param_info.is_initialized = True  # Parameters are always initialized
                if not self.current_scope.declare(param.name, param_info):
                    self.add_error(f"Parameter '{param.name}' already declared in function '{node.name}'", node)

            # Analyze function body
            for statement in node.body:
                statement.accept(self)

        finally:
            self.current_scope = func_scope.parent

    def visit_classdef(self, node: ClassDef):
        """Analyze a class definition"""
        # Create new scope for class
        class_scope = Scope(self.current_scope, f"class_{node.name}")
        self.current_scope = class_scope

        try:
            # Add fields to scope
            for field in node.fields:
                field_info = SymbolInfo(field.name, field.type_node, is_variable=True,
                                      is_constant=field.is_constant, visibility=field.visibility)
                if not self.current_scope.declare(field.name, field_info):
                    self.add_error(f"Field '{field.name}' already declared in class '{node.name}'", node)

            # Add methods to scope (simplified - not adding to symbol table for now)
            for method in node.methods:
                method.accept(self)

        finally:
            self.current_scope = class_scope.parent

    def visit_variabledecl(self, node: VariableDecl):
        """Analyze a variable declaration"""
        # Check if variable already declared in current scope
        if self.current_scope.lookup_current_scope(node.name):
            self.add_error(f"Variable '{node.name}' already declared in current scope", node)
            return

        # Create symbol info
        info = SymbolInfo(node.name, node.type_node, is_variable=True,
                         is_constant=node.is_constant, visibility=node.visibility)
        self.current_scope.declare(node.name, info)

        # If there's an initializer, analyze it and mark as initialized
        if node.initializer:
            init_type = self.analyze_expression(node.initializer)
            if init_type and node.type_node:
                # Normalize type names for comparison
                declared_type = self.normalize_type_name(node.type_node.name)
                init_type_normalized = self.normalize_type_name(init_type)

                if not self.type_checker.is_compatible(init_type_normalized, declared_type):
                    self.add_error(f"Cannot assign value of type '{init_type}' to variable of type '{node.type_node.name}'", node)
            info.is_initialized = True

    def visit_assignment(self, node: Assignment):
        """Analyze an assignment"""
        # Analyze target
        target_info = self.analyze_expression(node.target)
        if isinstance(node.target, Variable):
            var_info = self.current_scope.lookup(node.target.name)
            if var_info:
                if var_info.is_constant:
                    self.add_error(f"Cannot assign to constant '{node.target.name}'", node)
                    return
                var_info.is_used = True
                var_info.is_initialized = True
            else:
                self.add_error(f"Variable '{node.target.name}' not declared", node)
                return

        # Analyze value
        value_type = self.analyze_expression(node.value)

        # Type checking
        if target_info and value_type:
            if isinstance(node.target, Variable):
                var_info = self.current_scope.lookup(node.target.name)
                if var_info and var_info.type_node:
                    # Normalize types for comparison
                    declared_type = self.normalize_type_name(var_info.type_node.name)
                    value_type_normalized = self.normalize_type_name(value_type)

                    if not self.type_checker.is_compatible(value_type_normalized, declared_type):
                        self.add_error(f"Cannot assign value of type '{value_type}' to variable of type '{var_info.type_node.name}'", node)

    def visit_ifstatement(self, node: IfStatement):
        """Analyze an if statement"""
        # Check condition type
        condition_type = self.analyze_expression(node.condition)
        if condition_type and condition_type != 'boolean':
            self.add_error(f"If condition must be boolean, got {condition_type}", node)

        # Analyze body
        for statement in node.then_body:
            statement.accept(self)

        if node.else_body:
            for statement in node.else_body:
                statement.accept(self)

    def visit_forstatement(self, node: ForStatement):
        """Analyze a for statement"""
        # Create new scope for loop variable
        loop_scope = Scope(self.current_scope, "for_loop")
        self.current_scope = loop_scope

        try:
            # Add loop variable to scope
            iterator_info = SymbolInfo(node.iterator, None, is_variable=True)
            iterator_info.is_initialized = True
            self.current_scope.declare(node.iterator, iterator_info)

            # Analyze iterable
            iterable_type = self.analyze_expression(node.iterable)

            # Analyze body
            for statement in node.body:
                statement.accept(self)

        finally:
            self.current_scope = loop_scope.parent

    def visit_whilestatement(self, node: WhileStatement):
        """Analyze a while statement"""
        # Check condition type
        condition_type = self.analyze_expression(node.condition)
        if condition_type and condition_type != 'boolean':
            self.add_error(f"While condition must be boolean, got {condition_type}", node)

        # Analyze body
        for statement in node.body:
            statement.accept(self)

    def visit_returnstatement(self, node: ReturnStatement):
        """Analyze a return statement"""
        if node.value:
            return_type = self.analyze_expression(node.value)
            # Note: In a full implementation, we'd check this against the function's return type
            # For now, we just validate the expression is well-formed

    def visit_functioncall(self, node: FunctionCall):
        """Analyze a function call"""
        # Look up function
        func_info = self.current_scope.lookup(node.function)
        if not func_info:
            self.add_error(f"Function '{node.function}' not declared", node)
            return None

        if not func_info.is_function:
            self.add_error(f"'{node.function}' is not a function", node)
            return None

        func_info.is_used = True

        # Analyze arguments
        for arg in node.arguments:
            self.analyze_expression(arg)

        # Return function's return type
        return func_info.type_node.name if func_info.type_node else 'void'

    def analyze_expression(self, node: ASTNode) -> Optional[str]:
        """Analyze an expression and return its type"""
        if isinstance(node, Literal):
            return node.type_name
        elif isinstance(node, Variable):
            var_info = self.current_scope.lookup(node.name)
            if var_info:
                if not var_info.is_initialized:
                    self.add_warning(f"Variable '{node.name}' may not be initialized", node)
                var_info.is_used = True
                return var_info.type_node.name if var_info.type_node else 'any'
            else:
                self.add_error(f"Variable '{node.name}' not declared", node)
                return None
        elif isinstance(node, BinaryOp):
            left_type = self.analyze_expression(node.left)
            right_type = self.analyze_expression(node.right)

            if left_type and right_type:
                result_type = self.type_checker.check_binary_op(left_type, node.operator, right_type)
                if not result_type:
                    self.add_error(f"Invalid operation: {left_type} {node.operator} {right_type}", node)
                return result_type
            return None
        elif isinstance(node, UnaryOp):
            operand_type = self.analyze_expression(node.operand)
            if node.operator == '!':
                if operand_type and operand_type != 'boolean':
                    self.add_error(f"Unary ! operator requires boolean operand, got {operand_type}", node)
                return 'boolean'
            elif node.operator in ['+', '-']:
                if operand_type and operand_type not in ('int', 'float'):
                    self.add_error(f"Unary {node.operator} operator requires numeric operand, got {operand_type}", node)
                return operand_type
            return operand_type
        elif isinstance(node, FunctionCall):
            return self.visit_functioncall(node)
        elif isinstance(node, This):
            # In a full implementation, we'd return the current class type
            return 'any'
        elif isinstance(node, ListLiteral):
            # Analyze all items
            item_types = []
            for item in node.items:
                item_type = self.analyze_expression(item)
                if item_type:
                    item_types.append(item_type)

            # For simplicity, return the type of the first item
            return item_types[0] if item_types else 'any'
        elif isinstance(node, DictLiteral):
            # Analyze all key-value pairs
            for key, value in node.items:
                self.analyze_expression(key)
                self.analyze_expression(value)
            return 'dict'

        return 'any'  # Default fallback

    def add_error(self, message: str, node: ASTNode = None):
        """Add a semantic error"""
        self.errors.append(message)

    def add_warning(self, message: str, node: ASTNode = None):
        """Add a semantic warning"""
        self.warnings.append(message)

    def normalize_type_name(self, type_name: str) -> str:
        """Normalize type names for comparison"""
        # Map common type aliases
        type_mapping = {
            'Integer': 'int',
            'Float': 'float',
            'String': 'string',
            'Boolean': 'boolean',
        }
        return type_mapping.get(type_name, type_name.lower())

    def get_errors(self) -> List[str]:
        """Get all semantic errors"""
        return self.errors

    def get_warnings(self) -> List[str]:
        """Get all semantic warnings"""
        return self.warnings


def main():
    """Test the semantic analyzer"""
    from agk_lexer import AGKLexer
    from agk_parser import AGKParser
    from agk_ast import ASTPrinter

    test_code = '''
define function calculate_total that takes items:
    create total as Integer
    set total to 0
    set total to total + item
    return total

define function test_function:
    create x as Integer
    set y to 5
    return x + y
'''

    lexer = AGKLexer(test_code)
    tokens = lexer.tokenize()
    parser = AGKParser(tokens)
    ast = parser.parse()

    print("AST:")
    printer = ASTPrinter()
    ast.accept(printer)

    print("\n=== Semantic Analysis ===")
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)

    print(f"Analysis successful: {success}")
    print(f"Errors: {len(analyzer.get_errors())}")
    for error in analyzer.get_errors():
        print(f"  - {error}")

    print(f"Warnings: {len(analyzer.get_warnings())}")
    for warning in analyzer.get_warnings():
        print(f"  - {warning}")


if __name__ == "__main__":
    main()