"""
Application utility functions.
"""

from datetime import date, datetime, time, timedelta


def format_date(date: datetime | date) -> str:
    """
    Format a date in a human-friendly way

    The exact output depends on the system locale. :meth:`datetime.strftime`
    is used to do the formatting.

    :param date: The date to format. Note that, if a :class:`datetime`
        is given, time attributes are ignored.
    :type date: :class:`date` or :class:`datetime`

    :return: A human-friendly format of the date.
    :rtype: str
    """
    return date.strftime("%A, %d %B %Y")


def format_time(time: datetime | time) -> str:
    """
    Format a time in a human-friendly way

    The exact output depends on the system locale. :class:`datetime.strftime`
    is used to do the formatting.

    :param time: The date to format. Note that, if a :class:`datetime`
        is given, date attributes are ignored.
    :type time: :class:`time` or :class:`datetime`

    :return: A human-friendly format of the time.
    :rtype: str
    """
    return time.strftime("%I:%M%p")


def get_app_dir() -> str:
    r"""Returns the config folder for the application.  The default behavior
    is to return whatever is most appropriate for the operating system.

    To give you an idea, for an app called ``"Foo Bar"``, something like
    the following folders could be returned:

    Mac OS X:
      ``~/Library/Application Support/Foo Bar``
    Mac OS X (POSIX):
      ``~/.foo-bar``
    Unix:
      ``~/.config/foo-bar``
    Unix (POSIX):
      ``~/.foo-bar``
    Windows (roaming):
      ``C:\Users\<user>\AppData\Roaming\Foo Bar``
    Windows (not roaming):
      ``C:\Users\<user>\AppData\Local\Foo Bar``
    """
    from click import get_app_dir

    return get_app_dir("WorkTimer", True, False)


def make_app_dir() -> bool:
    """
    Ensure that the application data directory exists

    Attempt to create it if it does not.

    :return: Whether the directory now exists
    :rtype: bool
    """
    from pathlib import Path

    from worktimer.core import const

    directory = Path(const.PATH_APP)
    if directory.exists():
        return True
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        return False
    directory.chmod(0o755)  # drwxr-xr-x
    return True


def now() -> datetime:
    """
    Get the current date and time

    The resulting `datetime` object is the same as returned by
    :func:`datetime.now`, except that its microseconds are set to 0. This
    slightly abbreviated form, and timedeltas resulting from it, can
    be printed in a more visually pleasant way with less formatting
    consideration in cases where microseconds are not so important.

    :return: The date and time at the moment the function is called.
    :rtype: :class:`datetime`
    """
    dt = datetime.now()
    # Remove the microseconds.
    dt -= timedelta(microseconds=dt.microsecond)
    return dt


def time_difference(start: datetime, stop: datetime) -> timedelta:
    """
    Calculate the difference between two times

    :param start: The earlier moment.
    :type start: :class:`datetime`
    :param stop: The later moment.
    :type stop: :class:`datetime`

    :return: The length of time from `start` to `stop`.
    :rtype: :class:`timedelta`
    """
    return stop - start


def weekday_name(weekday: int, abbreviate: bool = False) -> str:
    """
    Convert a weekday (0-6) to a string (Mon-Sun).

    :param weekday: 0-6 representing the day of the week. Monday is 0.
    :type weekday: int
    :param Abbreviate: Whether to abbreviate the resulting name to
        its first three letters (e.g., "Monday" becomes "Mon").
    :type abbreviate: bool

    :return: The name of the given weekday, or "N/A" if `weekday` is not
        between 0 and 6 (inclusive).
    :rtype: str
    """
    days = (
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    )
    if not (0 <= weekday < len(days)):
        return "N/A"
    name = days[weekday]
    return name if not abbreviate else name[:3]
