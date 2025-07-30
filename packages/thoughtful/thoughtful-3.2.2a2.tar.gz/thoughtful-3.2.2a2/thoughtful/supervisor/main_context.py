"""
This module contains the code for the MainContext class. This class is
a context manager that supervises the execution of the main body of the process.

On entrance, it will verify the process manifest.

Upon exit, it will convert the step report into the run report. It will also
evaluate the ultimate status of the process—success if no exceptions were
raised, failure otherwise.

Without this context, the output manifest and run report would not be
generated at the end of the process.
"""

from __future__ import annotations

import base64
import datetime
import logging
import os
import pathlib
import warnings
from types import TracebackType
from typing import Callable, Optional, Type, Union
from urllib.parse import urlparse

import boto3
from opentelemetry import trace
from t_vault import bw_get_item

from thoughtful.supervisor.event_bus import ArtifactsUploadedEvent, EventBus
from thoughtful.supervisor.event_bus import NewManifestEvent, RunStatusChangeEvent
from thoughtful.supervisor.manifest import Manifest
from thoughtful.supervisor.reporting.report_builder import ReportBuilder
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.utilities.tracing_config import initialize_tracing

logger = logging.getLogger(__name__)


class MainContext:
    """
    Supervises an entire digital worker run and generates a work report
    and drift report for the run from the digital worker's manifest.

    You can optionally specify a callback function that will be run when
    this context is finished via the `callback` param in the constructor. A
    callback is a function that is invoked with two parameters: the
    current context (as the `MainContext` instance) and the `Report`
    generated from this digital worker's run.

    For example:

    .. code-block:: python

        def print_work_report(
            ctx: MainContext,
            work_report: Report
        ):
            print(work_report.__json__())

        def main()
            # ...

        with supervise(callback=print_work_report):
            main()
    """

    def __init__(
        self,
        report_builder: ReportBuilder,
        manifest: Union[Manifest, str, pathlib.Path],
        output_dir: Union[str, pathlib.Path],
        event_bus: EventBus,
        upload_uri: Optional[str] = None,
        callback: Optional[Callable] = None,
        is_robocorp_multistep_run: bool = False,
        otlp_config: Optional[dict[str, Union[str, dict[str, str]]]] = None,
    ):
        """
        Args:
            report_builder (ReportBuilder): A ReportBuilder object that will
                receive the step reports and provide the run report.
                messages and logs throughout the process execution.
            manifest (str, Path): A pathlike object that points to the manifest
                file for the process.
            output_dir (str, Path): A pathlike object that points to the output
                directory for the process. This will receive the run report and
                output manifest.
            event_bus (EventBus): This instance will send events, such as
                a new manifest or a change in the run's status, to this bus.
            upload_uri (str, optional): A URI to upload the output files to.
            callback (callable, optional): a function that is invoked with three
                parameters: the current context (as the `MainContext` instance)
                and the `Report` generated from this digital worker's run.
            is_robocorp_multistep_run (bool, optional): A flag to indicate if this is a
                Robocorp multi-step run or not. If it is, the run status will not be
                updated when the context is entered or exited.
            otlp_config (dict, optional): Configuration for OpenTelemetry tracing.
                Should contain 'endpoint' (str) and optionally 'headers' (dict[str, str]).
        """
        self.report_builder = report_builder
        self.output_path = pathlib.Path(output_dir)
        self.upload_uri = upload_uri

        self.manifest_path = (
            manifest if isinstance(manifest, (str, pathlib.Path)) else None
        )
        self.manifest = self._parse_manifest(manifest)
        self.callback = callback
        self.event_bus = event_bus
        self.is_robocorp_multistep_run = is_robocorp_multistep_run
        self._otlp_config = otlp_config
        self._root_span_cm = None
        self._root_span = None

    @staticmethod
    def _parse_manifest(
        manifest: Union[Manifest, str, pathlib.Path],
    ) -> Optional[Manifest]:
        if isinstance(manifest, Manifest):
            return manifest
        manifest_path = pathlib.Path(manifest)
        try:
            manifest = Manifest.from_file(manifest_path)
            return manifest
        except Exception:
            logger.exception("warning: could not read manifest")
        return None

    def __enter__(self) -> MainContext:
        """
        Logic for when this context is first started. Attempts to load the
        manifest and returns itself as the context.

        Returns:
            MainContext: This instance.
        """
        if self.manifest:
            self.event_bus.emit(
                NewManifestEvent(
                    manifest=self.manifest,
                )
            )

        if not self.is_robocorp_multistep_run:
            self._stream_run_status_change(Status.RUNNING)

        if self._otlp_config and "endpoint" in self._otlp_config:
            try:
                if "headers" not in self._otlp_config:
                    password = bw_get_item("otl-dev-password")["password"]
                    auth_string = f"otel-client:{password}"
                    auth_header = (
                        f"Basic {base64.b64encode(auth_string.encode()).decode()}"
                    )
                    self._otlp_config["headers"] = {"Authorization": auth_header}

                initialize_tracing(
                    endpoint=self._otlp_config["endpoint"],
                    headers=self._otlp_config["headers"],
                    service_name=self.manifest.name,
                )
                tracer = trace.get_tracer(__name__)
                # Create a root span that will be the parent of all other spans
                self._root_span_cm = tracer.start_as_current_span(
                    name=self.manifest.name,
                    kind=trace.SpanKind.SERVER,  # Mark as a server span to indicate it's the root
                    attributes={
                        "process.title": (self.manifest.name),
                        "deployment.environment.name": (
                            "PRODUCTION"
                            if os.environ.get("THOUGHTFUL_PRODUCTION")
                            else "DEVELOPMENT"
                        ),
                    },
                    end_on_exit=False,
                )
                self._root_span = self._root_span_cm.__enter__()
            except ValueError as e:
                logger.error("Failed to initialize tracing: %s", str(e))
                # Continue without tracing
                self._root_span_cm = None
                self._root_span = None

        return self

    def set_run_status(self, status: Union[Status, str], message: str = None) -> None:
        """
        Sets the run status of the process. This is the final status of the
        process, and will be used to determine the status of the run report.

        Args:
            status (Union[Status, str]): The status to set.
            message (str): The message for the status. Required. The use of None is deprecated.
        """
        if message is not None and len(message) > 125:
            warnings.warn(
                "Status Messages greater than 125 characters will be truncated in Empower "
            )
        # TODO: Next major version increase, make this argument required
        if message is None or not message.strip():
            warnings.warn(
                message="set_run_status missing message argument. This will become required in a future release.",
                category=DeprecationWarning,
                stacklevel=2,
            )

        self.report_builder.set_run_status(status, message)
        self._stream_run_status_change(status, message)

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
        if exc_type:
            self.report_builder.run_had_exception = True
        work_report = self.report_builder.to_report()

        if not self.is_robocorp_multistep_run:
            self._stream_run_status_change(
                work_report.status, work_report.status_message
            )

        # Create the output directory if it doesn't already exist
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Write the work report
        work_report_path = self._safe_report_path(file_prefix="run-report")
        work_report.write(work_report_path)

        # Write the manifest back out as a JSON file
        if self.manifest:
            manifest_json_path = self.output_path / "manifest.json"
            self.manifest.write_to_json_file(manifest_json_path)

        # Run the user-defined callback
        if self.callback:
            self.callback(self, work_report)

        # Upload output files to S3
        if self.upload_uri:
            try:
                self._upload_output_files_to_s3(self.upload_uri)
            except Exception:
                logger.exception("Failed to upload output files to S3")
        elif os.environ.get("ROBOCORP_HOME") is None:
            logger.warning(
                "SUPERVISOR_ARTIFACT_UPLOAD_URI is not set. Artifacts"
                " will not be uploaded to S3."
            )

        # Clean up the root tracing span if it was started
        if self._otlp_config and "endpoint" in self._otlp_config:
            try:
                # Set final status based on whether there was an exception
                if exc_type:
                    self._root_span.set_status(trace.Status(trace.StatusCode.ERROR))
                    if exc_val:
                        self._root_span.record_exception(exc_val)
                else:
                    self._root_span.set_status(trace.Status(trace.StatusCode.OK))
                # End the span and exit the context manager
                self._root_span.end()
                self._root_span_cm.__exit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                logger.error(f"Error closing root span: {e}")

        return False

    def _stream_run_status_change(
        self, status: Status, status_message: str = None
    ) -> None:
        """
        Post a status change to the stream callback if it exists.
        """
        self.event_bus.emit(
            RunStatusChangeEvent(status=status, status_message=status_message)
        )

    def _upload_output_files_to_s3(self, upload_uri: str) -> None:
        """
        It uploads all files in the output directory to S3. It requires the
        environment variable `SUPERVISOR_ARTIFACT_UPLOAD_URI` to be set with
        the S3 URI to upload the files to.

        Args:
            upload_uri (str): The S3 URI to upload the files to.
        """
        s3_client = boto3.client("s3")
        parsed_upload_uri = urlparse(upload_uri.strip())
        bucket = parsed_upload_uri.hostname
        path = parsed_upload_uri.path.strip("/")

        for file in self.output_path.glob("*"):
            try:
                if file.is_file():
                    obj = f"{path}/{file.name}" if path else file.name
                    s3_client.upload_file(str(file), bucket, obj)
            except Exception:
                logger.exception(f"Failed to upload {file} to S3")
        self.event_bus.emit(ArtifactsUploadedEvent(output_uri=upload_uri))

    def _safe_report_path(self, file_prefix: str) -> pathlib.Path:
        """
        A ``pathlib.Path`` instance that points to a new work report writable
        location that is safe across all OSes.

        Returns:
            pathlib.Path: The path to the new report to be written.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H%M%S"
        )
        filename = f"{file_prefix}-{timestamp}.json"

        # Remove any characters from the timestamp that OSes don't like
        invalid_chars = [":", "*", "?", '"', "<", ">" "|", "'"]
        for char in invalid_chars:
            filename = filename.replace(char, "_")

        return self.output_path / filename
