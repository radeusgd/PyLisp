from pylisp.errors import UndefinedIdentifier


class Environment:
    def __init__(self, mapping=None):
        self._mapping = mapping if mapping is not None else {}

    def copy(self):
        return Environment(mapping=self._mapping.copy())

    def lookup(self, identifier: str):
        try:
            return self._mapping[identifier]
        except KeyError:
            raise UndefinedIdentifier(identifier)

    def update(self, identifier: str, value):
        self._mapping[identifier] = value

    def __str__(self):
        return f"Env{str(self._mapping)}"


def empty_environment() -> Environment:
    return Environment()


def environment_with_builtins(builtins: dict) -> Environment:
    return Environment(mapping=builtins)