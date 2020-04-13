from typing import Callable, TypeVar

T = TypeVar('T')


class Tree:
    """
    To separate parsing and semantics, we create a separate AST class hierarchy.
    The parser returns an AST which is an abstract representation of the parsed program,
    this could be used for example for easier implementation of syntax analysis.
    Later the AST can be represented to our value representation that can then be interpreted.
    """
    def visit(self,
              identifier: Callable[["Identifier"], T],
              intlit: Callable[["IntLiteral"], T],
              strlit: Callable[["StringLiteral"], T],
              exprlist: Callable[["ExpressionList"], T]
              ) -> T:
        """
        visit represents the Scott's encoding of the Abstract Data Type representing our AST.
        Calling visit acts as a pattern match, the caller provides a function processing each case
        and the case is executed depending on the concrete object that has been unpacked.
        The result of the specific function is returned as the result of the pattern match.
        """
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


class Identifier(Tree):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def visit(self,
              identifier: Callable[["Identifier"], T],
              intlit: Callable[["IntLiteral"], T],
              strlit: Callable[["StringLiteral"], T],
              exprlist: Callable[["ExpressionList"], T]
              ) -> T:
        return identifier(self)

    def __str__(self):
        return f"Identifier({self.name})"

    def __eq__(self, other):
        if isinstance(other, Identifier):
            return self.name == other.name
        return False


class Literal(Tree):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def visit(self,
              identifier: Callable[["Identifier"], T],
              intlit: Callable[["IntLiteral"], T],
              strlit: Callable[["StringLiteral"], T],
              exprlist: Callable[["ExpressionList"], T]
              ) -> T:
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def __eq__(self, other):
        if isinstance(other, Literal):
            return self.value == other.value
        return False


class IntLiteral(Literal):
    def __init__(self, value):
        super().__init__(value)

    def visit(self,
              identifier: Callable[["Identifier"], T],
              intlit: Callable[["IntLiteral"], T],
              strlit: Callable[["StringLiteral"], T],
              exprlist: Callable[["ExpressionList"], T]
              ) -> T:
        return intlit(self)

    def __str__(self):
        return f"IntLiteral({str(self.value)})"


class StringLiteral(Literal):
    def __init__(self, value):
        super().__init__(value)

    def visit(self,
              identifier: Callable[["Identifier"], T],
              intlit: Callable[["IntLiteral"], T],
              strlit: Callable[["StringLiteral"], T],
              exprlist: Callable[["ExpressionList"], T]
              ) -> T:
        return strlit(self)

    def __str__(self):
        return f"StringLiteral('{self.value}')"


class ExpressionList(Tree):
    def __init__(self, values):
        super().__init__()
        self.values = values

    def visit(self,
              identifier: Callable[["Identifier"], T],
              intlit: Callable[["IntLiteral"], T],
              strlit: Callable[["StringLiteral"], T],
              exprlist: Callable[["ExpressionList"], T]
              ) -> T:
        return exprlist(self)

    def __str__(self):
        values = ", ".join(map(str, self.values))
        return f"ExpressionList({values})"

    def head(self) -> Tree:
        return self.values[0]

    def tail(self) -> "ExpressionList":
        return ExpressionList(self.values[1:])

    def is_empty(self) -> bool:
        return len(self.values) == 0

    def __len__(self):
        return len(self.values)

    def __eq__(self, other):
        if isinstance(other, ExpressionList):
            return self.values == other.values
        return False
