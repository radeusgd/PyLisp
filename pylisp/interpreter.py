from typing import Union, Iterable

from pylisp.ast import *
from pylisp.environment import Environment
from pylisp.errors import CannotCall, WrongOperatorUsage


class Builtin:
    def __init__(self, name, arity):
        """
        name - name of the operator used to invoke it
        arity - arguments count, if None the operator is Vararg
        """
        self.name = name
        self.arity = arity

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


def interpret(term: Tree, env: Environment):
    def interpret_symbol(symbol: Symbol):
        return env.lookup(symbol.name)

    def interpret_lit(lit: Literal):
        return lit.value

    def interpret_exprlist(exprlist: ExpressionList):
        return interpret_sexpr(exprlist, env)

    return term.visit(
        symbol=interpret_symbol,
        intlit=interpret_lit,
        strlit=interpret_lit,
        exprlist=interpret_exprlist
    )


def interpret_sexpr(sexpr: ExpressionList, env: Environment):
    if sexpr.is_empty():
        return []

    op = interpret(sexpr.head(), env)
    args = sexpr.tail()

    if isinstance(op, Builtin):
        if op.arity is not None and len(args) != op.arity:
            raise WrongOperatorUsage(f"{op.name} expects {op.arity} arguments but was given {len(args)})")
        return op(env, *args.values)

    if not callable(op):
        raise CannotCall(f"{str(sexpr.head())} cannot be applied")
    else:
        return op(sexpr.tail())


def interpret_list(terms: Iterable[Tree], env: Environment) -> list:
    """
    Helper function that takes a list of terms and interprets each of them, returning list of respective results on success.
    """
    return list(map(lambda term: interpret(term, env), terms))
