from __future__ import annotations

import json
import logging
from typing import Optional

import requests

from thoughtful.supervisor.event_bus import ArtifactsUploadedEvent, Event
from thoughtful.supervisor.event_bus import NewManifestEvent, RunStatusChangeEvent
from thoughtful.supervisor.event_bus import StepReportChangeEvent
from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.streaming.jwt_auth import JWTAuth
from thoughtful.supervisor.streaming.payloads import ArtifactsUploadedPayload
from thoughtful.supervisor.streaming.payloads import BotManifestPayload, Payload
from thoughtful.supervisor.streaming.payloads import RunStatusChangePayload
from thoughtful.supervisor.streaming.payloads import StepReportPayload
from thoughtful.supervisor.streaming.token import Token
from thoughtful.supervisor.utilities.json import JSONEncoder

logger = logging.getLogger(__name__)

POST_TIMEOUT_SECONDS = 10


class Streamer(requests.Session):
    """
    Provides run status updates to a third party client (eg, Fabric/Empower)
    by posting requests to its callback URL.
    """

    def __init__(
        self,
        run_id: str,
        callback_url: str,
        auth: JWTAuth,
    ):
        super().__init__()
        self.run_id = run_id
        self.callback_url = callback_url
        self.auth: JWTAuth = auth

    @classmethod
    def from_encoded_tokens(
        cls,
        run_id: str,
        callback_url: str,
        access_token: str,
        refresh_token: str,
        refresh_url: str,
    ) -> Streamer:
        """
        Convenience constructor for creating an instance from the string
        (encoded) JWT tokens.
        """
        logger.info(
            f"JWT Auth: {access_token}, {refresh_token}, {refresh_url}, {callback_url}"
        )
        new_auth = JWTAuth(
            access_token=Token(access_token) if access_token else None,
            refresh_token=Token(refresh_token) if refresh_token else None,
            refresh_url=refresh_url,
        )
        return cls(
            run_id=run_id,
            callback_url=callback_url,
            auth=new_auth,
        )

    def handle_event(self, event: Event):
        logger.info(f"Handling event: {event}")
        payload: Optional[Payload] = None
        if isinstance(event, StepReportChangeEvent):
            logger.info("Handling step report change event for %s", event.step_report)
            payload = StepReportPayload(
                step_report=event.step_report,
                run_id=self.run_id,
            )
        elif isinstance(event, NewManifestEvent):
            logger.info("Handling new manifest event for %s", event.manifest)
            payload = BotManifestPayload(
                manifest=event.manifest,
                run_id=self.run_id,
            )
        elif isinstance(event, ArtifactsUploadedEvent):
            logger.info("Handling artifacts uploaded event for %s", event.output_uri)
            payload = ArtifactsUploadedPayload(
                run_id=self.run_id,
                output_artifacts_uri=event.output_uri,
            )
        elif isinstance(event, RunStatusChangeEvent):
            logger.info("Handling run status change event for %s", event.status)
            payload = RunStatusChangePayload(
                run_id=self.run_id,
                status=event.status,
                status_message=event.status_message,
            )
        else:
            logger.warning(f"Unhandled event: {event}")

        if not payload:
            logger.warning("Could not convert event to a streamable payload")
            return
        self.post(payload=payload)

    def post(self, payload: Payload, **kwargs):
        message_json = json.loads(json.dumps(payload.__json__(), cls=JSONEncoder))

        try:
            logger.info("Posting streaming message")
            logger.info("URL: %s", self.callback_url)
            logger.info("Payload: %s", message_json)
            response = super().post(
                self.callback_url,
                json=message_json,
                timeout=POST_TIMEOUT_SECONDS,
                **kwargs,
            )
        except Exception:
            # A failed stream message shouldn't break a bot, so catch any possible
            # exception and log it
            logger.exception("Could not post step payload to endpoint")
            return

        logger.info(
            f"Received response: ({response.status_code}): {response.text}, {response.headers}"
        )

        return response


if __name__ == "__main__":
    at = "xxxxxx"
    rt = "yyyyyy"
    _id = "1"
    url = "https://YOUR_URL_ID.execute-api.us-east-1.amazonaws.com/STAGE/webhooks/users-processes-updates/jwt"
    ref_ur = (
        "https://YOUR_URL_ID.execute-api.us-east-1.amazonaws.com/STAGE/refresh-token"
    )

    callback = Streamer.from_encoded_tokens(
        run_id=_id,
        callback_url=url,
        access_token=at,
        refresh_token=rt,
        refresh_url=ref_ur,
    )
    callback.post(Status.SUCCEEDED)
