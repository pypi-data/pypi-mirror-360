import time
from dataclasses import dataclass

from aiomexc.session.base import Credentials


@dataclass
class WSCredentials(Credentials):
    listen_key: str | None = None
    expires_at: int | None = None

    def is_expired(self) -> bool:
        if self.expires_at is None or self.listen_key is None:
            return True

        return time.time() > self.expires_at

    def update(self, listen_key: str) -> None:
        self.listen_key = listen_key
        self.expires_at = int(time.time() + 3600)
