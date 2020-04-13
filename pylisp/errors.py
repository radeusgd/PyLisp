class LispError(BaseException):
    pass


class UndefinedIdentifier(LispError):
    pass


class WrongOperatorUsage(LispError):
    pass


class CannotCall(LispError):
    pass


class OutOfBounds(LispError):
    pass


class InvalidList(LispError):
    pass
