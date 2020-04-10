from typing import Callable, TypeVar, List

T = TypeVar('T')


class Tree:
    def visit(self,
              symbol: Callable[["Symbol"], T],
              intlit: Callable[["IntLiteral"], T],
              strlit: Callable[["StringLiteral"], T],
              exprlist: Callable[["ExpressionList"], T]
              ) -> T:
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


class Symbol(Tree):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def visit(self,
              symbol: Callable[["Symbol"], T],
              intlit: Callable[["IntLiteral"], T],
              strlit: Callable[["StringLiteral"], T],
              exprlist: Callable[["ExpressionList"], T]
              ) -> T:
        return symbol(self)

    def __str__(self):
        return f"Symbol({self.name})"


class Literal(Tree):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def visit(self,
              symbol: Callable[["Symbol"], T],
              intlit: Callable[["IntLiteral"], T],
              strlit: Callable[["StringLiteral"], T],
              exprlist: Callable[["ExpressionList"], T]
              ) -> T:
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


class IntLiteral(Literal):
    def __init__(self, value):
        super().__init__(value)

    def visit(self,
              symbol: Callable[["Symbol"], T],
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
              symbol: Callable[["Symbol"], T],
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
              symbol: Callable[["Symbol"], T],
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