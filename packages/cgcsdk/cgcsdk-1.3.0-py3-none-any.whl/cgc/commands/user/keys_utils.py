from typing import Optional
import click
from cgc.commands.user.keys_models import SSHKeyTypes


def create_ssh_key_payload(
    public_key: Optional[str] = None,
    key_type: Optional[str] = None,
    key: Optional[str] = None,
    comment: str = "",
) -> dict:
    """Create a payload for creating a new SSH key"""
    if public_key:
        try:
            key_parts = public_key.split(" ")
            key_type = key_parts[0] if key_parts[0] in SSHKeyTypes.get_list() else ""
            if not key_type:
                raise click.ClickException("Invalid key type")
            key = key_parts[1]
            comment = key_parts[2] if len(key_parts) > 2 else comment
        except IndexError:
            raise click.ClickException("Invalid public key format")
    if not key_type or not key:
        raise click.ClickException("Invalid public key or key_type")
    payload = {
        "key_type": key_type,
        "key": key,
        "comment": comment,
    }
    return payload


def update_ssh_key_payload(
    key_type: Optional[str] = None,
    key: Optional[str] = None,
    comment: Optional[str] = None,
) -> dict:
    """Create a payload for creating a new SSH key"""
    payload = {}
    if key_type:
        if not key:
            raise click.ClickException("Invalid public key")
        payload["key_type"] = key_type
    if key:
        if not key_type:
            raise click.ClickException("Invalid key_type")
        payload["key"] = key
    if comment:
        payload["comment"] = comment
    return payload


def get_user_ssh_keys(keys: list) -> list:
    """
    Format list of keys for user
    :param keys: list of user keys
    :type keys: list
    :return: formatted list of keys
    :rtype: list
    """
    output_data = []

    for key in keys:
        try:
            key_data = {
                "key_id": key["key_id"],
                "key_type": key["key_type"],
                "key": key["key"],
                "comment": key["comment"],
                "date_added": key["date_added"],
                "date_updated": key["date_updated"],
            }
            # appending the rest of labels
            key_data.update(key)
            output_data.append(key_data)
        except KeyError:
            pass

    return output_data
