import click
import json

from cgc.commands.db.db_models import DatabasesList
from cgc.commands.compute.compute_models import ComputesList
from cgc.commands.compute.compute_responses import (
    compute_scale_response,
    template_list_response,
    template_get_start_path_response,
    compute_restart_response,
    compute_delete_response,
)

from cgc.commands.compute.compute_utils import compute_delete_payload
from cgc.commands.resource.resource_responses import get_ingress_list_from_response

from cgc.utils.prepare_headers import get_api_url_and_prepare_headers
from cgc.utils.response_utils import (
    fill_missing_values_in_a_response,
    retrieve_and_validate_response_send_metric,
    tabulate_a_response,
)
from cgc.utils.click_group import CustomGroup, CustomCommand
from cgc.utils.requests_helper import call_api, EndpointTypes


@click.group(name="resource", cls=CustomGroup, hidden=False)
def resource_group():
    """
    Management of templates.
    """


@resource_group.command("list_templates", cls=CustomCommand)
def template_list():
    """Lists all available templates"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/list_available_templates"
    metric = "resource.template.list"
    __res = call_api(request=EndpointTypes.get, url=url, headers=headers)
    click.echo(
        template_list_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@resource_group.command("get_start_path", cls=CustomCommand)
@click.argument(
    "template", type=click.Choice([*ComputesList.get_list(), *DatabasesList.get_list()])
)
def template_get_start_path(template: str):
    """Displays start path of specified template"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/get_template_start_path?template_name={template}"
    metric = "resource.template.get_start_path"
    __res = call_api(request=EndpointTypes.get, url=url, headers=headers)
    click.echo(
        template_get_start_path_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@resource_group.command("restart", cls=CustomCommand)
@click.argument("name", type=click.STRING)
def compute_restart(name: str):
    """Restarts the specified app"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/restart"
    metric = "resource.restart"
    __payload = {"name": name}
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        compute_restart_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@resource_group.group(name="scale", cls=CustomGroup, hidden=False)
def scale_group():
    """
    Management of scaling resources replicas.
    """


@scale_group.command("up", cls=CustomCommand)
@click.argument("name", type=click.STRING)
# @click.option(
#     "-s",
#     "--scale",
#     "replicas",
#     type=NonNegativeInteger(),
#     required=True,
#     help="Scale factor - number of replicas (must be 0 or greater)",
# )
def compute_scale_up(name: str):
    """Scales the specified app up"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/scale?replicas=1"
    metric = "resource.scale"
    __payload = {"name": name}
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        compute_scale_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@scale_group.command("down", cls=CustomCommand)
@click.argument("name", type=click.STRING)
def compute_scale_down(name: str):
    """Scales the specified app down"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/scale?replicas=0"
    metric = "resource.scale"
    __payload = {"name": name}
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        compute_scale_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@resource_group.command("ingress", cls=CustomCommand)
@click.argument("name", type=click.STRING)
def get_resource_ingress(name: str):
    """Get ingress of given resource"""
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/ingress?resource_name={name}"
    metric = "resource.ingress"
    __res = call_api(
        request=EndpointTypes.get,
        url=url,
        headers=headers,
    )
    __res_list = get_ingress_list_from_response(
        retrieve_and_validate_response_send_metric(__res, metric)
    )
    table = fill_missing_values_in_a_response(__res_list)
    click.echo(tabulate_a_response(table))


@click.argument("name", type=click.STRING)
def resource_delete(name: str):
    """
    Delete an app using backend endpoint.
    \f
    :param name: name of app to delete
    :type name: str
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/resource/delete"
    metric = "resource.delete"
    __payload = compute_delete_payload(name=name)
    __res = call_api(
        request=EndpointTypes.delete,
        url=url,
        headers=headers,
        data=json.dumps(__payload).encode("utf-8"),
    )
    click.echo(
        compute_delete_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )
