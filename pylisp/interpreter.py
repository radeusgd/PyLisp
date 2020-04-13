from typing import Iterable, IO, Union, List

from pylisp.ast import *
from pylisp.environment import Environment
from pylisp.errors import CannotCall, WrongOperatorUsage
from pylisp.parser import Parser


class ConsCell:
    def __init__(self, head, tail):
        self._head = head
        self._tail = tail

    def head(self):
        return self._head

    def tail(self):
        return self._tail


class Symbol:
    def __init__(self, name):
        self.name = name


LispList = Union[ConsCell, None]


def python_list_to_lisp(lst: list) -> LispList:
    if len(lst) == 0:
        return None
    return ConsCell(lst[0], python_list_to_lisp(lst[1:]))


def lisp_list_length(lst: LispList) -> int:
    if lst is None:
        return 0
    return 1 + lisp_list_length(lst.tail())


def lisp_list_to_python(lst: LispList) -> list:
    # this is the simple solution but as it creates new lists instead of reusing the old one it can be O(N^2)
    # if isinstance(lst, Cons):
    #     return [lst.head] + lisp_list_to_python(lst.tail)
    # return []
    if lst is None:
        return []

    result = [None] * lisp_list_length(lst)
    idx = 0
    while isinstance(lst, ConsCell):
        result[idx] = lst.head()
        idx += 1
        lst = lst.tail()
    return result


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


def lisp_list_to_str(lst: LispList) -> str:
    def helper(lst, acc: List[str]) -> str:
        if isinstance(lst, ConsCell):
            return  helper(lst.tail(), acc + [lisp_data_to_str(lst.head())])
        if lst is None:
            return " ".join(acc)

        # invalid list case
        return " ".join(acc) + " . " + lisp_data_to_str(lst)
    return "(" + helper(lst, []) + ")"


def lisp_data_to_str(data):
    if isinstance(data, Symbol):
        return data.name
    if isinstance(data, ConsCell) or data is None:
        return lisp_list_to_str(data)
    if isinstance(data, Builtin):
        return f"<builtin operator {data.name}>"
    if isinstance(data, str):
        return f"\"{data}\""
    return str(data)


def represent_code(tree: Tree):
    """
    To adhere to code as data paradigm, we convert the AST into data
    that represents the program structure and can be evaluated
    """
    def represent_ident(identifier: Identifier) -> object:
        return Symbol(identifier.name)

    def represent_literal(lit: Literal) -> object:
        return lit.value

    def represent_exprlist(exprlst: ExpressionList) -> object:
        mapped = list(map(represent_code, exprlst.values))
        return python_list_to_lisp(mapped)

    return tree.visit(
        identifier=represent_ident,
        intlit=represent_literal,
        strlit=represent_literal,
        exprlist=represent_exprlist
    )


def interpret(term, env: Environment):
    # a list is executed according to its specific semantics (it can be a builtin, a macro or a function call)
    if isinstance(term, ConsCell):
        return interpret_sexpr(term, env)
    # a symbol is evaluated based on the environment to the value that is bound to it
    elif isinstance(term, Symbol):
        return env.lookup(term.name)
    # other data is already treated as a value
    return term


def interpret_sexpr(sexpr: ConsCell, env: Environment):
    op = interpret(sexpr.head(), env)
    args = lisp_list_to_python(sexpr.tail())
    
    if isinstance(op, Builtin):
        if op.arity is not None and len(args) != op.arity:
            raise WrongOperatorUsage(f"{op.name} expects {op.arity} arguments but was given {len(args)})")
        return op(env, *args)

    # TODO add macros with call-by-name

    # by default do a call-by-value
    if not callable(op):
        raise CannotCall(f"{str(sexpr.head())} cannot be applied")
    else:
        return op(interpret_list(args, env))


def interpret_list(terms: Iterable[Tree], env: Environment) -> list:
    """
    Helper function that takes a list of terms and interprets each of them, returning list of respective results on success.
    """
    return list(map(lambda term: interpret(term, env), terms))


def interpret_file(file: IO, env: Environment):
    code = file.read()
    ast = Parser().parse_file(code)
    for statement in map(represent_code, ast):
        interpret(statement, env)
