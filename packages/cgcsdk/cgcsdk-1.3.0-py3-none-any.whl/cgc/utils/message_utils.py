import click

from colorama import Fore, Style
from functools import wraps

from cgc.commands.exceptions import ResponseException
from cgc.telemetry.basic import increment_metric
from cgc.utils.consts.message_consts import UNKNOWN_ERROR, CONFIG_FILE_NOT_FOUND, CONFIG_FILE_CORRUPTED
from cgc.commands.auth import NoConfigFileFound, CorruptedConfigFile


def prepare_error_message(message: str) -> str:
    """Prepare error message for CLI.

    :param message: error message.
    :type message: str
    """
    return f"{Fore.RED}{message}{Style.RESET_ALL}"


def prepare_warning_message(message: str) -> str:
    """Prepare warning message for CLI.

    :param message: warning message.
    :type message: str
    """
    return f"{Fore.YELLOW}{message}{Style.RESET_ALL}"


# def prepare_success_message(message: str) -> str:
#     """Prepare success message for CLI.

#     :param message: success message.
#     :type message: str
#     """
#     return f"{Fore.GREEN}{message}{Style.RESET_ALL}"


def key_error_decorator_for_helpers(func):
    """Decorator for handling exceptions of responses

    :param func: _description_
    :type func: _type_
    :return: _description_
    :rtype: _type_
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NoConfigFileFound:
            click.echo(prepare_warning_message(CONFIG_FILE_NOT_FOUND))
            exit(1)
        except CorruptedConfigFile:
            click.echo(prepare_warning_message(CONFIG_FILE_CORRUPTED))
            exit(1)
        except (TypeError, KeyError, IndexError) as err:
            print(args, "\n", kwargs)
            increment_metric("client.parser", True)
            if "debug" in kwargs:
                raise err
            return prepare_error_message(UNKNOWN_ERROR)
        except (ResponseException, click.ClickException) as err:
            return prepare_warning_message(err)
        except KeyboardInterrupt:
            increment_metric(metric="client.interrupted", is_error=True)
            # silently exit
            exit(0)

    return wrapper
