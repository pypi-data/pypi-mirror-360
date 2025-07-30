from typing import Optional
from cgc.commands.exceptions import NonOnPremisesException
import cgc.utils.consts.env_consts as env_consts
from cgc.utils.get_headers_data import load_user_api_url


def list_get_mounted_volumes_paths(volume_list: list) -> str:
    """Formats and returns list of PVC volumes mounted to an app.

    :param volume_list: list of all volumes mounted to an app
    :type volume_list: list
    :return: list of volume paths
    :rtype: str
    """
    volume_name_list = []
    for volume in volume_list:
        volume_type = volume.get("type")
        if volume_type == "PVC":
            volume_mount_path = volume.get("mount_path")
            volume_name_list.append(volume_mount_path)
    volumes_mounted = (
        ", ".join(volume_name_list) if len(volume_name_list) != 0 else None
    )
    return volumes_mounted


def list_get_mounted_volumes(volume_list: list) -> str:
    """Formats and returns list of PVC volumes mounted to an app.

    :param volume_list: list of all volumes mounted to an app
    :type volume_list: list
    :return: list of PVC volumes
    :rtype: str
    """
    volume_name_list = []
    for volume in volume_list:
        volume_type = volume.get("type")
        if volume_type == "PVC":
            volume_name = volume.get("name")
            volume_name_list.append(volume_name)
    volumes_mounted = (
        ", ".join(volume_name_list) if len(volume_name_list) != 0 else None
    )
    return volumes_mounted


def get_app_mounts(pod_list: list) -> list:
    output_data = []

    for pod in pod_list:
        try:
            main_container_name = pod["labels"]["entity"]
            try:
                main_container = [
                    x for x in pod["containers"] if x["name"] == main_container_name
                ][0]
            except IndexError:
                raise Exception(
                    "Parser was unable to find main container in server output in container list"
                )
            volumes_mounted = list_get_mounted_volumes(main_container["mounts"])
            volumes_paths = list_get_mounted_volumes_paths(main_container["mounts"])
            pod_data = {
                "name": pod["labels"]["app-name"],
                "type": pod["labels"]["entity"],
                "status": pod["status"],
                "volumes_mounted": volumes_mounted,
                "volumes_paths": volumes_paths,
            }
            output_data.append(pod_data)
        except KeyError:
            pass
    return output_data


def get_app_list(pod_list: list, detailed: bool) -> list:
    """Formats and returns list of apps to print.

    :param pod_list: list of pods
    :type pod_list: list
    :return: formatted list of apps
    :rtype: list
    """
    output_data = []

    def update_output_data_count(pod_name):
        for pod in output_data:
            if pod["name"] == pod_name:
                pod["count"] += 1
                return True
        return False

    for pod in pod_list:
        try:
            main_container_name = pod["labels"]["entity"]
            try:
                main_container = [
                    x for x in pod["containers"] if x["name"] == main_container_name
                ][0]
            except IndexError:
                raise Exception(
                    "Parser was unable to find main container in server output in container list"
                )
            volumes_mounted = list_get_mounted_volumes(main_container.get("mounts", []))
            limits = main_container["resources"].get("limits")
            cpu = limits.get("cpu") if limits is not None else 0
            ram = limits.get("memory") if limits is not None else "0Gi"

            pod_data = {
                "name": pod["labels"]["app-name"],
                "type": pod["labels"]["entity"],
                "status": pod["status"],
                "volumes_mounted": volumes_mounted,
                "cpu": cpu,
                "ram": ram,
                "count": pod.get("replicas", 1), # first in the list are always pods
            }
            # getting rid of unwanted and used values
            if "pod-template-hash" in pod["labels"].keys():
                pod["labels"].pop("pod-template-hash")
            # getting rid of unwanted and used values
            unwanted_labels = [
                "app-name",
                "resource-type",
                "pod-template-hash",
                "entity",
            ]
            for unwanted_label in unwanted_labels:
                if unwanted_label in pod["labels"].keys():
                    pod["labels"].pop(unwanted_label, None)

            if detailed:
                pod["labels"]["url"] = pod["labels"]["pod_url"]
                if pod_data["type"] == "nvidia-pytorch":
                    pod["labels"]["url"] += f"""/?token={pod["labels"]['app-token']}"""
            else:
                pod["labels"]["url"] = pod["labels"]["pod_url"]
                pod["labels"].pop("app-token", None)
            pod["labels"].pop(
                "pod_url", None
            )  # should be always present in the payload
            pod["labels"].pop(
                "resource-type", None
            )  # should be always present in the payload
            pod["labels"].pop("api-key-id", None)
            pod["labels"].pop("user-id", None)

            # appending the rest of labels
            pod_data.update(pod["labels"])

            if not update_output_data_count(pod_data["name"]):
                output_data.append(pod_data)
        except KeyError:
            pass

    return output_data


