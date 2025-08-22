#!/usr/bin/env python3
"""
AGK Language Abstract Syntax Tree (AST) Nodes

Defines the data structures for representing parsed AGK code.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod


class ASTNode(ABC):
    """Base class for all AST nodes"""

    def accept(self, visitor):
        """Visitor pattern method"""
        method_name = f'visit_{self.__class__.__name__.lower()}'
        visit_method = getattr(visitor, method_name, None)
        if visit_method:
            return visit_method(self)
        else:
            return self.generic_visit(visitor)

    def generic_visit(self, visitor):
        """Default visitor implementation"""
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, ASTNode):
                field_value.accept(visitor)
            elif isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, ASTNode):
                        item.accept(visitor)


@dataclass
class Program(ASTNode):
    """Root node representing an entire program"""
    statements: List[ASTNode]
    imports: List['Import'] = None

    def __post_init__(self):
        if self.imports is None:
            self.imports = []


@dataclass
class Import(ASTNode):
    """Import statement"""
    module: str
    alias: Optional[str] = None
    specific_imports: List[str] = None

    def __post_init__(self):
        if self.specific_imports is None:
            self.specific_imports = []


@dataclass
class TypeNode(ASTNode):
    """Represents a type annotation"""
    name: str
    is_array: bool = False
    generic_args: List['TypeNode'] = None
    is_nullable: bool = False

    def __post_init__(self):
        if self.generic_args is None:
            self.generic_args = []


@dataclass
class Parameter(ASTNode):
    """Function parameter"""
    name: str
    type_node: Optional[TypeNode] = None
    default_value: Optional[ASTNode] = None


@dataclass
class FunctionDef(ASTNode):
    """Function definition"""
    name: str
    parameters: List[Parameter]
    return_type: Optional[TypeNode]
    body: List[ASTNode]
    decorators: List[str] = None
    visibility: str = "public"  # public, private, protected
    is_static: bool = False
    is_final: bool = False

    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []


@dataclass
class ClassDef(ASTNode):
    """Class definition"""
    name: str
    superclasses: List[str] = None
    interfaces: List[str] = None
    fields: List['VariableDecl'] = None
    methods: List[FunctionDef] = None
    constructors: List['ConstructorDef'] = None
    visibility: str = "public"
    is_abstract: bool = False
    is_final: bool = False

    def __post_init__(self):
        if self.superclasses is None:
            self.superclasses = []
        if self.interfaces is None:
            self.interfaces = []
        if self.fields is None:
            self.fields = []
        if self.methods is None:
            self.methods = []
        if self.constructors is None:
            self.constructors = []


@dataclass
class ConstructorDef(ASTNode):
    """Constructor definition"""
    parameters: List[Parameter]
    body: List[ASTNode]
    visibility: str = "public"


@dataclass
class InterfaceDef(ASTNode):
    """Interface definition"""
    name: str
    methods: List[FunctionDef] = None
    visibility: str = "public"

    def __post_init__(self):
        if self.methods is None:
            self.methods = []


@dataclass
class VariableDecl(ASTNode):
    """Variable declaration"""
    name: str
    type_node: Optional[TypeNode] = None
    initializer: Optional[ASTNode] = None
    visibility: str = "private"
    is_static: bool = False
    is_final: bool = False
    is_constant: bool = False


@dataclass
class Assignment(ASTNode):
    """Assignment statement"""
    target: ASTNode  # Variable, attribute access, etc.
    value: ASTNode
    operator: str = "="  # =, +=, -=, *=, /=, %=, etc.


@dataclass
class IfStatement(ASTNode):
    """If-elif-else statement"""
    condition: ASTNode
    then_body: List[ASTNode]
    elif_branches: List[tuple] = None  # List of (condition, body) tuples
    else_body: Optional[List[ASTNode]] = None

    def __post_init__(self):
        if self.elif_branches is None:
            self.elif_branches = []


@dataclass
class ForStatement(ASTNode):
    """For loop statement"""
    iterator: str
    iterable: ASTNode
    body: List[ASTNode]


@dataclass
class WhileStatement(ASTNode):
    """While loop statement"""
    condition: ASTNode
    body: List[ASTNode]


@dataclass
class ReturnStatement(ASTNode):
    """Return statement"""
    value: Optional[ASTNode] = None


@dataclass
class BreakStatement(ASTNode):
    """Break statement"""
    pass


@dataclass
class ContinueStatement(ASTNode):
    """Continue statement"""
    pass


@dataclass
class TryCatchStatement(ASTNode):
    """Try-catch-finally statement"""
    try_body: List[ASTNode]
    catch_clauses: List[tuple] = None  # List of (exception_type, variable, body)
    finally_body: Optional[List[ASTNode]] = None

    def __post_init__(self):
        if self.catch_clauses is None:
            self.catch_clauses = []


@dataclass
class ThrowStatement(ASTNode):
    """Throw statement"""
    exception: ASTNode


@dataclass
class BinaryOp(ASTNode):
    """Binary operation"""
    left: ASTNode
    operator: str  # +, -, *, /, %, ==, !=, <, >, <=, >=, &&, ||, etc.
    right: ASTNode


@dataclass
class UnaryOp(ASTNode):
    """Unary operation"""
    operator: str  # +, -, !, etc.
    operand: ASTNode


@dataclass
class FunctionCall(ASTNode):
    """Function call"""
    function: str
    arguments: List[ASTNode]
    is_method: bool = False
    object_name: Optional[str] = None


@dataclass
class AttributeAccess(ASTNode):
    """Attribute access (object.property)"""
    object: ASTNode
    attribute: str


@dataclass
class ArrayAccess(ASTNode):
    """Array access (array[index])"""
    array: ASTNode
    index: ASTNode


@dataclass
class Literal(ASTNode):
    """Literal value"""
    value: Any
    type_name: str  # "int", "float", "string", "boolean", etc.


@dataclass
class Variable(ASTNode):
    """Variable reference"""
    name: str


@dataclass
class This(ASTNode):
    """'this' reference"""
    pass


@dataclass
class ListLiteral(ASTNode):
    """List literal [item1, item2, ...]"""
    items: List[ASTNode]


@dataclass
class DictLiteral(ASTNode):
    """Dictionary literal {key1: value1, key2: value2, ...}"""
    items: List[tuple]  # List of (key, value) tuples


@dataclass
class NewExpression(ASTNode):
    """Object instantiation"""
    class_name: str
    arguments: List[ASTNode]


class ASTVisitor(ABC):
    """Base visitor class for traversing AST"""

    def visit_program(self, node: Program):
        self.generic_visit(node)

    def visit_import(self, node: Import):
        self.generic_visit(node)

    def visit_typenode(self, node: TypeNode):
        self.generic_visit(node)

    def visit_functiondef(self, node: FunctionDef):
        self.generic_visit(node)

    def visit_classdef(self, node: ClassDef):
        self.generic_visit(node)

    def visit_constructordef(self, node: ConstructorDef):
        self.generic_visit(node)

    def visit_interfacedef(self, node: InterfaceDef):
        self.generic_visit(node)

    def visit_variabledecl(self, node: VariableDecl):
        self.generic_visit(node)

    def visit_assignment(self, node: Assignment):
        self.generic_visit(node)

    def visit_ifstatement(self, node: IfStatement):
        self.generic_visit(node)

    def visit_forstatement(self, node: ForStatement):
        self.generic_visit(node)

    def visit_whilestatement(self, node: WhileStatement):
        self.generic_visit(node)

    def visit_returnstatement(self, node: ReturnStatement):
        self.generic_visit(node)

    def visit_breakstatement(self, node: BreakStatement):
        self.generic_visit(node)

    def visit_continuestatement(self, node: ContinueStatement):
        self.generic_visit(node)

    def visit_trycatchstatement(self, node: TryCatchStatement):
        self.generic_visit(node)

    def visit_throwstatement(self, node: ThrowStatement):
        self.generic_visit(node)

    def visit_binaryop(self, node: BinaryOp):
        self.generic_visit(node)

    def visit_unaryop(self, node: UnaryOp):
        self.generic_visit(node)

    def visit_functioncall(self, node: FunctionCall):
        self.generic_visit(node)

    def visit_attributeaccess(self, node: AttributeAccess):
        self.generic_visit(node)

    def visit_arrayaccess(self, node: ArrayAccess):
        self.generic_visit(node)

    def visit_literal(self, node: Literal):
        self.generic_visit(node)

    def visit_variable(self, node: Variable):
        self.generic_visit(node)

    def visit_this(self, node: This):
        self.generic_visit(node)

    def visit_listliteral(self, node: ListLiteral):
        self.generic_visit(node)

    def visit_dictliteral(self, node: DictLiteral):
        self.generic_visit(node)

    def visit_newexpression(self, node: NewExpression):
        self.generic_visit(node)

    def generic_visit(self, node: ASTNode):
        """Default visitor implementation"""
        node.generic_visit(self)


class ASTPrinter(ASTVisitor):
    """Visitor that prints a readable representation of the AST"""

    def __init__(self):
        self.indent_level = 0

    def indent(self):
        return "  " * self.indent_level

    def visit_program(self, node: Program):
        print(f"{self.indent()}Program:")
        self.indent_level += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent_level -= 1

    def visit_functiondef(self, node: FunctionDef):
        params_str = ", ".join([f"{p.name}: {p.type_node.name if p.type_node else 'Any'}" for p in node.parameters])
        return_str = f" -> {node.return_type.name}" if node.return_type else ""
        print(f"{self.indent()}FunctionDef: {node.name}({params_str}){return_str}")
        self.indent_level += 1
        for stmt in node.body:
            stmt.accept(self)
        self.indent_level -= 1

    def visit_classdef(self, node: ClassDef):
        print(f"{self.indent()}ClassDef: {node.name}")
        self.indent_level += 1
        for field in node.fields:
            field.accept(self)
        for method in node.methods:
            method.accept(self)
        self.indent_level -= 1

    def visit_variabledecl(self, node: VariableDecl):
        type_str = f": {node.type_node.name}" if node.type_node else ""
        init_str = f" = {node.initializer}" if node.initializer else ""
        print(f"{self.indent()}VariableDecl: {node.name}{type_str}{init_str}")

    def visit_assignment(self, node: Assignment):
        print(f"{self.indent()}Assignment: {node.target} {node.operator} {node.value}")

    def visit_binaryop(self, node: BinaryOp):
        print(f"{self.indent()}BinaryOp: {node.left} {node.operator} {node.right}")

    def visit_literal(self, node: Literal):
        print(f"{self.indent()}Literal: {node.value} ({node.type_name})")

    def visit_variable(self, node: Variable):
        print(f"{self.indent()}Variable: {node.name}")

    def visit_returnstatement(self, node: ReturnStatement):
        print(f"{self.indent()}Return: {node.value}")

    def visit_ifstatement(self, node: IfStatement):
        print(f"{self.indent()}If: {node.condition}")
        self.indent_level += 1
        print(f"{self.indent()}Then:")
        self.indent_level += 1
        for stmt in node.then_body:
            stmt.accept(self)
        self.indent_level -= 1
        if node.else_body:
            print(f"{self.indent()}Else:")
            self.indent_level += 1
            for stmt in node.else_body:
                stmt.accept(self)
            self.indent_level -= 1
        self.indent_level -= 1


def main():
    """Test the AST structures"""
    # Create a simple test AST
    literal_0 = Literal(0, "int")
    var_total = Variable("total")
    var_items = Variable("items")
    var_item = Variable("item")

    # create total as 0
    var_decl = VariableDecl("total", None, literal_0)

    # for each item in items:
    #     add item to total
    assignment = Assignment(var_total, BinaryOp(var_total, "+", var_item))

    for_loop = ForStatement("item", var_items, [assignment])

    # return total
    return_stmt = ReturnStatement(var_total)

    # define function calculate_total that takes items:
    #     ...
    func_def = FunctionDef("calculate_total", [Parameter("items", None)], None, [var_decl, for_loop, return_stmt])

    program = Program([func_def])

    # Print the AST
    printer = ASTPrinter()
    program.accept(printer)


if __name__ == "__main__":
    main()