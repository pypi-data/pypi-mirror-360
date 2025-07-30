from cgc.telemetry.basic import change_gauge
from cgc.telemetry.basic import setup_gauge
from cgc.commands.compute.compute_utils import get_app_list, get_app_mounts
from cgc.utils.config_utils import get_namespace
from cgc.utils.message_utils import key_error_decorator_for_helpers
from cgc.commands.compute import NoAppsToList
from cgc.commands.volume import PVCNotFound
from cgc.utils.response_utils import (
    tabulate_a_response,
    fill_missing_values_in_a_response,
)


@key_error_decorator_for_helpers
def get_compute_port_list(data: dict) -> list:
    resource_ports_data = data["details"]["ports"]["ports"]
    try:
        ingress_data = data["details"]["ingress"]
        ingress_port_names = [port["port_name"] for port in ingress_data]
        for port in resource_ports_data:
            port["ingress"] = True if port["name"] in ingress_port_names else False
            port_data = next(
                (
                    ingress
                    for ingress in ingress_data
                    if ingress["port_name"] == port["name"]
                ),
                None,
            )
            port["ingress_url"] = port_data.get("url", "") if port_data else ""
    except KeyError:
        pass  # no ingress data, server outdated
    return resource_ports_data


@key_error_decorator_for_helpers
def template_get_start_path_response(data: dict) -> str:
    start_path = data["details"]["start_path"]
    template = data["details"]["template_name"]
    return f"Start path for {template}: {start_path}."


@key_error_decorator_for_helpers
def template_list_response(data: dict) -> str:
    available_templates_list = data["details"]["available_templates_list"]
    return f"Available templates: {', '.join(available_templates_list)}"


@key_error_decorator_for_helpers
def compute_list_response(detailed: bool, data: dict) -> str:
    """Create response string for compute_list command, requires passing ctx

    :param ctx: _description_
    :type ctx: _type_
    :param data: parsed json data from server response
    :type data: dict
    :param detailed: flag if user requires detailed print
    :type detailed: bool
    :return: response string prepared for display
    :rtype: str
    """
    pod_list = data["details"]["pods_list"]
    setup_gauge(f"{get_namespace()}.compute.count", len(pod_list))

    # disabled resources pod list
    other_pods_list = data["details"].get("other_pods_list", [])
    pod_list.extend(other_pods_list)

    if not pod_list:
        raise NoAppsToList()

    list_of_json_data = get_app_list(pod_list, detailed)
    table = fill_missing_values_in_a_response(list_of_json_data)

    return tabulate_a_response(table)


@key_error_decorator_for_helpers
def compute_list_mounts_response(data: dict) -> str:
    """Create response string for compute list_mounts command.

    :param response: dict object from API response.
    :type response: requests.Response
    :return: Response string.
    :rtype: str
    """
    pod_list = data["details"]["pods_list"]
    list_of_json_data = get_app_mounts(pod_list)
    table = fill_missing_values_in_a_response(list_of_json_data)

    return tabulate_a_response(table)


@key_error_decorator_for_helpers
def compute_create_filebrowser_response(data: dict) -> str:
    """Create response string for compute create_filebrowser command

    :param response: dict object from API response.
    :type response: requests.Response
    :return: Response string.
    :rtype: str
    """

    # namespace = data["details"]["namespace"]
    app_url = data["details"]["created_template"]["pod_url"]
    app_token = data["details"]["created_template"]["app_token"]
    return f"Filebrowser creation started!\nWill be accessible at: {app_url}\nUsername: admin\nPassword: {app_token}"


@key_error_decorator_for_helpers
def compute_create_response(data: dict) -> str:
    """Create response string for compute create command.

    :param response: dict object from API response.
    :type response: requests.Response
    :return: Response string.
    :rtype: str
    """
    status = data["details"].get("mount_status")
    # TODO exceptions
    if status == "PVC NOT FOUND":
        raise PVCNotFound()
    change_gauge(f"{get_namespace()}.compute.count", 1)

    name = data["details"]["created_service"]["name"]
    entity = data["details"]["created_service"]["labels"]["entity"]
    volume_list = data["details"].get("mounted_pvc_list")
    volumes = ",".join(volume_list) if volume_list else None
    try:
        app_token = data["details"]["created_template"]["app_token"]
    except KeyError:
        app_token = None

    message = f"{entity} app {name} creation started!\n"
    if volumes:
        message += f" Volumes to mount: {volumes}\n"
        message += f"Container will be Ready after volumes can be see mounted.\n"

    app_url = data["details"]["created_template"]["pod_url"]
    if app_url == "None":
        message += "This app is not exposed via HTTPS\n"
    else:
        message += f"Will be accessible at: {app_url}\n"
    message += f"App token: {app_token}\nTo monitor the startup status use list command"

    return message


@key_error_decorator_for_helpers
def compute_delete_response(data: dict) -> str:
    """Create response string for compute delete command.

    :param response: dict object from API response.
    :type response: requests.Response
    :return: Response string.
    :rtype: str
    """
    name = data["details"]["deleted_service"]["name"]
    change_gauge(f"{get_namespace()}.compute.count", -1)
    return f"App {name} and its service successfully deleted."


@key_error_decorator_for_helpers
def compute_scale_response(data: dict) -> str:
    """Create response string for compute scale command.

    :param response: dict object from API response.
    :type response: requests.Response
    :return: Response string.
    :rtype: str
    """
    name = data["details"]["template_name"]
    replicas = data["details"]["replicas"]
    return f"App {name} has been successfully scaled to {replicas} replicas."


@key_error_decorator_for_helpers
def compute_restart_response(data: dict) -> str:
    """Create response string for compute restart command.

    :param response: dict object from API response.
    :type response: requests.Response
    :return: Response string.
    :rtype: str
    """

    name = data["details"]["template_name"]
    return f"App {name} has been successfully restarted."


@key_error_decorator_for_helpers
def compute_logs_response(data: dict) -> str:
    """prepare logs to print

    :param data: _description_
    :type data: dict
    :return: _description_
    :rtype: str
    """
    # converting dict o list
    logs_list = []
    for event in data["details"]["pod_event_list"]:
        row = []
        for key, value in event.items():
            row.append((key, value))
        logs_list.append(row)
    if len(logs_list) > 0:
        return tabulate_a_response(logs_list)
    else:
        return "No events to list for this app"
