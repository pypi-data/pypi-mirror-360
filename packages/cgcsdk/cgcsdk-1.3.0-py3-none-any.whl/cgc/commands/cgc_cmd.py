import click
import json

from cgc.commands.cgc_cmd_responses import (
    cgc_logs_response,
    cgc_status_response,
)
from cgc.commands.resource.resource_cmd import resource_delete
from cgc.utils.requests_helper import call_api, EndpointTypes
from cgc.utils.click_group import CustomCommand, CustomGroup
from cgc.utils.prepare_headers import get_api_url_and_prepare_headers
from cgc.utils.response_utils import retrieve_and_validate_response_send_metric
from cgc.telemetry.basic import telemetry_permission_set
from cgc.commands.compute.compute_responses import compute_logs_response

# from cgc.commands.auth.auth_cmd import auth_register
from cgc.utils import set_environment_data, check_if_config_exist, list_all_config_files
from cgc.commands.cgc_helpers import table_of_user_context_files
from cgc.utils.config_utils import config_path, save_to_local_config_context
from cgc.utils.consts.env_consts import ENV_FILE_PATH


@click.command("rm", cls=CustomCommand)
@click.argument("name", type=click.STRING)
def cgc_rm(name: str):
    """
    Delete an app in user namespace
    """
    resource_delete(name)


@click.command("events", cls=CustomCommand)
@click.argument("app_name", type=click.STRING)
def resource_events(app_name: str):
    """Get events of given app"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/get_pod_events"
    metric = "resource.events"
    __payload = {"name": app_name}
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        compute_logs_response(retrieve_and_validate_response_send_metric(__res, metric))
    )


@click.command("status", cls=CustomCommand)
def cgc_status():
    """Lists available and used resources"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/status"
    metric = "resource.status"
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
    )
    click.echo(
        cgc_status_response(retrieve_and_validate_response_send_metric(__res, metric))
    )


@click.command("telemetry", cls=CustomCommand)
def sending_telemetry_permission():
    """Changing permission for sending telemetry"""

    click.echo(
        f"Sending telemetry is now {'enabled' if telemetry_permission_set() else 'disabled'}"
    )


@click.group(name="context", cls=CustomGroup)
def context_group():
    """
    Switch between namespaces (contexts) that are at your disposal.
    """


@context_group.command("switch", cls=CustomCommand)
@click.argument("number", type=click.INT)
# @click.pass_context
def switch_context(number: int):
    """Set which namespace config should be used. After switching context your next command will be run in given namespace that corresponds to user namespace"""
    file_name = f"{number}.json" if number > 1 else "cfg.json"

    if not check_if_config_exist(file_name):
        click.echo("Selected context does not exist.")
        click.echo("To get all available contexts use:")
        click.echo("cgc context list")
        exit(0)
        # user_id = input("User ID: ")
        # access_key = input("Access key: ")
        # ctx.invoke(
        #     auth_register,
        #     user_id=user_id,
        #     access_key=access_key,
        #     config_filename=file_name,
        # )
    set_environment_data("CONFIG_FILE_NAME", file_name)
    save_to_local_config_context(file_name)
    click.echo(f"Context file changed to: {file_name}")


@context_group.command("list", cls=CustomCommand)
def list_context():
    """List all namespaces available to you"""
    click.echo(table_of_user_context_files(list_all_config_files()))


@context_group.command("folder", cls=CustomCommand)
def folder_of_contexts():
    """Check location of config files in case that you need to export them."""
    click.echo(f"All config files are located: {config_path}")
    click.echo(
        "If you'd like to use them on a different machine just copy all the files to corresponding folder."
    )
    click.echo(
        "You can check location of that folder on different machine with the same command."
    )


@context_group.command("get-env-path", cls=CustomCommand)
def get_env_path():
    """Displays current environment file path"""
    click.echo(f"Current environment file path: {ENV_FILE_PATH}")


@click.command("logs", cls=CustomCommand)
@click.argument("app_name", type=click.STRING)
@click.option("-t", "--timestamps", is_flag=True, default=False, help="Include timestamps for each log line")
def cgc_logs(app_name, timestamps):
    """Displays logs of a given app"""

    if not app_name:
        raise click.ClickException("Please provide a non-empty name")

    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/logs/{app_name}"
    metric = "logs.get"

    params = {"timestamps": timestamps} if timestamps else {}

    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
        params=params,
    )

    click.echo(
        cgc_logs_response(retrieve_and_validate_response_send_metric(__res, metric))
    )
