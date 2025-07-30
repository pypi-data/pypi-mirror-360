import click
import datetime
import sys
from tabulate import tabulate
from cgc.utils.message_utils import (
    prepare_error_message,
)


def verify_input_datetime(*args):
    try:
        for arg in args:
            datetime.datetime.strptime(arg, "%d-%m-%Y")
    except ValueError:
        click.echo(prepare_error_message("Incorrect date format, should be DD-MM-YYYY"))
        sys.exit()


def _get_costs_list_for_user(costs_list: list):
    """Format data in costs list to be displayed in a table and calculate user cost

    :param costs_list: list of costs for user
    :type costs_list: list
    :return: formatted list of costs and total cost for user
    :rtype: user_costs_list_to_print: list, total_user_cost: float
    """
    user_costs_list_to_print = []
    total_user_cost = 0

    for cost in costs_list:
        if "resource_cost" in cost:
            if cost.get("type", "") == "oneoff":
                for resource, value in cost["resource_cost"].items():
                    user_costs_list_to_print.append(
                        [
                            cost.get("type", ""),
                            cost.get("namespace", ""),
                            f"{resource}: {float(value):.2f} pln",
                            "-",
                            "-",
                            "<<-",
                        ]
                    )
                    total_user_cost += float(cost.get("cost_total", 0))
            else:
                resource_cost_str = ", ".join(
                    f"{k}: {float(v):.2f}" for k, v in cost["resource_cost"].items()
                )
                start, end = "-", "-"
                if "datetime_range" in cost and len(cost["datetime_range"]) == 2:
                    start, end = cost["datetime_range"]
                user_costs_list_to_print.append(
                    [
                        cost.get("type", ""),
                        cost.get("namespace", ""),
                        resource_cost_str,
                        start,
                        end,
                        f"{float(cost.get('cost_total', 0)):.2f} pln",
                    ]
                )
                total_user_cost += float(cost.get("cost_total", 0))

    if costs_list:
        user_costs_list_to_print.sort(key=lambda d: f"{d[0]} {d[1]}")
    return user_costs_list_to_print, total_user_cost


def _get_costs_list_for_user_with_details(costs_list: list):
    """Format data in costs list to be displayed in a table and calculate user cost with details

    :param costs_list: list of costs for user
    :type costs_list: list
    :return: formatted list of costs and total cost for user
    :rtype: user_costs_list_to_print: list, total_user_cost: float
    """
    user_costs_list_to_print = []
    total_user_cost = 0

    for cost in costs_list:
        # Support both old and new structure
        record = cost.get("record", {})
        name = record.get("name", cost.get("name", ""))
        # id_ = record.get("id", cost.get("id", ""))
        user_id = record.get("user_id", cost.get("user_id", ""))
        namespace = record.get("namespace", cost.get("namespace", ""))
        type_ = record.get("type", cost.get("type", ""))
        resource_cost = cost.get("resource_cost", {})
        if type_ == "oneoff":
            for resource, value in resource_cost.items():
                user_costs_list_to_print.append(
                    [
                        name,
                        user_id,
                        namespace,
                        type_,
                        f"{resource}: {float(value):.2f} pln",
                        "-",
                        "-",
                        "<<-",
                    ]
                )
                total_user_cost += float(cost.get("cost_total", 0))
        else:
            resource_cost_str = ", ".join(
                f"{k}: {float(v):.2f}" for k, v in resource_cost.items()
            )
            start = cost.get("calculation_start_time", "-")
            end = cost.get("calculation_end_time", "-")
            cost_total = cost.get("cost_total", 0)

            user_costs_list_to_print.append(
                [
                    name,
                    # id_,
                    user_id,
                    namespace,
                    type_,
                    resource_cost_str,
                    start,
                    end,
                    f"{float(cost_total):.2f} pln",
                ]
            )
        total_user_cost += float(cost_total)

    if costs_list:
        user_costs_list_to_print.sort(key=lambda d: f"{d[0]} {d[1]}")
    return user_costs_list_to_print, total_user_cost


def get_billing_status_message(billing_records: list, details: list = []):
    """Prints billing status for all users in a pretty table

    :param user_list: list of users with costs
    :type user_list: list
    """
    message = ""
    users = set(
        record.get("user_id", "") for record in billing_records
    )  # Get unique user IDs
    if not users:
        return "No billing records found."
    for user in users:
        user_records = [
            record for record in billing_records if record["user_id"] == user
        ]
        costs_list_to_print, _user_cost = _get_costs_list_for_user(user_records)
        list_headers = _get_status_list_headers()
        message += f"Billing status for user: {user}\n"
        message += tabulate(costs_list_to_print, headers=list_headers)
        message += f"\n\nSummary user cost: {float(_user_cost):.2f} pln\n\n"
    if details:
        message += "Detailed billing records:\n"
        costs_list_to_print, _ = _get_costs_list_for_user_with_details(details)
        if not costs_list_to_print:
            message += "No detailed billing records found.\n"
        else:
            list_headers = _get_billing_details_list_headers()
            message += tabulate(costs_list_to_print, headers=list_headers)
            message += "\n\n"
    return message


def _get_status_list_headers():
    """Generates headers for billing status command

    :return: list of headers
    :rtype: list
    """
    return ["type", "namespace", "resource breakdown", "start", "end", "cost"]


def _get_billing_details_list_headers():
    """Generates headers for billing details command

    :return: list of headers
    :rtype: list
    """
    return [
        "name",
        # "id",
        "user_id",
        "namespace",
        "type",
        "resource breakdown",
        "start",
        "end",
        "cost_total",
    ]


# TODO: refactor to use: tabulate_a_response(data: list) -> str:
def get_table_compute_stop_events_message(event_list: list):
    """Prints compute stop events info

    :param event_list: raw list of events
    :type event_list: list
    """
    message = "Compute stop events:"
    event_list_headers = ["id", "name", "entity", "date created"]
    event_list_to_print = []
    for event in event_list:
        event_id = event["event_id"]
        event_name = event["event_name"]
        event_date = event["date_created"]
        event_entity = event["entity"]
        row_list = [event_id, event_name, event_entity, event_date]
        event_list_to_print.append(row_list)
    message += tabulate(event_list_to_print, headers=event_list_headers)
    return message


# TODO: refactor to use: tabulate_a_response(data: list) -> str:
def get_table_volume_stop_events_message(event_list: list):
    """Prints volume stop events info

    :param event_list: raw list of events
    :type event_list: list
    """
    message = "Volume stop events:"
    event_list_headers = [
        "id",
        "name",
        "disks type",
        "access type",
        "size",
        "date created",
    ]
    event_list_to_print = []
    for event in event_list:
        event_id = event["event_id"]
        volume_name = event["volume_name"]
        event_date = event["date_created"]
        disks_type = event["disks_type"]
        access_type = event["access_type"]
        size = event["size"]
        row_list = [event_id, volume_name, disks_type, access_type, size, event_date]
        event_list_to_print.append(row_list)
    message += tabulate(event_list_to_print, headers=event_list_headers)
    return message
