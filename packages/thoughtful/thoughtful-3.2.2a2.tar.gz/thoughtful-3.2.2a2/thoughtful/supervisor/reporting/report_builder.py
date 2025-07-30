"""
This module handles the actual assembly of the run report. It converts each of
the step reports into a ``StepReport`` object and then converts the run
to a ``Report`` object containing the list of ``StepReport`` objects.

It returns this ``Report`` object as the final product of the run.
"""

from __future__ import annotations

import datetime
import logging
import time
import warnings
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple, Union

from thoughtful.supervisor.manifest import StepId
from thoughtful.supervisor.reporting.record import Record
from thoughtful.supervisor.reporting.record_report import RecordReport
from thoughtful.supervisor.reporting.report import Report
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.reporting.step_report import StepReport
from thoughtful.supervisor.reporting.timer import Timer

logger = logging.getLogger(__name__)


@dataclass
class RecordAccumulator:
    """
    Manages a list of records that are being processed by a step.
    """

    records_by_id: Dict[RecordId, Record] = field(default_factory=OrderedDict)

    def upsert(self, record: Record):
        """Insert a new Record, or update the record if it already exists."""
        self.records_by_id[record.record_id] = record

    def exists(self, _id: RecordId) -> bool:
        return _id in self.records_by_id.keys()

    def soft_update(self, record: Record):
        """
        Update a record *only* if it doesn't exist *or* the current status is
        RUNNING, otherwise do nothing.
        """
        if (
            self.exists(record.record_id)
            and self.records_by_id[record.record_id].status != Status.RUNNING
        ):
            return
        self.upsert(record)

    def to_reports(self, base_step_report: StepReport) -> List[RecordReport]:
        return [
            RecordReport.from_step_report(base_step_report, record)
            for record in self.records_by_id.values()
        ]

    def __iter__(self) -> Iterable[Record]:
        return iter(self.records_by_id.values())


@dataclass
class StepReportBuilder:
    """
    Builds a step report during the lifecycle of a step's execution. Once a step
    has finished executing, you can call ``_to_report`` to get the final
    ``StepReport``.
    """

    step_id: str
    """
    str: The ID of the step.
    """

    start_time: datetime.datetime
    """
    datetime.datetime: The start time of the step.
    """

    status: Status
    """
    Status: The status of the step.
    """

    end_time: Optional[datetime.datetime] = None
    """
    datetime.datetime: The end time of the step.
    """

    _record_accumulator: RecordAccumulator = field(default_factory=RecordAccumulator)
    """
    RecordAccumulator: Holds records that were processed by this step.
    """

    def update_from(self, other: StepReportBuilder) -> None:
        """
        Update a new ``StepReportBuilder`` from an existing ``StepReportBuilder``.

        Args:
            other (StepReportBuilder): The step report builder to update from.
        """
        # this bypasses StepReports created by decorator method (ie. do not have
        # records)
        other_records_by_id = {r.record_id: r for r in other.records}
        for record in self.records:
            if record.record_id in other_records_by_id:
                logger.warning(
                    f"Duplicate record '{record.record_id}' found in step '{self.step_id}'"
                )

        self.end_time = other.end_time
        self.status = other.status
        for other_record in other.records:
            self._record_accumulator.upsert(other_record)

    def to_reports(self) -> List[Union[StepReport, RecordReport]]:
        step_report = self._to_report()
        record_reports: List[
            Union[StepReport, RecordReport]
        ] = self._record_accumulator.to_reports(step_report)
        return record_reports + [step_report]

    def set_record_status(
        self,
        record_id: RecordId,
        status: Status,
        message: Optional[str] = None,
        metadata: Optional[dict] = None,
        is_soft_update: bool = False,
    ):
        message = message or ""
        metadata = metadata or {}
        new_record = Record(record_id, status, message, metadata)
        if is_soft_update:
            self._record_accumulator.soft_update(new_record)
        else:
            self._record_accumulator.upsert(new_record)

    @property
    def records(self) -> Tuple[Record]:
        return tuple(self._record_accumulator)

    def _to_report(self) -> StepReport:
        """
        An easily "jsonable" final report on this step's execution.

        Returns:
            StepReport: A final report on this step's execution.
        """

        # Build the report
        return StepReport(
            step_id=self.step_id,
            status=self.status,
            start_time=self.start_time,
            end_time=self.end_time,
        )


RecordId = str
StepId = str


