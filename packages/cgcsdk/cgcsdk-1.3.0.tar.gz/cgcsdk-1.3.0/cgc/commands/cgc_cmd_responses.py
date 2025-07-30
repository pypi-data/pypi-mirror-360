from enum import Enum
from typing import Union
from tabulate import tabulate
from cgc.utils.message_utils import key_error_decorator_for_helpers


def _resource_match(resource: str) -> Union[str, None]:
    if resource == "limits.cpu":
        return "Total CPU"
    elif resource == "limits.memory":
        return "Total RAM"
    elif resource == "requests.nvidia.com/gpu":
        return "Total GPU"
    elif resource.startswith("requests.comtegra.cloud/"):
        gpu_type = resource.split("/")[-1]
        return f"GPU {gpu_type.upper()}"
    elif resource == "persistentvolumeclaims":
        return "Volume Count"
    elif resource == "requests.storage":
        return "Total Storage"
    elif resource.endswith(".storageclass.storage.k8s.io/requests.storage"):
        storage_class = resource.split(".")[0]
        return f"Storage ({storage_class})"
    elif resource == "pods":
        return "Pod Count"
    else:
        return None


class ResourceOrder(Enum):
    CPU = 1
    MEMORY = 2
    GPU = 3
    STORAGE = 4
    VOLUME = 5
    GPU_TYPE = 6
    POD = 7
    OTHER = 8


def _resource_order(resource: str) -> ResourceOrder:
    if resource == "limits.cpu":
        return ResourceOrder.CPU
    elif resource == "limits.memory":
        return ResourceOrder.MEMORY
    elif resource == "requests.nvidia.com/gpu":
        return ResourceOrder.GPU
    elif resource.startswith("requests.comtegra.cloud/"):
        return ResourceOrder.GPU_TYPE
    elif resource == "persistentvolumeclaims":
        return ResourceOrder.VOLUME
    elif resource == "requests.storage":
        return ResourceOrder.STORAGE
    elif resource.endswith(".storageclass.storage.k8s.io/requests.storage"):
        return ResourceOrder.STORAGE
    elif resource == "pods":
        return ResourceOrder.POD
    else:
        return ResourceOrder.OTHER


@key_error_decorator_for_helpers
def cgc_status_response(data: dict):
    """Generates and prints resource limits and available resources in a pretty format

    :param data: data to extrct resources from
    :type data: dict
    :param metric_error: error metric for graphana
    :type metric_error: str
    """

    resources_available: dict = data["details"]["available_resources"]
    resources_limits: dict = data["details"]["limits_resources"]
    list_headers = ["Resource", "Available", "Limit"]
    resource_names = []

    resources_available_list = []
    resources_limits_list = []
    resources_available = {
        key: value
        for key, value in sorted(
            resources_available.items(),
            key=lambda x: (_resource_order(x[0]).value, x[1]),
        )
    }
    for resource, available in resources_available.items():
        if resource not in resources_limits.keys():
            continue
        resource_parsed = _resource_match(resource)
        if resource_parsed is None:
            continue
        resource_names.append(resource_parsed)
        limit = resources_limits[resource]
        if "storage" in resource or "memory" in resource:
            available = f"{available} GB"
            limit = f"{limit} GB"
        else:
            available = int(available)
            limit = int(limit)
        resources_available_list.append(available)
        resources_limits_list.append(limit)

    return tabulate(
        list(zip(resource_names, resources_available_list, resources_limits_list)),
        headers=list_headers,
    )


def cgc_logs_response(data: dict):
    return "\n".join(
        "==> %s/%s <==\n%s" % (pod, cont, log)
        for pod, containers in data["details"]["logs"].items()
        for cont, log in containers.items()
    )
