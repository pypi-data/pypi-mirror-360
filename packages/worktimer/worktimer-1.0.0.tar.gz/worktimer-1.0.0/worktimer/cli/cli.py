import click

from worktimer.cli.commands import register_commands


@click.group()
@click.version_option(
    prog_name="WorkTimer",
    message="%(prog)s v%(version)s",
)
def cli():
    """WorkTimer: Simple tracker of time spent at work"""
    from worktimer.core import util

    if not util.make_app_dir():
        msg = f"ERROR: Failed to create app directory: `{util.get_app_dir()}`"
        click.echo(msg)
        raise click.Abort()


register_commands(cli)