@dataclass
class ReportBuilder:
    """
    A work report builder that creates a new work report as a digital worker
    is executed.
    """

    timer: Timer = field(default_factory=Timer)
    """
    Timer: The timer used to time the execution of the workflow.
    """

    _step_report_builders: List[StepReportBuilder] = field(default_factory=list)
    """
    List[StepReportBuilder]: The list of step reports.
    """

    timer_start: float = time.perf_counter()
    """
    float: The start time of the workflow.
    """

    status: Optional[Status] = None
    """
    Status, optional: The status of the run.
    """

    status_message: Optional[str] = None
    """
    status_message, optional: Adds a message to the run status.
    """

    # These steps will be overridden with the specified status when the
    # `Report` is written
    _step_statuses_to_override: Dict[StepId, Status] = field(default_factory=dict)
    """
    Dict[StepId, Status]: The statuses to override for each step
    """
    _records_to_override: Dict[StepId, Dict[RecordId, Record]] = field(
        default_factory=lambda: defaultdict(dict)
    )
    """
    Dict[StepId, Dict[RecordId, Status]]: The statuses to override for each
    record
    """

    run_had_exception: bool = False
    """
    Boolean value to indicate if the run terminated on an exception.
    """

    _run_status_override: Optional[Status] = None
    """
    Override the status of the run to be in the status of `status`.
    """

    def __post_init__(self):
        self.timer.start()

    def fail_step(self, step_id: str) -> None:
        """
        Override a step to be in the `StepStatus.ERROR` state. Note: this
        overrides every step with this ID, so if the step ran multiple times
        in the workflow, they will all be marked as failed.

        Args:
            step_id (str): The step id to override.
        """
        self.set_step_status(step_id=step_id, status=Status.FAILED)

    def set_step_status(self, step_id: str, status: Union[Status, str]) -> None:
        """
        Override a step to be in the status of `status`. Note: this
        overrides every step with this ID, so if the step ran multiple times
        in the workflow, they will all be marked as this `status`.

        Args:
            step_id (str): The step id to override.
            status (Status | str): The status to override the step to.
        """
        # Convert the status to the correct type if necessary
        safe_status = Status(status)
        self._step_statuses_to_override[step_id] = safe_status

    def find_index(self, step_report_builder: StepReportBuilder) -> Union[int, None]:
        """
        Find the index of the step_report_builder in the ReportBuilder's _step_report_builders
        that matches the incoming steps and does not already have Records attached to it.
        """
        index = next(
            (
                index
                for index, step in enumerate(self._step_report_builders)
                if step.step_id == step_report_builder.step_id
            ),
            None,
        )
        return index

    def add_step_report(self, step_report_builder: StepReportBuilder) -> None:
        """
        Add a StepReport if it doesn't exist already. If it does exist, update
        the existing StepReport with the new StepReport's records.
        """
        index = self.find_index(step_report_builder)
        if index is not None or index == 0:
            self._step_report_builders[index].update_from(step_report_builder)
        else:
            self._step_report_builders.append(step_report_builder)

    def set_record_status(
        self,
        step_id: str,
        record_id: str,
        status: Union[Status, str],
        message: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Override a record to be in the status of `status`. Note: this
        overrides every step with this step ID and this record ID, so if the
        step ran multiple times in the workflow, they will all be marked as
        this `status`.

        Args:
            step_id (str): The step id a specific step that contains this record
            record_id (str): The id of the record to override.
            status (Status | str): The status to override the record to.
        """
        # Convert the status to the correct type if necessary
        if type(step_id) != str:
            raise TypeError("step_id must be a string")
        if type(record_id) != str:
            raise TypeError("record_id must be a string")
        message = message or ""
        metadata = metadata or {}
        safe_status = Status(status)
        self._records_to_override[step_id][record_id] = Record(
            record_id=record_id, status=safe_status, message=message, metadata=metadata
        )

    def set_run_status(self, status: Union[Status, str], message: str = None) -> None:
        """
        Manually set the status of the bot run. If not set, the run
        status will be determined automatically

        Args:
            status (Union[Status, str]): The status to override the run to.
            message (str): The message for the status. Required. The use of None is deprecated.
        """

        # TODO: Next major version increase, make this argument required
        if message is None or not message.strip():
            warnings.warn(
                message="set_run_status missing message argument. This will become required in a future release.",
                category=DeprecationWarning,
                stacklevel=2,
            )

        # Convert the status to the correct type if necessary
        safe_status = Status(status)
        self._run_status_override = safe_status
        self.status_message = message

    def to_report(self) -> Report:
        """
        Convert supervisor workflow to work report. It is here that we
        convert the entire workflow to a list of ``StepReport`` objects.
        After which, we pass over the entire list overriding the record
        and step statuses according to the ``_step_statuses_to_override``
        and ``_records_to_override`` dictionaries.

        Returns:
            Report: The finalized work report.
        """
        timed = self.timer.end()

        for step_builder in self._step_report_builders:
            # Override the step status if requested
            if step_builder.step_id in self._step_statuses_to_override:
                new_status = self._step_statuses_to_override[step_builder.step_id]
                step_builder.status = new_status
            # Override any of the step's record statuses if requested
            if step_builder.step_id in self._records_to_override:
                records = self._records_to_override[step_builder.step_id]
                # NOTE: need to make change here from status - ReportBuilder saving
                # Records instead of just status - in self._records_to_override
                for record_id, record in records.items():
                    step_builder.set_record_status(
                        record_id, record.status, record.message, record.metadata
                    )

        # Merge all the step reports together
        final_workflow = [
            report
            for step in self._step_report_builders
            for report in step.to_reports()
        ]

        # Set the run status
        self.status = Status.FAILED if self.run_had_exception else Status.SUCCEEDED
        if self._run_status_override is not None:
            self.status = self._run_status_override

        return Report(
            start_time=timed.start,
            end_time=timed.end,
            workflow=final_workflow,
            status=self.status,
            status_message=self.status_message,
        )
