import statsd
import click
from cgc.utils.consts.env_consts import ENV_FILE_PATH
import dotenv


def make_statsd_client():
    """Create a statsd client

    :return: statsd client
    :rtype: statsd.StatsClient
    """
    return statsd.StatsClient("77.79.251.163", 8125, prefix="cgc-client")


def telemetry_permission_set():
    """Set telemetry permission to .env file

    :return: TELEMETRY_PERMISSION value
    :rtype: bool
    """
    while True:
        permission = input(
            "We would like to make your experience with CGC even better! :)\n\
We would like to know which commands are utilized most often and if they have finished properly. Nothing else is collected. Only raw numbers.\n\
Would you agree to send us these numbers? (YES/no) [YES]: \n"
        )
        if permission.lower() in ["yes", "no", ""]:
            break
    permission = True if permission == "" or permission == "yes" else False

    f = open(file=ENV_FILE_PATH, mode="r")
    replaced_content = f.read()
    replaced_content = replaced_content.splitlines()
    f.close()
    for i, line in enumerate(replaced_content):
        splitted = line.split(" ")
        if splitted[0] == "TELEMETRY_PERMISSION":
            replaced_content[i] = line.replace(splitted[2], str(permission))
            with open(file=ENV_FILE_PATH, mode="w") as f:
                f.write("\n".join(replaced_content))
            break
    else:
        with open(file=ENV_FILE_PATH, mode="a") as f:
            f.write(f"\nTELEMETRY_PERMISSION = {permission}")

    return permission


def telemetry_permission_check():
    """Check if the user has the permission to send telemetry.
    if permission not included in envs set it to True.

    :return: bool if env is enabled
    :rtype: bool
    """
    env_dict = dotenv.dotenv_values(ENV_FILE_PATH)
    try:
        if env_dict["TELEMETRY_PERMISSION"] == str(True):
            return True
        else:
            return False
    except KeyError:
        telemetry_permission_set()


def increment_metric(metric, is_error: bool = False):
    """Increment a metric

    :param metric: name of metric
    :type metric: str
    """
    if not telemetry_permission_check():
        return
    if is_error:
        metric = f"{metric}.error"
        click.echo(
            "If you want to open support request, attach command used, status code and error message via support system at https://support.comtegra.pl/"
        )
    else:
        metric = f"{metric}.ok"

    client = make_statsd_client()
    client.incr(metric, 1)


def change_gauge(metric, value):
    """Change a gauge metric

    :param metric: name of metric
    :type metric: str
    :param value: value of metric
    :type value: int
    """
    if not telemetry_permission_check():
        return
    client = make_statsd_client()
    client.gauge(metric, value, delta=True)


def setup_gauge(metric, value):
    """Setup a gauge metric

    :param metric: name of metric
    :type metric: str
    :param value: value of metric
    :type value: int
    """
    if not telemetry_permission_check():
        return
    client = make_statsd_client()
    client.gauge(metric, value)
