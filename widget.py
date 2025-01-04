"""
One line description of what the script performs

    Output: output
    Other files required: none
    See also:
   
    Author: Shane Kepley
    Email: shnkeply@gmail.com
    Date: 12/31/2024
"""
from datetime import datetime
from time import monotonic
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import HorizontalGroup, VerticalScroll, Container
from textual.widgets import Button, Digits, Footer, Header, RadioButton, RadioSet
from textual import events, on
from textual.reactive import var


class MenuGroup(Container):
    """Menu screen widgets"""

    def compose(self) -> ComposeResult:
        """Add menu screen options"""

        # RadioSets built up from a collection of strings.
        yield RadioSet(
            "New Player",
            "Jason",
            "Julian",
            classes="menus")
        yield RadioSet(
            "Practice",
            "Challenge",
            "Resume Challenge",
            "View scores",
            classes="menus")
        yield RadioSet(
                "Multiplication",
                "Sums",
                classes="menus")
        yield RadioSet(*[f"Level {idx}" for idx in range(4, 12)],
                       classes="menus")


class Timer(Digits):
    """A widget to display the elapsed time"""

    start_time = reactive(monotonic)
    time = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.set_interval(1 / 60, self.update_time)

    def update_time(self) -> None:
        """Method to update the time to the current time."""
        self.time = monotonic() - self.start_time

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{minutes:02.0f}:{seconds:05.2f}")


class TimeGroup(HorizontalGroup):
    """The top layer where the timer sits"""

    def compose(self) -> ComposeResult:
        yield Timer("", id="timer")


class ProblemGroup(HorizontalGroup):
    """The middle layer where the problem is displayed"""

    def compose(self) -> ComposeResult:
        """Create child widgets of a problem."""
        yield Button("Pass", id="pass", variant="success")
        yield Digits("0x0", id="problem")
        yield Digits("42", id="answer")


class NumberGroup(Container):
    """A number grid which can be clicked on"""

    def compose(self) -> ComposeResult:
        with Container(id="numpad"):
            yield Button("7", id="number-7", classes="number")
            yield Button("8", id="number-8", classes="number")
            yield Button("9", id="number-9", classes="number")
            yield Button("4", id="number-4", classes="number")
            yield Button("5", id="number-5", classes="number")
            yield Button("6", id="number-6", classes="number")
            yield Button("1", id="number-1", classes="number")
            yield Button("2", id="number-2", classes="number")
            yield Button("3", id="number-3", classes="number")
            yield Button("0", id="number-0", classes="number")
            yield Button("<-", id="backspace")
            yield Button("Enter", id="enter")


class MathChallenge(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "mathchallenge.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    answer = var("")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield MenuGroup()
        yield Button("Start", id="start")
        yield VerticalScroll(TimeGroup(id="time_group"),
                             ProblemGroup(id="problem_group"),
                             NumberGroup(id="number_group")
                             )

    def on_mount(self):
        self.add_class("menu")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def watch_answer(self, value: str) -> None:
        """Called when answer is updated."""
        self.query_one("#answer", Digits).update(value)

    def on_key(self, event: events.Key) -> None:
        if event.key.isdecimal() and len(self.answer) < 5:
            self.answer = self.answer.lstrip("0") + event.key

        elif event.key == 'backspace':
            self.answer = self.answer[:len(self.answer) - 1]

        elif event.key == 'space':
            self.answer = ""

    @on(Button.Pressed, ".number")
    def number_pressed(self, event: Button.Pressed) -> None:
        """Pressed a number."""

        if len(self.answer) < 5:
            assert event.button.id is not None
            number = event.button.id.partition("-")[-1]
            self.answer = self.answer.lstrip("0") + number

    @on(Button.Pressed, "#backspace")
    def backspace_pressed(self) -> None:
        """Pressed backspace"""
        self.answer = self.answer[:len(self.answer) - 1]

    @on(Button.Pressed, "#start")
    def start_pressed(self) -> None:
        """Pressed start"""

        self.remove_class("menu")
        self.query_one("#timer").time = 0

    @on(Button.Pressed, "#enter")
    def enter_pressed(self) -> None:
        """Pressed enter"""
        self.answer = ""


if __name__ == "__main__":
    app = MathChallenge()
    app.run()
