import click


@click.command
def start():
    """Start the work timer"""
    from .util import create_worktimer

    wt = create_worktimer()
    msg = wt.log_work_start()
    click.echo(msg)
