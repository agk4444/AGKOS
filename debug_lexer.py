#!/usr/bin/env python3
from agk_lexer import AGKLexer

test_code = '''
define function fibonacci that takes n as Integer and returns Integer:
    if n is less than 2:
        return n
'''

lexer = AGKLexer(test_code)
tokens = lexer.tokenize()

print("Tokens for 'if n is less than 2:'")
for i, token in enumerate(tokens):
    print(f"{i:2d}: {token}")