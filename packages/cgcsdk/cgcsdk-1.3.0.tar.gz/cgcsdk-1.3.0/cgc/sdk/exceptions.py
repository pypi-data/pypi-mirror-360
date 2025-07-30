from cgc.commands.exceptions import ResponseException


class SDKException(ResponseException):
    def __init__(self, code: int, *args, **kwargs):
        self.code = code
        super().__init__(*args, **kwargs)
