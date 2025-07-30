from enum import Enum

from cgc.commands.cgc_models import CGCEntityList
from cgc.utils.config_utils import read_from_local_cfg
import cgc.utils.version_control as version_control


class ComputesList(CGCEntityList):
    """List of compute templates in cgc-server"""

    @staticmethod
    def load_data() -> list[str]:
        try:
            return read_from_local_cfg("compute_templates")
        except FileNotFoundError:
            version_control.get_server_version()  # possible loop on error
            return ComputesList.load_data()


class GPUsList(Enum):
    """List of templates in cgc-server

    :param Enum: name of template
    :type Enum: str
    """

    V100 = "V100"
    A100 = "A100"
    A5000 = "A5000"
    H100 = "H100"
    P40 = "P40"
    P100 = "P100"
    RTX6000 = "RTX6000"

    def get_list() -> list[str]:
        return [el.value for el in GPUsList]
