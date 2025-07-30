from cgc.utils.config_utils import read_from_local_cfg
import cgc.utils.version_control as version_control


class StorageClassList:
    """List of compute templates in cgc-server"""

    @staticmethod
    def load_data() -> list[str]:
        try:
            return read_from_local_cfg("storage_classes")
        except FileNotFoundError:
            version_control.get_server_version()  # possible loop on error
            return StorageClassList.load_data()

    @staticmethod
    def load_default_storage_class() -> str:
        try:
            return read_from_local_cfg("default_storage_class")
        except FileNotFoundError:
            version_control.get_server_version()  # possible loop on error
            return StorageClassList.load_default_storage_class()
