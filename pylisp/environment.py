class Environment(object):
    def __init__(self, mapping=None):
        self._mapping = mapping if mapping is not None else {}

    def lookup(self, symbol):
        return self._mapping[symbol]

    def extend(self, symbol, value):
        new_mapping = self._mapping.copy()
        new_mapping[symbol] = value
        return Environment(new_mapping)


def empty_environment():
    return Environment()
