from datetime import datetime

import click


@click.command
@click.option(
    "-d",
    "--date",
    help="The date to display, in YYYY-MM-DD format  [default: today's date]",
    default=lambda: datetime.now().isoformat(),
)
def day(date: str):
    """Display detailed time worked on a given day"""
    from .util import create_worktimer

    try:
        dt = datetime.fromisoformat(date)
    except ValueError:
        error = click.BadParameter("Format must be YYYY-MM-DD")
        error.param_hint = "date"
        raise error

    wt = create_worktimer()
    msg = wt.get_daily_time_worked(dt)
    click.echo(msg)
