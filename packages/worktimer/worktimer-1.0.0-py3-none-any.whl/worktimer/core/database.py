"""
Application Database class module
"""

import sqlite3
from datetime import datetime, timedelta

from worktimer.core import util


class Database:
    """
    Interface to the underlying db.
    """

    def __init__(self, file_name: str) -> None:
        """
        Initialize the db.

        :param file_name: The name of the SQLite database to which to
            connect.
        :type file_name: str
        """
        self.file_name = file_name
        # Do any necessary setup transparently.
        self.connect()
        self._create_tables()
        self._ensure_time_pairs()
        self.close()

    def connect(self):
        self.connection = sqlite3.connect(self.file_name)
        self.cursor = self.connection.cursor()
        # Return rows as dict-like objects.
        self.cursor.row_factory = sqlite3.Row

    def _create_tables(self) -> bool:
        """
        Create necessary tables if they do not already exist

        Create an 'event' table with 'timestamp' and 'working' columns.
        If that table already exists (e.g., when this is not the first
        time using this db), do nothing.

        :return: Whether the table now exists.
        :rtype: bool
        """
        sql = """
            CREATE TABLE IF NOT EXISTS event(
                event_id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                working INTEGER NOT NULL
            );
        """
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except sqlite3.OperationalError:
            self.connection.rollback()
            return False
        return True

    def _ensure_time_pairs(self) -> bool:
        """
        Ensure that all time blocks have a start and an end

        Given our means of tracking events and the fickle nature of
        our users, we cannot trust that all start events will have
        corresponding stop events. If the user logs a start on Mon,
        for example, but forgets to log a stop, or works through the
        night until Tue, our pairs might become unpaired.
        This method attempts to correct these types of logging errors
        by checking the most recent logged event. If it occured today,
        do nothing. If it occured yesterday and is not a stop, then add
        a stop at the end of that day. If the latter occurs and the date
        was yesterday, assume the user worked overnight and helpfully
        add a start event at midnight today.

        :return: Whether the db is now in a correct state.
        :rtype: bool
        """
        sql = """
            SELECT timestamp, working
            FROM event
            ORDER BY timestamp DESC LIMIT 1;
        """
        row = self.cursor.execute(sql).fetchone()

        if row is None or row["working"] == 0:
            # No events in db, or the previous time block was logged
            # as ended. No extra work needed.
            return True

        last_timestamp = datetime.fromisoformat(row["timestamp"])
        last_date = last_timestamp.date()
        now = util.now()
        current_date = now.date()
        if current_date == last_date:
            # No need to worry about unfinished time pairs today, as
            # will be handled either by the user or by us the next time
            # we connect to the db.
            return True

        # The latest event is on a day prior to today, and it is an
        # unfinished time pair (i.e., a start event was logged but no
        # corresponding stop event was logged). We have to assume that
        # work ended some time that day. Our best guess is at
        # 11:59:59PM. Here we transparently log a stop event at that
        # time.
        try:
            end_day_timestamp = datetime(
                year=last_date.year,
                month=last_date.month,
                day=last_date.day,
                hour=23,
                minute=59,
                second=59,
            ).isoformat()
            end_day_working = 0
            sql = """
                INSERT INTO event
                (timestamp, working)
                VALUES
                (?, ?);
            """
            self.cursor.execute(sql, (end_day_timestamp, end_day_working))
            self.connection.commit()
        except sqlite3.OperationalError:
            self.connection.rollback()
            return False

        # On the other hand, possibly a stop event was purposely not
        # logged (e.g., user is working the night shift from one day to
        # the next). If this most recent event occured more
        # than a day ago, we do not assume that is the case, because
        # no one works continuously for more than a day. If the event
        # was only yesterday, however, assume that the user is still
        # working.
        time_difference = current_date - last_date
        if time_difference.days > 1:
            return True

        try:
            start_day_timestamp = datetime(
                year=current_date.year,
                month=current_date.month,
                day=current_date.day,
                hour=0,
                minute=0,
                second=0,
            ).isoformat()
            start_day_working = 1
            sql = """
                INSERT INTO event
                (timestamp, working)
                VALUES
                (?, ?);
            """
            self.cursor.execute(sql, (start_day_timestamp, start_day_working))
            self.connection.commit()
        except sqlite3.OperationalError:
            self.connection.rollback()
            return False

        # Finally, all discrepancies should by now be addressed.
        return True

    def close(self) -> None:
        """
        Close the connection to the database.
        """
        self.connection.close()
        self.connection = None
        self.cursor = None

    def get_daily_events(self, dt: datetime) -> list:
        """
        Collect all events logged on the given date

        :param: dt: The date/time whose events are to be retrieved.
        :type dt: :class:`datetime`

        :return: A list of dicts, each containing keys 'timestamp' and 'working'.
        :rtype: list[dict[str, str]]
        """
        # Convert the given date to a string for db lookup. Add '%'
        # to the end to match all events on that date, no matter at what
        # time they occured.
        date = dt.date().isoformat() + "%"
        sql = """
            SELECT timestamp, working
            FROM event
            WHERE timestamp LIKE ?
            ORDER BY timestamp
            ;
        """
        rows = self.cursor.execute(sql, (date,))

        # Convert the data returned into useful Python types, rather
        # than simple str and int.
        cleaned_rows = []
        for row in rows.fetchall():
            # Convert text timestamp to a datetime object.
            cleaned_timestamp = datetime.fromisoformat(row["timestamp"])
            # Convert int to bool.
            cleaned_working = True if row["working"] == 1 else False
            cleaned_row = {
                "timestamp": cleaned_timestamp,
                "working": cleaned_working,
            }
            cleaned_rows.append(cleaned_row)
        return cleaned_rows

    def get_weekly_events(self, dt: datetime) -> list:
        """
        Collect all events logged on the given week

        :param dt: A date/time that falls within the week whose events
            are to be retrieved.
        :type dt: :class:`datetime`

        :return: a list of lists, possibly empty, one for each day of
            the week. Non-empty elements contain dicts equivalent to
            those returned by `.get_daily_events`.
        :rtype: list[list]
        """
        # Determine which day of the week was given (0-6).
        weekday = dt.weekday()
        # Use the above to calculate the date of the first day of the
        # week.
        start_of_week = dt - timedelta(days=weekday)

        DAYS_PER_WEEK = 7
        results = []
        for i in range(DAYS_PER_WEEK):
            # Shift the day forward by `i` (starting at 0).
            day_shift = timedelta(days=i)
            daily_events = self.get_daily_events(start_of_week + day_shift)
            results.append(daily_events)
        return results

    def log_event(self, dt: datetime, working: bool) -> bool:
        """
        Log a work event

        :param dt: The time at which the event is to be logged.
        :type dt: :class:`datetime`
        :param working: Whether work started (True) or finished (False)
            at that time.
        :type working: bool

        :return: Whether the event was successfully logged.
        :rtype: bool
        """
        # Convert the time to a string for the db.
        time = dt.isoformat()
        # Convert the bool to an int for the db.
        working_code = 1 if working else 0
        sql = """
            INSERT INTO event
            (timestamp, working)
            VALUES
            (?, ?);
        """
        try:
            self.cursor.execute(sql, (time, working_code))
            self.connection.commit()
        except sqlite3.OperationalError:
            self.connection.rollback()
            return False
        return True
