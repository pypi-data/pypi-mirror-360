from cgc.commands.exceptions import ResponseException


class VolumeCommandException(ResponseException):
    pass


class NoVolumesToList(VolumeCommandException):
    def __init__(self) -> None:
        super().__init__("No volumes to list.")


class PVCNotFound(VolumeCommandException):
    def __init__(self) -> None:
        super().__init__("Volume name not found in namespace.")
