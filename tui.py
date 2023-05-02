from textual.app import App, ComposeResult
from textual.widgets import Welcome

"""
Make a tui for onesync
"""


class WelcomeApp(App):
    def compose(self) -> ComposeResult:
        yield Welcome()

    def on_button_pressed(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = WelcomeApp()
    app.run()
