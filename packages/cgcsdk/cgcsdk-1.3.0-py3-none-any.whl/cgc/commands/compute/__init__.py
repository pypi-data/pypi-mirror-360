from cgc.commands.exceptions import ResponseException


class ComputeCommandException(ResponseException):
    pass


class NoAppsToList(ComputeCommandException):
    def __init__(self) -> None:
        super().__init__("No apps to list.")
