from pylisp.environment import Environment
from pylisp.errors import LispError
from pylisp.interpreter import Builtin, interpret, interpret_list, interpret_file, ConsCell, python_list_to_lisp, \
    Symbol, lisp_list_length, lisp_list_to_python, lisp_list_is_valid, lisp_data_to_str, Macro


class FuncBuiltin(Builtin):
    """
    A class to wrap a simple function into a 'Builtin' value.
    """
    def __init__(self, name, arity, doc, func):
        super().__init__(name, arity, doc)
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class FuncMacro(Macro):
    """
    A class to wrap a simple function into a 'Macro' value.
    """
    def __init__(self, func):
        super().__init__()
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


# list of exported builtins, will be expanded by register_* functions
builtins = {"false": False, "true": True, "nil": None}


def register_builtin(arity, name=None):
    """
    A decorator to register the wrapped function as a builtin with the provided arity.
    If the name is not provided it is based on the function's __name__.
    """
    def wrapper(func):
        nonlocal name
        if name is None:
            name = func.__name__

        def syntax_wrapper(env: Environment, *args):
            try:
                return func(env, *args)
            except LispError as err:
                reconstructed_form = python_list_to_lisp([Symbol(name)] + list(args))
                if len(str(err).splitlines()) > 3:
                    # we don't add more than 3 traces
                    raise
                raise LispError(str(err) + f"\n in: {lisp_data_to_str(reconstructed_form)}") from err
        builtin = FuncBuiltin(name, arity, func.__doc__, syntax_wrapper)
        if builtin.name in builtins:
            raise AssertionError(f"Builtin names have to be unique: {builtin.name}")
        builtins[builtin.name] = builtin
        return func
    return wrapper


def register_vararg_builtin(name=None):
    """
    A decorator to register the wrapped function as a builtin with variable arity.
    If the name is not provided it is based on the function's __name__.
    """
    return register_builtin(None, name)


@register_builtin(2)
def let(env: Environment, binding, body):  # this function could be a macro but is kept for simplicity of tests
    """
    (let (name value) body)
    Binds result of value to name inside of body.
    """
    return letrec(env, python_list_to_lisp([binding]), body)


@register_builtin(2)
def letrec(env: Environment, bindings, body):
    def form_error():
        raise LispError(f"Wrong let form: (letrec {lisp_data_to_str(bindings)} ...)")

    def process_binding(binding):
        if not isinstance(binding, ConsCell):
            form_error()
        if lisp_list_length(binding) != 2:
            form_error()
        [symb, inner] = lisp_list_to_python(binding)
        if not isinstance(symb, Symbol):
            form_error()
        return symb.name, inner

    bindings = list(map(process_binding, lisp_list_to_python(bindings)))
    inner_env = env.fork()
    # we first allocate forward references to all mutually recursive bindings
    for name, _ in bindings:
        inner_env.allocate_forward_reference(name)
    # and afterwards we fill them in with computed values,
    # while the values are computed, their forked environments will be successively updated
    for name, inner in bindings:
        inner_env.fill_forward_reference(name, interpret(inner, inner_env))
    return interpret(body, inner_env)


@register_builtin(2, "define!")
def define(env: Environment, name, body):
    if not isinstance(name, Symbol):
        raise LispError(f"You can only bind to symbols, not to: {lisp_data_to_str(name)}")
    inner = interpret(body, env)
    env.update(name.name, inner)


@register_vararg_builtin("+")
def plus(env: Environment, *args):
    return sum(interpret_list(args, env))


def register_eager_binary_builtin(name, func):
    """
    A helper decorator to register a simple 2 argument operator that expects evaluated arguments.
    Useful for defining basic arithmetic primitives etc.
    """
    def helper(env: Environment, a, b):
        a_val = interpret(a, env)
        b_val = interpret(b, env)
        return func(a_val, b_val)
    register_builtin(2, name)(helper)


def divide(a, b):
    if b == 0:
        raise LispError("Division by 0")
    return a / b


register_eager_binary_builtin("-", lambda a, b: a - b)
register_eager_binary_builtin("*", lambda a, b: a * b)
register_eager_binary_builtin("/", divide)
register_eager_binary_builtin("mod", lambda a, b: a % b)
register_eager_binary_builtin("=", lambda a, b: a == b)
register_eager_binary_builtin("<=", lambda a, b: a <= b)
register_eager_binary_builtin(">=", lambda a, b: a >= b)
register_eager_binary_builtin("<", lambda a, b: a < b)
register_eager_binary_builtin(">", lambda a, b: a > b)


@register_builtin(3, "if")
def conditional(env: Environment, cond, branch_true, branch_else):
    cond = interpret(cond, env)
    if cond:
        return interpret(branch_true, env)
    else:
        return interpret(branch_else, env)


