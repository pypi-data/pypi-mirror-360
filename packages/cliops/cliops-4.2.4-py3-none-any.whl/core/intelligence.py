import re
from typing import Dict, List, Tuple

class PromptIntelligence:
    """Analyzes prompts to determine optimal patterns and generate contextual content."""
    
    DOMAIN_PATTERNS = {
        'web_frontend': [
            r'\b(react|vue|angular|svelte|next|nuxt|gatsby|html|css|sass|scss|less|tailwind)\b',
            r'\b(component|hook|state|props|dom|browser|webpack|vite|rollup)\b',
            r'\b(ui|ux|responsive|mobile|desktop|layout|design|frontend|landing|page|website|saas)\b'
        ],
        'web_backend': [
            r'\b(api|endpoint|server|database|sql|rest|graphql|grpc)\b',
            r'\b(express|django|flask|fastapi|spring|node|laravel|rails|asp\.net)\b',
            r'\b(auth|middleware|route|controller|service|backend|microservice)\b'
        ],
        'mobile': [
            r'\b(ios|android|flutter|react native|ionic|xamarin|swift|kotlin|dart)\b',
            r'\b(app|mobile|device|platform|store|xcode|android studio)\b',
            r'\b(native|hybrid|cross-platform|pwa)\b'
        ],
        'data_science': [
            r'\b(pandas|numpy|matplotlib|seaborn|plotly|sklearn|tensorflow|pytorch|keras)\b',
            r'\b(data|analysis|model|ml|ai|algorithm|dataset|jupyter|notebook)\b',
            r'\b(statistics|regression|classification|clustering|deep learning)\b'
        ],
        'devops': [
            r'\b(docker|kubernetes|aws|azure|gcp|terraform|ansible|jenkins)\b',
            r'\b(deploy|ci/cd|pipeline|infrastructure|monitoring|helm|istio)\b',
            r'\b(cloud|serverless|container|orchestration|automation)\b'
        ],
        'game_development': [
            r'\b(unity|unreal|godot|pygame|phaser|three\.js|webgl)\b',
            r'\b(game|gaming|2d|3d|sprite|animation|physics|collision)\b',
            r'\b(c#|c\+\+|lua|gdscript|shader|texture|mesh)\b'
        ],
        'blockchain': [
            r'\b(solidity|ethereum|bitcoin|web3|smart contract|dapp|nft)\b',
            r'\b(blockchain|crypto|defi|dao|token|wallet|metamask)\b',
            r'\b(truffle|hardhat|ganache|remix|openzeppelin)\b'
        ],
        'desktop': [
            r'\b(electron|tauri|qt|gtk|wpf|winforms|javafx|swing)\b',
            r'\b(desktop|gui|window|native|cross-platform)\b',
            r'\b(c#|java|c\+\+|python|rust|go)\b'
        ],
        'embedded': [
            r'\b(arduino|raspberry pi|esp32|microcontroller|firmware|rtos)\b',
            r'\b(embedded|iot|sensor|actuator|gpio|i2c|spi|uart)\b',
            r'\b(c|c\+\+|assembly|micropython|circuitpython)\b'
        ],
        'security': [
            r'\b(security|vulnerability|penetration|exploit|malware|encryption)\b',
            r'\b(auth|oauth|jwt|ssl|tls|https|firewall|vpn)\b',
            r'\b(cybersecurity|infosec|pentest|owasp|cve)\b'
        ],
        'testing': [
            r'\b(test|testing|unit|integration|e2e|selenium|cypress|jest)\b',
            r'\b(mock|stub|fixture|assertion|coverage|tdd|bdd)\b',
            r'\b(pytest|junit|mocha|jasmine|karma|playwright)\b'
        ],
        'database': [
            r'\b(mysql|postgresql|mongodb|redis|elasticsearch|cassandra|sqlite)\b',
            r'\b(database|db|sql|nosql|query|schema|migration|orm)\b',
            r'\b(prisma|sequelize|mongoose|sqlalchemy|hibernate)\b'
        ],
        'system_programming': [
            r'\b(rust|c|c\+\+|go|zig|assembly|kernel|driver|compiler)\b',
            r'\b(system|low-level|memory|performance|optimization|concurrency)\b',
            r'\b(linux|unix|windows|macos|operating system)\b'
        ],
        'ai_ml': [
            r'\b(machine learning|deep learning|neural network|ai|artificial intelligence)\b',
            r'\b(tensorflow|pytorch|scikit-learn|huggingface|openai|llm|gpt)\b',
            r'\b(model|training|inference|dataset|feature|algorithm)\b'
        ],
        'api_integration': [
            r'\b(api|rest|graphql|webhook|integration|third-party|sdk)\b',
            r'\b(postman|curl|axios|fetch|http|json|xml)\b',
            r'\b(oauth|authentication|rate limit|pagination)\b'
        ]
    }
    
    COMPLEXITY_INDICATORS = [
        r'\b(implement|create|build|develop|design)\b',
        r'\b(optimize|refactor|improve|enhance)\b',
        r'\b(integrate|connect|sync|merge)\b',
        r'\b(test|debug|fix|solve)\b'
    ]
    
    @classmethod
    def detect_domain(cls, prompt: str) -> str:
        """Detects the primary domain of the prompt."""
        prompt_lower = prompt.lower()
        domain_scores = {}
        
        for domain, patterns in cls.DOMAIN_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, prompt_lower))
                score += matches
            domain_scores[domain] = score
        
        if not any(domain_scores.values()):
            return 'general'
        
        return max(domain_scores, key=domain_scores.get)
    
    @classmethod
    def assess_complexity(cls, prompt: str) -> str:
        """Assesses prompt complexity level."""
        if len(prompt) < 50:
            return 'simple'
        
        complexity_matches = 0
        for pattern in cls.COMPLEXITY_INDICATORS:
            complexity_matches += len(re.findall(pattern, prompt.lower()))
        
        if complexity_matches >= 3 or len(prompt) > 200:
            return 'complex'
        elif complexity_matches >= 1 or len(prompt) > 100:
            return 'moderate'
        
        return 'simple'
    
    @classmethod
    def suggest_pattern(cls, prompt: str) -> str:
        """Suggests the best pattern based on prompt analysis."""
        domain = cls.detect_domain(prompt)
        complexity = cls.assess_complexity(prompt)
        
        # Pattern selection logic
        if complexity == 'complex' or domain != 'general':
            return 'adaptive_generation'
        elif any(word in prompt.lower() for word in ['fix', 'bug', 'error', 'debug']):
            return 'precision_engineering'
        elif complexity == 'moderate':
            return 'adaptive_generation'
        
        return 'adaptive_generation'
    
    @classmethod
    def generate_contextual_constraints(cls, prompt: str, domain: str) -> str:
        """Generates domain-specific constraints."""
        constraints_map = {
            'web_frontend': 'Ensure responsive design, accessibility compliance, SEO optimization, and modern web standards.',
            'web_backend': 'Follow REST/GraphQL principles, implement proper error handling, security, and scalability.',
            'mobile': 'Optimize for performance, battery life, follow platform guidelines, and ensure intuitive UX.',
            'data_science': 'Validate data integrity, document assumptions, ensure reproducibility, and statistical rigor.',
            'devops': 'Prioritize reliability, implement monitoring, follow IaC principles, and ensure security.',
            'game_development': 'Optimize for performance, frame rate, memory usage, and engaging gameplay mechanics.',
            'blockchain': 'Ensure security, gas optimization, audit readiness, and decentralization principles.',
            'desktop': 'Follow platform UI guidelines, ensure cross-platform compatibility, and optimize resource usage.',
            'embedded': 'Minimize memory footprint, optimize power consumption, ensure real-time constraints.',
            'security': 'Follow OWASP guidelines, implement defense in depth, and ensure compliance standards.',
            'testing': 'Ensure comprehensive coverage, maintainable tests, and fast execution times.',
            'database': 'Optimize queries, ensure ACID properties, implement proper indexing, and data integrity.',
            'system_programming': 'Ensure memory safety, optimize performance, handle concurrency, and system compatibility.',
            'ai_ml': 'Validate model performance, ensure data privacy, implement proper evaluation metrics.',
            'api_integration': 'Handle rate limits, implement proper error handling, ensure data validation.',
            'general': 'Follow clean code principles, ensure maintainability, and include comprehensive documentation.'
        }
        
        base_constraint = constraints_map.get(domain, constraints_map['general'])
        
        # Add specific constraints based on prompt content
        if 'performance' in prompt.lower():
            base_constraint += ' Focus on optimization and performance.'
        if 'security' in prompt.lower():
            base_constraint += ' Implement security best practices.'
        if 'test' in prompt.lower():
            base_constraint += ' Include comprehensive testing.'
            
        return base_constraint
    
    @classmethod
    def generate_success_criteria(cls, prompt: str, domain: str) -> str:
        """Generates contextual success criteria."""
        criteria_map = {
            'web_frontend': 'UI renders correctly across devices, accessibility standards met, performance optimized.',
            'web_backend': 'API endpoints respond correctly, security implemented, scalability considered.',
            'mobile': 'App functions on target platforms, smooth performance, intuitive user experience.',
            'data_science': 'Analysis produces accurate results, code is reproducible, insights are actionable.',
            'devops': 'Infrastructure deploys successfully, monitoring implemented, system is reliable and secure.',
            'game_development': 'Game runs smoothly, engaging mechanics implemented, performance targets met.',
            'blockchain': 'Smart contracts are secure, gas-optimized, and thoroughly tested.',
            'desktop': 'Application runs on target platforms, UI follows guidelines, performance is optimal.',
            'embedded': 'System meets real-time constraints, power consumption optimized, hardware compatibility ensured.',
            'security': 'Vulnerabilities identified and mitigated, compliance requirements met, security tested.',
            'testing': 'Comprehensive test coverage achieved, tests are maintainable, CI/CD integration works.',
            'database': 'Queries perform efficiently, data integrity maintained, backup/recovery implemented.',
            'system_programming': 'Code is memory-safe, performance optimized, system compatibility verified.',
            'ai_ml': 'Model meets accuracy targets, training is reproducible, deployment is scalable.',
            'api_integration': 'Integration works reliably, error handling robust, rate limits respected.',
            'general': 'Code works as intended, follows best practices, is well-documented and maintainable.'
        }
        
        return criteria_map.get(domain, criteria_map['general'])