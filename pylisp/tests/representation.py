from pylisp.interpreter import represent_code, Symbol, ConsCell
from pylisp.ast import *


def test_represent():
    assert represent_code(IntLiteral(1)) == 1
    assert represent_code(StringLiteral("abc")) == "abc"
    assert represent_code(Identifier("ref")) == Symbol("ref")
    assert represent_code(ExpressionList([IntLiteral(0), ExpressionList([IntLiteral(1), IntLiteral(2)])])) \
        == ConsCell(0, ConsCell(ConsCell(1, ConsCell(2, None)), None))
