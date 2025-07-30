import click


class CustomGroup(click.Group):
    """Class to customize help message for click groups"""

    def format_usage(self, ctx, formatter):
        pieces = self.collect_usage_pieces(ctx)
        cmd_path = ctx.command_path.removeprefix("python -m ")
        formatter.write_usage(cmd_path, " ".join(pieces))


class CustomCommand(click.Command):
    """Class to customize help message for click commands"""

    def format_usage(self, ctx, formatter):
        pieces = self.collect_usage_pieces(ctx)
        cmd_path = ctx.command_path.removeprefix("python -m ")
        formatter.write_usage(cmd_path, " ".join(pieces))


class NonNegativeInteger(click.types.IntParamType):
    """A parameter that only accepts non-negative integers."""

    name = "non-negative-integer"

    def convert(self, value, param, ctx):
        # First convert using the parent class method
        result = super().convert(value, param, ctx)
        if result < 0:
            self.fail(f"{value} is not a non-negative integer", param, ctx)
        return result
