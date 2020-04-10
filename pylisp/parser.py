from parsy import regex, string, generate

from pylisp.ast import *


class Parser(object):
    def __init__(self):
        whitespace = regex(r'\s*')

        def lexeme(p):
            return p << whitespace

        number_literal = lexeme(regex("\\-?[0-9]+")).map(lambda v: IntLiteral(int(v)))
        symbol = lexeme(regex("[a-zA-Z+\\-*/=<>!?][a-zA-Z+\\-*/=<>!?0-9]*")).map(Symbol)
        string_part = regex(r'[^"\\]+')
        string_literal = lexeme(string("\"") >> string_part.many().concat() << string("\"") | string("'") >> string_part.many().concat() << string("'")).map(StringLiteral)
        open_paren = lexeme(string("("))
        close_paren = lexeme(string(")"))

        @generate
        def exprlist():
            yield open_paren
            elements = yield self._expr_.many()
            yield close_paren
            return ExpressionList(elements)

        self._expr_ = number_literal | string_literal | symbol | exprlist

    def parse_expr(self, code):
        return self._expr_.parse(code)
