class LispError(BaseException):
    pass


class UndefinedIdentifier(LispError):
    pass


class InvalidList(LispError):
    pass
