from cgc.commands.exceptions import ResponseException


class AuthCommandException(ResponseException):
    pass


class NoNamespaceInConfig(AuthCommandException):
    def __init__(self) -> None:
        super().__init__("Namespace not readable from config file.")


class NoConfigFileFound(AuthCommandException):
    def __init__(self) -> None:
        super().__init__("Config does not exists.")


class CorruptedConfigFile(AuthCommandException):
    def __init__(self) -> None:
        super().__init__("Config file is corrupted. Please check the file format or contact support at support@comtegra.pl")
