from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, ListItem, ListView, Label

from onesync import service


class ModuleView(Static):
    def compose(self) -> ComposeResult:
        items = (ListItem(Label(mod)) for mod in service.list_modules())
        yield ListView(*items)


class OneSync(App):
    BINDINGS = [
        ("q", "quit", "quit the app"),
        ("i", "install", "install the app"),
        ("s", "sync", "sync the config file"),
    ]

    def compose(self) -> ComposeResult:
        yield ModuleView()
        yield Footer()

    def action_quit(self) -> None:
        self.exit()

    def action_install(self) -> None:
        """
        install the intended app
        """
        ...

    def action_sync(self) -> None:
        ...


if __name__ == "__main__":
    tui = OneSync()
    tui.run()
