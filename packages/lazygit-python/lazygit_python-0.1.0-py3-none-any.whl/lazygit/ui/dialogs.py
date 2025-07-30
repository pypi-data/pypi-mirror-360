from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, Input, TextArea, Button, Label
from textual.screen import Screen
from textual.binding import Binding
from typing import Optional


class InputDialog(Screen):
    CSS = """
    #dialog-title {
        text-style: bold;
        margin-bottom: 1;
    }
    
    #dialog-prompt {
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm"),
    ]
    
    def __init__(self, title: str, prompt: str, placeholder: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.prompt = prompt
        self.placeholder = placeholder
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title, id="dialog-title"),
            Static(self.prompt, id="dialog-prompt"),
            Input(placeholder=self.placeholder, id="dialog-input"),
            id="input-dialog"
        )
    
    def on_mount(self) -> None:
        self.query_one("#dialog-input").focus()
    
    def action_confirm(self) -> None:
        value = self.query_one("#dialog-input", Input).value
        if value.strip():
            self.dismiss(value.strip())
    
    def action_cancel(self) -> None:
        self.dismiss(None)


class ConfirmDialog(Screen):
    BINDINGS = [
        Binding("y", "yes", "Yes"),
        Binding("n", "no", "No"),
        Binding("escape", "no", "Cancel"),
    ]
    
    def __init__(self, title: str, message: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.message = message
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title, id="dialog-title"),
            Static(self.message, id="dialog-message"),
            Static("Press [Y]es or [N]o", id="dialog-hint"),
            id="confirm-dialog"
        )
    
    def action_yes(self) -> None:
        self.dismiss(True)
    
    def action_no(self) -> None:
        self.dismiss(False)


class StashDialog(Screen):
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Stash changes", id="stash-title"),
            Static("Enter stash message (optional):", id="stash-prompt"),
            Input(placeholder="WIP on branch...", id="stash-input"),
            id="stash-dialog"
        )
    
    def on_mount(self) -> None:
        self.query_one("#stash-input").focus()
    
    def action_save(self) -> None:
        message = self.query_one("#stash-input", Input).value
        self.dismiss(message)
    
    def action_cancel(self) -> None:
        self.dismiss(None)