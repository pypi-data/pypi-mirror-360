"""
This module holds the logic for the runtime storage and generation of the
run report. It contains metadata about the two main entities in the run report:
the run as a whole and its children, the steps.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from thoughtful.__version__ import __version__
from thoughtful.supervisor.reporting.record_report import RecordReport
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.reporting.step_report import StepReport
from thoughtful.supervisor.reporting.timed_report import TimedReport
from thoughtful.supervisor.utilities.json import JSONEncoder


@dataclass
class Report(TimedReport):
    """
    A report is a representation of a run's execution, and it includes metadata
    about the run, a list of the steps that were executed, and records that
    were processed in each step (if any). There will only be one report per run.
    """

    supervisor_version = str(__version__)
    """
    str: The version of the supervisor that generated the report.
    """

    workflow: List[Union[StepReport, RecordReport]] = field(default_factory=list)
    """
    List[StepReport]: The list of steps that were executed.
    """

    status: Optional[Status] = None
    """
    Status, optional: The status of the run.
    """

    status_message: Optional[str] = None
    """
    Status, optional: The status of the run.
    """

    def __json__(self) -> Dict[str, Any]:
        return {
            **super().__json__(),
            "supervisor_version": self.supervisor_version,
            "workflow": [step.__json__() for step in self.workflow],
            "status": self.status.value,
            "status_message": self.status_message,
        }

    def write(self, filename: Union[str, pathlib.Path]) -> None:
        """
        Write the report as a JSON object to a file.

        Args:
            filename: Where to write the file.
        """
        path = (
            filename if isinstance(filename, pathlib.Path) else pathlib.Path(filename)
        )

        with path.open("w") as out:
            report_dict = self.__json__()
            json.dump(report_dict, out, cls=JSONEncoder)
