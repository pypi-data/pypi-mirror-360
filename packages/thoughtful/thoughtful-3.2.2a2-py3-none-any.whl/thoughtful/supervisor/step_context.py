"""
The step context is a context manager that is used to supervise a single step
of a digital worker. It is used in lieu of the ``@step`` decorator for
situations when you do not want to write a function for a step. For example,
it is very useful when iterating over a list of items:

.. code-block:: python

    from thoughtful.supervisor import supervise, step_scope

    def times_two(integers: list) -> None:
        return integers * 2

    def times_three(integer: int) -> None:
        return integer * 3

    def main():
        num_list = [1, 2, 3, 4, 5]

        with step_scope("1.1"):
            num_list = times_two(num_list)

        for num in num_list:
            with step_scope("1.2"):
                num = times_three(num)

    if __name__ == '__main__':
        with supervise():
            main()

Aside: There are a few scenarios where this is actually more convenient than
using the decorator on a lower level. Thanks to the fact that we can yield
the ``self`` object from a context manager, we can use this to update
attributes such as the record status, the step status, and is even a bit
cleaner when setting the record ID.
"""

from __future__ import annotations

import logging
from types import TracebackType
from typing import Callable, Optional, Type, Union

from opentelemetry import trace
from opentelemetry.trace import Span
from opentelemetry.trace import Status as TraceStatus
from opentelemetry.trace import StatusCode

from thoughtful.supervisor.event_bus import EventBus, StepReportChangeEvent
from thoughtful.supervisor.reporting.report_builder import ReportBuilder
from thoughtful.supervisor.reporting.report_builder import StepReportBuilder
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.reporting.timer import Timer

logger = logging.getLogger(__name__)


StepLifecycleCallbackType = Callable[[str], None]


