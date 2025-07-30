import os
import subprocess
import sys
import click
from cgc.utils.config_utils import is_config_file_present
from cgc.utils.prepare_headers import get_api_url_and_prepare_headers_version_control
from cgc.utils.message_utils import (
    prepare_error_message,
    prepare_warning_message,
    key_error_decorator_for_helpers,
)
from cgc.utils.consts.env_consts import MAJOR_VERSION, MINOR_VERSION, RELEASE
from cgc.utils.consts.message_consts import (
    OUTDATED_MAJOR,
    OUTDATED_MINOR,
)

from cgc.utils.requests_helper import call_api, EndpointTypes
from cgc.utils.config_utils import save_to_local_config
import logging


def get_server_version():
    """Queries the server about its current version

    :return: server version data
    :rtype: dict
    """
    api_url, headers = get_api_url_and_prepare_headers_version_control()
    __res = call_api(request=EndpointTypes.get, url=api_url, headers=headers)
    try:
        __res.raise_for_status()
    except Exception:
        logging.debug("Your current context server is not reachable.")
    else:
        save_to_local_config(**__res.json())
        return __res.json()


def print_compare_versions(server_version: str, client_version: str):
    click.echo(f"Server version: {server_version}")
    click.echo(f"Installed version: {client_version}")


@key_error_decorator_for_helpers
def check_version():
    """Checks if Client version is up to date with Server version."""
    if not is_config_file_present():
        return
    data = get_server_version()
    if data is None:
        return
    server_release, server_major, server_minor = (
        data["server_version"]["release"],
        data["server_version"]["major"],
        data["server_version"]["minor"],
    )
    server_status = data[
        "server_status"
    ]  # braking change - 0.9.0, will not work with lower server version
    server_version = f"{server_release}.{server_major}.{server_minor}"
    client_version = _get_version()
    if (
        server_major > MAJOR_VERSION and server_release == RELEASE
    ) or server_release > RELEASE:
        click.echo(prepare_error_message(OUTDATED_MAJOR))
        print_compare_versions(server_version, client_version)
        while True:
            answer = input("Update now? (Y/N): ").lower()
            if answer in ("y", "yes"):
                update_file_path = os.path.join(os.path.dirname(__file__), "update.py")
                try:
                    subprocess.Popen([sys.executable, update_file_path])
                    sys.exit()
                except subprocess.SubprocessError:
                    click.echo(
                        prepare_error_message(
                            "Could not initiate update, try again or install update manually with: pip install --upgrade cgcsdk"
                        )
                    )
            if answer in ("n", "no"):
                sys.exit()
            else:
                click.echo(prepare_warning_message("wrong input, please try again."))
    if (
        server_release == RELEASE
        and server_major == MAJOR_VERSION
        and server_minor > MINOR_VERSION
    ):
        click.echo(prepare_warning_message(OUTDATED_MINOR))
        print_compare_versions(server_version, client_version)
    if server_status != "OK":
        click.echo(
            prepare_warning_message(
                f"Server at maintenance, current status: {server_status}"
            )
        )
    if server_release == RELEASE and (
        server_major < MAJOR_VERSION or server_minor < MINOR_VERSION
    ):
        click.echo(
            prepare_warning_message(
                "You are using a newer client version than the server."
            )
        )
        print_compare_versions(server_version, client_version)
    elif server_release != RELEASE:
        click.echo(
            prepare_warning_message(
                f"Server version is not compatible with the client version. Server version: {server_version}, Client version: {client_version}"
            )
        )


def _get_version():
    """Returns version of cgcsdk."""
    return f"{RELEASE}.{MAJOR_VERSION}.{MINOR_VERSION}"
