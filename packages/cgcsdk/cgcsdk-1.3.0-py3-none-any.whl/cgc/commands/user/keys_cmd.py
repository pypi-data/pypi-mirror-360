import json
import click
from typing import Optional
from cgc.commands.user.keys_responses import (
    create_ssh_key_response,
    delete_ssh_key_response,
    list_ssh_keys_response,
    update_ssh_key_response,
)
from cgc.commands.user.keys_utils import create_ssh_key_payload, update_ssh_key_payload
from cgc.commands.user.keys_models import SSHKeyTypes
from cgc.utils.prepare_headers import get_api_url_and_prepare_headers
from cgc.utils.response_utils import retrieve_and_validate_response_send_metric
from cgc.utils.click_group import CustomGroup, CustomCommand
from cgc.utils.requests_helper import call_api, EndpointTypes


@click.group(name="keys", cls=CustomGroup)
def keys_group():
    """
    Management of keys.
    """


@keys_group.group(name="ssh", cls=CustomGroup)
def ssh_keys_group():
    """
    Management of ssh keys.
    """


@ssh_keys_group.command("create", cls=CustomCommand)
@click.option(
    "-pk",
    "--pub-key",
    "public_key",
    type=click.STRING,
    required=False,
    help="Whole Public key string",
)
@click.option(
    "-kt",
    "--key-type",
    "key_type",
    type=click.Choice(SSHKeyTypes.get_list(), case_sensitive=False),
    required=False,
    # default="ssh-rsa",
    help="Type of the key",
)
@click.option(
    "-k",
    "--key",
    "key",
    type=click.STRING,
    required=False,
    help="Public key",
)
@click.option(
    "-c",
    "--comment",
    "comment",
    type=click.STRING,
    required=False,
    default="",
    help="Comment for the key",
)
def create_ssh_key(
    public_key: Optional[str] = None,
    key_type: Optional[str] = None,
    key: Optional[str] = None,
    comment: str = "",
):
    """Create a new SSH key"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/keys/ssh/create"
    metric = "keys.create"
    __payload = create_ssh_key_payload(public_key, key_type, key, comment)
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        create_ssh_key_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        ),
        color="green",
    )


@ssh_keys_group.command("update", cls=CustomCommand)
@click.argument("key_id", type=click.STRING)
@click.option(
    "-kt",
    "--key-type",
    "key_type",
    type=click.Choice(SSHKeyTypes.get_list(), case_sensitive=False),
    # default="ssh-rsa",
    required=False,
    help="Type of the key",
)
@click.option(
    "-k",
    "--key",
    "key",
    type=click.STRING,
    required=False,
    help="Public key",
)
@click.option(
    "-c",
    "--comment",
    "comment",
    type=click.STRING,
    required=False,
    help="Comment for the key",
)
def update_ssh_key(
    key_id: str,
    key_type: Optional[str] = None,
    key: Optional[str] = None,
    comment: Optional[str] = None,
):
    """Update an existing SSH key"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/keys/ssh/update/{key_id}"
    metric = "keys.update"
    __payload = update_ssh_key_payload(key_type, key, comment)
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        update_ssh_key_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        ),
        color="green",
    )


@ssh_keys_group.command("delete", cls=CustomCommand)
@click.argument("key_id", type=click.STRING)
def delete_ssh_key(key_id: str):
    """Delete an SSH key"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/keys/ssh/delete/{key_id}"
    metric = "keys.delete"
    __res = call_api(
        request=EndpointTypes.delete,
        url=url,
        headers=headers,
    )
    click.echo(
        delete_ssh_key_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        ),
        color="green",
    )


@ssh_keys_group.command("list", cls=CustomCommand)
def list_ssh_keys():
    """List all SSH keys"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/keys/ssh/list"
    metric = "keys.list"
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
    )
    click.echo(
        list_ssh_keys_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )
