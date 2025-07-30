from cgc.commands.jobs import NoJobsToList
from cgc.commands.jobs.job_utils import get_job_list
from cgc.telemetry.basic import change_gauge, setup_gauge
from cgc.utils.config_utils import get_namespace
from cgc.utils.message_utils import key_error_decorator_for_helpers
from cgc.utils.response_utils import (
    fill_missing_values_in_a_response,
    tabulate_a_response,
)


@key_error_decorator_for_helpers
def job_delete_response(data: dict) -> str:
    """Create response string for job delete command.

    :param response: dict object from API response.
    :type response: requests.Response
    :return: Response string.
    :rtype: str
    """
    name = data.get("details", {}).get("job_deleted", {}).get("name")
    change_gauge(f"{get_namespace()}.job.count", -1)
    return f"Job {name} and its service successfully deleted."


@key_error_decorator_for_helpers
def job_list_response(data: dict) -> list:
    job_pod_list = data.get("details", {}).get("job_pod_list", [])
    job_list = data.get("details", {}).get("job_list", [])
    setup_gauge(f"{get_namespace()}.job.count", len(job_list))

    if not job_list:
        raise NoJobsToList()

    list_of_json_data = get_job_list(job_list, job_pod_list)
    table = fill_missing_values_in_a_response(list_of_json_data)

    return tabulate_a_response(table)


@key_error_decorator_for_helpers
def job_create_response(data: dict) -> str:
    """Create response string for job create command.

    :param response: dict object from API response.
    :type response: requests.Response
    :return: Response string.
    :rtype: str
    """
    name = data.get("details", {}).get("job_created", {}).get("name")
    change_gauge(f"{get_namespace()}.job.count", 1)
    return f"Job {name} created successfully."
