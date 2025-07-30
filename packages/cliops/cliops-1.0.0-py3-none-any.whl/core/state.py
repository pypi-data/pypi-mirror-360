import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

class CLIState:
    """Manages persistent key-value state for CLI operations."""
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """Loads state from the JSON file."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                console.print(f"[bold yellow]Warning:[/bold yellow] Could not decode JSON from {self.file_path}. Starting with empty state.", style="yellow")
                return {}
        return {}

    def _save_state(self):
        """Saves the current state to the JSON file."""
        with open(self.file_path, 'w') as f:
            json.dump(self.state, f, indent=4)

    def set(self, key: str, value: str):
        """Sets a key-value pair in the state."""
        self.state[key.upper()] = value
        self._save_state()
        console.print(f"State '[bold green]{key.upper()}[/bold green]' set to '[cyan]{value}[/cyan]'.")

    def get(self, key: str) -> str | None:
        """Gets a value from the state."""
        return self.state.get(key.upper())

    def show(self):
        """Displays the current state."""
        if not self.state:
            console.print("No CLI state currently set.", style="italic dim")
            return
        
        table = Table(title="Current CLI State", box=box.ROUNDED, style="blue")
        table.add_column("Key", style="bold cyan")
        table.add_column("Value", style="green")

        for key, value in self.state.items():
            table.add_row(key, value)
        
        console.print(table)

    def clear(self):
        """Clears all entries from the state."""
        self.state = {}
        self._save_state()
        console.print("CLI state cleared.", style="red")