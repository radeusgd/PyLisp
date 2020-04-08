class Tree(object):
    def visit(self, symbol, intlit, strlit, exprlist):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


class Symbol(Tree):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def visit(self, symbol, intlit, strlit, exprlist):
        symbol(self)

    def __str__(self):
        return f"Symbol({self.name})"


class IntLiteral(Tree):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def visit(self, symbol, intlit, strlit, exprlist):
        intlit(self)

    def __str__(self):
        return f"IntLiteral({str(self.value)})"


class StringLiteral(Tree):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def visit(self, symbol, intlit, strlit, exprlist):
        strlit(self)

    def __str__(self):
        return f"StringLiteral('{self.value}')"


class ExpressionList(Tree):
    def __init__(self, values):
        super().__init__()
        self.values = values

    def visit(self, symbol, intlit, strlit, exprlist):
        exprlist(self)

    def __str__(self):
        values = ", ".join(map(str, self.values))
        return f"ExpressionList({values})"
