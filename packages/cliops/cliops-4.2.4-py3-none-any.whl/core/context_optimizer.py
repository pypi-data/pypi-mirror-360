from typing import Dict, List
from .scanner import ProjectScanner, ProjectContext
from .enhancer import PromptEnhancer
from .intelligence import PromptIntelligence

class ContextAwareOptimizer:
    """Context-aware prompt optimizer that uses project intelligence."""
    
    def __init__(self, cli_state):
        self.cli_state = cli_state
        
    def optimize_with_context(self, raw_prompt: str, folder_path: str = '.') -> Dict[str, str]:
        """Main optimization function using project context."""
        # Scan project for context
        project_context = ProjectScanner.scan_project(folder_path)
        
        if project_context.is_empty:
            return self._handle_empty_project(raw_prompt, project_context)
        else:
            return self._handle_existing_project(raw_prompt, project_context)
    
    def _handle_empty_project(self, raw_prompt: str, context: ProjectContext) -> Dict[str, str]:
        """Handle empty project folders with smart initialization."""
        # Detect intended domain from prompt
        domain = PromptIntelligence.detect_domain(raw_prompt)
        
        # Suggest appropriate tech stack for domain
        suggested_stack = self._suggest_tech_stack(domain, raw_prompt)
        
        return {
            'requirements_section': self._build_empty_requirements(domain, suggested_stack, raw_prompt),
            'tech_specs_section': self._build_empty_tech_specs(domain, suggested_stack),
            'implementation_section': self._build_empty_implementation(domain, suggested_stack),
            'deliverables_section': self._build_empty_deliverables(domain, suggested_stack),
            'code_section': raw_prompt
        }
    
    def _handle_existing_project(self, raw_prompt: str, context: ProjectContext) -> Dict[str, str]:
        """Handle existing projects with discovered context."""
        # If context is too generic/unknown, treat as empty project
        if context.tech_stack == 'unknown' and context.framework == 'unknown' and context.language == 'unknown':
            return self._handle_empty_project(raw_prompt, context)
            
        return {
            'requirements_section': self._build_project_requirements(context, raw_prompt),
            'tech_specs_section': self._build_project_tech_specs(context, raw_prompt),
            'implementation_section': self._build_project_implementation(context, raw_prompt),
            'deliverables_section': self._build_project_deliverables(context, raw_prompt),
            'code_section': raw_prompt
        }
    
    def _suggest_tech_stack(self, domain: str, prompt: str) -> str:
        """Suggest modern tech stack for empty projects."""
        stacks = {
            'web_frontend': 'Next.js 14 + TypeScript + Tailwind CSS',
            'web_backend': 'Node.js + Express + TypeScript + Prisma',
            'mobile': 'Flutter + Dart',
            'desktop': 'Tauri + Rust + TypeScript',
            'game_development': 'Unity + C#',
            'blockchain': 'Solidity + Hardhat + OpenZeppelin',
            'data_science': 'Python + FastAPI + Pandas + Scikit-learn',
            'devops': 'Docker + Kubernetes + Terraform',
            'testing': 'Jest + Cypress + Playwright',
            'cli_tools': 'Node.js + TypeScript + Commander',
            'api_integration': 'Node.js + Express + TypeScript + Axios',
            'general': 'Node.js + TypeScript'
        }
        return stacks.get(domain, stacks['general'])
    
    def _build_empty_requirements(self, domain: str, stack: str, prompt: str) -> str:
        """Build requirements for empty projects."""
        keyword_enhancements = PromptEnhancer.enhance_by_keywords(prompt)
        
        base_reqs = [
            f"Initialize new {domain.replace('_', ' ')} project with {stack}",
            "Set up modern development environment with best practices",
            "Configure linting, formatting, and type checking",
            "Implement proper project structure and organization"
        ]
        
        if keyword_enhancements:
            base_reqs.extend(keyword_enhancements[:2])
        
        return '\n'.join(f"- {req}" for req in base_reqs)
    
    def _build_empty_tech_specs(self, domain: str, stack: str) -> str:
        """Build tech specs for empty projects."""
        specs = {
            'web_frontend': [
                f"Project setup with {stack}",
                "Component architecture with TypeScript",
                "Responsive design system with Tailwind CSS",
                "State management and routing configuration"
            ],
            'web_backend': [
                f"API server setup with {stack}",
                "Database schema design and migrations",
                "Authentication and authorization middleware",
                "API documentation with OpenAPI/Swagger"
            ],
            'mobile': [
                f"Mobile app initialization with {stack}",
                "Navigation and state management setup",
                "Platform-specific configurations",
                "Development and build environment"
            ],
            'desktop': [
                f"Desktop application setup with {stack}",
                "Cross-platform compatibility and native APIs",
                "UI framework and component architecture",
                "Build and distribution configuration"
            ],
            'game_development': [
                f"Game project initialization with {stack}",
                "Scene management and game object architecture",
                "Physics, rendering, and audio systems",
                "Asset pipeline and build optimization"
            ],
            'blockchain': [
                f"Smart contract project with {stack}",
                "Development environment and testing framework",
                "Security patterns and gas optimization",
                "Deployment and verification scripts"
            ],
            'data_science': [
                f"Data science environment with {stack}",
                "Data pipeline and preprocessing workflows",
                "Model training and evaluation frameworks",
                "Visualization and reporting tools"
            ],
            'devops': [
                f"Infrastructure setup with {stack}",
                "CI/CD pipeline configuration",
                "Container orchestration and scaling",
                "Monitoring and logging systems"
            ],
            'testing': [
                f"Testing framework setup with {stack}",
                "Unit, integration, and E2E test suites",
                "Test automation and reporting",
                "Performance and load testing"
            ],
            'cli_tools': [
                f"CLI application setup with {stack}",
                "Command parsing and argument validation",
                "Interactive prompts and output formatting",
                "Cross-platform compatibility and distribution"
            ]
        }.get(domain, [
            f"Project initialization with {stack}",
            "Development environment setup",
            "Code quality tools and standards",
            "Testing and deployment configuration"
        ])
        
        return '\n'.join(f"- {spec}" for spec in specs)
    
    def _build_empty_implementation(self, domain: str, stack: str) -> str:
        """Build implementation steps for empty projects."""
        steps = {
            'web_frontend': [
                "Initialize Next.js project with TypeScript template",
                "Configure Tailwind CSS and component structure",
                "Set up routing and layout components",
                "Implement core features and styling"
            ],
            'web_backend': [
                "Initialize Node.js project with Express and TypeScript",
                "Set up database connection and schema",
                "Create API routes and middleware",
                "Implement authentication and error handling"
            ],
            'mobile': [
                "Initialize Flutter project with Dart",
                "Set up navigation and state management",
                "Create UI components and screens",
                "Implement platform-specific features"
            ],
            'desktop': [
                "Initialize Tauri project with Rust backend",
                "Set up frontend framework integration",
                "Implement native API bindings",
                "Configure build and packaging"
            ],
            'game_development': [
                "Create Unity project with C# scripts",
                "Set up scene hierarchy and game objects",
                "Implement game mechanics and systems",
                "Configure build settings and optimization"
            ],
            'blockchain': [
                "Initialize Hardhat project with Solidity",
                "Write and compile smart contracts",
                "Create deployment and testing scripts",
                "Set up frontend Web3 integration"
            ],
            'data_science': [
                "Set up Python environment with virtual env",
                "Create data pipeline and preprocessing",
                "Implement model training and evaluation",
                "Build visualization and reporting"
            ],
            'devops': [
                "Create Docker containers and compose files",
                "Set up Kubernetes manifests",
                "Configure CI/CD pipelines",
                "Implement monitoring and logging"
            ],
            'testing': [
                "Set up testing framework and configuration",
                "Write unit and integration tests",
                "Create E2E test automation",
                "Configure test reporting and coverage"
            ],
            'cli_tools': [
                "Initialize CLI project with command framework",
                "Implement command parsing and validation",
                "Create interactive prompts and output",
                "Set up build and distribution"
            ]
        }.get(domain, [
            f"Initialize project with {stack}",
            "Configure development environment",
            "Implement core functionality",
            "Set up testing and deployment"
        ])
        
        return '\n'.join(f"- {step}" for step in steps)
    
    def _build_empty_deliverables(self, domain: str, stack: str) -> str:
        """Build deliverables for empty projects."""
        deliverables = [
            f"Fully configured {domain.replace('_', ' ')} project",
            "Development environment with hot reload",
            "Code quality tools (ESLint, Prettier, TypeScript)",
            "README with setup and development instructions"
        ]
        
        return '\n'.join(f"- {deliverable}" for deliverable in deliverables)
    
    def _build_project_requirements(self, context: ProjectContext, prompt: str) -> str:
        """Build requirements using actual project context."""
        keyword_enhancements = PromptEnhancer.enhance_by_keywords(prompt)
        
        # Filter out unknown/generic values
        domain = context.domain if context.domain != 'unknown' else 'application'
        tech_stack = context.tech_stack if context.tech_stack != 'unknown' else 'current technology stack'
        framework = context.framework if context.framework != 'unknown' else 'existing framework'
        
        base_reqs = [
            f"Extend existing {domain.replace('_', ' ')} project using {tech_stack}",
            f"Maintain compatibility with current {framework} setup",
            "Follow existing code patterns and architecture",
            f"Integrate with current dependencies: {', '.join(list(context.dependencies.keys())[:3])}"
        ]
        
        if keyword_enhancements:
            base_reqs.extend(keyword_enhancements[:2])
        
        return '\n'.join(f"- {req}" for req in base_reqs)
    
    def _build_project_tech_specs(self, context: ProjectContext, prompt: str) -> str:
        """Build tech specs using discovered project details."""
        # Filter out unknown values
        tech_stack = context.tech_stack if context.tech_stack != 'unknown' else 'Modern technology stack'
        framework = context.framework if context.framework != 'unknown' else 'Current framework'
        
        specs = [
            f"Current stack: {tech_stack}",
            f"Framework: {framework}",
            f"Existing structure: {', '.join(context.structure)}" if context.structure else "Standard project structure"
        ]
        
        # Add specific dependencies
        key_deps = ['typescript', 'tailwindcss', 'prisma', 'redux', 'axios']
        found_deps = [dep for dep in key_deps if dep in context.dependencies]
        if found_deps:
            specs.append(f"Key dependencies: {', '.join(found_deps)}")
        
        return '\n'.join(f"- {spec}" for spec in specs)
    
    def _build_project_implementation(self, context: ProjectContext, prompt: str) -> str:
        """Build implementation using actual project structure."""
        # Filter out unknown values
        framework = context.framework if context.framework != 'unknown' else 'current'
        tech_stack = context.tech_stack if context.tech_stack != 'unknown' else 'established technologies'
        
        steps = [
            f"Work within existing {framework} architecture",
            f"Follow current project structure in /{', /'.join(context.structure)}" if context.structure else "Follow existing project patterns",
            f"Use established dependencies: {tech_stack}",
            "Maintain code consistency with existing patterns"
        ]
        
        return '\n'.join(f"- {step}" for step in steps)
    
    def _build_project_deliverables(self, context: ProjectContext, prompt: str) -> str:
        """Build deliverables based on existing project."""
        # Filter out unknown values
        domain = context.domain if context.domain != 'unknown' else 'application'
        framework = context.framework if context.framework != 'unknown' else 'current'
        
        deliverables = [
            f"Enhanced {domain.replace('_', ' ')} functionality",
            f"Integration with existing {framework} codebase",
            "Maintained compatibility with current dependencies",
            "Updated documentation reflecting changes"
        ]
        
        return '\n'.join(f"- {deliverable}" for deliverable in deliverables)