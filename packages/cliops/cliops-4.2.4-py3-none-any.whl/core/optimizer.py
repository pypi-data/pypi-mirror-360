import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text
from rich import box
from .intelligence import PromptIntelligence
from .enhancer import PromptEnhancer
from .context_optimizer import ContextAwareOptimizer

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
        """Generates specific, actionable, and measurable content sections."""
        arch = self.cli_state.get('ARCHITECTURE') or 'modern tech stack'
        focus = self.cli_state.get('FOCUS') or 'core functionality'
        
        # Remove test values and enhance with specifics
        if arch == 'Test Architecture':
            arch = 'modern tech stack'
        if focus == 'Test Focus':
            focus = 'core functionality'
            
        # Apply vague term replacement
        arch = PromptEnhancer.replace_vague_terms(arch, domain)
        focus = PromptEnhancer.replace_vague_terms(focus, domain)
        
        # Get keyword-based enhancements
        keyword_enhancements = PromptEnhancer.enhance_by_keywords(raw_prompt)
        
        generators = {
            'requirements_section': self._build_requirements(domain, arch, focus, keyword_enhancements),
            'tech_specs_section': self._build_tech_specs(domain, raw_prompt),
            'implementation_section': self._build_implementation(domain, raw_prompt),
            'deliverables_section': self._build_deliverables(domain, raw_prompt),
            'code_section': raw_prompt
        }
        
        return generators.get(field_name, '')
    
    def _build_requirements(self, domain: str, arch: str, focus: str, enhancements: list) -> str:
        """Build specific, measurable requirements."""
        base_reqs = [
            f"{domain.replace('_', ' ')} solution using {arch}",
            PromptEnhancer.replace_vague_terms("clean, maintainable code", domain),
            PromptEnhancer.replace_vague_terms("best practices implementation", domain),
            f"focus on {focus}"
        ]
        
        # Add first 2 keyword enhancements to requirements
        if enhancements:
            base_reqs.extend(enhancements[:2])
            
        return '\n'.join(f"- {req}" for req in base_reqs)
    
    def _build_tech_specs(self, domain: str, prompt: str) -> str:
        """Build comprehensive technical specifications."""
        domain_specs = PromptEnhancer.add_domain_specs(domain)
        keyword_specs = PromptEnhancer.enhance_by_keywords(prompt)
        
        # Combine and deduplicate
        all_specs = domain_specs + keyword_specs[2:4] if len(keyword_specs) > 2 else domain_specs
        unique_specs = list(dict.fromkeys(all_specs))[:4]  # Keep top 4 unique specs
        
        return '\n'.join(f"- {spec}" for spec in unique_specs)
    
    def _build_implementation(self, domain: str, prompt: str) -> str:
        """Build actionable implementation steps."""
        impl_steps = {
            'web_frontend': [
                "Component architecture setup with TypeScript",
                "Responsive layout implementation with CSS Grid/Flexbox", 
                "State management integration (Redux/Zustand)",
                "Performance optimization (code splitting, lazy loading)"
            ],
            'web_backend': [
                "API endpoint design with OpenAPI specification",
                "Authentication middleware with JWT tokens",
                "Database schema design with migrations",
                "Error handling and logging implementation"
            ],
            'mobile': [
                "App architecture with navigation system",
                "UI components following platform guidelines",
                "State management with Provider/Bloc pattern",
                "Platform-specific optimizations and testing"
            ],
            'blockchain': [
                "Smart contract development with security patterns",
                "Gas optimization and testing framework",
                "Web3 integration with frontend",
                "Deployment and verification scripts"
            ],
            'data_science': [
                "Data pipeline setup with validation",
                "Model development with cross-validation",
                "Feature engineering and preprocessing",
                "Model deployment with monitoring"
            ]
        }.get(domain, [
            "Architecture planning with design patterns",
            "Core functionality implementation", 
            "Comprehensive testing strategy",
            "Documentation and deployment setup"
        ])
        
        return '\n'.join(f"- {step}" for step in impl_steps)
    
    def _build_deliverables(self, domain: str, prompt: str) -> str:
        """Build measurable deliverables."""
        deliverables = {
            'web_frontend': [
                "Production-ready web application with 95%+ Lighthouse score",
                "Cross-browser compatibility (Chrome, Firefox, Safari, Edge)",
                "WCAG 2.1 AA accessibility compliance report",
                "Performance metrics and optimization documentation"
            ],
            'web_backend': [
                "RESTful API with OpenAPI 3.0 documentation",
                "Database schema with migration scripts",
                "Security implementation with penetration test report",
                "Load testing results (1000+ concurrent users)"
            ],
            'mobile': [
                "Native mobile application for iOS/Android",
                "App store submission packages and guidelines",
                "Performance benchmarks (60fps, <3s load time)",
                "User acceptance testing results"
            ],
            'blockchain': [
                "Audited smart contracts with security report",
                "Gas optimization analysis and recommendations",
                "Testnet deployment with interaction examples",
                "Integration documentation for frontend"
            ],
            'data_science': [
                "Trained model with >85% accuracy metrics",
                "Data pipeline with automated validation",
                "Model deployment API with monitoring dashboard",
                "Reproducible analysis with documented methodology"
            ]
        }.get(domain, [
            "Complete working solution with test coverage >80%",
            "Comprehensive documentation with setup instructions",
            "Deployment guide with environment configurations",
            "User manual with feature explanations"
        ])
        
        return '\n'.join(f"- {deliverable}" for deliverable in deliverables)

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

        # Generate context-aware content for both patterns
        if pattern.name in ["adaptive_generation", "precision_engineering"]:
            # Use context-aware optimizer for project intelligence
            context_optimizer = ContextAwareOptimizer(self.cli_state)
            content_sections = context_optimizer.optimize_with_context(raw_prompt)
            
            # Remove duplicates across sections
            content_sections = PromptEnhancer.remove_duplicates(content_sections)
            template_fields.update(content_sections)

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