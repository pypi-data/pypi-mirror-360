import json
from pathlib import Path
from dataclasses import dataclass

from aiomexc import Credentials


CONFIG_DIR = Path.home() / ".config" / "aiomexc"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"


@dataclass
class CliCredentials(Credentials):
    name: str
    socks5_proxy: str | None = None
    is_active: bool = False

    def __post_init__(self):
        self.name = self.name.lower()


class CredentialsManager:
    def __init__(self):
        self._credentials = self._load_credentials()

    def _load_credentials(self) -> dict[str, CliCredentials]:
        if not CREDENTIALS_FILE.exists():
            return {}

        with Path(CREDENTIALS_FILE).open() as f:
            data = json.load(f)
            return {
                name: CliCredentials(
                    name=name,
                    access_key=credentials["access_key"],
                    secret_key=credentials["secret_key"],
                    socks5_proxy=credentials.get("socks5_proxy"),
                    is_active=credentials.get("is_active", False),
                )
                for name, credentials in data.items()
            }

    def _dump_credentials(self) -> dict[str, dict]:
        return {
            name: {
                "access_key": credentials.access_key,
                "secret_key": credentials.secret_key,
                "socks5_proxy": credentials.socks5_proxy,
                "is_active": credentials.is_active,
            }
            for name, credentials in self._credentials.items()
        }

    def _save_credentials(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with Path(CREDENTIALS_FILE).open("w") as f:
            json.dump(self._dump_credentials(), f, indent=2)

    def get_active_credentials(self) -> CliCredentials | None:
        """
        Get the active credentials. If no active credentials are set, return the first
        credentials in the list.
        """
        # First try to find credentials with is_active=True
        for credentials in self._credentials.values():
            if credentials.is_active:
                return credentials

        # If no active credentials found, return the first one
        if not self._credentials:
            return None

        return next(iter(self._credentials.values()))

    def list_credentials(self) -> list[CliCredentials]:
        return list(self._credentials.values())

    def save_credentials(self, credentials: CliCredentials) -> None:
        self._credentials[credentials.name] = credentials
        self._save_credentials()

    def delete_credentials(self, name: str) -> None:
        credentials = self._credentials.pop(name, None)
        if credentials is not None:
            self._save_credentials()

    def set_active_credentials(self, credentials: CliCredentials) -> None:
        # Set all credentials to inactive first
        for cred in self._credentials.values():
            cred.is_active = False

        # Set the specified credentials as active
        credentials.is_active = True
        self._credentials[credentials.name] = credentials
        self._save_credentials()
