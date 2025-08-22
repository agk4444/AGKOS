#!/usr/bin/env python3
"""
AGK Language Lexer

Tokenizes natural language programming syntax for the AGK compiler.
"""

import re
from enum import Enum
from typing import List, Tuple, Optional


class TokenType(Enum):
    # Keywords
    DEFINE = "DEFINE"
    FUNCTION = "FUNCTION"
    EXTERNAL = "EXTERNAL"
    CLASS = "CLASS"
    INTERFACE = "INTERFACE"
    ABSTRACT = "ABSTRACT"
    IMPLEMENTS = "IMPLEMENTS"
    EXTENDS = "EXTENDS"
    CONSTRUCTOR = "CONSTRUCTOR"
    METHOD = "METHOD"
    VARIABLE = "VARIABLE"
    CONSTANT = "CONSTANT"
    RETURN = "RETURN"
    IF = "IF"
    ELSE = "ELSE"
    ELIF = "ELIF"
    FOR = "FOR"
    WHILE = "WHILE"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    TRY = "TRY"
    CATCH = "CATCH"
    FINALLY = "FINALLY"
    THROW = "THROW"
    IMPORT = "IMPORT"
    FROM = "FROM"
    AS = "AS"
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    PROTECTED = "PROTECTED"
    STATIC = "STATIC"
    FINAL = "FINAL"

    # Natural language constructs
    THAT = "THAT"
    TAKES = "TAKES"
    RETURNS = "RETURNS"
    CREATE = "CREATE"
    SET = "SET"
    TO = "TO"
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    IS = "IS"
    ARE = "ARE"
    EQUALS = "EQUALS"
    GREATER = "GREATER"
    LESS = "LESS"
    THAN = "THAN"
    EACH = "EACH"
    IN = "IN"
    WITH = "WITH"
    USING = "USING"
    CALL = "CALL"
    THE = "THE"
    THIS = "THIS"
    TRUE = "TRUE"
    FALSE = "FALSE"

    # Operators
    PLUS = "+"
    MINUS = "-"
    MULTIPLY_OP = "*"
    DIVIDE_OP = "/"
    MODULO_OP = "%"
    ASSIGN = "="
    EQUALS_OP = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    AND_OP = "&&"
    OR_OP = "||"
    NOT_OP = "!"

    # Delimiters
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    COMMA = ","
    DOT = "."
    COLON = ":"
    SEMICOLON = ";"
    QUOTE = '"'
    SINGLE_QUOTE = "'"

    # Literals and identifiers
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"

    # Special
    EOF = "EOF"
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"


class Token:
    def __init__(self, type_: TokenType, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, column={self.column})"


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at line {line}, column {column}: {message}")


class AGKLexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.current = 0
        self.line = 1
        self.column = 1
        self.indent_stack = [0]
        self.current_indent = 0

        # Keywords mapping
        self.keywords = {
            'define': TokenType.DEFINE,
            'function': TokenType.FUNCTION,
            'external': TokenType.EXTERNAL,
            'class': TokenType.CLASS,
            'interface': TokenType.INTERFACE,
            'abstract': TokenType.ABSTRACT,
            'implements': TokenType.IMPLEMENTS,
            'extends': TokenType.EXTENDS,
            'constructor': TokenType.CONSTRUCTOR,
            'method': TokenType.METHOD,
            'variable': TokenType.VARIABLE,
            'constant': TokenType.CONSTANT,
            'return': TokenType.RETURN,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'elif': TokenType.ELIF,
            'for': TokenType.FOR,
            'while': TokenType.WHILE,
            'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE,
            'try': TokenType.TRY,
            'catch': TokenType.CATCH,
            'finally': TokenType.FINALLY,
            'throw': TokenType.THROW,
            'import': TokenType.IMPORT,
            'from': TokenType.FROM,
            'as': TokenType.AS,
            'public': TokenType.PUBLIC,
            'private': TokenType.PRIVATE,
            'protected': TokenType.PROTECTED,
            'static': TokenType.STATIC,
            'final': TokenType.FINAL,
        }

        # Natural language constructs
        self.nl_constructs = {
            'that': TokenType.THAT,
            'takes': TokenType.TAKES,
            'returns': TokenType.RETURNS,
            'create': TokenType.CREATE,
            'set': TokenType.SET,
            'to': TokenType.TO,
            'add': TokenType.ADD,
            'subtract': TokenType.SUBTRACT,
            'multiply': TokenType.MULTIPLY,
            'divide': TokenType.DIVIDE,
            'modulo': TokenType.MODULO,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            'is': TokenType.IS,
            'are': TokenType.ARE,
            'equals': TokenType.EQUALS,
            'greater': TokenType.GREATER,
            'less': TokenType.LESS,
            'than': TokenType.THAN,
            'each': TokenType.EACH,
            'in': TokenType.IN,
            'with': TokenType.WITH,
            'using': TokenType.USING,
            'call': TokenType.CALL,
            'the': TokenType.THE,
            'this': TokenType.THIS,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
        }

    def tokenize(self) -> List[Token]:
        """Main tokenization method"""
        while not self.is_at_end():
            self.scan_token()
        self.add_token(TokenType.EOF, "", self.line, self.column)
        return self.tokens

    def scan_token(self):
        char = self.advance()

        # Handle indentation at start of line
        if char == '\n':
            self.add_token(TokenType.NEWLINE, char, self.line - 1, self.column - 1)
            self.line += 1
            self.column = 1
            self.handle_indentation()
            return

        # Skip whitespace
        if char.isspace() and char != '\n':
            self.column += 1
            return

        # Skip comments
        if char == '#':
            while not self.is_at_end() and self.peek() != '\n':
                self.advance()
                self.column += 1
            return

        # Single character tokens
        if char == '+': self.add_token(TokenType.PLUS, char)
        elif char == '-': self.add_token(TokenType.MINUS, char)
        elif char == '*': self.add_token(TokenType.MULTIPLY_OP, char)
        elif char == '/': self.add_token(TokenType.DIVIDE_OP, char)
        elif char == '%': self.add_token(TokenType.MODULO_OP, char)
        elif char == '=':
            if self.match('='):
                self.add_token(TokenType.EQUALS_OP, "==")
            else:
                self.add_token(TokenType.ASSIGN, "=")
        elif char == '!':
            if self.match('='):
                self.add_token(TokenType.NOT_EQUALS, "!=")
            else:
                self.add_token(TokenType.NOT_OP, "!")
        elif char == '>':
            if self.match('='):
                self.add_token(TokenType.GREATER_EQUAL, ">=")
            else:
                self.add_token(TokenType.GREATER_THAN, ">")
        elif char == '<':
            if self.match('='):
                self.add_token(TokenType.LESS_EQUAL, "<=")
            else:
                self.add_token(TokenType.LESS_THAN, "<")
        elif char == '&':
            if self.match('&'):
                self.add_token(TokenType.AND_OP, "&&")
        elif char == '|':
            if self.match('|'):
                self.add_token(TokenType.OR_OP, "||")
        elif char == '(': self.add_token(TokenType.LPAREN, char)
        elif char == ')': self.add_token(TokenType.RPAREN, char)
        elif char == '{': self.add_token(TokenType.LBRACE, char)
        elif char == '}': self.add_token(TokenType.RBRACE, char)
        elif char == '[': self.add_token(TokenType.LBRACKET, char)
        elif char == ']': self.add_token(TokenType.RBRACKET, char)
        elif char == ',': self.add_token(TokenType.COMMA, char)
        elif char == '.': self.add_token(TokenType.DOT, char)
        elif char == ':': self.add_token(TokenType.COLON, char)
        elif char == ';': self.add_token(TokenType.SEMICOLON, char)
        elif char == '"': self.string('"')
        elif char == "'": self.string("'")

        # Numbers
        elif char.isdigit():
            self.number()

        # Identifiers and keywords
        elif char.isalpha() or char == '_':
            self.identifier()

        else:
            raise LexerError(f"Unexpected character: {char}", self.line, self.column - 1)

    def handle_indentation(self):
        """Handle Python-style indentation"""
        spaces = 0
        while not self.is_at_end() and self.peek() == ' ':
            self.advance()
            spaces += 1
            self.column += 1

        if spaces > self.current_indent:
            self.indent_stack.append(spaces)
            self.current_indent = spaces
            self.add_token(TokenType.INDENT, "INDENT", self.line, self.column)
        elif spaces < self.current_indent:
            while spaces < self.current_indent and len(self.indent_stack) > 1:
                self.indent_stack.pop()
                self.current_indent = self.indent_stack[-1]
                self.add_token(TokenType.DEDENT, "DEDENT", self.line, self.column)

    def identifier(self):
        start = self.current - 1
        start_col = self.column - 1

        while not self.is_at_end() and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()
            self.column += 1

        text = self.source[start:self.current]
        token_type = self.keywords.get(text.lower(), None)
        if token_type is None:
            token_type = self.nl_constructs.get(text.lower(), TokenType.IDENTIFIER)

        self.add_token(token_type, text, self.line, start_col)

    def number(self):
        start = self.current - 1
        start_col = self.column - 1

        while not self.is_at_end() and self.peek().isdigit():
            self.advance()
            self.column += 1

        # Handle decimal numbers
        if not self.is_at_end() and self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            self.column += 1

            while not self.is_at_end() and self.peek().isdigit():
                self.advance()
                self.column += 1

        text = self.source[start:self.current]
        self.add_token(TokenType.NUMBER, text, self.line, start_col)

    def string(self, quote_type: str):
        start = self.current - 1
        start_col = self.column - 1

        while not self.is_at_end() and self.peek() != quote_type:
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
            self.advance()
            self.column += 1

        if self.is_at_end():
            raise LexerError("Unterminated string", self.line, start_col)

        # Consume the closing quote
        self.advance()
        self.column += 1

        text = self.source[start:self.current]
        self.add_token(TokenType.STRING, text, self.line, start_col)

    def match(self, expected: str) -> bool:
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def add_token(self, type_: TokenType, value: str, line: int = None, column: int = None):
        if line is None:
            line = self.line
        if column is None:
            column = self.column - len(value) if value else self.column
        self.tokens.append(Token(type_, value, line, column))

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)


def main():
    """Test the lexer with sample AGK code"""
    test_code = '''
define function calculate_total that takes items:
    create total as 0
    for each item in items:
        add item to total
    return total

define class Person:
    private name as String
    private age as Integer

    define constructor that takes name as String, age as Integer:
        set this name to name
        set this age to age

    define function get_name that returns String:
        return this name
'''

    lexer = AGKLexer(test_code)
    try:
        tokens = lexer.tokenize()
        for token in tokens:
            print(token)
    except LexerError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()