from dataclasses import dataclass, field
from typing import Callable, List, Optional, Union
from venv import logger

from thoughtful.supervisor.manifest import Manifest
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.reporting.step_report import StepReport


@dataclass
class StepReportChangeEvent:
    step_report: StepReport


@dataclass
class NewManifestEvent:
    manifest: Manifest


@dataclass
class RunStatusChangeEvent:
    status: Status
    status_message: Optional[str] = None


@dataclass
class ArtifactsUploadedEvent:
    output_uri: str


Event = Union[
    StepReportChangeEvent,
    NewManifestEvent,
    RunStatusChangeEvent,
    ArtifactsUploadedEvent,
]


@dataclass
class EventBus:
    subscribers: List[Callable[[Event], None]] = field(default_factory=list)

    def subscribe(self, callback: Callable[[Event], None]):
        self.subscribers.append(callback)

    def emit(self, event: Event):
        logger.info(f"emit event: {event}")
        for subscriber in self.subscribers:
            subscriber(event)
