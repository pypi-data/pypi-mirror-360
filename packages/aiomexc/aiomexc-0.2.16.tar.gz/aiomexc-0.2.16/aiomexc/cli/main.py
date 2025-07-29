import asyncio

from pprint import pprint
from enum import StrEnum
from dataclasses import dataclass

from questionary import select, Choice, text, password, Separator

from aiomexc.client import MexcClient

from .credentials import CredentialsManager, CliCredentials
from .aiohttp_session import CliAiohttpSession


@dataclass
class MenuItem:
    """Represents a menu item with its display text and value."""

    text: str
    value: str
    is_separator: bool = False


class Action(StrEnum):
    """Available actions in the application."""

    # Main menu actions
    MAIN = "Main"
    MANAGE_KEYS = "Manage API Keys"
    METHODS = "Methods"
    EXIT = "Exit"

    # API Key management actions
    ADD = "Add new API key"
    LIST = "List saved keys"
    DELETE = "Delete API key"
    SET_ACTIVE = "Set active API key"
    BACK = "Back to main menu"

    # Method actions
    GET_ACCOUNT_INFO = "Get account info"
    GET_OPEN_ORDERS = "Get open orders"
    GET_ORDER = "Get order"


class MexcCli:
    """Main CLI application class."""

    def __init__(self):
        self.credentials_manager = CredentialsManager()
        self.mexc_client = MexcClient(session=CliAiohttpSession())
        self._setup_menus()

    def _setup_menus(self) -> None:
        """Initialize menu structures."""
        self.api_key_menu = [
            MenuItem(Action.ADD, Action.ADD),
            MenuItem("", "", is_separator=True),
            MenuItem(Action.LIST, Action.LIST),
            MenuItem("", "", is_separator=True),
            MenuItem(Action.DELETE, Action.DELETE),
            MenuItem("", "", is_separator=True),
            MenuItem(Action.SET_ACTIVE, Action.SET_ACTIVE),
            MenuItem("", "", is_separator=True),
            MenuItem(Action.BACK, Action.BACK),
        ]

        self.methods_menu = [
            MenuItem(Action.GET_ACCOUNT_INFO, Action.GET_ACCOUNT_INFO),
            MenuItem("", "", is_separator=True),
            MenuItem(Action.GET_OPEN_ORDERS, Action.GET_OPEN_ORDERS),
            MenuItem("", "", is_separator=True),
            MenuItem(Action.GET_ORDER, Action.GET_ORDER),
            MenuItem("", "", is_separator=True),
            MenuItem(Action.BACK, Action.BACK),
        ]

        self.main_menu = [
            MenuItem(Action.MANAGE_KEYS, Action.MANAGE_KEYS),
            MenuItem("", "", is_separator=True),
            MenuItem(Action.METHODS, Action.METHODS),
            MenuItem("", "", is_separator=True),
            MenuItem(Action.EXIT, Action.EXIT),
        ]

    def _get_menu_choices(self, menu: list[MenuItem]) -> list[Choice]:
        """Convert menu items to questionary choices."""
        return [
            Choice(item.text, value=item.value)
            if not item.is_separator
            else Separator()
            for item in menu
        ]

    async def _list_credentials(self) -> None:
        """List all saved credentials."""
        keys = self.credentials_manager.list_credentials()
        if not keys:
            print("No API keys saved.")
        else:
            print("\nSaved API keys:")
            for key in keys:
                print(
                    f"- {key.name} ({key.access_key}) {'[active]' if key.is_active else ''}"
                )

    async def _add_credentials(self) -> None:
        """Add new credentials."""
        name = await text("Enter a name for this API key:").ask_async()
        access_key = await text("Enter API Access Key:").ask_async()
        secret_key = await password("Enter API Secret Key:").ask_async()
        socks5_proxy = await text("Enter socks5 proxy (optional):").ask_async()

        self.credentials_manager.save_credentials(
            CliCredentials(
                name=name,
                access_key=access_key,
                secret_key=secret_key,
                socks5_proxy=socks5_proxy,
            )
        )
        print(f"API key {name!r} saved successfully!")

    async def _delete_credentials(self) -> None:
        """Delete existing credentials."""
        keys = self.credentials_manager.list_credentials()
        if not keys:
            print("No API keys saved.")
            return

        selected = await select(
            "Select API key to delete:",
            choices=[Choice(key.name, value=key.name) for key in keys],
        ).ask_async()

        self.credentials_manager.delete_credentials(selected)
        print(f"API key {selected!r} deleted successfully!")

    async def _set_active_credentials(self) -> None:
        """Set active credentials."""
        keys = self.credentials_manager.list_credentials()
        if not keys:
            print("No API keys saved.")
            return

        selected = await select(
            "Select API key to set as active:",
            choices=[
                Choice(
                    f"{key.name} ({key.access_key})", value=key, checked=key.is_active
                )
                for key in keys
            ],
        ).ask_async()

        self.credentials_manager.set_active_credentials(selected)
        print(f"API key {selected.name!r} set as active successfully!")

    async def _get_account_info(self) -> None:
        """Get account information."""
        credentials = self.credentials_manager.get_active_credentials()
        try:
            response = await self.mexc_client.get_account_information(credentials)
            pprint(response)
        except Exception as e:
            print(f"Error getting account info: {e}")

    async def _get_open_orders(self) -> None:
        """Get open orders."""
        symbol = await text("Enter symbol:").ask_async()
        credentials = self.credentials_manager.get_active_credentials()
        try:
            response = await self.mexc_client.get_open_orders(symbol, credentials)
            pprint(response)
        except Exception as e:
            print(f"Error getting open orders: {e}")

    async def _get_order(self) -> None:
        """Get specific order information."""
        symbol = await text("Enter symbol:").ask_async()
        order_id = await text("Enter order id:").ask_async()

        if not symbol or not order_id:
            print("Symbol and order id are required")
            return

        credentials = self.credentials_manager.get_active_credentials()
        try:
            response = await self.mexc_client.query_order(
                symbol, order_id, credentials=credentials
            )
            pprint(response)
        except Exception as e:
            print(f"Error getting order: {e}")

    async def _handle_action(self, action: Action) -> Action | None:
        """Handle the selected action and return the next menu to show."""
        if action == Action.EXIT:
            return None

        if action == Action.MANAGE_KEYS:
            return Action.MANAGE_KEYS

        if action == Action.METHODS:
            return Action.METHODS

        if action == Action.BACK:
            return Action.MAIN

        # Handle API key management actions
        if action == Action.ADD:
            await self._add_credentials()
            return Action.MANAGE_KEYS
        elif action == Action.LIST:
            await self._list_credentials()
            return Action.MANAGE_KEYS
        elif action == Action.DELETE:
            await self._delete_credentials()
            return Action.MANAGE_KEYS
        elif action == Action.SET_ACTIVE:
            await self._set_active_credentials()
            return Action.MANAGE_KEYS

        # Handle method actions
        elif action == Action.GET_ACCOUNT_INFO:
            await self._get_account_info()
            return Action.METHODS
        elif action == Action.GET_OPEN_ORDERS:
            await self._get_open_orders()
            return Action.METHODS
        elif action == Action.GET_ORDER:
            await self._get_order()
            return Action.METHODS

        return Action.MANAGE_KEYS

    async def run(self) -> None:
        """Run the main application loop."""
        try:
            current_menu = Action.MAIN

            while True:
                if current_menu == Action.MANAGE_KEYS:
                    menu = self.api_key_menu
                    title = "API Key Management"
                elif current_menu == Action.METHODS:
                    menu = self.methods_menu
                    title = "Select method"
                else:
                    menu = self.main_menu
                    title = "What do you want to do?"

                action = await select(
                    title, choices=self._get_menu_choices(menu)
                ).ask_async()

                next_menu = await self._handle_action(action)
                if next_menu is None:
                    break
                current_menu = next_menu

        finally:
            await self.mexc_client.session.close()


def main():
    """Entry point for the application."""
    cli = MexcCli()
    asyncio.run(cli.run())
