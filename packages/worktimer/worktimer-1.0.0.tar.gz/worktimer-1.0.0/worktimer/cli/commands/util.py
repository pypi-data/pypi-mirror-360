"""
Command utility functions
"""


def create_worktimer():
    """
    Create a ready-to-use WorkTimer

    :return: A WorkTimer with database and other dependencies already
        set up.
    :rtype: :class:`worktimer.core.worktimer.WorkTimer`
    """
    from worktimer.core import const
    from worktimer.core.database import Database
    from worktimer.core.worktimer import WorkTimer

    db = Database(const.PATH_DB)
    wt = WorkTimer(db)
    return wt


def register_commands(cli):
    """
    Register all commands with the top-level Click group

    :param cli: The top-level Click group to hold the commands.
    :type cli: :class:`click.Group`
    """
    from .day import day
    from .start import start
    from .stop import stop
    from .week import week

    cli.add_command(start)
    cli.add_command(stop)
    cli.add_command(day)
    cli.add_command(week)
