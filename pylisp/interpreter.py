from typing import Union

from pylisp.ast import *
from pylisp.environment import Environment


class Interpreter(object):
    def interpret(self, term: Tree, env: Environment) -> object:
        def interpret_symbol(symbol: Symbol):
            return env.lookup(symbol.name)

        def interpret_lit(lit: Literal):
            return lit.value

        def interpret_exprlist(exprlist: ExpressionList):
            return self.interpret_sexpr(exprlist, env)

        return term.visit(
            symbol=interpret_symbol,
            intlit=interpret_lit,
            strlit=interpret_lit,
            exprlist=interpret_exprlist
        )

    def interpret_sexpr(self, sexpr: ExpressionList, env: Environment):
        if sexpr.isempty():
            return []

        if isinstance(sexpr.head(), Symbol):
            car = sexpr.head().name  # TODO handle the cast in a better way
            if car == "let":
                return self.interpret_let(sexpr.tail(), env)
            elif car == "+":
                args = map(lambda t: self.interpret(t, env), sexpr.tail())
                return sum(args)

        fun = self.interpret(sexpr.head(), env)
        if not callable(fun):
            raise RuntimeError(f"{str(fun)} is not a function")
        else:
            args = list(map(lambda t: self.interpret(t, env), sexpr.tail()))
            return fun(args)

    def interpret_let(self, args, env: Environment):
        # TODO recursive let
        if len(args) != 2:
            raise RuntimeError("Wrong let form")
        bindings = args[0]
        # TODO more robust DSL for defining macros
        if not isinstance(bindings, ExpressionList):
            raise RuntimeError("Wrong let form")
        if len(bindings.values) != 2:
            raise RuntimeError("Wrong let form")

        [symb, inner] = bindings.values
        outer = args[1]

        if not isinstance(symb, Symbol):
            raise RuntimeError("You can only let to symbols")

        v = self.interpret(inner, env)
        extended_env = env.extend(symb.name, v)
        return self.interpret(outer, extended_env)
