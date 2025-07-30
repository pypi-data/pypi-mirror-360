import click

from cgc.commands.user import NoSecretsToList
from cgc.commands.user.secret_utils import get_secret_list
from cgc.telemetry.basic import setup_gauge
from cgc.utils.config_utils import get_namespace
from cgc.utils.message_utils import key_error_decorator_for_helpers
from cgc.utils.response_utils import (
    fill_missing_values_in_a_response,
    tabulate_a_response,
)


@key_error_decorator_for_helpers
def create_secret_response(data: dict) -> str:
    """Create a response for creating a new secret in the namespace"""
    return f'Secret {data.get("details", {}).get("secret_name")} successfully created.'


@key_error_decorator_for_helpers
def update_secret_response(data: dict) -> str:
    """Create a response for updating a secret in the namespace"""
    return f'Secret {data.get("details", {}).get("secret_name")} successfully updated.'


@key_error_decorator_for_helpers
def delete_secret_response(data: dict) -> str:
    """Create a response for deleting a secret in the namespace"""
    return f'Secret {data.get("details", {}).get("secret_name")} successfully deleted.'


@key_error_decorator_for_helpers
def list_secrets_response(data: dict) -> str:
    """Create a response for listing all secrets in the namespace"""
    secret_list = data.get("details", {}).get("secret_names", [])
    setup_gauge(f"{get_namespace()}.secret.count", len(secret_list))

    if not secret_list:
        raise NoSecretsToList()

    list_of_json_data = get_secret_list(secret_list)
    table = fill_missing_values_in_a_response(list_of_json_data)

    return tabulate_a_response(table)
