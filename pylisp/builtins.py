from pylisp.ast import Symbol, ExpressionList
from pylisp.environment import Environment
from pylisp.errors import OutOfBounds, WrongOperatorUsage
from pylisp.interpreter import Builtin, interpret, interpret_list


class FuncBuiltin(Builtin):
    def __init__(self, name, arity, func):
        super().__init__(name, arity)
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


builtins = {}


def register_builtin(arity, name=None):
    def wrapper(func):
        nonlocal name
        if name is None:
            name = func.__name__

        builtin = FuncBuiltin(name, arity, func)
        if builtin.name in builtins:
            raise AssertionError(f"Builtin names have to be unique: {builtin.name}")
        builtins[builtin.name] = builtin
        return func
    return wrapper


def register_vararg_builtin(name=None):
    return register_builtin(None, name)


@register_builtin(2)
def let(env: Environment, binding, body):
    return letrec(env, ExpressionList([binding]), body)


@register_builtin(2)
def letrec(env: Environment, bindings, body):
    def process_binding(binding):
        if not isinstance(binding, ExpressionList):
            raise RuntimeError("Wrong let form")
        if len(binding) != 2:
            raise RuntimeError("Wrong let form")
        [symb, inner] = binding.values
        if not isinstance(symb, Symbol):
            raise RuntimeError("You can only bind to symbols")
        return symb.name, inner

    bindings = list(map(process_binding, bindings.values))
    inner_env = env.copy()
    for name, inner in bindings:
        inner_env.set(name, interpret(inner, inner_env))
    return interpret(body, inner_env)


@register_builtin(2)
def define(env: Environment, name, body):
    if not isinstance(name, Symbol):
        raise RuntimeError("You can only bind to symbols")
    inner = interpret(body, env)
    env.update(name.name, inner)


@register_vararg_builtin("+")
def plus(env: Environment, *args):
    return sum(interpret_list(args, env))


@register_builtin(2, "-")
def minus(env: Environment, a, b):
    a_val = interpret(a, env)
    b_val = interpret(b, env)
    return a_val - b_val


@register_builtin(2, "*")
def times(env: Environment, a, b):
    a_val = interpret(a, env)
    b_val = interpret(b, env)
    return a_val * b_val


@register_builtin(2, "/")
def div(env: Environment, a, b):
    a_val = interpret(a, env)
    b_val = interpret(b, env)
    return a_val / b_val


@register_builtin(2)
def mod(env: Environment, a, b):
    a_val = interpret(a, env)
    b_val = interpret(b, env)
    return a_val % b_val


class Block:
    def __init__(self, size):
        self.values = [None] * size

    def set(self, idx, value):
        if idx < 0 or idx >= len(self.values):
            raise OutOfBounds(f"Index {idx} is out of bounds")
        self.values[idx] = value

    def get(self, idx):
        if idx < 0 or idx >= len(self.values):
            raise OutOfBounds(f"Index {idx} is out of bounds")
        return self.values[idx]


@register_builtin(1, "alloc!")
def block_alloc(env: Environment, size):
    size = interpret(size, env)
    if not isinstance(size, int):
        raise WrongOperatorUsage("alloc! needs an integer")
    return Block(size)


@register_builtin(2, "get!")
def block_get(env: Environment, block, idx):
    block = interpret(block, env)
    idx = interpret(idx, env)
    if not isinstance(block, Block):
        raise WrongOperatorUsage("get! works only on blocks")
    if not isinstance(idx, int):
        raise WrongOperatorUsage("get! idx has to be an integer")
    return block.get(idx)


@register_builtin(3, "set!")
def block_get(env: Environment, block, idx, value):
    block = interpret(block, env)
    idx = interpret(idx, env)
    value = interpret(value, env)
    if not isinstance(block, Block):
        raise WrongOperatorUsage("set! works only on blocks")
    if not isinstance(idx, int):
        raise WrongOperatorUsage("set! idx has to be an integer")
    return block.set(idx, value)
