import re
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

class PromptAnalyzer:
    """Analyzes a raw prompt for common issues based on optimization principles."""
    def __init__(self, pattern_registry):
        self.pattern_registry = pattern_registry
        self.principles = {
            "Structure and Clarity": {
                "keywords": ["directive", "scope", "constraints", "output format", "success criteria"],
                "suggestion": "Ensure your prompt has a clear structure with explicit sections like 'DIRECTIVE', 'SCOPE', 'CONSTRAINTS', 'OUTPUT FORMAT', and 'SUCCESS CRITERIA'."
            },
            "Specificity and Detail": {
                "keywords": ["specific", "detailed", "precise", "exact", "example"],
                "suggestion": "Add more specific details about the task, desired output, edge cases, and expected behavior. Consider using few-shot examples."
            },
            "Context-Aware Generation": {
                "keywords": ["context", "background", "system", "environment", "state"],
                "suggestion": "Provide relevant context, system state, or background information the LLM needs to understand the scenario fully. Leverage `cliops state`."
            },
            "Output Format": {
                "keywords": ["json", "xml", "yaml", "markdown", "code block", "format", "structure"],
                "suggestion": "Clearly define the desired output format (e.g., JSON, YAML, Markdown code block, specific class structure)."
            },
            "Error Prevention": {
                "keywords": ["handle errors", "robust", "mitigate", "assumptions", "potential issues", "safeguards"],
                "suggestion": "Instruct the LLM on how to handle potential errors, edge cases, or invalid inputs. Define explicit assumptions."
            }
        }

    def analyze_prompt(self, prompt_text: str):
        """Analyzes a raw prompt for adherence to prompt engineering principles."""
        console.print(Panel("[bold green]Prompt Analysis[/bold green]", expand=False, border_style="green"))
        issues = []
        recommendations = []

        # Check for general structure and key fields
        if not re.search(r"DIRECTIVE:", prompt_text, re.IGNORECASE):
            issues.append("Missing or unclear 'DIRECTIVE'.")
            recommendations.append(self.principles["Structure and Clarity"]["suggestion"])
        if not re.search(r"CONSTRAINTS:", prompt_text, re.IGNORECASE):
            issues.append("Missing or unclear 'CONSTRAINTS'.")
            recommendations.append(self.principles["Structure and Clarity"]["suggestion"])
        if not re.search(r"OUTPUT FORMAT:", prompt_text, re.IGNORECASE):
            issues.append("Missing or unclear 'OUTPUT FORMAT'.")
            recommendations.append(self.principles["Output Format"]["suggestion"])

        # Check for keywords related to other principles
        for principle, data in self.principles.items():
            if principle in ["Structure and Clarity", "Output Format"]:
                continue

            found_keyword = False
            for keyword in data["keywords"]:
                if re.search(r"\b" + re.escape(keyword) + r"\b", prompt_text, re.IGNORECASE):
                    found_keyword = True
                    break
            if not found_keyword:
                recommendations.append(f"Consider: {data['suggestion']}")

        if issues:
            console.print(Panel("[bold red]Identified Issues[/bold red]", expand=False, border_style="red"))
            for issue in sorted(list(set(issues))):
                console.print(f"[red]- {issue}[/red]")
        else:
            console.print("[bold green]No critical issues identified in prompt structure.[/bold green]", style="green")

        if recommendations:
            console.print(Panel("[bold yellow]Recommendations for Improvement[/bold yellow]", expand=False, border_style="yellow"))
            for rec in sorted(list(set(recommendations))):
                console.print(f"[yellow]- {rec}[/yellow]")
        else:
            console.print("[bold green]Prompt appears well-structured and comprehensive.[/bold green]", style="green")
        console.print(Panel.fit("[dim]Analysis Complete[/dim]", border_style="dim"))