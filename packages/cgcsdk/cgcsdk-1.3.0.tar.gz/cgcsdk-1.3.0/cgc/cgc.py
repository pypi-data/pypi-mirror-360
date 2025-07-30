import click
from cgc.commands.volume.volume_cmd import volume_group
from cgc.commands.compute.compute_cmd import compute_group
from cgc.commands.compute.billing.billing_cmd import billing_group
from cgc.commands.db.db_cmd import db_group
from cgc.commands.resource.resource_cmd import resource_group
from cgc.commands.jobs.jobs_cmd import job_group
from cgc.commands.auth.auth_cmd import (
    api_keys_group,
    auth_register,
)

from cgc.commands.debug.debug_cmd import debug_group
from cgc.commands.cgc_cmd import (
    cgc_rm,
    cgc_status,
    cgc_logs,
    sending_telemetry_permission,
    resource_events,
    context_group,
)
from cgc.commands.user.keys_cmd import keys_group
from cgc.commands.user.secret_cmd import secret_group

from cgc.utils.version_control import check_version, _get_version
from cgc.utils.click_group import CustomGroup


@click.group(cls=CustomGroup)
@click.version_option(_get_version())
def cli():
    """CGC application developed by Comtegra S.A."""
    check_version()


cli.add_command(debug_group)
cli.add_command(context_group)
cli.add_command(auth_register)
cli.add_command(api_keys_group)
cli.add_command(volume_group)
cli.add_command(compute_group)
cli.add_command(db_group)
cli.add_command(cgc_rm)
cli.add_command(resource_events)
cli.add_command(resource_group)
cli.add_command(billing_group)
cli.add_command(cgc_status)
cli.add_command(sending_telemetry_permission)
cli.add_command(cgc_logs)
cli.add_command(job_group)
cli.add_command(keys_group)
cli.add_command(secret_group)

if __name__ == "__main__" or __name__ == "cgc.cgc":
    cli()
else:
    raise Exception("This program is not intended for importing!")
