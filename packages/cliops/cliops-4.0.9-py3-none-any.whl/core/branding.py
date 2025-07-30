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
    tagline = Text("your terminal prompt engineer, ready to serve", style="dim italic")
    
    console.print()
    console.print(logo_text, justify="center")
    console.print(tagline, justify="center")
    console.print()

def show_input_frame(prompt_text: str) -> str:
    """Display simple input prompt without styling"""
    console.print(f"\n[bold cyan]{prompt_text}[/bold cyan]")
    return input(">>> ")