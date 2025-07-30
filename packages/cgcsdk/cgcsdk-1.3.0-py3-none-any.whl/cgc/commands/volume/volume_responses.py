from tabulate import tabulate

from cgc.telemetry.basic import change_gauge, setup_gauge
from cgc.commands.volume import NoVolumesToList
from cgc.commands.volume.volume_utils import (
    get_formatted_volume_list_and_total_size,
    convert_node_resource_value_from_string,
)

from cgc.utils.config_utils import get_namespace
from cgc.utils.message_utils import key_error_decorator_for_helpers


# TODO: refactor using: tabulate_a_response(data: list) -> str
@key_error_decorator_for_helpers
def volume_list_response(data: dict) -> str:
    """Create response string for volume list command.

    :return: Response string.
    :rtype: str
    """
    list_of_volumes = data["details"]["volume_list"]

    if not list_of_volumes:
        raise NoVolumesToList()
    volume_list_to_print, total_size = get_formatted_volume_list_and_total_size(
        list_of_volumes
    )
    list_headers = ["name", "used", "size", "type", "disks type", "mounted to"]

    setup_gauge(f"{get_namespace()}.volume.count", len(list_of_volumes))
    setup_gauge(f"{get_namespace()}.volume.totalSizeAccumulated", total_size)
    return tabulate(volume_list_to_print, headers=list_headers)


@key_error_decorator_for_helpers
def volume_storage_class_details_response(data: dict) -> str:
    """Create response string for volume storage class details command.

    :return: Response string.
    :rtype: str
    """
    # ["details"]["storage_class"] -> storage class name
    # ["details"]["storage_class_info"] -> storage_type, reclaim_policy, volume_binding_mode

    storage_class_headers = [
        "name",
        *data["details"]["storage_class_info"].keys(),
    ]
    storage_class_data = [
        (
            data["details"]["storage_class"],
            *data["details"]["storage_class_info"].values(),
        )
    ]
    return tabulate(storage_class_data, headers=storage_class_headers)


@key_error_decorator_for_helpers
def volume_create_response(data: dict) -> str:
    """Create response string for volume create command.

    :return: Response string.
    :rtype: str
    """
    name = data["details"]["volume_created"]["name"]
    size = (
        convert_node_resource_value_from_string(
            data["details"]["volume_created"]["size"]
        )
        / 1000
    )
    access = data["details"]["volume_created"]["access_type"][0]
    try:
        disk_type = data["details"]["volume_created"]["disks_type"]
    except KeyError:
        disk_type = data["details"]["storage_class"]
    change_gauge(f"{get_namespace()}.volume.count", 1)
    change_gauge(f"{get_namespace()}.volume.totalSizeAccumulated", size)

    return (
        f"Volume {name} of size {size} GB on {disk_type} created. Volume is {access}."
    )


@key_error_decorator_for_helpers
def volume_delete_response(data: dict) -> str:
    """Create response string for volume delete command.

    :return: Response string.
    :rtype: str
    """

    name = data["details"]["volume_deleted"]["name"]
    size = (
        convert_node_resource_value_from_string(
            data["details"]["volume_deleted"]["size"]
        )
        / 1000
    )
    change_gauge(f"{get_namespace()}.volume.count", -1)
    change_gauge(f"{get_namespace()}.volume.totalSizeAccumulated", -size)
    return f"Volume {name} deleted."


@key_error_decorator_for_helpers
def volume_umount_response(data: dict) -> str:
    """Create response string for volume unmount command.

    :return: Response string.
    :rtype: str
    """
    name = data["details"]["pvc_name"]
    return f"Volume {name} successfully unmounted from selected apps."


@key_error_decorator_for_helpers
def volume_mount_response(data: dict) -> str:
    """Create response string for volume mount command.

    :return: Response string.
    :rtype: str
    """
    name = data["details"]["pvc_name"]
    target = data["details"]["target_template_name"]
    mount_path = data["details"]["mount_path"]
    return f"Volume {name} successfully mounted to {target}, mount path: {mount_path}."
