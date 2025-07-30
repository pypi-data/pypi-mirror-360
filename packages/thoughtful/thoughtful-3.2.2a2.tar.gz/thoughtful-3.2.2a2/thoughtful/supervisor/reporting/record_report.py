from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from thoughtful.supervisor.reporting.record import Record
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.reporting.step_report import StepReport
from thoughtful.supervisor.reporting.timed_report import TimedReport


@dataclass
class RecordReport(TimedReport):
    step_id: str
    """
    str: The ID of the step.
    """

    status: Status
    """
    Status: The status of the step.
    """

    record: Record
    """
    Record: The record that was processed by the step.
    """

    @classmethod
    def from_step_report(cls, step_report: StepReport, record: Record) -> RecordReport:
        return cls(
            start_time=step_report.start_time,
            end_time=step_report.end_time,
            step_id=step_report.step_id,
            status=step_report.status,
            record=record,
        )

    def __json__(self) -> Dict[str, Any]:
        return {
            **super().__json__(),
            "step_id": self.step_id,
            "step_status": self.status.value,
            "record": self.record.__json__(),
        }
