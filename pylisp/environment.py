from pylisp.errors import UndefinedIdentifier


class Environment:
    def __init__(self, mapping=None):
        self._mapping = mapping if mapping is not None else {}

    def lookup(self, identifier: str):
        try:
            return self._mapping[identifier]
        except KeyError:
            raise UndefinedIdentifier(identifier)

    def extend(self, identifier: str, value):
        new_mapping = self._mapping.copy()
        new_mapping[identifier] = value
        return Environment(new_mapping)


def empty_environment() -> Environment:
    return Environment()


def environment_with_builtins(builtins: dict) -> Environment:
    return Environment(mapping=builtins)