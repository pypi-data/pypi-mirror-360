from __future__ import annotations

import datetime
import math
from dataclasses import dataclass
from typing import Any, Dict, Optional

import isodate


@dataclass
class TimedReport:
    """
    Jsonable report with start time, optional end time, and optional duration
    """

    start_time: datetime.datetime
    """
    datetime.datetime: The start time of the step.
    """

    end_time: Optional[datetime.datetime]
    """
    datetime.datetime: The end time of the step.
    """

    @property
    def duration(self) -> Optional[datetime.timedelta]:
        """
        datetime.timedelta: The duration of the step.
        """
        return (self.end_time - self.start_time) if self.end_time else None

    @property
    def duration_isoformat(self) -> Optional[str]:
        # Adding this because self.duration == 0 would evaluate false
        if self.duration is None:
            return None
        return isodate.duration_isoformat(self.duration)

    @property
    def duration_in_milliseconds(self) -> Optional[int]:
        # Adding this because self.duration == 0 would evaluate false
        if self.duration is None:
            return None
        return math.ceil(self.duration.total_seconds() * 1000)

    def __json__(self) -> Dict[str, Any]:
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration_isoformat,
            "duration_in_ms": self.duration_in_milliseconds,
        }
