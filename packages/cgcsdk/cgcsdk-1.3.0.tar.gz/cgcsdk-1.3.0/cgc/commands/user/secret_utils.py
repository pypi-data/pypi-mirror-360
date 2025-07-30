from typing import Set


def create_secret_payload(
    secret_name: str, registry_list: Set[str], username: str, password: str
) -> dict:
    """Create a payload for creating a new secret"""
    payload = {
        "name": secret_name,
        "registry_list": registry_list,
        "username": username,
        "password": password,
    }
    return payload


def update_secret_payload(
    registry_list: Set[str], username: str, password: str
) -> dict:
    """Create a payload for updating a secret"""
    payload = {}
    if registry_list:
        payload["registry_list"] = registry_list
    if username:
        payload["username"] = username
    if password:
        payload["password"] = password
    return payload


def _get_secret_json_data(secret_list: list):
    """Formats and returns list of secrets to print.

    :param job_list: list of secrets
    :type job_list: list
    :return: formatted list of secrets
    :rtype: list
    """
    output_data = []

    for secret in secret_list:
        try:

            secret_data = {
                "name": secret.get("secret"),
                "secret_type": secret.get("secret_type"),
                "registry_list": secret.get("registry_list", []),
                "secret_admin": secret.get("secret_admin"),
                "date_created": f'{secret.get("date_created")} UTC',
                "whitelist": secret.get("whitelist", ["*"]),
            }
            output_data.append(secret_data)
        except KeyError:
            pass

    return output_data


def get_secret_list(secret_list: list):
    return _get_secret_json_data(secret_list)
