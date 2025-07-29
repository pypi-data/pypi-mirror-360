"""
WorkTimer class module
"""

from copy import deepcopy
from datetime import datetime, timedelta

from worktimer.core import util
from worktimer.core.database import Database


class WorkTimer:
    """
    Representation of a timer that tracks working hours.
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize the timer.

        :param db: The Database object which will handle the storing
            and retrieving of work events.
        :type db: :class:`database`
        """
        self.db = db

    def log_work_start(self) -> str:
        """
        Start the work timer

        If the timer is already running, do nothing.

        :return: A user-friendly message indicating success or failure.
        :rtype: str
        """
        now = util.now()
        self.db.connect()
        events = self.db.get_daily_events(now)

        # Make sure that we don't start the clock if it is already
        # running (i.e., if the latest event is a start event).
        if len(events) > 0 and events[-1]["working"]:
            self.db.close()
            return "You are already on the clock."

        # Now it's safe to try to log this event.
        if self.db.log_event(now, True):
            self.db.close()
            return "You are now on the clock."
        self.db.close()
        return f"ERROR: Failed to log event ({now}, 1)."

    def log_work_end(self) -> str:
        """
        Stop the work timer

        If the timer is already stopped, do nothing.

        :return: A user-friendly message indicating success or failure.
        :rtype: str
        """
        now = util.now()
        self.db.connect()
        events = self.db.get_daily_events(now)

        # Make sure that we don't stop the clock if it is already
        # stopped (i.e., if the latest event is a stop event).
        if len(events) == 0 or not events[-1]["working"]:
            self.db.close()
            return "You are already off the clock."

        # Now it's safe to try to log the event.
        if self.db.log_event(now, False):
            self.db.close()
            return "You are no longer on the clock."
        self.db.close()
        return f"ERROR: Failed to log event ({now}, 0)."

    def calculate_daily_blocks(self, events: list) -> tuple:
        """
        Find all blocks of time spent at work in a given day

        :param events: A list of dicts containing keys "timestamp" and
            "working", that represent start and stop work events for
            the day.
        :type events: list[dict[str, str]]

        :return: A tuple containing two objects.
            * The first is a :class:`timedelta` representing the total
            time worked in the given day.
            * The second is a (possibly empty) list of tuples, each of
            which represent a block of time spent at work in the
            given day. Blocks are length three and contain the
            block's start time (as a :class:`datetime`), its end
            time (as a :class:`datetime`), and the length of the
            block (as a :class:`timedelta`).
        :rtype: tuple
        """
        # Copy the list because we may need to add a temporary event of
        # our own and do not want to modify the caller's version.
        events = deepcopy(events)

        # If the number of events is not even, we know we have an
        # incomplete time pair. In this case, we'll need to add a temp-
        # orary stop event of our own.
        if len(events) % 2 != 0:
            temp_event = {
                "timestamp": util.now(),
                "working": False,
            }
            events.append(temp_event)

        event_count = len(events)
        results = []
        total_time = timedelta()
        # Iterate through the events, starting at the first (always a
        # start event) and skipping every other (stop) event.
        for i in range(0, event_count, 2):
            # Save this event, which is always a start event.
            start = events[i]["timestamp"]
            # Save the next event, which is the corresponding stop.
            stop = events[i + 1]["timestamp"]
            # Calculate how much time was spent from `start` to `stop`.
            duration = util.time_difference(start, stop)
            # Add this duration to the total time worked for the day.
            total_time += duration
            block = (start, stop, duration)
            results.append(block)
        return total_time, results

    def calculate_weekly_blocks(self, weekly_events: list) -> tuple:
        """
        Find all time spent at work in a given week

        :param weekly_events: a length-7 list of daily event lists,
            representing all events for each day of the week. Each
            element is equivalent to that which
            `.calculate_daily_blocks` expects.
        :type weekly_events: list

        :return: A tuple containing two objects.
            * The total time spent at work in the given week (as a
            :class:`timedelta`).
            * a list of 7 :class:`timedelta` objects, representing the
            total length of time at work each day of the week.
        :rtype: tuple
        """
        results = []
        total_time = timedelta()
        for day in weekly_events:
            daily_total, blocks = self.calculate_daily_blocks(day)
            total_time += daily_total
            results.append(daily_total)
        return total_time, results

    def get_daily_time_worked(self, dt: datetime) -> str:
        """
        Generate a list of time blocks spent working for a given day

        :param dt: The date/datetime of the day to view.
        :type dt: :class:`datetime`

        :return: A human-friendly view of the time spent at work on that day. It
            includes a header containing the full date; a list of
            time pairs including start time, stop time, and duration;
            and a footer which shows the total time spent at work.
        :rtype: str
        """
        results = []
        # Format the header, including the full date (e.g., "Monday,
        # 19 May 2025").
        header = f"Time Worked on {util.format_date(dt)}\n"
        results.append(header)

        self.db.connect()
        events = self.db.get_daily_events(dt)
        self.db.close()

        total_time, blocks = self.calculate_daily_blocks(events)
        for block in blocks:
            start, stop, duration = block
            # Create human-friendly formats of start and stop times
            # (e.g., "12:00PM".
            start_time = util.format_time(start)
            stop_time = util.format_time(stop)
            # Create a human-friendly line detailing this block.
            line = f"{start_time} - {stop_time}: {duration}"
            results.append(line)

        # Add the total time worked for the entire day.
        footer = f"\nTotal time worked: {total_time}"
        results.append(footer)

        return "\n".join(results)

    def get_weekly_time_worked(self, dt: datetime) -> str:
        """
        Generate a list of daily work hours for a given week

        :param dt: A date/datetime which falls within the week
            to view.
        :type dt: :class:`datetime`

        :return: A human-friendly view of the time spent at work in that week. It
            includes a header containing the full date; a list of
            all days including total time worked per day; and a footer
            which shows the total time spent at work.
        :rtype: str
        """
        results = []
        # Format a header, including the full date (e.g., "Monday,
        # 19 May 2025").
        header = f"Time worked through the Week of {util.format_date(dt)}\n"
        results.append(header)

        self.db.connect()
        events = self.db.get_weekly_events(dt)
        self.db.close()

        total_time, blocks = self.calculate_weekly_blocks(events)
        for i, daily_time in enumerate(blocks):
            # Convert each day number (0-6) to the name of that day.
            day_name = util.weekday_name(i, True)
            # Format a human-friendly view of this day.
            line = f"{day_name}: {daily_time}"
            results.append(line)

        # Add a footer including the total time work that week.
        footer = f"\nTotal time worked: {total_time}"
        results.append(footer)

        return "\n".join(results)
