from __future__ import annotations

import datetime

import jwt


class Token:
    """A JWT token."""

    def __init__(self, encoded_value: str, algorithm="HS256"):
        self.encoded_value = encoded_value

        decoded_values = jwt.decode(
            jwt=self.encoded_value,
            algorithms=[algorithm],
            options={"verify_signature": False},
        )
        self.expires_at = datetime.datetime.fromtimestamp(
            decoded_values["exp"], tz=datetime.timezone.utc
        )
        self.issued_at = datetime.datetime.fromtimestamp(
            decoded_values["iat"], tz=datetime.timezone.utc
        )

    def __str__(self):
        return self.encoded_value

    @property
    def is_expired(self, expiry_margin: float = 0.1) -> bool:
        """
        Returns True if the token is expired or will expire soon.

        expiry_margin: A float between 0 and 1. For example, if set to 0.1, the
            token will be considered expired if it will expire within 10% of its
            total lifetime.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        if now >= self.expires_at:
            return True

        time_to_expire_seconds = (self.expires_at - self.issued_at).total_seconds()
        expiry_threshold = time_to_expire_seconds * expiry_margin
        will_expire_soon = abs(time_to_expire_seconds) <= expiry_threshold
        if will_expire_soon:
            return True

        return False
