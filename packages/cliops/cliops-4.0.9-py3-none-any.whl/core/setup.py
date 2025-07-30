from rich.console import Console
from rich.panel import Panel

from .validation import StateSchema
from .branding import show_input_frame
from pydantic import ValidationError

console = Console()

class StateSetup:
    def __init__(self, cli_state):
        self.cli_state = cli_state
        self.required_fields = ["ARCHITECTURE", "FOCUS", "PATTERNS"]

    def is_setup_complete(self) -> bool:
        """Check if all required state fields are configured"""
        for field in self.required_fields:
            if not self.cli_state.get(field):
                return False
        return True

    def run_interactive_setup(self):
        """Run interactive state setup"""
        console.print(Panel(
            "[bold yellow]Initial Setup Required[/bold yellow]\n\n"
            "Before using CLIOPS, please configure your project settings:",
            border_style="yellow"
        ))

        setup_data = {}
        
        # Architecture setup
        architecture = show_input_frame("Enter your project architecture (e.g., 'React + Node.js', 'Django + PostgreSQL'):")
        setup_data["ARCHITECTURE"] = architecture

        # Focus setup  
        focus = show_input_frame("Enter your current project focus (e.g., 'API development', 'UI components'):")
        setup_data["FOCUS"] = focus

        # Patterns setup
        console.print(Panel(
            "Available patterns: context_aware_generation, bug_fix_precision, code_review, api_design",
            border_style="dim"
        ))
        patterns = show_input_frame("Enter preferred patterns (comma-separated):")
        setup_data["PATTERNS"] = patterns

        # Default pattern
        default_pattern = show_input_frame("Enter default pattern (optional, press Enter for 'context_aware_generation'):")
        if default_pattern:
            setup_data["DEFAULT_PATTERN"] = default_pattern
        else:
            setup_data["DEFAULT_PATTERN"] = "context_aware_generation"

        # Validate and save
        try:
            validated_data = StateSchema(**setup_data)
            for key, value in validated_data.model_dump().items():
                if value:  # Only set non-None values
                    self.cli_state.set(key, value)
            
            console.print(Panel(
                "[bold green]Setup Complete![/bold green]\n\n"
                "You can now use CLIOPS to optimize and analyze prompts.",
                border_style="green"
            ))
            
        except ValidationError as e:
            console.print(f"[bold red]Setup Error:[/bold red] {e}", style="red")
            raise ValueError("Setup validation failed")

    def check_and_setup(self):
        """Check setup status and run setup if needed"""
        if not self.is_setup_complete():
            self.run_interactive_setup()
            return True
        return False