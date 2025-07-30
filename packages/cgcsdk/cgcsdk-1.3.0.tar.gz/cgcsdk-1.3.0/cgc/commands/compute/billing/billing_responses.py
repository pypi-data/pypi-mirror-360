import calendar
import click
from decimal import Decimal
from tabulate import tabulate
from cgc.commands.compute.billing import (
    NoCostsFound,
    NoInvoiceFoundForSelectedMonth,
)
from cgc.commands.compute.billing.billing_utils import get_billing_status_message
from cgc.utils.message_utils import key_error_decorator_for_helpers


@key_error_decorator_for_helpers
def billing_status_response(data: dict) -> str:
    total_cost = data["details"]["cost_total"]
    namespace = data["details"]["namespace"]
    billing_records = data["details"]["billing_records"]
    details = data["details"].get("details", [])
    if not billing_records:
        raise NoCostsFound()
    message = get_billing_status_message(billing_records, details)
    message += f"Total cost for namespace {namespace}: {total_cost:.2f} pln"
    return message


@key_error_decorator_for_helpers
def billing_invoice_response(year: int, month: int, data: dict) -> str:
    total_cost = float(data["details"]["cost_total"])
    namespace = data["details"]["namespace"]
    billing_records = data["details"]["billing_records"]
    details = data["details"].get("details", [])
    if (
        not billing_records or total_cost == 0
    ):  # TODO: total_cost == 0 is it correct thinking?
        raise NoInvoiceFoundForSelectedMonth(year, month)
    message = get_billing_status_message(billing_records, details)
    message += f"Total cost for namespace {namespace} in {calendar.month_name[month]} {year}: {total_cost:.2f} pln"
    return message


@key_error_decorator_for_helpers
def billing_pricing_response(data: dict) -> str:
    """Create response string for billing pricing command.

    :return: Response string.
    :rtype: str
    """
    pricing_details = data["details"]["pricing_details"]
    if not pricing_details:
        return "No pricing details available."
    if pricing_details.get("tier"):
        tier = pricing_details["tier"] or "DEFAULT"
        click.echo(f"Current pricing tier: {tier}")
    if not pricing_details.get("resources"):
        return "No resources costs available."
    headers = ["Resource", "Price per unit (pln) / (second OR token)"]
    pricing_data = [
        (resource, f"{Decimal(str(price)):.7f}")
        for resource, price in pricing_details.get("resources").items()
    ]
    click.echo(
        "Pricing values displayed are approximated due to float representation. For exact values, refer to the billing system dashboard."
    )

    return tabulate(pricing_data, headers=headers)
