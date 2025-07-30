import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text
from rich import box
from .intelligence import PromptIntelligence

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

    def _generate_intelligent_content(self, field_name: str, raw_prompt: str, domain: str, extracted_fields: dict) -> str:
        """Generates clean, actionable content sections."""
        arch = self.cli_state.get('ARCHITECTURE') or 'modern tech stack'
        focus = self.cli_state.get('FOCUS') or 'core functionality'
        
        # Remove test values
        if arch == 'Test Architecture':
            arch = 'modern tech stack'
        if focus == 'Test Focus':
            focus = 'core functionality'
        
        generators = {
            'requirements_section': f"- {domain.replace('_', ' ')} solution using {arch}\n- clean, maintainable code\n- best practices implementation\n- focus on {focus}",
            
            'tech_specs_section': {
                'web_frontend': "- mobile-first responsive design\n- WCAG accessibility\n- SEO optimization\n- semantic HTML",
                'web_backend': "- RESTful API design\n- JWT authentication\n- database integration\n- scalable architecture",
                'mobile': "- native performance\n- platform UI guidelines\n- state management\n- cross-platform compatibility",
                'blockchain': "- gas-optimized contracts\n- security auditing\n- Web3 integration\n- decentralized architecture",
                'data_science': "- data validation\n- statistical analysis\n- model deployment\n- reproducible workflows",
                'general': "- clean architecture\n- error handling\n- performance optimization\n- maintainable design"
            }.get(domain, "- best practices\n- clean code\n- comprehensive testing\n- documentation"),
            
            'implementation_section': {
                'web_frontend': "- component structure\n- responsive layout\n- accessibility features\n- performance optimization",
                'web_backend': "- API endpoints\n- authentication middleware\n- validation\n- database setup",
                'mobile': "- app structure\n- UI components\n- state management\n- platform features",
                'general': "- architecture planning\n- core functionality\n- error handling\n- testing"
            }.get(domain, "- structure planning\n- best practices implementation\n- testing\n- documentation"),
            
            'deliverables_section': {
                'web_frontend': "- responsive web application\n- cross-browser compatibility\n- accessibility compliance\n- performance metrics",
                'web_backend': "- production API endpoints\n- database schema\n- API documentation\n- security implementation",
                'mobile': "- native mobile app\n- platform builds\n- app store guidelines\n- performance benchmarks",
                'general': "- working solution\n- clean code\n- documentation\n- test coverage"
            }.get(domain, "- complete solution\n- documented code\n- testing coverage\n- usage instructions"),
            
            'code_section': raw_prompt
        }
        
        return generators.get(field_name, '')

    def optimize_prompt(self, raw_prompt: str, pattern_name: str, overrides: dict, dry_run: bool = False) -> str:
        """Creates highly personalized, non-repetitive optimized prompts."""
        pattern = self.pattern_registry.get_pattern(pattern_name)
        if not pattern:
            raise ValueError(f"Pattern '{pattern_name}' not found.")

        # Intelligent analysis and pattern selection
        domain = PromptIntelligence.detect_domain(raw_prompt)
        complexity = PromptIntelligence.assess_complexity(raw_prompt)
        
        # Auto-upgrade pattern based on intelligence
        if pattern_name == "context_aware_generation":
            suggested_pattern = PromptIntelligence.suggest_pattern(raw_prompt)
            better_pattern = self.pattern_registry.get_pattern(suggested_pattern)
            if better_pattern:
                pattern = better_pattern
        
        # Extract components with domain awareness
        extracted_fields = self._extract_components(raw_prompt, pattern)
        extracted_fields['detected_domain'] = domain
        extracted_fields['complexity'] = complexity

        # Build dynamic template fields
        template_fields = dict(extracted_fields)
        
        # Inject CLI state
        class StateObject:
            def __init__(self, state_dict):
                for key, value in state_dict.items():
                    setattr(self, key, value)
            def __getattr__(self, name):
                return 'Not set'
        
        cli_state_values = {key: self.cli_state.get(key) for key in self.cli_state.state.keys()}
        template_fields['STATE'] = StateObject(cli_state_values)

        # Apply overrides
        template_fields.update(overrides)

        # Generate intelligent content for both patterns
        if pattern.name in ["adaptive_generation", "precision_engineering"]:
            for field in ['requirements_section', 'tech_specs_section', 'implementation_section', 'deliverables_section', 'code_section']:
                if field not in template_fields:
                    template_fields[field] = self._generate_intelligent_content(field, raw_prompt, domain, extracted_fields)

        # Clean directive based on user input
        smart_defaults = {
            'directive': extracted_fields.get('directive') or raw_prompt.capitalize(),
        }

        # Apply smart defaults only for missing fields
        for field, default_value in smart_defaults.items():
            if field not in template_fields or not template_fields[field]:
                template_fields[field] = default_value

        if dry_run:
            console.print(Panel("[bold blue]Dry Run: Intelligent Prompt Analysis[/bold blue]", expand=False, border_style="blue"))
            console.print(f"Detected Domain: {domain}")
            console.print(f"Complexity Level: {complexity}")
            console.print(f"Selected Pattern: {pattern.name}")
            console.print(f"Intelligence Score: {len(raw_prompt)} chars, {len(raw_prompt.split())} words")
            return "Dry run complete. No prompt generated."

        try:
            optimized_prompt = pattern.template.format(**template_fields)
            return optimized_prompt
        except KeyError as e:
            # Fallback with missing field filled
            template_fields[str(e).strip("'")] = f"[{e} not specified]"
            return pattern.template.format(**template_fields)