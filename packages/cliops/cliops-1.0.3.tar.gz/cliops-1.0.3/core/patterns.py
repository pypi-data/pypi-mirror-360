import json
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich import box
from .config import Config

console = Console()

class OptimizationPattern:
    """Represents a prompt optimization pattern with its template and extraction logic."""
    def __init__(self, name: str, description: str, template: str, principles: list[str], specific_extract_func=None):
        self.name = name
        self.description = description
        self.template = template
        self.principles = principles
        self.specific_extract_func = specific_extract_func

    @classmethod
    def from_dict(cls, data: dict):
        """Creates an OptimizationPattern instance from a dictionary."""
        return cls(
            name=data['name'],
            description=data['description'],
            template=data['template'],
            principles=data.get('principles', []),
            specific_extract_func=None
        )

    def to_dict(self):
        """Converts the pattern to a dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'template': self.template,
            'principles': self.principles
        }

class PatternRegistry:
    """Manages available optimization patterns."""
    def __init__(self, cli_state):
        self.patterns: dict[str, OptimizationPattern] = {}
        self.cli_state = cli_state
        self._load_default_patterns()
        self._load_user_patterns()

    def _load_default_patterns(self):
        """Loads hardcoded default patterns."""
        # Generic extraction helpers
        def extract_colon_value(text, field_name):
            match = re.search(rf"^{re.escape(field_name)}:\s*(.*?)(?:\n##|\n<|\Z)", text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                next_header_match = re.search(r"##\s*\w+", content, re.DOTALL)
                if next_header_match:
                    content = content[:next_header_match.start()].strip()
                next_tag_match = re.search(r"<\w+>", content, re.DOTALL)
                if next_tag_match:
                    content = content[:next_tag_match.start()].strip()
                return content
            return None

        def extract_between_tags(text, start_tag, end_tag):
            match = re.search(rf"{re.escape(start_tag)}(.*?){re.escape(end_tag)}", text, re.DOTALL)
            return match.group(1).strip() if match else None

        # Pattern-specific extraction functions
        def specific_extract_context_aware(prompt_text):
            extracted = {}
            extracted['CONTEXT'] = extract_between_tags(prompt_text, "<CONTEXT>", "</CONTEXT>")
            extracted['CURRENT_FOCUS'] = extract_colon_value(prompt_text, "Current Focus")
            extracted['MINDSET'] = extract_colon_value(prompt_text, "Mindset")
            return {k: v for k, v in extracted.items() if v is not None}

        default_patterns_data = [
            {"name": "context_aware_generation",
             "description": "Guides generation based on specific context, mindset, and current focus.",
             "template": "# DIRECTIVE: {directive}\n\n"
                         "## CONTEXT:\n"
                         "<CONTEXT>{context}</CONTEXT>\n\n"
                         "## CURRENT FOCUS:\n"
                         "{current_focus}\n\n"
                         "## MINDSET:\n"
                         "{mindset}\n\n"
                         "## CONSTRAINTS:\n"
                         "{constraints}\n\n"
                         "## OUTPUT FORMAT:\n"
                         "{output_format}\n\n"
                         "## EXAMPLES:\n"
                         "{examples}\n\n"
                         "## SUCCESS CRITERIA:\n"
                         "{success_criteria}\n\n"
                         "## STATE:\n"
                         "Project Architecture: {STATE.ARCHITECTURE}\n"
                         "Common Patterns: {STATE.PATTERNS}\n"
                         "Current Project Focus: {STATE.FOCUS}\n\n"
                         "{code_here}",
             "principles": ["Context-Aware Generation", "Adaptive Nuance", "State Anchoring"],
             "specific_extract_func": specific_extract_context_aware}
        ]

        for p_data in default_patterns_data:
            pattern = OptimizationPattern.from_dict(p_data)
            if pattern.name == "context_aware_generation":
                pattern.specific_extract_func = specific_extract_context_aware
            self.patterns[pattern.name] = pattern

    def _load_user_patterns(self):
        """Loads user-defined patterns from patterns.json."""
        patterns_file = Config.get_patterns_file_path()
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    user_patterns_data = json.load(f)
                    for p_data in user_patterns_data:
                        pattern_name = p_data.get('name')
                        if pattern_name:
                            pattern = OptimizationPattern.from_dict(p_data)
                            self.patterns[pattern_name] = pattern
            except json.JSONDecodeError:
                console.print(f"[bold yellow]Warning:[/bold yellow] Could not decode JSON from user patterns file {patterns_file}. Ignoring user patterns.", style="yellow")
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] loading user patterns from {patterns_file}: {e}", style="red")

    def get_pattern(self, name: str) -> OptimizationPattern | None:
        """Retrieves a pattern by name."""
        return self.patterns.get(name)

    def list_patterns(self):
        """Lists all available patterns."""
        table = Table(title="Available Optimization Patterns", box=box.ROUNDED, style="magenta")
        table.add_column("Pattern Name", style="bold cyan", justify="left")
        table.add_column("Description", style="green", justify="left")
        table.add_column("Principles", style="blue", justify="left")

        for name, pattern in self.patterns.items():
            principles_text = ", ".join(pattern.principles) if pattern.principles else "N/A"
            table.add_row(name, pattern.description, principles_text)
        
        console.print(table)