def port_modification_payload(
    port_name: str,
    port_number: int,
    ingress: bool,
    app_name: str,
):
    """
    Create payload for port update.
    """
    extra_data = {}
    if port_number is not None:
        extra_data["port"] = port_number
    payload = {
        "resource_data": {
            "name": app_name,
        },
        "port_data": {"name": port_name, "ingress": ingress, **extra_data},
    }
    return payload


def port_delete_payload(port_name: str, app_name: str):
    """
    Create payload for port deletion.
    """
    payload = {
        "resource_data": {
            "name": app_name,
        },
        "port_data": {
            "name": port_name,
        },
    }
    return payload


def compute_create_payload(
    name,
    entity,
    cpu,
    memory,
    volumes: list,
    volume_full_path: Optional[str] = None,
    resource_data: list = [],
    config_maps_data: list = [],
    gpu: int = 0,
    gpu_type: str = None,
    shm_size: int = 0,
    image_name: str = "",
    startup_command: str = "",
    repository_secret: str = "",
    node_port_enabled: bool = False,
):
    """
    Create payload for app creation.
    """
    extra_payload = {}
    if shm_size is not None and shm_size != 0:
        extra_payload["shared_memory"] = shm_size

    if volume_full_path is not None:
        extra_payload["full_mount_path"] = volume_full_path

    payload = {
        "resource_data": {
            "name": name,
            "entity": entity,
            "cpu": cpu,
            "gpu": gpu,
            "memory": memory,
            "gpu_type": gpu_type,
            **extra_payload,
        }
    }
    try:
        if len(volumes) != 0:
            if volume_full_path is not None and not volume_full_path:
                payload["resource_data"]["pv_volume"] = volumes
            elif (
                volume_full_path is not None and volume_full_path and len(volumes) != 1
            ):
                raise Exception(
                    "Volume full path can only be used with a single volume"
                )
            else:
                payload["resource_data"]["pv_volume"] = volumes
    except TypeError:
        pass
    try:
        resource_data_dict = {"resource_data": {}}
        if len(resource_data) != 0:
            for resource in resource_data:
                try:
                    key, value = resource.split("=")
                    resource_data_dict["resource_data"][key] = value
                except ValueError:
                    raise Exception(
                        "Invalid resource data format. Use key=value format"
                    )
        if (
            node_port_enabled
            or "node_port_enabled" in resource_data_dict["resource_data"]
        ):
            if env_consts.CGC_API_URL == load_user_api_url():
                raise NonOnPremisesException(
                    "NodePort is supported in on-premises environments only."
                )
            resource_data_dict["resource_data"]["node_port_enabled"] = True
        if image_name:
            resource_data_dict["resource_data"]["custom_image"] = image_name
        if startup_command:
            resource_data_dict["resource_data"]["custom_command"] = startup_command
        if repository_secret:
            resource_data_dict["resource_data"][
                "image_pull_secret_name"
            ] = repository_secret
        if resource_data_dict["resource_data"] != {}:
            payload["template_specific_data"] = resource_data_dict
    except TypeError:
        pass
    try:
        if len(config_maps_data) != 0:
            config_maps_data_dict = {}
            for config_map in config_maps_data:
                try:
                    key, value = config_map.split(
                        "="
                    )  # where key is name of config map and value is data
                    config_maps_data_dict[key] = (
                        value  # value is dict, ex.: {"key": "value"}
                    )
                except ValueError:
                    raise Exception(
                        "Invalid config map data format. Use key=value format"
                    )
            payload["config_maps_data"] = config_maps_data_dict
    except TypeError:
        pass
    return payload


def compute_delete_payload(name):
    """
    Create payload for app creation.
    """
    payload = {
        "name": name,
    }
    return payload
