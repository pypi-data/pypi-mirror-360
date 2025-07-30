import click
import json
import sys

from cgc.commands.jobs.job_utils import job_delete_payload, job_create_payload
from cgc.commands.jobs.jobs_responses import (
    job_delete_response,
    job_list_response,
    job_create_response,
)
from cgc.commands.compute.compute_models import GPUsList
from cgc.utils.prepare_headers import get_api_url_and_prepare_headers
from cgc.utils.response_utils import (
    retrieve_and_validate_response_send_metric,
)
from cgc.utils.click_group import CustomGroup, CustomCommand
from cgc.utils.requests_helper import call_api, EndpointTypes


@click.group(name="job", cls=CustomGroup, hidden=False)
def job_group():
    """
    Management of jobs.
    """


@job_group.command("delete", cls=CustomCommand)
@click.argument("name", type=click.STRING)
def job_delete(name: str):
    """
    Delete an job using backend endpoint.
    \f
    :param name: name of job to delete
    :type name: str
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/job/delete"
    metric = "job.delete"
    __payload = job_delete_payload(name=name)
    __res = call_api(
        request=EndpointTypes.delete,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        job_delete_response(retrieve_and_validate_response_send_metric(__res, metric))
    )


@job_group.command("list", cls=CustomCommand)
def job_list():
    """List all ports for a running resource"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/job/list"
    metric = "job.list"
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
    )
    click.echo(
        job_list_response(retrieve_and_validate_response_send_metric(__res, metric))
    )


@job_group.command("create", cls=CustomCommand)
@click.argument("startup_command", required=False)
@click.option(
    "-n", "--name", "name", type=click.STRING, required=True, help="Desired app name"
)
@click.option(
    "-g",
    "--gpu",
    "gpu",
    type=click.INT,
    default=0,
    help="How much GPU cards app will use",
)
@click.option(
    "-gt",
    "--gpu-type",
    "gpu_type",
    type=click.Choice(GPUsList.get_list(), case_sensitive=False),
    default="A5000",
    help="Graphic card used by the app",
)
@click.option(
    "-c",
    "--cpu",
    "cpu",
    type=click.INT,
    default=1,
    help="How much CPU cores app can use",
)
@click.option(
    "-m",
    "--memory",
    "memory",
    type=click.INT,
    default=2,
    help="How much Gi RAM app can use",
)
@click.option(
    "-v",
    "--volume",
    "volumes",
    multiple=True,
    help="List of volume names to be mounted with default mount path",
)
@click.option(
    "-fp",
    "--full-path",
    "volume_full_path",
    type=click.STRING,
    help="If set, full path will be used for volume mount. Valid for 1 volume.",
)
@click.option(
    "-d",
    "--resource-data",
    "resource_data",
    multiple=True,
    help="List of optional arguments to be passed to the app, key=value format",
)
@click.option(
    "--image",
    "image_name",
    type=click.STRING,
    help="Image to be used by the app",
)
@click.option(
    "--repository-secret",
    "repository_secret",
    type=click.STRING,
    help="Use secret to pull image from private repository",
)
@click.option(
    "-cm",
    "--config-map",
    "config_maps_data",
    multiple=True,
    help="List of optional arguments to be passed to the app, key=value format",
)
@click.option(
    "--shm",
    "shm_size",
    type=click.IntRange(0, 1024, clamp=True),
    default=0,
    help="Size of shared memory in Gi",
)
@click.option(
    "--ttl",
    "ttl_seconds_after_finished",
    type=click.INT,
    default=None,
    help="Time to live in seconds after app is finished",
)
@click.option(
    "--ads",
    "active_deadline_seconds",
    type=click.INT,
    default=None,
    help="Time to live in seconds after app is started",
)
def job_create(
    gpu: int,
    gpu_type: str,
    cpu: int,
    memory: int,
    volumes: list[str],
    volume_full_path: str,
    resource_data: list[str],
    config_maps_data: list[str],
    name: str,
    shm_size: int,
    image_name: str,
    startup_command: str,
    repository_secret: str,
    ttl_seconds_after_finished: int,
    active_deadline_seconds: int,
):
    """
    Create job in user namespace.
    \f
    :param gpu: number of gpus to be used by app
    :type gpu: int
    :param cpu: number of cores to be used by app
    :type cpu: int
    :param memory: GB of memory to be used by app
    :type memory: int
    :param volumes: list of volumes to mount
    :type volumes: list[str]
    :param volume_full_path: if set, full path will be used for volume mount
    :type volume_full_path: str
    :param resource_data: list of optional arguments to be passed to the app
    :type resource_data: list[str]
    :param config_maps_data: list of optional arguments to be passed to the app
    :type config_maps_data: list[str]
    :param name: name of app
    :type name: str
    :param shm_size: size of shared memory
    :type shm_size: int
    :param image_name: name of image to be used by the app
    :type image_name: str
    :param startup_command: command to be executed on app startup; it is stdin input
    :type startup_command: str
    :param repository_secret: use secret to pull image from private repository
    :type repository_secret: str
    :param ttl_seconds_after_finished: time to live in seconds after app is finished
    :type ttl_seconds_after_finished: int
    :param active_deadline_seconds: time to live in seconds after app is started
    :type active_deadline_seconds: int
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/job/create"
    cleaned_data = ""
    if not sys.stdin.isatty():
        input_data = sys.stdin.read()
        cleaned_data = input_data.replace("|", "")
        startup_command = cleaned_data
    elif startup_command:
        cleaned_data = startup_command
    metric = "job.create"
    __payload = job_create_payload(
        name=name,
        cpu=cpu,
        memory=memory,
        gpu=gpu,
        volumes=volumes,
        volume_full_path=volume_full_path,
        resource_data=resource_data,
        config_maps_data=config_maps_data,
        gpu_type=gpu_type,
        shm_size=shm_size,
        image_name=image_name,
        startup_command=cleaned_data,
        repository_secret=repository_secret,
        ttl_seconds_after_finished=ttl_seconds_after_finished,
        active_deadline_seconds=active_deadline_seconds,
    )
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        job_create_response(retrieve_and_validate_response_send_metric(__res, metric))
    )
