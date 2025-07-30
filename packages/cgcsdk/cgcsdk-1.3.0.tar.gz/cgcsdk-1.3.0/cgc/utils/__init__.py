from typing import List
from os import listdir
from os.path import isfile, join
from cgc.utils.config_utils import config_path
from operator import is_not
from functools import partial
from random import randrange

from cgc.utils.consts.env_consts import ENV_FILE_PATH
from cgc.utils.config_utils import read_from_cfg
from cgc.commands.auth import NoConfigFileFound


def require_confirm_loop(message: str):
    while True:
        answer = input(f"{message} (Y/N): ").lower()
        if answer in ("y", "yes"):
            break
        if answer in ("n", "no"):
            exit(0)


def require_answer_loop(message: str, default: str):
    while True:
        answer = input(f"{message}: [{default}]")
        if answer == "":
            return default
        return answer


def quick_sort(collection: list) -> list:
    """A pure Python implementation of quick sort algorithm

    :param collection: a mutable collection of comparable items
    :return: the same collection ordered by ascending

    Examples:
    >>> quick_sort([0, 5, 3, 2, 2])
    [0, 2, 2, 3, 5]
    >>> quick_sort([])
    []
    >>> quick_sort([-2, 5, 0, -45])
    [-45, -2, 0, 5]
    """
    if len(collection) < 2:
        return collection
    pivot_index = randrange(len(collection))  # Use random element as pivot
    pivot = collection[pivot_index]
    greater: list[int] = []  # All elements greater than pivot
    lesser: list[int] = []  # All elements less than or equal to pivot

    for element in collection[:pivot_index]:
        (greater if element > pivot else lesser).append(element)

    for element in collection[pivot_index + 1 :]:
        (greater if element > pivot else lesser).append(element)

    return [*quick_sort(lesser), pivot, *quick_sort(greater)]


def set_environment_data(variable: str, value: str):
    """Set variable to .env file

    :return: new value
    :rtype: str
    """
    f = open(file=ENV_FILE_PATH, mode="r")
    replaced_content = f.read()
    replaced_content = replaced_content.splitlines()
    f.close()
    for i, line in enumerate(replaced_content):
        splitted = line.split(" ")
        if splitted[0] == variable.upper():
            replaced_content[i] = line.replace(splitted[2], value)
            with open(file=ENV_FILE_PATH, mode="w") as f:
                f.write("\n".join(replaced_content))
            break
    else:
        with open(file=ENV_FILE_PATH, mode="a") as f:
            f.write(f"\n{variable.upper()} = {value}")

    return value


def find_first_available_config_name() -> str:
    increment = 2
    while True:
        filename = f"{increment}.json"
        try:
            read_from_cfg(None, filename)
            increment += 1
        except NoConfigFileFound:
            break
    return filename


def check_if_config_exist(filename: str) -> bool:
    try:
        read_from_cfg(None, filename)
    except NoConfigFileFound:
        return False
    return True


def list_all_config_files() -> List[str]:
    try:
        only_files = [f for f in listdir(config_path) if isfile(join(config_path, f))]
    except FileNotFoundError:
        return []

    def only_json_file(filename: str):
        return filename if filename.endswith(".json") else None

    def cgc_config_file(filename: str):
        filename_prefix = filename.split(".")[0]
        try:
            int(filename_prefix)
            return filename
        except ValueError:
            if filename_prefix == "cfg":
                return filename

    json_files = list(filter(partial(is_not, None), map(only_json_file, only_files)))
    return list(filter(partial(is_not, None), map(cgc_config_file, json_files)))
