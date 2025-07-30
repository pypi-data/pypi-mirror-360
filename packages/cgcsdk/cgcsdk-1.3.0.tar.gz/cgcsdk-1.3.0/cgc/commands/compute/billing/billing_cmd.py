import click

from datetime import datetime

from cgc.commands.compute.billing.billing_responses import (
    billing_pricing_response,
    billing_status_response,
    billing_invoice_response,
)
from cgc.utils.prepare_headers import get_api_url_and_prepare_headers
from cgc.utils.response_utils import retrieve_and_validate_response_send_metric
from cgc.utils.click_group import CustomGroup, CustomCommand
from cgc.utils.requests_helper import call_api, EndpointTypes


@click.group("billing", cls=CustomGroup)
def billing_group():
    """
    Access and manage billing information.
    """
    pass


@billing_group.command("status", cls=CustomCommand)
@click.option(
    "--detailed",
    "-d",
    "detailed",
    prompt=True,
    type=bool,
    default=False,
    help="If true, returns detailed invoice information",
    is_flag=True,
)
def billing_status(detailed: bool):
    """
    Shows billing status for user namespace
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v2/api/billing/status?details={detailed}"
    metric = "billing.status"
    __res = call_api(request=EndpointTypes.get, url=url, headers=headers)
    click.echo(
        billing_status_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


def _get_previous_month():
    return datetime.now().month - 1 if datetime.now().month > 1 else 12


def _get_previous_year_if_required():
    return datetime.now().year - 1 if datetime.now().month == 1 else datetime.now().year


@billing_group.command("invoice", cls=CustomCommand)
@click.option(
    "--year",
    "-y",
    "year",
    prompt=True,
    type=int,
    default=_get_previous_year_if_required(),
)
@click.option(
    "--month",
    "-m",
    "month",
    prompt=True,
    type=click.IntRange(1, 12),
    default=_get_previous_month(),
)
@click.option(
    "--detailed",
    "-d",
    "detailed",
    prompt=True,
    type=bool,
    default=False,
    help="If true, returns detailed invoice information",
    is_flag=True,
)
def billing_invoice(year: int, month: int, detailed: bool):
    """
    Opens invoice from given year and month
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = (
        f"{api_url}/v2/api/billing/invoice?year={year}&month={month}&details={detailed}"
    )
    metric = "billing.invoice"
    __res = call_api(request=EndpointTypes.get, url=url, headers=headers)

    click.echo(
        billing_invoice_response(
            year,
            month,
            retrieve_and_validate_response_send_metric(__res, metric),
        )
    )


@billing_group.command("pricing", cls=CustomCommand)
def billing_pricing():
    """
    Shows billing pricing information for user
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v2/api/billing/user_pricing"
    metric = "billing.pricing"
    __res = call_api(request=EndpointTypes.get, url=url, headers=headers)
    click.echo(
        billing_pricing_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )
