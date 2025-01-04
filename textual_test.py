"""
One line description of what the script performs

    Output: output
    Other files required: none
    See also:
   
    Author: Shane Kepley
    Email: shnkeply@gmail.com
    Date: 1/3/2025
"""
from textual import events
from textual.app import App, ComposeResult
from textual.widgets import RichLog


class KeyLogger(RichLog):
    def on_key(self, event: events.Key) -> None:
        self.write(event)


class InputApp(App):
    """App to display key events."""

    CSS_PATH = "test.tcss"

    def compose(self) -> ComposeResult:
        yield KeyLogger()
        yield KeyLogger()
        yield KeyLogger()
        yield KeyLogger()


if __name__ == "__main__":
    app = InputApp()
    app.run()