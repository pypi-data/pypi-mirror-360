import sys
import click
import pprint
import requests
import json
from tabulate import tabulate
from cgc.commands.auth import NoNamespaceInConfig, NoConfigFileFound
from cgc.utils.message_utils import prepare_error_message
from cgc.utils.consts.message_consts import (
    UNKNOWN_ERROR,
    UNAUTHORIZED_ERROR,
    ENDPOINT_DISABLED,
)
from cgc.utils.custom_exceptions import CUSTOM_EXCEPTIONS
from cgc.telemetry.basic import increment_metric
from cgc.utils.config_utils import get_namespace
from cgc.sdk.exceptions import SDKException


def _get_response_json_error_message(response_json: dict):
    if "message" in response_json:
        return response_json["message"]
    return UNKNOWN_ERROR


def retrieve_and_validate_response_send_metric_for_sdk(
    response: requests.Response, metric: str, json_return: bool = True
):
    """Checks if server is available and user is authorized

    :param response: dict object from API response.
    :type response: requests.Response
    """
    error_message = UNKNOWN_ERROR
    try:
        try:
            if metric is not None:
                metric = f"{get_namespace()}.{metric}"
        except NoNamespaceInConfig:
            metric = f"unknown-namespace.{metric}"
        except NoConfigFileFound:
            print("No config file found. Please use:")
            print("cgc register")
            metric = f"bad-client.{metric}"

        if response.status_code == 200:
            increment_metric(
                metric=metric, is_error=False
            )  # if metric is None, will not increment metric
            if json_return:
                return response.json()
            else:
                return response
        increment_metric(
            metric=metric, is_error=False
        )  # ALL "VALID" error messages are not Errors
        if response.status_code == 401:
            raise SDKException(response.status_code, UNAUTHORIZED_ERROR)
        elif response.status_code == 302:
            raise SDKException(response.status_code, ENDPOINT_DISABLED)
        else:
            try:
                response_json = response.json()
                if "details" in response_json:
                    raise SDKException(response.status_code, response_json["details"])
                else:
                    raise SDKException(
                        response.status_code,
                        CUSTOM_EXCEPTIONS[response.status_code][
                            response_json["reason"]
                        ],
                    )
            except KeyError as e:
                error_message = _get_response_json_error_message(response_json)
                increment_metric(metric=metric, is_error=True)
                raise SDKException(response.status_code, error_message) from e

    except (AttributeError, json.JSONDecodeError) as e:
        increment_metric(metric=metric, is_error=True)
        raise SDKException(
            response.status_code, f"Response reading error. {error_message}"
        ) from e


def retrieve_and_validate_response_send_metric(
    response: requests.Response, metric: str, json_return: bool = True
):
    """Checks if server is available and user is authorized

    :param response: dict object from API response.
    :type response: requests.Response
    """
    error_message = UNKNOWN_ERROR
    try:
        try:
            if metric is not None:
                metric = f"{get_namespace()}.{metric}"
        except NoNamespaceInConfig:
            metric = f"unknown-namespace.{metric}"
        except NoConfigFileFound:
            print("No config file found. Please use:")
            print("cgc register")
            metric = f"bad-client.{metric}"

        if response.status_code == 200:
            increment_metric(
                metric=metric, is_error=False
            )  # if metric is None, will not increment metric
            if json_return:
                return response.json()
            else:
                return response
        click.echo(prepare_error_message(f"Error code: {response.status_code}"))
        if response.status_code == 401:
            click.echo(prepare_error_message(UNAUTHORIZED_ERROR))
        elif response.status_code == 302:
            click.echo(prepare_error_message(ENDPOINT_DISABLED))
        else:
            try:
                response_json = response.json()
                status_code = response.status_code
                reason = response_json.get("reason", "")
                if (
                    status_code in CUSTOM_EXCEPTIONS
                    and reason in CUSTOM_EXCEPTIONS[status_code]
                ):
                    click.echo(
                        prepare_error_message(
                            CUSTOM_EXCEPTIONS[response.status_code][
                                response_json["reason"]
                            ]
                        )
                    )
                elif "details" in response_json:
                    click.echo(prepare_error_message(response_json["details"]))
                else:
                    raise KeyError("No specific error message or details field found.")
            except KeyError:
                error_message = _get_response_json_error_message(response_json)
                if isinstance(error_message, str):
                    click.echo(prepare_error_message(error_message))
                else:
                    pp = pprint.PrettyPrinter(indent=2, width=60, compact=True)
                    pp.pprint(prepare_error_message(error_message))
                increment_metric(metric=metric, is_error=True)
                sys.exit()

        increment_metric(
            metric=metric, is_error=False
        )  # ALL "VALID" error messages are not Errors
        sys.exit()
    except (AttributeError, json.JSONDecodeError):
        click.echo(prepare_error_message(f"Response reading error. {error_message}"))
        increment_metric(metric=metric, is_error=True)
        sys.exit()


def fill_missing_values_in_a_response(data: list) -> list:
    """Filling missing values so that every row has
    the same number of columns

    :param data: list of rows (dicts)
    :type data: list
    :return: _description_
    :rtype: list
    """
    headers = []
    for row in data:
        if len(list(row.keys())) > len(headers):
            headers = list(row.keys())

    # convert list of dicts to list of tuples to save order
    table = []
    for row in data:
        # if row has only 1 field it means its warning, so we dont change that row
        row_tuple = list(row.items())
        if len(row_tuple) > 1:
            for i, h in enumerate(headers):
                try:
                    if row_tuple[i][0] != h:
                        row_tuple.insert(i, (h, None))
                except IndexError:
                    row_tuple.append((h, None))
        # else:
        #     click.echo(prepare_error_message(row_tuple))
        table.append(row_tuple)

    return table


def tabulate_a_response(data: list) -> str:
    """Converts list of list of tuples/pairs
    to tabulated string , where 1 element of pair is header

    :param data: list of lists of tuples, list of lists of pairs
    like [
        row -> [("name", "foo"), ("type", "jakis")]
    ]
    every row has to have the same number of tuples, so try using
    fill_missing_values_in_a_response first
    :type data: list
    :return: tabulated
    :rtype: str
    """
    if len(data) > 0:
        headers = [column[0] for column in data[0]]
        table = []
        for row in data:
            table.append([column[1] for column in row])
        return tabulate(table, headers=headers)
    else:
        return tabulate([], headers=[])
