import re
from typing import Dict, List, Set

class PromptEnhancer:
    """Enhances prompts with specific, actionable, and measurable content."""
    
    # 1. Placeholder Detection & Replacement
    VAGUE_TERMS = {
        "modern tech stack": {
            "web_frontend": "React 18/TypeScript/Vite",
            "web_backend": "Node.js/Express/TypeScript", 
            "mobile": "Flutter/Dart",
            "blockchain": "Solidity/Hardhat/OpenZeppelin",
            "data_science": "Python/Pandas/Scikit-learn",
            "general": "TypeScript/Node.js"
        },
        "best practices": {
            "web_frontend": "React hooks patterns, component composition, performance optimization",
            "web_backend": "SOLID principles, dependency injection, error handling middleware",
            "mobile": "Material Design guidelines, state management patterns, platform conventions",
            "blockchain": "security audits, gas optimization, reentrancy protection",
            "data_science": "reproducible workflows, data validation, model versioning",
            "general": "SOLID principles, clean architecture, comprehensive testing"
        },
        "clean code": {
            "web_frontend": "ESLint/Prettier standards, TypeScript strict mode, component documentation",
            "web_backend": "ESLint standards, API documentation, error logging",
            "mobile": "Dart analyzer rules, widget documentation, state management",
            "blockchain": "Solidity style guide, NatSpec documentation, security comments",
            "data_science": "PEP 8 compliance, docstrings, type hints",
            "general": "linting standards, documented functions, type safety"
        },
        "core functionality": {
            "web_frontend": "user interface interactions and data display",
            "web_backend": "API endpoints and business logic",
            "mobile": "native app features and user experience",
            "blockchain": "smart contract logic and token mechanics",
            "data_science": "data analysis and model training",
            "general": "primary application features"
        }
    }
    
    # 2. Context-Aware Specification Addition
    DOMAIN_SPECS = {
        "web_frontend": [
            "Component architecture (functional components, custom hooks)",
            "State management (Redux Toolkit/Zustand)",
            "Styling system (CSS modules/Styled-components)",
            "Build optimization (code splitting, lazy loading)",
            "Testing framework (Jest/React Testing Library)"
        ],
        "web_backend": [
            "API versioning (v1, v2 endpoints)",
            "Error handling (4xx, 5xx responses with proper codes)",
            "Rate limiting (100 requests/minute per IP)",
            "Input validation (Joi/Zod schemas)",
            "Database ORM (Prisma/TypeORM with migrations)"
        ],
        "mobile": [
            "Navigation system (React Navigation/Flutter Navigator)",
            "State management (Provider/Bloc pattern)",
            "Local storage (SQLite/Hive)",
            "Platform-specific UI (Material/Cupertino)",
            "Performance monitoring (Firebase Performance)"
        ],
        "blockchain": [
            "Smart contract framework (Hardhat/Foundry)",
            "Gas optimization strategies (storage packing, function modifiers)",
            "Security patterns (ReentrancyGuard, access control)",
            "Testing suite (Hardhat tests, coverage reports)",
            "Deployment scripts (mainnet/testnet configurations)"
        ],
        "data_science": [
            "Data pipeline (ETL processes, data validation)",
            "Model evaluation (cross-validation, metrics tracking)",
            "Feature engineering (preprocessing, scaling)",
            "Model deployment (containerization, API endpoints)",
            "Monitoring system (model drift detection, performance tracking)"
        ]
    }
    
    # 3. Domain-Specific Enhancement
    KEYWORD_ENHANCEMENTS = {
        "dashboard": [
            "Real-time data updates via WebSocket/SSE",
            "Interactive charts (Chart.js/D3.js)",
            "Data filtering and search functionality",
            "Export capabilities (PDF/CSV)",
            "User role-based access control"
        ],
        "authentication": [
            "JWT token management (access/refresh tokens)",
            "Password hashing (bcrypt/Argon2)",
            "Multi-factor authentication (TOTP/SMS)",
            "Session management and logout",
            "OAuth integration (Google/GitHub)"
        ],
        "e-commerce": [
            "Payment processing (Stripe/PayPal integration)",
            "Inventory management system",
            "Order tracking and notifications",
            "Shopping cart persistence",
            "Product search and filtering"
        ],
        "api": [
            "OpenAPI/Swagger documentation",
            "Request/response validation",
            "CORS configuration",
            "API key authentication",
            "Response caching strategies"
        ]
    }
    
    @classmethod
    def replace_vague_terms(cls, text: str, domain: str) -> str:
        """Replace generic terms with domain-specific alternatives."""
        enhanced_text = text
        for vague_term, replacements in cls.VAGUE_TERMS.items():
            if vague_term in enhanced_text:
                specific_term = replacements.get(domain, replacements.get("general", vague_term))
                enhanced_text = enhanced_text.replace(vague_term, specific_term)
        return enhanced_text
    
    @classmethod
    def add_domain_specs(cls, domain: str) -> List[str]:
        """Add missing technical specifications based on domain."""
        return cls.DOMAIN_SPECS.get(domain, [
            "Architecture patterns and design principles",
            "Error handling and logging strategies", 
            "Testing framework and coverage requirements",
            "Performance optimization techniques",
            "Documentation and code standards"
        ])
    
    @classmethod
    def enhance_by_keywords(cls, prompt: str) -> List[str]:
        """Add context-specific requirements based on prompt keywords."""
        enhancements = []
        prompt_lower = prompt.lower()
        
        for keyword, specs in cls.KEYWORD_ENHANCEMENTS.items():
            if keyword in prompt_lower:
                enhancements.extend(specs)
        
        return enhancements
    
    @classmethod
    def remove_duplicates(cls, sections: Dict[str, str]) -> Dict[str, str]:
        """Remove redundancy while maintaining completeness."""
        # Track used concepts across sections
        used_concepts = set()
        cleaned_sections = {}
        
        for section_name, content in sections.items():
            lines = content.split('\n')
            unique_lines = []
            
            for line in lines:
                # Extract key concepts from line
                concepts = cls._extract_concepts(line)
                if not any(concept in used_concepts for concept in concepts):
                    unique_lines.append(line)
                    used_concepts.update(concepts)
            
            cleaned_sections[section_name] = '\n'.join(unique_lines)
        
        return cleaned_sections
    
    @classmethod
    def _extract_concepts(cls, text: str) -> Set[str]:
        """Extract key concepts from text for deduplication."""
        # Simple concept extraction based on key terms
        concepts = set()
        key_terms = [
            'authentication', 'validation', 'testing', 'documentation',
            'performance', 'security', 'database', 'api', 'ui', 'responsive'
        ]
        
        text_lower = text.lower()
        for term in key_terms:
            if term in text_lower:
                concepts.add(term)
        
        return concepts