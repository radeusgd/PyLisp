from pylisp.errors import UndefinedIdentifier, LispError


class ForwardReference:
    """
    A reference that can be set only once.
    See: Environment for more details.
    """
    def __init__(self, name):
        self._ref = None
        self.is_set = False
        self._name = name  # name is only used for better error reporting

    def set(self, value):
        if self.is_set:
            raise LispError(f"A forward reference {self._name} has been set a second time")
        self._ref = value
        self.is_set = True

    def get(self):
        if not self.is_set:
            raise LispError(f"A forward reference {self._name} has been accessed before initialization"
                            f", do you have a loop?")
        return self._ref


class Environment:
    """
    A mutable environment representation.
    The environment can be mutated using update - this is used by define!.
    It can also be 'forked' to create a sub-environment that can be modified independently
    - this is used in let, letrec and function closures.
    A function closure will fork the environment to achieve static binding - we want the following program:
    > (define! x 2)
    > (define! f (fun () (print x)))
    > (define! x 3)
    > (f)
    to print 2 and not 3, but the original environment has been modified.
    However as we do a copy of the environment, we have an issue when using letrec
    - all mutually recursive functions need to know each other but when we are interpreting their code,
    they are not yet defined. But as they copy the environment, we cannot mutate the environment afterwards.
    To solve that issue we introduce ForwardReference which is added to the environment
    and is shallowly copied into environment forks, so once the forward reference is filled-in,
    it is updated in all forks.
    """
    def __init__(self, mapping=None):
        self._mapping = mapping if mapping is not None else {}

    def fork(self):
        return Environment(mapping=self._mapping.copy())

    def lookup(self, identifier: str):
        try:
            value = self._mapping[identifier]
            if isinstance(value, ForwardReference):
                return value.get()
            return value
        except KeyError:
            raise UndefinedIdentifier(f"{identifier} is not defined")

    def update(self, identifier: str, value):
        self._mapping[identifier] = value

    def allocate_forward_reference(self, identifier: str):
        self._mapping[identifier] = ForwardReference(identifier)

    def fill_forward_reference(self, identifier: str, value):
        try:
            ref = self._mapping[identifier]
            if not isinstance(ref, ForwardReference):
                raise LispError(f"{identifier} is not a forward reference")
            ref.set(value)
        except KeyError:
            raise LispError(f"forward reference {identifier} has not been declared")

    def __str__(self):
        return f"Env{str(self._mapping)}"


def empty_environment() -> Environment:
    return Environment()


def environment_with_builtins(builtins: dict) -> Environment:
    return Environment(mapping=builtins)