class StepContext:
    """
    A context manager for a step that is running inside another step.
    This is an alternative to ``@step`` decorator when you don't want
    to write an entire function for a step.
    """

    _on_step_enter_callback: Optional[StepLifecycleCallbackType] = None
    _on_step_exit_callback: Optional[StepLifecycleCallbackType] = None

    def __init__(
        self,
        builder: ReportBuilder,
        step_id: str,
        event_bus: EventBus,
        on_context_enter: Optional[StepLifecycleCallbackType] = None,
        on_context_exit: Optional[StepLifecycleCallbackType] = None,
    ):
        """
        Args:
            builder (ReportBuilder): Where the step report will be written.
            step_id (str): The step id of this step, ie `"1.1"`
            event_bus (EventBus): The decorator will emit events, such as when
                a step report has been created or updated, to this bus.
            on_context_enter (callable, optional): A function that will be called
                when the context is entered. This is useful for setting up logging
                or other context-specific settings. The function should take the
                step_id as an argument.
            on_context_exit (callable, optional): A function that will be called
                when the context is exited. This is useful for cleaning up logging
                or other context-specific settings.
        """
        self.step_id = str(step_id)
        self.report_builder = builder
        self.timer = Timer()
        self._status_override: Optional[Status] = None
        self.event_bus = event_bus
        self.step_report_builder: StepReportBuilder
        self.on_context_enter = on_context_enter
        self.on_context_exit = on_context_exit
        self._span: Optional[Span] = None
        self._span_cm = None

    @classmethod
    def get_on_step_enter_callback(cls) -> Optional[StepLifecycleCallbackType]:
        """
        Get the callback to be called when a step is entered.

        Returns:
            Optional[StepLifecycleCallbackType]: The callback to be called when a step is entered.
        """
        return cls._on_step_enter_callback

    @classmethod
    def set_on_step_enter_callback(cls, callback: StepLifecycleCallbackType) -> None:
        """
        Set a callback to be called when a step is entered.

        Args:
            callback (StepLifecycleCallbackType): A function to be called when a step is entered.
        """
        cls._on_step_enter_callback = callback

    @classmethod
    def get_on_step_exit_callback(cls) -> Optional[StepLifecycleCallbackType]:
        """
        Get the callback to be called when a step is exited.

        Returns:
            Optional[StepLifecycleCallbackType]: The callback to be called when a step is exited.
        """
        return cls._on_step_exit_callback

    @classmethod
    def set_on_step_exit_callback(cls, callback: StepLifecycleCallbackType) -> None:
        """
        Set a callback to be called when a step is exited.

        Args:
            callback (StepLifecycleCallbackType): A function to be called when a step is exited.
        """
        cls._on_step_exit_callback = callback

    def __enter__(self):
        """
        Logic for when this context is first started.

        Returns:
            MainContext: This instance.
        """
        on_step_enter_callback = (
            self.on_context_enter or StepContext._on_step_enter_callback
        )
        if on_step_enter_callback and callable(on_step_enter_callback):
            try:
                on_step_enter_callback(self.step_id)
            except Exception as e:
                logger.error(f"Error running on_step_enter_callback: {e}")

        start_time = self.timer.start()
        self.step_report_builder = StepReportBuilder(
            step_id=self.step_id,
            start_time=start_time,
            status=Status.RUNNING,
        )

        try:
            tracer = trace.get_tracer(__name__)
            # Activate a new span as the current span (child of whatever is active)
            self._span_cm = tracer.start_as_current_span(
                name=f"step.{self.step_id}",
                attributes={"step.id": self.step_id},
                end_on_exit=False,
            )
            self._span = self._span_cm.__enter__()
        except Exception:
            # Tracing not configured or failed
            pass

        for report in self.step_report_builder.to_reports():
            new_event = StepReportChangeEvent(step_report=report)

            self.event_bus.emit(new_event)

        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """
        Runs when the context is about to close, whether caused
        by a raised Exception or now.

        Returns:
            bool: True if the parent caller should ignore the
                Exception raised before entering this function
                (if any), False otherwise.
        """
        timed_info = self.timer.end()
        if self._status_override:
            step_status = self._status_override
        else:
            step_status = Status.FAILED if exc_type else Status.SUCCEEDED

        # Update step report with finished step details
        self.step_report_builder.end_time = timed_info.end
        self.step_report_builder.status = step_status

        # End the span with proper status and attributes
        if self._span is not None:
            if self._status_override == Status.FAILED:
                self._span.set_status(TraceStatus(StatusCode.ERROR))
            elif exc_type:
                self._span.set_status(TraceStatus(StatusCode.ERROR))
                if exc_val:
                    self._span.record_exception(exc_val)
            else:
                self._span.set_status(TraceStatus(StatusCode.OK))
            self._span.end()
            # Exit the context manager to restore previous span
            self._span_cm.__exit__(exc_type, exc_val, exc_tb)

        for report in self.step_report_builder.to_reports():
            new_event = StepReportChangeEvent(step_report=report)
            self.event_bus.emit(new_event)

        self.report_builder.add_step_report(self.step_report_builder)

        on_step_exit_callback = (
            self.on_context_exit or StepContext._on_step_exit_callback
        )
        if on_step_exit_callback and callable(on_step_exit_callback):
            try:
                on_step_exit_callback(self.step_id)
            except Exception as e:
                logger.error(f"Error running on_step_exit_callback: {e}")

        return False

    def error(self) -> None:
        """
        Sets the status of this step to `Status.FAILED` in its `StepReport`.

        .. code-block:: python

            with step_scope("1.1") as s:
                ...  # do some stuff
                s.error()

        .. code-block:: json

            {
                "workflow": [
                    {
                        "step_id": "1.1",
                        "step_status": "failed"
                    }
                ]
            }
        """
        self.set_status(Status.FAILED)

    def set_status(self, status: Union[str, Status]) -> None:
        """
        Override the step context's status to be in the status of ``status``

        Args:
            status (str, Status): The status to set the step to

        .. code-block:: python

            with step_scope("1.1") as s:
                ...  # do some stuff
                s.set_status("warning")

        .. code-block:: json

            {
                "workflow": [
                    {
                        "step_id": "1.1",
                        "step_status": "warning"
                    }
                ]
            }
        """
        # Convert the status to the correct type if necessary
        safe_status = Status(status)
        self._status_override = safe_status
        if self._span is not None:
            if safe_status == Status.FAILED:
                self._span.set_status(TraceStatus(StatusCode.ERROR))
            else:
                self._span.set_status(TraceStatus(StatusCode.OK))

    def set_record_status(
        self,
        status: Union[str, Status],
        record_id: str,
        message: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Override a step context's record to be in the status of ``status``

        Args:
            status (str, Status): The status to set the record to
            record_id (str): The ID of the record
            message (str, optional): A short message to attach to the record
            metadata (dict, optional): A dictionary of metadata to attach to the
                record. These should be short, tag-like values.

        .. code-block:: python

            with step_scope("1.1") as s:
                ...  # do some stuff
                s.set_record_status("warning", "record01")

        .. code-block:: json

            {
                "workflow": [
                    {
                        "step_id": "1.1",
                        "step_status": "succeeded",
                        "record": {
                            "id": "kaleb_cool_guy",
                            "status": "warning"
                        }
                    }
                ]
            }

        """
        # Convert the status to the correct type if necessary
        if type(record_id) != str:
            raise TypeError("record_id must be a string")
        if message is not None and not type(message) == str:
            raise ValueError("Record message must be a string")
        if metadata is not None and not type(metadata) == dict:
            raise ValueError("Record metadata must be a dict")
        message = message or ""
        metadata = metadata or {}
        safe_status = Status(status)
        self.step_report_builder.set_record_status(
            record_id, safe_status, message, metadata
        )


if __name__ == "__main__":
    report_builder = ReportBuilder()

    substep = StepContext

    with substep(report_builder, 1) as s:
        print("hello world")

        with substep(report_builder, "1.1") as s2:
            print("inner step")

    print(report_builder._step_report_builders)
