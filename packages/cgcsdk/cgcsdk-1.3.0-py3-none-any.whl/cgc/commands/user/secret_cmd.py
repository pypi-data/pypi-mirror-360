import json
from typing import Optional, Set
import click

from cgc.utils.prepare_headers import get_api_url_and_prepare_headers
from cgc.utils.response_utils import retrieve_and_validate_response_send_metric
from cgc.utils.click_group import CustomGroup, CustomCommand
from cgc.utils.requests_helper import call_api, EndpointTypes
from cgc.commands.user.secret_utils import create_secret_payload, update_secret_payload
from cgc.commands.user.secret_responses import (
    create_secret_response,
    update_secret_response,
    delete_secret_response,
    list_secrets_response,
)


@click.group(name="secret", cls=CustomGroup)
def secret_group():
    """
    Management of secrets.
    """


@secret_group.command("create", cls=CustomCommand)
@click.argument("secret_name", type=click.STRING)
@click.option(
    "-r",
    "--registry-list",
    "registry_list",
    multiple=True,
    help="URL of the registry",
    required=True,
)
@click.option(
    "-u",
    "--username",
    "username",
    type=click.STRING,
    help="Username for the registry",
    required=True,
)
@click.option(
    "-p",
    "--password",
    "password",
    type=click.STRING,
    help="Password for the username",
    required=True,
)
def create_secret(
    secret_name: str, registry_list: Set[str], username: str, password: str
):
    """Create a new secret in the namespace"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/secret/create"
    metric = "user.secret.create"
    __payload = create_secret_payload(secret_name, registry_list, username, password)
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        create_secret_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        ),
        color="green",
    )


@secret_group.command("update", cls=CustomCommand)
@click.argument("secret_name", type=click.STRING)
@click.option(
    "-r",
    "--registry-list",
    "registry_list",
    multiple=True,
    help="URL of the registry",
)
@click.option(
    "-u",
    "--username",
    "username",
    type=click.STRING,
    help="Username for the registry",
)
@click.option(
    "-p",
    "--password",
    "password",
    type=click.STRING,
    help="Password for the username",
)
def update_secret(
    secret_name: str,
    registry_list: Optional[Set[str]] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
):
    """Update an existing secret in the namespace"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/secret/manage/{secret_name}"
    metric = "user.secret.update"
    __payload = update_secret_payload(registry_list, username, password)
    __res = call_api(
        request=EndpointTypes.put,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        update_secret_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        ),
        color="green",
    )


@secret_group.command("delete", cls=CustomCommand)
@click.argument("secret_name", type=click.STRING)
def delete_secret(secret_name: str):
    """Delete an secret"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/secret/manage/{secret_name}"
    metric = "user.secret.delete"
    __res = call_api(
        request=EndpointTypes.delete,
        url=url,
        headers=headers,
    )
    click.echo(
        delete_secret_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        ),
        color="green",
    )


@secret_group.command("list", cls=CustomCommand)
def list_secrets():
    """List all secrets in the namespace"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/secret/list"
    metric = "user.secret.list"
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
    )
    click.echo(
        list_secrets_response(retrieve_and_validate_response_send_metric(__res, metric))
    )
