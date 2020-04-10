from pylisp.ast import Symbol, ExpressionList
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
def let(env, binding, body):
    # TODO more robust DSL for defining macros
    if not isinstance(binding, ExpressionList):
        raise RuntimeError("Wrong let form")
    if len(binding) != 2:
        raise RuntimeError("Wrong let form")

    [symb, inner] = binding.values

    if not isinstance(symb, Symbol):
        raise RuntimeError("You can only let to symbols")

    v = interpret(inner, env)
    extended_env = env.extend(symb.name, v)
    return interpret(body, extended_env)


@register_builtin(2)
def letrec(env, bindings, body):
    raise NotImplementedError


@register_vararg_builtin("+")
def plus(env, *args):
    return sum(interpret_list(args, env))


@register_builtin(2, "-")
def minus(env, a, b):
    a_val = interpret(a, env)
    b_val = interpret(b, env)
    return a_val - b_val


@register_builtin(2, "*")
def times(env, a, b):
    a_val = interpret(a, env)
    b_val = interpret(b, env)
    return a_val * b_val


@register_builtin(2, "/")
def div(env, a, b):
    a_val = interpret(a, env)
    b_val = interpret(b, env)
    return a_val / b_val


@register_builtin(2)
def mod(env, a, b):
    a_val = interpret(a, env)
    b_val = interpret(b, env)
    return a_val % b_val
