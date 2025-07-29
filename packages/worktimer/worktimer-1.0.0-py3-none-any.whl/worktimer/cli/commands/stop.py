import click


@click.command
def stop():
    """Stop the work timer"""
    from .util import create_worktimer

    wt = create_worktimer()
    msg = wt.log_work_end()
    click.echo(msg)
