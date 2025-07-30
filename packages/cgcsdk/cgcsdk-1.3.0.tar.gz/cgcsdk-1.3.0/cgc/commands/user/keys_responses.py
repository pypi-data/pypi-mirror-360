import click
from cgc.utils.message_utils import key_error_decorator_for_helpers
from cgc.commands.user.keys_utils import get_user_ssh_keys
from cgc.utils.response_utils import (
    fill_missing_values_in_a_response,
    tabulate_a_response,
)


@key_error_decorator_for_helpers
def create_ssh_key_response(data: dict) -> str:
    """Create a response for creating a new SSH key"""
    try:
        key_id = data["details"]["key_id"]
    except KeyError:
        raise click.ClickException("Key creation failed!")
    return f"Key created with ID: {key_id}"


@key_error_decorator_for_helpers
def delete_ssh_key_response(data: dict) -> str:
    """Create a response for deleting an SSH key"""
    try:
        key_id = data["details"]["key_id"]
    except KeyError:
        raise click.ClickException("Key deletion failed!")
    return f"Key with ID: {key_id} deleted."


@key_error_decorator_for_helpers
def list_ssh_keys_response(data: dict) -> str:
    """Create a response for listing all SSH keys"""
    list_of_json_data = get_user_ssh_keys(data["details"])
    if not list_of_json_data:
        return "No keys found."
    table = fill_missing_values_in_a_response(list_of_json_data)

    return tabulate_a_response(table)


@key_error_decorator_for_helpers
def update_ssh_key_response(_: dict) -> str:
    """Create a response for updating an SSH key"""
    return "Key updated."
