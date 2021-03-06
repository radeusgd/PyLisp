from typing import Iterable, IO, Union, List

from pylisp.ast import *
from pylisp.environment import Environment
from pylisp.errors import LispError, InvalidList
from pylisp.parser import Parser


class ConsCell:
    """
    A basic building block of a LISP list.
    """
    def __init__(self, head, tail):
        self._head = head
        self._tail = tail

    def head(self):
        return self._head

    def tail(self):
        return self._tail

    def __eq__(self, other):
        if isinstance(other, ConsCell):
            return self.head() == other.head() and self.tail() == other.tail()
        return False


class Symbol:
    """
    A name in the program, used as function argument names, bindings etc.
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Symbol({self.name})"

    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.name == other.name
        return False


LispList = Union[ConsCell, None]  # a LISP list is either a ConsCell or nil (None)


def python_list_to_lisp(lst: list) -> LispList:
    """
    Converts a Python list to a LISP list.
    """
    if len(lst) == 0:
        return None
    return ConsCell(lst[0], python_list_to_lisp(lst[1:]))


def lisp_list_is_valid(lst) -> bool:
    """
    Checks if a LISP list is valid.
    """
    if lst is None:
        return True
    if isinstance(lst, ConsCell):
        return lisp_list_is_valid(lst.tail())
    return False


def lisp_list_length(lst) -> int:
    """
    Returns the length of a valid LISP list.
    """
    if lst is None:
        return 0
    if isinstance(lst, ConsCell):
        return 1 + lisp_list_length(lst.tail())
    raise InvalidList("Expected a valid list")


def lisp_list_to_python(lst) -> list:
    """
    Converts a valid LISP list to a Python list.
    """
    if not lisp_list_is_valid(lst):
        raise InvalidList(f"Expected a valid list, got {lisp_data_to_str(lst)}")
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
    """
    Represents builtin operations.
    Such an operation is called with its environment and the provided arguments' code values,
    a lot of interpretation logic actually happens in the builtins implementations.
    """
    def __init__(self, name, arity, doc):
        """
        name - name of the operator used to invoke it
        arity - arguments count, if None the operator is Vararg
        """
        self.name = name
        self.arity = arity
        self.doc = doc

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class Macro:
    """
    Represents a macro - a function that is called without evaluating its arguments.
    The value that it returns is then executed.
    """
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


def lisp_list_to_str(lst: LispList) -> str:
    """
    Helper function to convert a LISP list to a string,
    special care is taken to also handle invalid lists.
    """
    def helper(lst, acc: List[str]) -> str:
        if isinstance(lst, ConsCell):
            return helper(lst.tail(), acc + [lisp_data_to_str(lst.head())])
        if lst is None:
            return " ".join(acc)

        # invalid list case
        return " ".join(acc) + " . " + lisp_data_to_str(lst)
    return "(" + helper(lst, []) + ")"


def lisp_data_to_str(data):
    """
    Converts our LISP data into a pretty string representation
    """
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
    """
    Interprets the given code value in the environment
    """
    # a list is executed according to its specific semantics (it can be a builtin, a macro or a function call)
    if isinstance(term, ConsCell):
        return interpret_sexpr(term, env)
    # a symbol is evaluated based on the environment to the value that is bound to it
    elif isinstance(term, Symbol):
        return env.lookup(term.name)
    # other data is already treated as a value
    return term


def interpret_sexpr(sexpr: ConsCell, env: Environment):
    """
    A helper function to interpret a list of expressions - usually a function or builtin application
    """
    op = interpret(sexpr.head(), env)
    args = lisp_list_to_python(sexpr.tail())
    
    if isinstance(op, Builtin):
        if op.arity is not None and len(args) != op.arity:
            raise LispError(f"{op.name} expects {op.arity} arguments but was given {len(args)})")
        return op(env, *args)

    elif isinstance(op, Macro):
        code = op(args)
        return interpret(code, env)
    elif callable(op):  # by default do a call-by-value
        return op(interpret_list(args, env))
    else:
        raise LispError(f"{lisp_data_to_str(sexpr.head())} cannot be applied"
                        f"\n in {lisp_data_to_str(sexpr)}")


def interpret_list(terms: Iterable[Tree], env: Environment) -> list:
    """
    Helper function that takes a list of terms and interprets each of them, returning list of respective results on success.
    """
    return list(map(lambda term: interpret(term, env), terms))


def interpret_file(file: IO, env: Environment):
    """
    Reads a provided file and interprets all contained lines, mutating the provided environment
    """
    code = file.read()
    ast = Parser().parse_file(code)
    for statement in map(represent_code, ast):
        interpret(statement, env)