@register_builtin(2)
def fun(env: Environment, args, body):
    def process_arg(arg):
        if not isinstance(arg, Symbol):
            raise LispError(f"Function arguments in the definition have to be symbols"
                            f"\n in: (fun {lisp_data_to_str(args)} ...)")
        return arg.name
    if not lisp_list_is_valid(args):
        raise LispError(f"Wrong function form: (fun {lisp_data_to_str(args)} ...)")
    args = list(map(process_arg, lisp_list_to_python(args)))
    function_env = env.fork()  # we do a copy to achieve static-binding

    def closure(arg_values):
        if len(arg_values) != len(args):
            raise LispError("Function applied to a wrong number of arguments")
        invokation_env = function_env.fork()  # copy to preserve the closure for future calls
        for arg_name, arg_value in zip(args, arg_values):
            invokation_env.update(arg_name, arg_value)
        return interpret(body, invokation_env)
    return closure


@register_builtin(2)
def macro(env: Environment, args, body):
    def process_arg(arg):
        if not isinstance(arg, Symbol):
            raise LispError(f"Macro arguments in the definition have to be symbols"
                            f"\n in: (macro {lisp_data_to_str(args)} ...)")
        return arg.name
    if not lisp_list_is_valid(args):
        raise LispError(f"Wrong macro form: (macro {lisp_data_to_str(args)} ...)")
    args = list(map(process_arg, lisp_list_to_python(args)))
    function_env = env.fork()  # we do a copy to achieve static-binding

    def closure(arg_values):
        if len(arg_values) != len(args):
            raise LispError("Macro applied to a wrong number of arguments")
        invokation_env = function_env.fork()  # copy to preserve the closure for future calls
        for arg_name, arg_value in zip(args, arg_values):
            invokation_env.update(arg_name, arg_value)
        return interpret(body, invokation_env)
    return FuncMacro(closure)


@register_vararg_builtin()
def begin(env: Environment, *args):
    return interpret_list(args, env)[-1]  # return the value of the last statement


class Block:
    """
    An instance of block, can be used to handle imperative arrays in the language.
    """
    def __init__(self, size):
        self.values = [None] * size

    def set(self, idx, value):
        if idx < 0 or idx >= len(self.values):
            raise LispError(f"Index {idx} is out of bounds")
        self.values[idx] = value

    def get(self, idx):
        if idx < 0 or idx >= len(self.values):
            raise LispError(f"Index {idx} is out of bounds")
        return self.values[idx]

    def __str__(self):
        return f"<allocated block of size {len(self.values)}>"


@register_builtin(1, "alloc!")
def block_alloc(env: Environment, size):
    size = interpret(size, env)
    if not isinstance(size, int):
        raise LispError("alloc! needs an integer")
    return Block(size)


@register_builtin(2, "get!")
def block_get(env: Environment, block, idx):
    block = interpret(block, env)
    idx = interpret(idx, env)
    if not isinstance(block, Block):
        raise LispError("get! works only on blocks")
    if not isinstance(idx, int):
        raise LispError("get! idx has to be an integer")
    return block.get(idx)


@register_builtin(3, "set!")
def block_get(env: Environment, block, idx, value):
    block = interpret(block, env)
    idx = interpret(idx, env)
    value = interpret(value, env)
    if not isinstance(block, Block):
        raise LispError("set! works only on blocks")
    if not isinstance(idx, int):
        raise LispError("set! idx has to be an integer")
    return block.set(idx, value)


@register_vararg_builtin("list")
def list_make(env: Environment, *args):
    args = interpret_list(args, env)
    return python_list_to_lisp(args)


register_eager_binary_builtin("cons", lambda h, t: ConsCell(h, t))


@register_builtin(1, "head")
def list_head(env: Environment, lst):
    lst = interpret(lst, env)
    if not isinstance(lst, ConsCell):
        raise LispError("head can only be applied to a non-empty list")
    return lst.head()


@register_builtin(1, "tail")
def list_tail(env: Environment, lst):
    lst = interpret(lst, env)
    if not isinstance(lst, ConsCell):
        raise LispError("tail can only be applied to a non-empty list")
    return lst.tail()


@register_builtin(1, "quote")
def quote(env: Environment, code):
    return code


@register_vararg_builtin("print!")
def builtin_print(env: Environment, *args):
    args = map(lisp_data_to_str, interpret_list(args, env))
    print(" ".join(args))
    return None


@register_builtin(1, "str")
def builtin_str(env: Environment, arg):
    return lisp_data_to_str(interpret(arg, env))


@register_builtin(0, "read_line!")
def read_line(_: Environment):
    return input()


@register_builtin(1, "require!")
def require(env: Environment, path):
    path = interpret(path, env)
    if not isinstance(path, str):
        raise LispError("Can only import a string path")
    try:
        with open(path) as f:
            interpret_file(f, env)
    except IOError as e:
        raise LispError(str(e)) from e


@register_builtin(1, "help!")
def builtin_help(env: Environment, builtin):
    builtin = interpret(builtin, env)
    if not isinstance(builtin, Builtin):
        print("Not a builtin operator")
        return
    if builtin.doc is None:
        print("No documentation found for:", builtin.name)
        return
    print("Documentation for:", builtin.name)
    print(builtin.doc)
