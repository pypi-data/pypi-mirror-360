"""
Defines json payloads to be delivered to the streaming endpoint
"""
import datetime
from dataclasses import dataclass

import thoughtful
from thoughtful.supervisor.manifest import Manifest
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.reporting.step_report import StepReport
from thoughtful.supervisor.streaming.action import Action


@dataclass
class Payload:
    """
    Base payload format for all streaming messages.
    """

    run_id: str
    action: Action
    client: str = "supervisor"
    version: str = thoughtful.__version__

    def __json__(self) -> dict:
        return {
            "run_id": self.run_id,
            "client": self.client,
            "version": self.version,
            "action": self.action.value,
            "payload": {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            },
        }


class StepReportPayload(Payload):
    """
    Payload for sending a step report action.
    """

    def __init__(self, step_report: StepReport, run_id: str):
        super().__init__(run_id=run_id, action=Action.STEP_REPORT)
        self.step_report = step_report

    def __json__(self) -> dict:
        _json = super().__json__()
        _json["payload"]["step_report"] = self.step_report.__json__()
        return _json


class BotManifestPayload(Payload):
    """
    Payload for sending the manifest.
    """

    def __init__(self, manifest: Manifest, run_id: str):
        self.manifest = manifest
        super().__init__(run_id=run_id, action=Action.BOT_MANIFEST)

    def __json__(self) -> dict:
        _json = super().__json__()
        _json["payload"]["bot_manifest"] = self.manifest.__json__()
        return _json


class ArtifactsUploadedPayload(Payload):
    """
    Payload for notifying the stream consumer that artifacts have been uploaded
    to S3.
    """

    def __init__(self, run_id: str, output_artifacts_uri: str):
        self.output_artifacts_uri = output_artifacts_uri
        super().__init__(run_id, action=Action.ARTIFACTS_UPLOADED)

    def __json__(self) -> dict:
        _json = super().__json__()
        _json["payload"]["output_artifacts_uri"] = self.output_artifacts_uri
        return _json


class RunStatusChangePayload(Payload):
    """
    Payload for notifying the stream consumer that a bot's status has changed
    """

    def __init__(self, run_id: str, status: Status, status_message: str = None):
        self.status = status
        self.status_message = status_message
        super().__init__(run_id, action=Action.STATUS_CHANGE)

    def __json__(self) -> dict:
        _json = super().__json__()
        _json["payload"]["status"] = self.to_fabric_process_status(self.status)
        _json["payload"]["status_message"] = self.status_message
        return _json

    @staticmethod
    def to_fabric_process_status(status: Status) -> str:
        if status == Status.RUNNING:
            return "processing"
        elif status == Status.FAILED:
            return "failed"
        elif status == Status.SUCCEEDED:
            return "finished"
        elif status == Status.WARNING:
            return "warning"
        else:
            raise ValueError(f"Unknown status: {status}")
