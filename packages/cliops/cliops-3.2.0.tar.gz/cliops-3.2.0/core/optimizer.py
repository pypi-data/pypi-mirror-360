import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text
from rich import box

console = Console()

class PromptOptimizer:
    """Optimizes raw prompts using predefined patterns."""
    def __init__(self, pattern_registry, cli_state, verbose: bool = False):
        self.pattern_registry = pattern_registry
        self.cli_state = cli_state
        self.verbose = verbose

    def _parse_prompt_into_sections(self, raw_prompt: str) -> dict:
        """Parses a raw prompt into a dictionary of sections based on '## SECTION:' headers and <TAG>...</TAG> blocks."""
        sections = {}
        main_body_content = raw_prompt
        extracted_sections = {}

        # Extract tagged blocks (e.g., <CODE>, <CONTEXT>)
        tag_block_pattern = re.compile(r"<(\w+)>(.*?)</\1>", re.DOTALL | re.IGNORECASE)
        
        matches_to_remove = []
        for match in tag_block_pattern.finditer(main_body_content):
            tag_name = match.group(1).upper()
            content = match.group(2).strip()
            extracted_sections[tag_name] = content
            matches_to_remove.append(match.span())
        
        # Remove extracted tag blocks from the main body content
        for start, end in sorted(matches_to_remove, key=lambda x: x[0], reverse=True):
            main_body_content = main_body_content[:start] + main_body_content[end:]

        # Extract ## sections from the remaining text
        parts = re.split(r'(?m)^(##\s*[\w\s\/]+?:)', main_body_content)

        current_key = "MAIN_BODY"
        if parts and parts[0].strip():
            extracted_sections[current_key] = parts[0].strip()
        
        for i in range(1, len(parts), 2):
            header = parts[i].strip()
            key = header.replace('##', '').replace(':', '').strip().replace(' ', '_').upper()
            content = parts[i+1].strip() if i+1 < len(parts) else ""
            extracted_sections[key] = content

        # Handle 'code_here' specifically if it's the main body or implied
        if "CODE" in extracted_sections:
             extracted_sections["CODE_HERE"] = extracted_sections.pop("CODE")

        return extracted_sections

    def _extract_components(self, raw_prompt: str, pattern) -> dict:
        """Extracts common and pattern-specific components from a raw prompt."""
        parsed_sections = self._parse_prompt_into_sections(raw_prompt)
        extracted_fields = {}

        # Map common section names to expected template field names
        common_mappings = {
            'DIRECTIVE': 'directive',
            'SCOPE': 'scope',
            'CONSTRAINTS': 'constraints',
            'OUTPUT_FORMAT': 'output_format',
            'SUCCESS_CRITERIA': 'success_criteria',
            'CODE_HERE': 'code_here',
            'CODE': 'code_here',
            'CONTEXT': 'context',
            'CURRENT_FOCUS': 'current_focus',
            'MINDSET': 'mindset',
            'MAIN_BODY': 'code_here'
        }

        for section_key, template_field in common_mappings.items():
            if section_key in parsed_sections and parsed_sections[section_key] != "":
                extracted_fields[template_field] = parsed_sections[section_key]

        # Apply pattern-specific extraction logic
        if pattern.specific_extract_func:
            specific_extracted = pattern.specific_extract_func(raw_prompt)
            for k,v in specific_extracted.items():
                if v is not None and v != '':
                    extracted_fields[k.lower()] = v

        return {k: v for k, v in extracted_fields.items() if v is not None}

    def optimize_prompt(self, raw_prompt: str, pattern_name: str, overrides: dict, dry_run: bool = False) -> str:
        """Applies an optimization pattern to a raw prompt."""
        pattern = self.pattern_registry.get_pattern(pattern_name)
        if not pattern:
            raise ValueError(f"Pattern '{pattern_name}' not found.")

        # Extract components from raw_prompt
        extracted_fields = self._extract_components(raw_prompt, pattern)

        # Prepare fields for template formatting
        template_fields = {}
        for key in extracted_fields:
            template_fields[key] = extracted_fields[key]

        # Inject CLI state
        cli_state_values = {key: self.cli_state.get(key) for key in self.cli_state.state.keys()}
        StateObject = type('StateObject', (object,), cli_state_values)
        template_fields['STATE'] = StateObject()

        # Apply explicit CLI argument overrides
        for key, value in overrides.items():
            if key in template_fields:
                template_fields[key] = value
            elif key.upper() in cli_state_values:
                setattr(template_fields['STATE'], key.upper(), value)

        # Set defaults if fields are still missing
        default_fields = {
            'directive': 'Please complete the task.',
            'scope': 'The entire codebase.',
            'constraints': 'No specific constraints.',
            'output_format': 'Clean code/text.',
            'success_criteria': 'The task is completed as per the directive.',
            'code_here': 'No code provided.',
            'context': 'General context.',
            'current_focus': 'Overall system.',
            'mindset': 'Standard development mindset.',
            'examples': 'No examples provided.'
        }

        for field, default_value in default_fields.items():
            if field not in template_fields or template_fields[field] is None or template_fields[field] == '':
                template_fields[field] = default_value

        if dry_run:
            console.print(Panel("[bold blue]Dry Run: Prompt Optimization Details[/bold blue]", expand=False, border_style="blue"))
            console.print("Dry run complete. No prompt generated.")
            return "Dry run complete. No prompt generated."

        try:
            optimized_prompt = pattern.template.format(**template_fields)
            return optimized_prompt
        except KeyError as e:
            raise ValueError(f"Template for pattern '{pattern_name}' missing field {e}.")