from __future__ import annotations

import logging
from dataclasses import dataclass

import requests
from requests.auth import AuthBase

from thoughtful.supervisor.streaming.token import Token

logger = logging.getLogger(__name__)

POST_TIMEOUT_SECONDS = 10


@dataclass
class JWTAuth(AuthBase):
    access_token: Token
    refresh_token: Token
    refresh_url: str

    def __call__(self, r: requests.Request) -> requests.Request:
        self.refresh()
        r.headers["Authorization"] = f"Bearer {self.access_token}"
        logger.debug(
            f"JWT auth called with token {self.access_token} and headers: {r.headers}"
        )

        return r

    def refresh(self) -> None:
        if not self.access_token.is_expired:
            return

        logger.info("Access token expired, refreshing")
        response = requests.post(
            self.refresh_url,
            json={
                "refreshToken": str(self.refresh_token),
            },
            timeout=POST_TIMEOUT_SECONDS,
        )

        if not response.ok:
            logging.warning("Could not refresh JWT token!")
            logging.warning(
                f"Received response {response.status_code}: {response.text}"
            )
            return

        logging.info("Successfully refreshed JWT token")
        new_values = response.json()
        self.access_token = Token(new_values["accessToken"])
        self.refresh_token = Token(new_values["refreshToken"])
