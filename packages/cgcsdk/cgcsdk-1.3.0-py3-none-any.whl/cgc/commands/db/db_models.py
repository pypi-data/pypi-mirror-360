from cgc.commands.cgc_models import CGCEntityList
from cgc.commands.exceptions import DatabaseCreationException
from cgc.utils.config_utils import read_from_local_cfg
import cgc.utils.version_control as version_control


class DatabasesList(CGCEntityList):
    """List of database templates in cgc-server"""

    @staticmethod
    def load_data() -> list[str]:
        try:
            list_of_templates = read_from_local_cfg("database_templates")
        except FileNotFoundError:
            version_control.get_server_version()  # possible loop on error
            return DatabasesList.load_data()
        list_of_templates.extend(["mongodb", "redis"])
        return list_of_templates

    @staticmethod
    def verify(entity: str) -> str:
        if entity == "mongodb":
            raise DatabaseCreationException(
                """
Due to license agreement we can not serve MongoDB as a single click app.
If you like to use it you can spawn one as custom image.

cgc compute create custom -n name -c 4 -m 8 --image mongo
"""
            )
        elif entity == "redis":
            raise DatabaseCreationException(
                """
Due to license agreement we can not serve Redis as a single click app.
If you like to use it you can spawn one as custom image.

cgc compute create custom -n name -c 4 -m 8 --image redis
"""
            )
