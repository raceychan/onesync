from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, ListItem, ListView, Label

from pathlib import Path
from onesync.importer import get_submodules, as_importable


"""
Make a tui for onesync
"""


class ModuleView(Static):
    def compose(self) -> ComposeResult:
        pkgs = Path("packages")
        mods = get_submodules(pkgs)
        items = (ListItem(Label(as_importable(module.name))) for module in mods)
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


if __name__ == "__main__":
    tui = OneSync()
    tui.run()
