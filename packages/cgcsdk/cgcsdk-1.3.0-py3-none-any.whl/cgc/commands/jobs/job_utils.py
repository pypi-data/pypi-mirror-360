from typing import Optional
from cgc.commands.compute.compute_utils import list_get_mounted_volumes
import cgc.utils.consts.env_consts as env_consts


def job_delete_payload(name):
    """
    Create payload for job delete.
    """
    payload = {
        "name": name,
    }
    return payload


def job_create_payload(
    name,
    cpu,
    memory,
    volumes: list,
    volume_full_path: str,
    resource_data: list = [],
    config_maps_data: list = [],
    gpu: int = 0,
    gpu_type: str = None,
    shm_size: int = 0,
    image_name: str = "",
    startup_command: str = "",
    repository_secret: str = "",
    ttl_seconds_after_finished: Optional[int] = None,
    active_deadline_seconds: Optional[int] = None,
):
    """
    Create payload for app creation.
    """
    extra_payload = {}
    if shm_size is not None and shm_size != 0:
        extra_payload["shared_memory"] = shm_size

    if ttl_seconds_after_finished is not None:
        extra_payload["ttl_seconds_after_finished"] = ttl_seconds_after_finished
    if active_deadline_seconds is not None:
        extra_payload["active_deadline_seconds"] = active_deadline_seconds

    payload = {
        "resource_data": {
            "name": name,
            "cpu": cpu,
            "gpu": gpu,
            "memory": memory,
            "gpu_type": gpu_type,
            "full_mount_path": volume_full_path,
            **extra_payload,
        }
    }
    try:
        if len(volumes) != 0:
            if not volume_full_path:
                payload["resource_data"]["pv_volume"] = volumes
            elif volume_full_path and len(volumes) != 1:
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


def get_job_list(job_list: list, job_pod_list: list):
    list_of_json_job_data = get_job_json_data(job_list)

    for i, job_data in enumerate(job_list):
        list_of_json_job_data[i]["name"] = job_data.get("name", "")
        list_of_json_job_data[i]["ttl"] = job_data.get(
            "ttl_seconds_after_finished", "N/A"
        )
        list_of_json_job_data[i]["ads"] = job_data.get("active_deadline_seconds", "N/A")
    for job in list_of_json_job_data:
        for job_pod in job_pod_list:
            job_pod_labels: dict = job_pod.get("labels", {})
            if job_pod_labels.get("app-name", "") == job.get("name"):
                if job["status"] is not None and job["status"] == "Unknown":
                    job["status"] = job_pod["status"]  # try to get status from pod
                elif job["status"] is None:  # support older server versions
                    job["status"] = job_pod["status"]
                job["gpu-count"] = job_pod_labels.get("gpu-count", 0)
                job["gpu-label"] = job_pod_labels.get("gpu-label", "N/A")
                # job["status_reason"] = [
                #     x.get("reason", "N/A") for x in job_pod.get("status_reasons", [])
                # ]
                # job["status_message"] = [
                #     x.get("message", "N/A") for x in job_pod.get("status_reasons", [])
                # ]
                break

    return list_of_json_job_data


def get_job_json_data(job_list: list):
    """Formats and returns list of jobs to print.

    :param job_list: list of jobs
    :type job_list: list
    :return: formatted list of jobs
    :rtype: list
    """
    output_data = []

    for job in job_list:
        try:
            main_container_name = "custom-job"
            try:
                main_container = [
                    x
                    for x in job.get("containers", [])
                    if x.get("name") == main_container_name
                ][0]
            except IndexError:
                raise Exception(
                    "Parser was unable to find main container in server output in container list"
                )
            volumes_mounted = list_get_mounted_volumes(main_container.get("mounts", []))
            limits = main_container.get("resources", {}).get("limits")
            cpu = limits.get("cpu") if limits is not None else 0
            ram = limits.get("memory") if limits is not None else "0Gi"
            gpu_label = job.get("labels", {}).get("gpu-type", "N/A")
            gpu_count = job.get("labels", {}).get("gpu-count", "N/A")

            job_data = {
                "name": job.get("labels", {}).get("app-name"),
                "status": job.get("status", {}).get("phase", "Unknown"),
                "volumes_mounted": volumes_mounted,
                "cpu": cpu,
                "ram": ram,
                "gpu-label": gpu_label,
                "gpu-count": gpu_count,
            }
            # getting rid of unwanted and used values
            unwanted_labels = [
                "app-name",
                "api-key-id",
                "resource-type",
                "pod-template-hash",
                "entity",
            ]
            for unwanted_label in unwanted_labels:
                if unwanted_label in job["labels"].keys():
                    job["labels"].pop(unwanted_label)

            # appending the rest of labels
            job_data.update(job["labels"])
            output_data.append(job_data)
        except KeyError:
            pass

    return output_data
