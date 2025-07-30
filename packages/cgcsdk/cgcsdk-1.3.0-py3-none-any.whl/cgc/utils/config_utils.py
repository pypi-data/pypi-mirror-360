import json
import os
import sys
from typing import Union
import click

from cgc.commands.auth import NoNamespaceInConfig, NoConfigFileFound, CorruptedConfigFile
from cgc.utils.message_utils import prepare_error_message
from cgc.utils.consts.env_consts import CGC_API_URL, CGC_SECRET


def get_config_file_name():
    try:
        return read_from_local_cfg("context_filename")
    except Exception:
        return os.getenv("CONFIG_FILE_NAME")


def get_config_path():
    """Function to get the path to the config file

    :return: path to the config file
    :rtype: str
    """
    try:
        config_path = os.path.join(
            os.environ.get("APPDATA")
            or os.environ.get("XDG_CONFIG_HOME")
            or os.path.join(os.environ["HOME"], ".config"),
            "cgcsdk",
        )
    except KeyError:
        message = "Could not validate config path, try again or contact support at support@comtegra.pl"
        click.echo(prepare_error_message(message))
        sys.exit()

    return config_path


config_path = get_config_path()


def save_to_local_config_context(context_filename: str):
    """Function allowing adding a variable number of key-value pairs to the config file.
    If config file does not exist, it is created, otherwise key-value pairs are appended to existing config.
    Values for existing keys are overwritten.

    :param kwargs: key-value pairs to be saved in the config file
    :type kwargs: dict
    """
    read_cfg = {}
    user_config_file = os.path.join(config_path, "cgc.json")
    if not os.path.isdir(config_path):
        os.makedirs(config_path, mode=0o700)
    try:
        with open(user_config_file, "r", encoding="UTF-8") as f:
            read_cfg = json.load(f)
    except FileNotFoundError:
        pass
    except json.decoder.JSONDecodeError:
        pass

    prev_umask = os.umask(0o077)
    try:
        with open(user_config_file, "w", encoding="UTF-8") as f:
            final_cfg = {**read_cfg, "context_filename": context_filename}
            json.dump(final_cfg, f)
    finally:
        os.umask(prev_umask)


def save_to_local_config(**kwargs):
    """Function allowing adding a variable number of key-value pairs to the config file.
    If config file does not exist, it is created, otherwise key-value pairs are appended to existing config.
    Values for existing keys are overwritten.

    :param kwargs: key-value pairs to be saved in the config file
    :type kwargs: dict
    """
    read_cfg = {}
    user_config_file = os.path.join(config_path, "cgc.json")
    if not os.path.isdir(config_path):
        os.makedirs(config_path, mode=0o700)
    try:
        with open(user_config_file, "r", encoding="UTF-8") as f:
            read_cfg = json.load(f)
    except FileNotFoundError:
        pass
    except json.decoder.JSONDecodeError:
        pass

    prev_umask = os.umask(0o077)
    try:
        with open(user_config_file, "w", encoding="UTF-8") as f:
            cgc_api_url = read_from_cfg("cgc_api_url")
            if "context_filename" in kwargs:
                kwargs.pop("context_filename")
            previous_server_values: dict = read_cfg.get(cgc_api_url, {})
            new_server_values = {**previous_server_values, **kwargs}
            previous_server_values = new_server_values
            final_cfg = {
                **read_cfg,
                cgc_api_url: {**previous_server_values},
            }
            json.dump(final_cfg, f)
    finally:
        os.umask(prev_umask)


def save_to_config(**kwargs):
    """Function allowing adding a variable number of key-value pairs to the config file.
    If config file does not exist, it is created, otherwise key-value pairs are appended to existing config.
    Values for existing keys are overwritten.

    :param kwargs: key-value pairs to be saved in the config file
    :type kwargs: dict
    """
    read_cfg = {}
    user_config_file = os.path.join(config_path, get_config_file_name())
    if not os.path.isdir(config_path):
        os.makedirs(config_path, mode=0o700)
    try:
        with open(user_config_file, "r", encoding="UTF-8") as f:
            read_cfg = json.load(f)
    except FileNotFoundError:
        pass

    prev_umask = os.umask(0o077)
    try:
        with open(user_config_file, "w", encoding="UTF-8") as f:
            final_cfg = {**read_cfg, **kwargs}
            json.dump(final_cfg, f)
    finally:
        os.umask(prev_umask)


def is_config_file_present():
    """Function to check if the config file is present

    :return: True if the config file is present, False otherwise
    :rtype: bool
    """
    try:
        with open(
            os.path.join(config_path, get_config_file_name()), "r", encoding="UTF-8"
        ) as _:
            return True
    except FileNotFoundError:
        return False


def read_from_local_cfg(key: str) -> Union[list, str]:
    """Function to read a single value from the CGC config

    :param key: key name to read the value from config
    :type key: str
    :return: value for the provided key
    :rtype: _type_
    """
    filename_with_path = os.path.join(config_path, "cgc.json")
    try:
        with open(filename_with_path, "r", encoding="UTF-8") as f:
            read_cfg: dict = json.load(f)
            if key == "context_filename":
                return read_cfg[key]
            try:
                cgc_api_url = read_from_cfg("cgc_api_url")
            except (NoConfigFileFound, CorruptedConfigFile):
                cgc_api_url = CGC_API_URL
            if key is None:
                return read_cfg[cgc_api_url]
            return read_cfg[cgc_api_url][key]
    except FileNotFoundError as e:
        raise e
    except KeyError as e:
        if (
            key == "compute_templates"
            or key == "database_templates"
            or key == "storage_classes"
        ):
            return []
        elif key == "default_storage_class":
            return None
        raise NoConfigFileFound() from e
    except json.decoder.JSONDecodeError as e:
        if key == "context_filename":
            raise FileNotFoundError from e
        return []


def read_from_cfg(key: str, filename=None):
    """Function to read a single value from config

    :param key: key name to read the value from config
    :type key: str
    :return: value for the provided key
    :rtype: _type_
    """
    if filename is None:
        filename_with_path = os.path.join(config_path, get_config_file_name())
    else:
        filename_with_path = os.path.join(config_path, filename)
    try:
        with open(filename_with_path, "r", encoding="UTF-8") as f:
            read_cfg = json.load(f)
            if key is None:
                return read_cfg
            return read_cfg[key]
    except FileNotFoundError:
        if key == "cgc_secret":
            return CGC_SECRET
        if key == "cgc_api_url":
            return CGC_API_URL
        elif key == "namespace":
            raise NoNamespaceInConfig()
        raise NoConfigFileFound()
    except KeyError:
        if key == "namespace":
            raise NoNamespaceInConfig()
        elif key == "cgc_secret":
            return CGC_SECRET
        elif key == "cgc_api_url":
            return CGC_API_URL
        raise CorruptedConfigFile()
    except json.decoder.JSONDecodeError:
        raise CorruptedConfigFile()


def get_namespace() -> str:
    """Function to get the namespace from the config file

    :return: namespace
    :rtype: str
    """
    return read_from_cfg("namespace")
