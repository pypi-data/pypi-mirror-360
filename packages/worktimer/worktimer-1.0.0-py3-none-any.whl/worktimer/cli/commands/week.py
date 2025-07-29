from datetime import datetime

import click


@click.command
@click.option(
    "-d",
    "--date",
    help="The date to display, in YYYY-MM-DD format  [default: today's date]",
    default=lambda: datetime.now().isoformat(),
)
def week(date: str):
    """Display time worked on each day in a given week"""
    from .util import create_worktimer

    try:
        dt = datetime.fromisoformat(date)
    except ValueError:
        error = click.BadParameter("Format must be YYYY-MM-DD")
        error.param_hint = "date"
        raise error

    wt = create_worktimer()
    msg = wt.get_weekly_time_worked(dt)
    click.echo(msg)
