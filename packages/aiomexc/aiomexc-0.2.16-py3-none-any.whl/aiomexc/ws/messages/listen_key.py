from dataclasses import dataclass


@dataclass
class ListenKeyExtendedMessage:
    listen_key: str
    expires_at: int
