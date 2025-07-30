class ResponseException(Exception):
    pass


class InternalException(Exception):
    pass


class DatabaseCreationException(InternalException):
    pass


class NonOnPremisesException(ResponseException):
    pass
