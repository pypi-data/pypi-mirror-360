import json
import sys
import click

from cgc.commands.volume.data_model import (
    volume_create_payload_validator,
    volume_delete_payload_validator,
    volume_mount_payload_validator,
    volume_umount_payload_validator,
)
from cgc.commands.volume.volume_models import StorageClassList
from cgc.commands.volume.volume_responses import (
    volume_storage_class_details_response,
    volume_list_response,
    volume_mount_response,
    volume_umount_response,
    volume_create_response,
    volume_delete_response,
)
from cgc.utils.prepare_headers import get_api_url_and_prepare_headers
from cgc.utils.response_utils import retrieve_and_validate_response_send_metric
from cgc.utils.click_group import CustomGroup, CustomCommand
from cgc.utils.requests_helper import call_api, EndpointTypes


@click.group("volume", cls=CustomGroup)
def volume_group():
    """
    Management of volumes.
    """
    pass


@volume_group.command("list", cls=CustomCommand)
def volume_list():
    """
    List all volumes for user namespace.
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/storage/volume/list"
    metric = "volume.list"
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
    )
    click.echo(
        volume_list_response(retrieve_and_validate_response_send_metric(__res, metric))
    )


@volume_group.command("details", cls=CustomCommand)
@click.argument("storage_class")
def volume_storage_class_details(storage_class: str):
    """Get details of storage class.
    \f
    :param storage_class: type of disk
    :type storage_class: str
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/storage/volume/details/{storage_class}"
    metric = "volume.details"
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
    )
    click.echo(
        volume_storage_class_details_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@volume_group.command("create", cls=CustomCommand)
@click.argument("name")
@click.option(
    "-s",
    "--size",
    "size",
    help="Volume size in GiB",
    type=click.IntRange(1, 4096),
    required=True,
)
@click.option(
    "-sc",
    "--storage-class",
    "storage_class",
    type=click.Choice([*StorageClassList.load_data()]),
    default=StorageClassList.load_default_storage_class(),
    help="Type of disk",
)
def volume_create(name: str, size: int, storage_class: str):
    """Create volume in user namespace.
    \f
    :param name: name of volume
    :type name: str
    :param size: size of volume in GiB
    :type size: int
    :param storage_class: type of disk
    :type storage_class: str
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/storage/volume/create"
    metric = "volume.create"
    __payload = volume_create_payload_validator(
        name=name, size=size, storage_class=storage_class
    )
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        data=json.dumps(__payload).encode("utf-8"),
        headers=headers,
    )
    click.echo(
        volume_create_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@volume_group.command("delete", cls=CustomCommand)
@click.argument("name")
@click.option(
    "-f",
    "--force",
    "force_delete",
    is_flag=True,
    default=False,
    help="Force delete volume",
)
def volume_delete(name: str, force_delete: bool):
    """Delete specific volume from user namespace.
    \f
    :param name: name of the volume to delete
    :type name: str
    :param force_delete: delete volume even if it is still mounted
    :type force_delete: bool
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/storage/volume/delete"
    metric = "volume.delete"
    __payload = volume_delete_payload_validator(
        name=name,
        force_delete=force_delete,
    )
    __res = call_api(
        request=EndpointTypes.delete,
        url=url,
        data=json.dumps(__payload).encode("utf-8"),
        headers=headers,
    )
    click.echo(
        volume_delete_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@volume_group.command("umount", cls=CustomCommand)
@click.argument("name")
@click.option(
    "-t",
    "--target",
    "target_template_names",
    multiple=True,
    default=None,
    help="This template will have volume unmounted",
)
def volume_umount(name: str, target_template_names):
    """Umount volume from compute resources.
    \f
    :param name: name of the volume to umount
    :type name: str
    """
    while True:
        if len(target_template_names) == 0:
            click.echo(
                "Unmounting a volume will reload all compute resources it was mounted to"
            )
        else:
            click.echo(
                f'Unmounting a volume will reload those resources: "{target_template_names}"'
            )
        answer = input("Do you want to continue? (Y/N): ").lower()
        if answer in ("y", "yes"):
            break
        if answer in ("n", "no"):
            sys.exit()

    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/storage/volume/umount"
    metric = "volume.umount"
    __payload = volume_umount_payload_validator(
        name=name, target_template_names=target_template_names
    )
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        data=json.dumps(__payload).encode("utf-8"),
        headers=headers,
    )
    click.echo(
        volume_umount_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@volume_group.command("mount", cls=CustomCommand)
@click.argument("name")
@click.option(
    "-t",
    "--target",
    "target",
    type=str,
    required=True,
    help="This template will have volume mounted",
)
@click.option(
    "-sp",
    "--start_mount_path",
    "start_mount_path",
    type=str,
    default=None,
    help="Under this path (not default) will be volume mounted",
)
@click.option(
    "-fp",
    "--full_mount_path",
    "full_mount_path",
    type=str,
    default=None,
    help="Specifies full mount path, can lead to errors",
)
def volume_mount(
    name: str,
    target: str,
    start_mount_path: str,
    full_mount_path: str,
):
    """Mount volume to specific template.
    \f
    :param name: name of the volume to mount
    :type name: str
    :param target_template_type: type of template to mount volume to
    :type target_template_type: str
    :param target: name of the template to mount volume to
    :type target: str
    :param start_mount_path: path to mount volume to
    :type start_mount_path: str
    :param full_mount_path: path to mount volume to
    :type full_mount_path: str
    """
    while True:
        click.echo(
            "Mounting a volume will reload the compute resources it will be mounted to."
        )
        answer = input("Do you want to continue? (Y/N): ").lower()
        if answer in ("y", "yes"):
            break
        if answer in ("n", "no"):
            sys.exit()

    if full_mount_path is not None:
        while True:
            click.echo(
                "Using full_mount_path can lead to errors when used incorrectly. Template might not be able to start."
            )
            answer = input("Do you want to continue? (Y/N): ").lower()
            if answer in ("y", "yes"):
                break
            if answer in ("n", "no"):
                sys.exit()

    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/storage/volume/mount"
    metric = "volume.mount"
    __payload = volume_mount_payload_validator(
        name=name,
        target=target,
        start_mount_path=start_mount_path,
        full_mount_path=full_mount_path,
    )
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        data=json.dumps(__payload).encode("utf-8"),
        headers=headers,
    )
    click.echo(
        volume_mount_response(retrieve_and_validate_response_send_metric(__res, metric))
    )
