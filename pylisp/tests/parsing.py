from pylisp.parser import Parser
from pylisp.ast import *


def test_parser():
    par = Parser()

    assert par.parse_expr("42") == IntLiteral(42)
    assert par.parse_expr('"łabądź"') == StringLiteral("łabądź")
    assert par.parse_expr("abc") == Identifier("abc")
    assert par.parse_expr("(f 2 3)") == ExpressionList([Identifier("f"), IntLiteral(2), IntLiteral(3)])
    assert par.parse_expr("'a") == ExpressionList([Identifier("quote"), Identifier("a")])
    assert par.parse_expr("'(1 2)") == \
           ExpressionList([Identifier("quote"), ExpressionList([IntLiteral(1), IntLiteral(2)])])
    assert par.parse_expr("(f (a b))") == \
           ExpressionList([Identifier("f"), ExpressionList([Identifier("a"), Identifier("b")])])
    assert par.parse_expr("(())") == \
           ExpressionList([ExpressionList([])])
