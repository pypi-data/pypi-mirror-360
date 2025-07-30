"""
This module handles one of the primary functions of Supervisor, which is to
track the timing of steps, as well as the duration of the entire run.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class TimerResult:
    """
    The start time, end time, and duration of running a timer.
    """

    start: datetime.datetime
    """
    datetime.datetime: The start time of the timer.
    """

    end: datetime.datetime
    """
    datetime.datetime: The end time of the timer.
    """

    duration: datetime.timedelta
    """
    datetime.timedelta: The duration of the timer.
    """


@dataclass
class Timer:
    """
    Times an action by calling `start()` and `end()`.
    """

    start_time: Optional[datetime.datetime] = None
    """
    datetime.datetime, optional: The start time of the timer.
    """

    end_time: Optional[datetime.datetime] = None
    """
    datetime.datetime, optional: The end time of the timer.
    """

    duration: Optional[datetime.timedelta] = None
    """
    datetime.timedelta, optional: The duration of the timer.
    """

    def start(self) -> datetime.datetime:
        """
        Starts the timer.
        """
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        return self.start_time

    def end(self) -> TimerResult:
        """
        Ends the timer and records the duration.

        Returns:
            TimerResult: How long the timer ran and when it started.
        """
        self.end_time = datetime.datetime.now(datetime.timezone.utc)
        self.duration = self.end_time - self.start_time

        return TimerResult(
            start=self.start_time, end=self.end_time, duration=self.duration
        )
