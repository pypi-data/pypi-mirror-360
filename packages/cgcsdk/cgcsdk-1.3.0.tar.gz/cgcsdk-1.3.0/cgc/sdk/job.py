import json as _json
from typing import Optional
import cgc.sdk.exceptions as _exceptions
from cgc.utils.custom_exceptions import CUSTOM_EXCEPTIONS
import cgc.utils.prepare_headers as _prepare_headers
import cgc.commands.jobs.job_utils as _job_utils
import cgc.utils.requests_helper as _requests_helper
import cgc.utils.response_utils as _response_utils
from cgc.commands.compute.compute_models import GPUsList


def job_create(
    name: str,
    image_name: str,
    cpu: int = 1,
    memory: int = 2,
    shm_size: int = 0,
    gpu: int = 0,
    gpu_type: str = "A5000",
    volumes: list = [],
    volume_full_path: str = "",
    startup_command: str = "",
    repository_secret: str = "",
    resource_data: list = [],
    config_maps_data: list = [],
    ttl_seconds_after_finished: Optional[int] = None,
):
    """
    Create a custom compute resource.

    :param name: The name of the compute resource.
    :type name: str
    :param image_name: The name of the image to use for the compute resource.
    :type image_name: str,
    :param cpu: The number of CPUs for the compute resource, defaults to 1.
    :type cpu: int, optional
    :param memory: The amount of memory (in GB) for the compute resource, defaults to 2.
    :type memory: int, optional
    :param shm_size: The size of the shared memory (in GB) for the compute resource, defaults to 0.
    :type shm_size: int, optional
    :param gpu: The number of GPUs for the compute resource, defaults to 0.
    :type gpu: int, optional
    :param gpu_type: The type of GPU for the compute resource, defaults to "A5000".
    :type gpu_type: str, optional
    :param volumes: The list of volumes to attach to the compute resource, defaults to [].
    :type volumes: list, optional
    :param volume_full_path: The full path of the volume, defaults to "".
    :type volume_full_path: str, optional
    :param startup_command: The startup command for the compute resource, defaults to "".
    :type startup_command: str, optional
    :param repository_secret: The secret for accessing the repository, defaults to "".
    :type repository_secret: str, optional
    :param resource_data: The additional resource data, defaults to [].
    :type resource_data: list, optional
    :param config_maps_data: The additional config maps data, defaults to [].
    :type config_maps_data: list, optional
    :param ttl_seconds_after_finished: The time to live in seconds after the app is finished, defaults to None.
    :type ttl_seconds_after_finished: int, optional
    :raises _SDKException: If the image name is not provided.
    :raises _SDKException: If an invalid GPU type is specified.
    :return: The response from the API call.
    :rtype: _type_
    """
    if not image_name:
        raise _exceptions.SDKException(-2, "Image name is required")
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/job/create"
    metric = "job.create"
    gpu_type = gpu_type.upper()
    if gpu_type not in GPUsList.get_list():
        raise _exceptions.SDKException(-3, f"Invalid GPU type: {gpu_type}")
    __payload = _job_utils.job_create_payload(
        name=name,
        cpu=cpu,
        memory=memory,
        gpu=gpu,
        gpu_type=gpu_type,
        volumes=volumes,
        volume_full_path=volume_full_path,
        resource_data=resource_data,
        config_maps_data=config_maps_data,
        shm_size=shm_size,
        image_name=image_name,
        startup_command=startup_command,
        repository_secret=repository_secret,
        ttl_seconds_after_finished=ttl_seconds_after_finished,
    )

    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.post,
        url=url,
        headers=headers,
        data=_json.dumps(__payload).encode("utf-8"),
    )

    return _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
        __res, metric
    )


def job_list():
    """
    List jobs using backend endpoint.

    :return: response from the API call
    :rtype: dict
    """
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/job/list"
    metric = "job.list"
    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.get,
        url=url,
        headers=headers,
    )

    return _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
        __res, metric
    )
    # job_pod_list = _response.get("details", {}).get("job_pod_list", [])
    # job_list = _response.get("details", {}).get("job_list", [])
    # return _job_utils.get_job_list(job_list)


def job_delete(name: str):
    """
    Delete job using backend endpoint.

    :param name: name of job to delete
    :type name: str
    :return: response from the API call
    :rtype: dict
    """
    api_url, headers = _prepare_headers.get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/job/delete"
    metric = "job.delete"
    __payload = _job_utils.job_delete_payload(name=name)
    __res = _requests_helper.call_api(
        request=_requests_helper.EndpointTypes.delete,
        url=url,
        headers=headers,
        data=_json.dumps(__payload).encode("utf-8"),
    )

    return _response_utils.retrieve_and_validate_response_send_metric_for_sdk(
        __res, metric
    )
