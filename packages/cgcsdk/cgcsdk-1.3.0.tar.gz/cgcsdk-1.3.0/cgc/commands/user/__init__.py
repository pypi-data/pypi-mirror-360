from cgc.commands.exceptions import ResponseException


class KeysCommandException(ResponseException):
    """Base exception for all key commands."""


class SecretsCommandException(ResponseException):
    """Base exception for all secret commands."""


class NoSecretsToList(SecretsCommandException):
    def __init__(self) -> None:
        super().__init__("No secrets to list.")
