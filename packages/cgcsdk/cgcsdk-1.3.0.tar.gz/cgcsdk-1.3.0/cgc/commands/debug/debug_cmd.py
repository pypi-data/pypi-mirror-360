import click
from cgc.commands.auth.auth_utils import (
    _get_jwt_from_server,
)
from cgc.utils.click_group import CustomCommand, CustomGroup


@click.group("debug", cls=CustomGroup, hidden=True)
def debug_group():
    """
    Debug commands for testing.
    """
    pass


@debug_group.command("get-jwt", cls=CustomCommand)
def get_jwt_from_server():
    click.echo(_get_jwt_from_server())
