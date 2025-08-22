#!/usr/bin/env python3
"""
AGK Language Parser

Parses natural language tokens into an Abstract Syntax Tree (AST).
"""

from typing import List, Optional, Dict, Any
from agk_lexer import AGKLexer, Token, TokenType
from agk_ast import (
    Program, Import, TypeNode, Parameter, FunctionDef, ExternalFunctionDef, ClassDef,
    ConstructorDef, InterfaceDef, VariableDecl, Assignment, IfStatement,
    ForStatement, WhileStatement, ReturnStatement, BreakStatement,
    ContinueStatement, TryCatchStatement, ThrowStatement, BinaryOp,
    UnaryOp, FunctionCall, AttributeAccess, ArrayAccess, Literal,
    Variable, This, ListLiteral, DictLiteral, NewExpression
)


class ParserError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parser error at line {token.line}, column {token.column}: {message}")


class AGKParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.indent_level = 0

    def parse(self) -> Program:
        """Main parsing method"""
        statements = []
        imports = []

        while not self.is_at_end():
            # Skip newlines and handle indentation
            while self.match(TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
                pass

            if self.is_at_end():
                break

            if self.match(TokenType.IMPORT):
                imports.append(self.parse_import())
            elif self.match(TokenType.DEFINE):
                if self.check(TokenType.FUNCTION):
                    statements.append(self.parse_function())
                elif self.check(TokenType.CLASS):
                    statements.append(self.parse_class())
                elif self.check(TokenType.INTERFACE):
                    statements.append(self.parse_interface())
                else:
                    raise ParserError(f"Expected function, class, or interface after 'define'", self.peek())
            elif self.match(TokenType.EXTERNAL):
                if self.check(TokenType.FUNCTION):
                    statements.append(self.parse_external_function())
                else:
                    raise ParserError(f"Expected function after 'external'", self.peek())
            elif self.match(TokenType.PRIVATE, TokenType.PUBLIC, TokenType.PROTECTED):
                visibility = self.previous().value
                if self.match(TokenType.VARIABLE):
                    statements.append(self.parse_variable_declaration(visibility))
                else:
                    self.backtrack()
                    statements.append(self.parse_statement())
            elif self.match(TokenType.VARIABLE):
                statements.append(self.parse_variable_declaration())
            elif self.check(TokenType.IDENTIFIER) or self.check(TokenType.CREATE) or self.check(TokenType.IF) or self.check(TokenType.FOR) or self.check(TokenType.WHILE) or self.check(TokenType.RETURN) or self.check(TokenType.TRY):
                statements.append(self.parse_statement())
            else:
                self.advance()  # Skip unrecognized tokens for now

        return Program(statements, imports)

    def parse_import(self) -> Import:
        """Parse import statement"""
        if self.match(TokenType.FROM):
            module = self.consume(TokenType.IDENTIFIER, "Expected module name after 'from'").value
            self.consume(TokenType.IMPORT, "Expected 'import' after module name")
            specific_imports = []

            if self.match(TokenType.IDENTIFIER):
                specific_imports.append(self.previous().value)
                while self.match(TokenType.COMMA):
                    specific_imports.append(self.consume(TokenType.IDENTIFIER, "Expected identifier after comma").value)

            alias = None
            if self.match(TokenType.AS):
                alias = self.consume(TokenType.IDENTIFIER, "Expected alias after 'as'").value

            return Import(module, alias, specific_imports)
        else:
            # Simple import
            module = self.consume(TokenType.IDENTIFIER, "Expected module name").value
            alias = None
            if self.match(TokenType.AS):
                alias = self.consume(TokenType.IDENTIFIER, "Expected alias after 'as'").value
            return Import(module, alias)

    def parse_function(self) -> FunctionDef:
        """Parse function definition"""
        visibility = "public"
        is_static = False
        is_final = False

        # Handle modifiers
        while self.match(TokenType.STATIC, TokenType.FINAL, TokenType.PUBLIC, TokenType.PRIVATE, TokenType.PROTECTED):
            mod = self.previous().value
            if mod in ["public", "private", "protected"]:
                visibility = mod
            elif mod == "static":
                is_static = True
            elif mod == "final":
                is_final = True

        self.consume(TokenType.FUNCTION, "Expected 'function' keyword")
        name = self.consume(TokenType.IDENTIFIER, "Expected function name").value

        parameters = []
        if self.match(TokenType.THAT):
            self.consume(TokenType.TAKES, "Expected 'takes' after 'that'")
            parameters = self.parse_parameters()

        return_type = None
        if self.match(TokenType.AND):
            self.consume(TokenType.RETURNS, "Expected 'returns' after 'and'")
            return_type = self.parse_type()

        self.consume(TokenType.COLON, "Expected ':' after function signature")

        # Handle function body with proper indentation
        body = []
        expected_indent = self.indent_level + 1

        while not self.is_at_end():
            # Skip newlines
            while self.match(TokenType.NEWLINE):
                pass

            if self.is_at_end():
                break

            # Check for end of function body (dedent or lower indentation)
            if self.check(TokenType.DEDENT) or (self.check(TokenType.DEFINE) or self.check(TokenType.CLASS) or self.check(TokenType.EOF)):
                break

            # Parse statements at the expected indentation level
            if self.match(TokenType.INDENT):
                # We found an indent, parse the statement
                stmt = self.parse_statement()
                if stmt is not None:
                    body.append(stmt)
            elif not self.check(TokenType.DEDENT):
                # Parse statement at current level
                stmt = self.parse_statement()
                if stmt is not None:
                    body.append(stmt)
            else:
                break

        return FunctionDef(name, parameters, return_type, body, [], visibility, is_static, is_final)

    def parse_external_function(self) -> ExternalFunctionDef:
        """Parse external function declaration"""
        visibility = "public"

        # Handle modifiers
        while self.match(TokenType.PUBLIC, TokenType.PRIVATE, TokenType.PROTECTED):
            visibility = self.previous().value

        self.consume(TokenType.FUNCTION, "Expected 'function' keyword")
        name = self.consume(TokenType.IDENTIFIER, "Expected function name").value

        # Parse parameters - support both syntaxes
        parameters = []
        if self.match(TokenType.LPAREN):
            # Simple syntax: function_name(param as type, ...)
            parameters = self.parse_simple_parameters()
            self.consume(TokenType.RPAREN, "Expected ')' after parameters")
        elif self.match(TokenType.THAT):
            # Natural language syntax: that takes param as type
            self.consume(TokenType.TAKES, "Expected 'takes' after 'that'")
            parameters = self.parse_parameters()

        # Parse "from" clause
        self.consume(TokenType.FROM, "Expected 'from' after function parameters")
        library_path = self.consume(TokenType.STRING, "Expected library path after 'from'").value
        library_path = library_path[1:-1]  # Remove quotes

        # Parse return type
        self.consume(TokenType.AS, "Expected 'as' before return type")
        return_type = self.parse_type()

        return ExternalFunctionDef(name, parameters, return_type, library_path, visibility)

    def parse_simple_parameters(self) -> List[Parameter]:
        """Parse parameter list in simple syntax: (param as type, ...)"""
        parameters = []

        if not self.check(TokenType.RPAREN):  # Empty parameter list
            param_name = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
            param_type = None

            if self.match(TokenType.AS):
                param_type = self.parse_type()

            parameters.append(Parameter(param_name, param_type))

            while self.match(TokenType.COMMA):
                param_name = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
                param_type = None

                if self.match(TokenType.AS):
                    param_type = self.parse_type()

                parameters.append(Parameter(param_name, param_type))

        return parameters

    def parse_class(self) -> ClassDef:
        """Parse class definition"""
        visibility = "public"
        is_abstract = False
        is_final = False

        # Handle modifiers
        while self.match(TokenType.ABSTRACT, TokenType.FINAL, TokenType.PUBLIC, TokenType.PRIVATE, TokenType.PROTECTED):
            mod = self.previous().value
            if mod in ["public", "private", "protected"]:
                visibility = mod
            elif mod == "abstract":
                is_abstract = True
            elif mod == "final":
                is_final = True

        self.consume(TokenType.CLASS, "Expected 'class' keyword")
        name = self.consume(TokenType.IDENTIFIER, "Expected class name").value

        superclasses = []
        interfaces = []

        if self.match(TokenType.EXTENDS):
            superclasses.append(self.consume(TokenType.IDENTIFIER, "Expected superclass name").value)
            while self.match(TokenType.COMMA):
                superclasses.append(self.consume(TokenType.IDENTIFIER, "Expected superclass name").value)

        if self.match(TokenType.IMPLEMENTS):
            interfaces.append(self.consume(TokenType.IDENTIFIER, "Expected interface name").value)
            while self.match(TokenType.COMMA):
                interfaces.append(self.consume(TokenType.IDENTIFIER, "Expected interface name").value)

        self.consume(TokenType.COLON, "Expected ':' after class signature")

        # Parse class members
        fields = []
        methods = []
        constructors = []

        expected_indent = self.indent_level + 1

        while not self.is_at_end() and not self.check_next_indent(expected_indent):
            if self.check_indent(expected_indent):
                if self.match(TokenType.PRIVATE, TokenType.PUBLIC, TokenType.PROTECTED):
                    visibility = self.previous().value
                    if self.check(TokenType.VARIABLE):
                        fields.append(self.parse_variable_declaration(visibility))
                    elif self.check(TokenType.FUNCTION):
                        methods.append(self.parse_function())
                        methods[-1].visibility = visibility
                    elif self.check(TokenType.CONSTRUCTOR):
                        constructors.append(self.parse_constructor())
                        constructors[-1].visibility = visibility
                    else:
                        self.backtrack()
                        methods.append(self.parse_statement())  # Assume method
                elif self.check(TokenType.DEFINE):
                    if self.check_next(TokenType.FUNCTION):
                        methods.append(self.parse_function())
                    elif self.check_next(TokenType.CONSTRUCTOR):
                        constructors.append(self.parse_constructor())
                else:
                    fields.append(self.parse_variable_declaration())
            else:
                break

        return ClassDef(name, superclasses, interfaces, fields, methods, constructors, visibility, is_abstract, is_final)

    def parse_interface(self) -> InterfaceDef:
        """Parse interface definition"""
        visibility = "public"

        if self.match(TokenType.PUBLIC, TokenType.PRIVATE, TokenType.PROTECTED):
            visibility = self.previous().value

        self.consume(TokenType.INTERFACE, "Expected 'interface' keyword")
        name = self.consume(TokenType.IDENTIFIER, "Expected interface name").value
        self.consume(TokenType.COLON, "Expected ':' after interface name")

        methods = []
        expected_indent = self.indent_level + 1

        while not self.is_at_end() and not self.check_next_indent(expected_indent):
            if self.check_indent(expected_indent):
                if self.check(TokenType.DEFINE) and self.check_next(TokenType.FUNCTION):
                    methods.append(self.parse_function())
            else:
                break

        return InterfaceDef(name, methods, visibility)

    def parse_constructor(self) -> ConstructorDef:
        """Parse constructor definition"""
        visibility = "public"

        if self.match(TokenType.PUBLIC, TokenType.PRIVATE, TokenType.PROTECTED):
            visibility = self.previous().value

        self.consume(TokenType.CONSTRUCTOR, "Expected 'constructor' keyword")

        parameters = []
        if self.match(TokenType.THAT):
            self.consume(TokenType.TAKES, "Expected 'takes' after 'that'")
            parameters = self.parse_parameters()

        self.consume(TokenType.COLON, "Expected ':' after constructor signature")

        body = []
        expected_indent = self.indent_level + 1

        while not self.is_at_end() and not self.check_next_indent(expected_indent):
            if self.check_indent(expected_indent):
                body.append(self.parse_statement())
            else:
                break

        return ConstructorDef(parameters, body, visibility)

    def parse_parameters(self) -> List[Parameter]:
        """Parse parameter list"""
        parameters = []

        if not self.check(TokenType.COLON):  # Empty parameter list
            param_name = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
            param_type = None

            if self.match(TokenType.AS):
                param_type = self.parse_type()

            parameters.append(Parameter(param_name, param_type))

            while self.match(TokenType.COMMA):
                param_name = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
                param_type = None

                if self.match(TokenType.AS):
                    param_type = self.parse_type()

                parameters.append(Parameter(param_name, param_type))

        return parameters

    def parse_type(self) -> TypeNode:
        """Parse type annotation"""
        type_name = self.consume(TokenType.IDENTIFIER, "Expected type name").value
        is_array = False
        generic_args = []

        # Check for generic arguments
        if self.match(TokenType.LESS_THAN):
            while not self.check(TokenType.GREATER_THAN) and not self.is_at_end():
                generic_args.append(self.parse_type())
                if not self.match(TokenType.COMMA):
                    break
            self.consume(TokenType.GREATER_THAN, "Expected '>' after generic arguments")

        # Check for array notation
        if self.match(TokenType.LBRACKET):
            self.consume(TokenType.RBRACKET, "Expected ']' after '['")
            is_array = True

        return TypeNode(type_name, is_array, generic_args)

    def parse_variable_declaration(self, visibility: str = "private") -> VariableDecl:
        """Parse variable declaration"""
        self.consume(TokenType.VARIABLE, "Expected 'variable' keyword")
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        type_node = None
        initializer = None

        if self.match(TokenType.AS):
            type_node = self.parse_type()

        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()

        return VariableDecl(name, type_node, initializer, visibility)

    def parse_statement(self) -> Any:
        """Parse a statement"""
        # Skip any indentation tokens
        while self.match(TokenType.INDENT, TokenType.DEDENT, TokenType.NEWLINE):
            pass

        if self.is_at_end():
            return None

        if self.match(TokenType.CREATE):
            return self.parse_create_statement()
        elif self.match(TokenType.SET):
            return self.parse_set_statement()
        elif self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.FOR):
            return self.parse_for_statement()
        elif self.match(TokenType.WHILE):
            return self.parse_while_statement()
        elif self.match(TokenType.RETURN):
            return self.parse_return_statement()
        elif self.match(TokenType.TRY):
            return self.parse_try_catch_statement()
        elif self.match(TokenType.THROW):
            return self.parse_throw_statement()
        elif self.match(TokenType.BREAK):
            return BreakStatement()
        elif self.match(TokenType.CONTINUE):
            return ContinueStatement()
        else:
            # Expression statement
            expr = self.parse_expression()
            return expr

    def parse_create_statement(self) -> VariableDecl:
        """Parse 'create variable as type' statement"""
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.AS, "Expected 'as' after variable name")
        type_node = self.parse_type()

        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()

        return VariableDecl(name, type_node, initializer)

    def parse_set_statement(self) -> Assignment:
        """Parse 'set variable to value' statement"""
        target = self.parse_expression()
        self.consume(TokenType.TO, "Expected 'to' in set statement")
        value = self.parse_expression()
        return Assignment(target, value)

    def parse_if_statement(self) -> IfStatement:
        """Parse if-elif-else statement"""
        condition = self.parse_expression()
        self.consume(TokenType.COLON, "Expected ':' after condition")

        then_body = []
        expected_indent = self.indent_level + 1

        while not self.is_at_end() and not self.check_next_indent(expected_indent):
            if self.check_indent(expected_indent):
                then_body.append(self.parse_statement())
            else:
                break

        elif_branches = []
        else_body = None

        # Handle elif branches
        while self.match(TokenType.ELIF):
            self.consume(TokenType.COLON, "Expected ':' after elif condition")
            elif_condition = self.parse_expression()
            elif_body = []

            while not self.is_at_end() and not self.check_next_indent(expected_indent):
                if self.check_indent(expected_indent):
                    elif_body.append(self.parse_statement())
                else:
                    break

            elif_branches.append((elif_condition, elif_body))

        # Handle else branch
        if self.match(TokenType.ELSE):
            self.consume(TokenType.COLON, "Expected ':' after else")
            else_body = []

            while not self.is_at_end() and not self.check_next_indent(expected_indent):
                if self.check_indent(expected_indent):
                    else_body.append(self.parse_statement())
                else:
                    break

        return IfStatement(condition, then_body, elif_branches, else_body)

    def parse_for_statement(self) -> ForStatement:
        """Parse for loop statement"""
        self.consume(TokenType.EACH, "Expected 'each' in for loop")
        iterator = self.consume(TokenType.IDENTIFIER, "Expected iterator variable").value
        self.consume(TokenType.IN, "Expected 'in' in for loop")
        iterable = self.parse_expression()
        self.consume(TokenType.COLON, "Expected ':' after for condition")

        body = []
        expected_indent = self.indent_level + 1

        while not self.is_at_end() and not self.check_next_indent(expected_indent):
            if self.check_indent(expected_indent):
                body.append(self.parse_statement())
            else:
                break

        return ForStatement(iterator, iterable, body)

    def parse_while_statement(self) -> WhileStatement:
        """Parse while loop statement"""
        condition = self.parse_expression()
        self.consume(TokenType.COLON, "Expected ':' after while condition")

        body = []
        expected_indent = self.indent_level + 1

        while not self.is_at_end() and not self.check_next_indent(expected_indent):
            if self.check_indent(expected_indent):
                body.append(self.parse_statement())
            else:
                break

        return WhileStatement(condition, body)

    def parse_return_statement(self) -> ReturnStatement:
        """Parse return statement"""
        value = None
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.EOF):
            value = self.parse_expression()
        return ReturnStatement(value)

    def parse_try_catch_statement(self) -> TryCatchStatement:
        """Parse try-catch-finally statement"""
        self.consume(TokenType.COLON, "Expected ':' after try")
        try_body = []
        expected_indent = self.indent_level + 1

        while not self.is_at_end() and not self.check_next_indent(expected_indent):
            if self.check_indent(expected_indent):
                try_body.append(self.parse_statement())
            else:
                break

        catch_clauses = []
        finally_body = None

        # Handle catch clauses
        while self.match(TokenType.CATCH):
            exception_type = self.consume(TokenType.IDENTIFIER, "Expected exception type").value
            variable = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
            self.consume(TokenType.COLON, "Expected ':' after catch clause")

            catch_body = []
            while not self.is_at_end() and not self.check_next_indent(expected_indent):
                if self.check_indent(expected_indent):
                    catch_body.append(self.parse_statement())
                else:
                    break

            catch_clauses.append((exception_type, variable, catch_body))

        # Handle finally clause
        if self.match(TokenType.FINALLY):
            self.consume(TokenType.COLON, "Expected ':' after finally")
            finally_body = []

            while not self.is_at_end() and not self.check_next_indent(expected_indent):
                if self.check_indent(expected_indent):
                    finally_body.append(self.parse_statement())
                else:
                    break

        return TryCatchStatement(try_body, catch_clauses, finally_body)

    def parse_throw_statement(self) -> ThrowStatement:
        """Parse throw statement"""
        exception = self.parse_expression()
        return ThrowStatement(exception)

    def parse_expression(self) -> Any:
        """Parse expression with precedence"""
        return self.parse_assignment()

    def parse_assignment(self) -> Any:
        """Parse assignment expression"""
        expr = self.parse_logical_or()

        if self.match(TokenType.ASSIGN, TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY_OP, TokenType.DIVIDE_OP, TokenType.MODULO_OP):
            operator = self.previous().value
            if operator != "=":
                operator += "="
            value = self.parse_assignment()
            return Assignment(expr, value, operator)

        return expr

    def parse_logical_or(self) -> Any:
        """Parse logical OR expression"""
        expr = self.parse_logical_and()

        while self.match(TokenType.OR_OP):
            operator = self.previous().value
            right = self.parse_logical_and()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_logical_and(self) -> Any:
        """Parse logical AND expression"""
        expr = self.parse_equality()

        while self.match(TokenType.AND_OP):
            operator = self.previous().value
            right = self.parse_equality()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_equality(self) -> Any:
        """Parse equality expression"""
        expr = self.parse_comparison()

        while self.match(TokenType.EQUALS_OP, TokenType.NOT_EQUALS):
            operator = self.previous().value
            right = self.parse_comparison()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_comparison(self) -> Any:
        """Parse comparison expression"""
        expr = self.parse_term()

        while True:
            # Handle natural language comparisons
            if self.match(TokenType.IS):
                if self.match(TokenType.LESS):
                    self.consume(TokenType.THAN, "Expected 'than' after 'less'")
                    operator = "<"
                elif self.match(TokenType.GREATER):
                    self.consume(TokenType.THAN, "Expected 'than' after 'greater'")
                    operator = ">"
                elif self.match(TokenType.EQUALS):
                    operator = "=="
                else:
                    raise ParserError("Expected comparison operator after 'is'", self.peek())
            elif self.match(TokenType.LESS):
                self.consume(TokenType.THAN, "Expected 'than' after 'less'")
                operator = "<"
            elif self.match(TokenType.GREATER):
                self.consume(TokenType.THAN, "Expected 'than' after 'greater'")
                operator = ">"
            # Handle standard operators
            elif self.match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL, TokenType.LESS_THAN, TokenType.LESS_EQUAL):
                operator = self.previous().value
            else:
                break

            right = self.parse_term()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_term(self) -> Any:
        """Parse term expression (addition and subtraction)"""
        expr = self.parse_factor()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous().value
            right = self.parse_factor()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_factor(self) -> Any:
        """Parse factor expression (multiplication and division)"""
        expr = self.parse_unary()

        while self.match(TokenType.MULTIPLY_OP, TokenType.DIVIDE_OP, TokenType.MODULO_OP):
            operator = self.previous().value
            right = self.parse_unary()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_unary(self) -> Any:
        """Parse unary expression"""
        if self.match(TokenType.NOT_OP, TokenType.PLUS, TokenType.MINUS):
            operator = self.previous().value
            right = self.parse_unary()
            return UnaryOp(operator, right)

        return self.parse_primary()

    def parse_primary(self) -> Any:
        """Parse primary expression"""
        if self.match(TokenType.NUMBER):
            return Literal(float(self.previous().value) if '.' in self.previous().value else int(self.previous().value),
                          "float" if '.' in self.previous().value else "int")
        elif self.match(TokenType.STRING):
            return Literal(self.previous().value[1:-1], "string")  # Remove quotes
        elif self.match(TokenType.TRUE):
            return Literal(True, "boolean")
        elif self.match(TokenType.FALSE):
            return Literal(False, "boolean")
        elif self.match(TokenType.THIS):
            return This()
        elif self.match(TokenType.IDENTIFIER):
            name = self.previous().value
            return self.parse_identifier_expression(name)
        elif self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        elif self.match(TokenType.LBRACKET):
            return self.parse_list_literal()
        elif self.match(TokenType.LBRACE):
            return self.parse_dict_literal()

        raise ParserError("Expected expression", self.peek())

    def parse_identifier_expression(self, name: str) -> Any:
        """Parse identifier-based expressions (variables, function calls, attribute access)"""
        expr = Variable(name)

        # Handle function calls
        if self.match(TokenType.LPAREN):
            arguments = []
            if not self.check(TokenType.RPAREN):
                arguments.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    arguments.append(self.parse_expression())
            self.consume(TokenType.RPAREN, "Expected ')' after function arguments")
            expr = FunctionCall(name, arguments)

        # Handle attribute access
        elif self.match(TokenType.DOT):
            attribute = self.consume(TokenType.IDENTIFIER, "Expected attribute name").value
            expr = AttributeAccess(expr, attribute)

            # Handle method calls
            if self.match(TokenType.LPAREN):
                arguments = []
                if not self.check(TokenType.RPAREN):
                    arguments.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        arguments.append(self.parse_expression())
                self.consume(TokenType.RPAREN, "Expected ')' after method arguments")
                expr = FunctionCall(attribute, arguments, True, name)

        # Handle array access
        elif self.match(TokenType.LBRACKET):
            index = self.parse_expression()
            self.consume(TokenType.RBRACKET, "Expected ']' after array index")
            expr = ArrayAccess(expr, index)

        return expr

    def parse_list_literal(self) -> ListLiteral:
        """Parse list literal"""
        items = []
        if not self.check(TokenType.RBRACKET):
            items.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                items.append(self.parse_expression())
        self.consume(TokenType.RBRACKET, "Expected ']' after list items")
        return ListLiteral(items)

    def parse_dict_literal(self) -> DictLiteral:
        """Parse dictionary literal"""
        items = []
        if not self.check(TokenType.RBRACE):
            key = self.parse_expression()
            self.consume(TokenType.COLON, "Expected ':' after dictionary key")
            value = self.parse_expression()
            items.append((key, value))
            while self.match(TokenType.COMMA):
                key = self.parse_expression()
                self.consume(TokenType.COLON, "Expected ':' after dictionary key")
                value = self.parse_expression()
                items.append((key, value))
        self.consume(TokenType.RBRACE, "Expected '}' after dictionary items")
        return DictLiteral(items)

    # Helper methods
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def peek(self) -> Token:
        return self.tokens[self.current] if not self.is_at_end() else None

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)

    def match(self, *types) -> bool:
        for type_ in types:
            if self.check(type_):
                self.advance()
                return True
        return False

    def check(self, type_: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type_

    def check_next(self, type_: TokenType) -> bool:
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type == type_

    def consume(self, type_: TokenType, message: str) -> Token:
        if self.check(type_):
            return self.advance()
        raise ParserError(message, self.peek())

    def backtrack(self):
        """Backtrack by one token"""
        if self.current > 0:
            self.current -= 1

    def check_indent(self, expected_level: int) -> bool:
        """Check if current position has expected indentation level"""
        # This is a simplified version - in practice you'd need to handle INDENT/DEDENT tokens
        return True

    def check_next_indent(self, expected_level: int) -> bool:
        """Check if next position would have different indentation"""
        # This is a simplified version - in practice you'd need to handle INDENT/DEDENT tokens
        return False


def main():
    """Test the parser with sample AGK code"""
    test_code = '''
define function calculate_total that takes items:
    create total as Integer
    set total to 0
    return total
'''

    lexer = AGKLexer(test_code)
    try:
        tokens = lexer.tokenize()
        print("Tokens:")
        for i, token in enumerate(tokens):
            print(f"{i}: {token}")
        print("\nParsing...")
        parser = AGKParser(tokens)
        ast = parser.parse()

        # Print the AST
        from agk_ast import ASTPrinter
        printer = ASTPrinter()
        ast.accept(printer)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()