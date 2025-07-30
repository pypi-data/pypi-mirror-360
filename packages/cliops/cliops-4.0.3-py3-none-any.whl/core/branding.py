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
    """Display chatbox-style input prompt"""
    # Input prompt panel
    panel = Panel(
        f"[bold cyan]>> {prompt_text}[/bold cyan]",
        border_style="white",
        padding=(1, 2),
        title="[dim]CLIOPS Input[/dim]",
        title_align="left"
    )
    console.print(panel)
    
    # Input area with border
    input_panel = Panel(
        "[dim]Type your response here...[/dim]",
        border_style="white", 
        padding=(0, 1)
    )
    console.print(input_panel)
    console.print("[bold white]>>> [/bold white]", end="")
    return input()