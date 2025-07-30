from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

ASCII_LOGO = r"""
  _____ _      _____ ____  _____   _____ 
 / ____| |    |_   _/ __ \|  __ \ / ____|
| |    | |      | || |  | | |__) | (___  
| |    | |      | || |  | |  ___/ \___ \ 
| |____| |____ _| || |__| | |     ____) |
 \_____|______|_____\____/|_|    |_____/ 
"""

def show_banner():
    """Display CLIOPS ASCII art banner"""
    logo_text = Text(ASCII_LOGO, style="bold cyan")
    tagline = Text("Command Line Interface for Prompt Optimization", style="dim italic")
    
    console.print()
    console.print(logo_text, justify="center")
    console.print(tagline, justify="center")
    console.print()

def show_input_frame(prompt_text: str) -> str:
    """Display framed input prompt"""
    panel = Panel(
        f"[bold white]{prompt_text}[/bold white]",
        border_style="white",
        padding=(0, 1)
    )
    console.print(panel)
    return input(">>> ")