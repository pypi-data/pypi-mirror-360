from dataclasses import dataclass


@dataclass
class ListenKey:
    listen_key: str


@dataclass
class ListenKeys:
    listen_key: list[str]
