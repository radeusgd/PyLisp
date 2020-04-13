from parsy import regex, string, generate

from pylisp.ast import *


class Parser(object):
    def __init__(self):
        whitespace = regex(r'\s*')

        def lexeme(p):
            return p << whitespace

        number_literal = lexeme(regex("\\-?[0-9]+")).map(lambda v: IntLiteral(int(v)))
        symbol = lexeme(regex("[a-zA-Z+\\-*/=<>!?_][a-zA-Z+\\-*/=<>!?0-9_]*")).map(Identifier)
        string_part = regex(r'[^"\\]+')
        string_literal = lexeme(string("\"") >> string_part.many().concat() << string("\"") | string("'") >> string_part.many().concat() << string("'")).map(StringLiteral)
        open_paren = lexeme(string("("))
        close_paren = lexeme(string(")"))

        @generate
        def exprlist():
            yield open_paren
            elements = yield self._expr.many()
            yield close_paren
            return ExpressionList(elements)

        # sample of desugaring
        @generate
        def quote():
            yield string("'")
            expr = yield self._expr
            return ExpressionList([Identifier("quote"), expr])

        self._expr = number_literal | string_literal | quote | symbol | exprlist
        self._file = self._expr.many()

    def parse_expr(self, code):
        return self._expr.parse(code)

    def parse_file(self, code):
        return self._file.parse(code)
