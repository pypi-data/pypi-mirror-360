import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

@dataclass
class ProjectContext:
    """Holds discovered project information."""
    tech_stack: str
    framework: str
    language: str
    dependencies: Dict[str, str]
    structure: List[str]
    config_files: List[str]
    is_empty: bool
    domain: str

class ProjectScanner:
    """Scans project folders to detect tech stack and structure."""
    
    CONFIG_PATTERNS = {
        # JavaScript/TypeScript
        'package.json': 'javascript',
        'tsconfig.json': 'typescript',
        'yarn.lock': 'javascript',
        'pnpm-lock.yaml': 'javascript',
        
        # Python
        'requirements.txt': 'python',
        'pyproject.toml': 'python',
        'setup.py': 'python',
        'Pipfile': 'python',
        'poetry.lock': 'python',
        
        # Java
        'pom.xml': 'java',
        'build.gradle': 'java',
        'build.gradle.kts': 'java',
        'gradle.properties': 'java',
        
        # C#
        '*.csproj': 'csharp',
        '*.sln': 'csharp',
        'Directory.Build.props': 'csharp',
        
        # Other Languages
        'Cargo.toml': 'rust',
        'composer.json': 'php',
        'Gemfile': 'ruby',
        'go.mod': 'go',
        'mix.exs': 'elixir',
        'build.sbt': 'scala',
        'Package.swift': 'swift',
        
        # Mobile
        'pubspec.yaml': 'flutter',
        'android/app/build.gradle': 'android',
        'ios/Podfile': 'ios',
        
        # Desktop
        'tauri.conf.json': 'tauri',
        'CMakeLists.txt': 'cpp',
        
        # Game Development
        'ProjectSettings.asset': 'unity',
        '*.uproject': 'unreal',
        'project.godot': 'godot',
        
        # Blockchain
        'hardhat.config.js': 'blockchain',
        'truffle-config.js': 'blockchain',
        'foundry.toml': 'blockchain'
    }
    
    FRAMEWORK_PATTERNS = {
        # Web Frontend
        'next.config.js': 'Next.js',
        'nuxt.config.js': 'Nuxt.js',
        'vue.config.js': 'Vue.js',
        'angular.json': 'Angular',
        'svelte.config.js': 'Svelte',
        'gatsby-config.js': 'Gatsby',
        'remix.config.js': 'Remix',
        'vite.config.js': 'Vite',
        'webpack.config.js': 'Webpack',
        
        # Web Backend
        'artisan': 'Laravel',
        'manage.py': 'Django',
        'app.py': 'Flask',
        'main.py': 'FastAPI',
        'wp-config.php': 'WordPress',
        'config/application.rb': 'Ruby on Rails',
        'Startup.cs': 'ASP.NET Core',
        'mix.exs': 'Phoenix',
        
        # Mobile
        'capacitor.config.ts': 'Capacitor',
        'ionic.config.json': 'Ionic',
        'metro.config.js': 'React Native',
        'nativescript.config.ts': 'NativeScript',
        
        # Desktop
        'tauri.conf.json': 'Tauri',
        'electron-builder.json': 'Electron',
        'main.cpp': 'Qt',
        'App.xaml': 'WPF',
        
        # Game Development
        'ProjectSettings.asset': 'Unity',
        '*.uproject': 'Unreal Engine',
        'project.godot': 'Godot',
        
        # Testing
        'jest.config.js': 'Jest',
        'cypress.config.js': 'Cypress',
        'playwright.config.js': 'Playwright',
        'pytest.ini': 'Pytest'
    }
    
    @classmethod
    def scan_project(cls, folder_path: str = '.') -> ProjectContext:
        """Main scanning function."""
        path = Path(folder_path)
        
        # Check if folder is empty or has minimal files
        if cls._is_empty_project(path):
            return ProjectContext(
                tech_stack="unknown",
                framework="unknown", 
                language="unknown",
                dependencies={},
                structure=[],
                config_files=[],
                is_empty=True,
                domain="general"
            )
        
        # Scan for config files and dependencies
        config_files = cls._find_config_files(path)
        language = cls._detect_language(config_files, path)
        framework = cls._detect_framework(config_files, path)
        dependencies = cls._extract_dependencies(config_files, path)
        structure = cls._analyze_structure(path)
        tech_stack = cls._build_tech_stack(language, framework, dependencies)
        domain = cls._detect_domain(dependencies, structure, config_files)
        
        return ProjectContext(
            tech_stack=tech_stack,
            framework=framework,
            language=language,
            dependencies=dependencies,
            structure=structure,
            config_files=config_files,
            is_empty=False,
            domain=domain
        )
    
    @classmethod
    def _is_empty_project(cls, path: Path) -> bool:
        """Check if project folder is empty or minimal."""
        files = list(path.glob('*'))
        # Consider empty if no files or only README/git files or development tools
        insignificant_files = {'.git', 'README.md', '.gitignore', 'LICENSE', '__pycache__', 
                              '.pytest_cache', 'node_modules', '.vscode', '.idea', 
                              'dist', 'build', '.env', 'venv', '.venv'}
        significant_files = [f for f in files if f.name not in insignificant_files]
        
        # Check for actual empty projects only
        
        return len(significant_files) == 0
    
    @classmethod
    def _find_config_files(cls, path: Path) -> List[str]:
        """Find configuration files in project."""
        found_configs = []
        for config_file in cls.CONFIG_PATTERNS.keys():
            if (path / config_file).exists():
                found_configs.append(config_file)
        
        # Also check for framework configs
        for framework_file in cls.FRAMEWORK_PATTERNS.keys():
            if (path / framework_file).exists():
                found_configs.append(framework_file)
                
        return found_configs
    
    @classmethod
    def _detect_language(cls, config_files: List[str], path: Path) -> str:
        """Detect primary programming language."""
        for config_file in config_files:
            if config_file in cls.CONFIG_PATTERNS:
                return cls.CONFIG_PATTERNS[config_file]
        
        # Fallback: analyze file extensions
        extensions = {}
        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix:
                ext = file_path.suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1
        
        if extensions:
            most_common = max(extensions, key=extensions.get)
            lang_map = {
                '.js': 'node_js', '.ts': 'node_js', '.jsx': 'node_js', '.tsx': 'node_js',
                '.py': 'python', '.rs': 'rust', '.java': 'java', '.php': 'php',
                '.rb': 'ruby', '.go': 'go', '.dart': 'flutter', '.sol': 'blockchain'
            }
            return lang_map.get(most_common, 'unknown')
        
        return 'unknown'
    
    @classmethod
    def _detect_framework(cls, config_files: List[str], path: Path) -> str:
        """Detect framework being used."""
        for config_file in config_files:
            if config_file in cls.FRAMEWORK_PATTERNS:
                return cls.FRAMEWORK_PATTERNS[config_file]
        
        # Check package.json for framework dependencies
        package_json = path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    if 'next' in deps: return 'Next.js'
                    if 'nuxt' in deps: return 'Nuxt.js'
                    if 'vue' in deps: return 'Vue.js'
                    if '@angular/core' in deps: return 'Angular'
                    if 'svelte' in deps: return 'Svelte'
                    if 'gatsby' in deps: return 'Gatsby'
                    if 'react' in deps: return 'React'
                    if 'express' in deps: return 'Express.js'
                    if '@nestjs/core' in deps: return 'NestJS'
            except:
                pass
        
        return 'unknown'
    
    @classmethod
    def _extract_dependencies(cls, config_files: List[str], path: Path) -> Dict[str, str]:
        """Extract dependencies and versions."""
        dependencies = {}
        
        # Node.js dependencies
        package_json = path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    dependencies.update(deps)
            except:
                pass
        
        # Python dependencies
        requirements_txt = path / 'requirements.txt'
        if requirements_txt.exists():
            try:
                with open(requirements_txt) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '==' in line:
                                name, version = line.split('==', 1)
                                dependencies[name] = version
                            else:
                                dependencies[line] = 'latest'
            except:
                pass
        
        return dependencies
    
    @classmethod
    def _analyze_structure(cls, path: Path) -> List[str]:
        """Analyze project structure."""
        structure = []
        common_dirs = ['src', 'lib', 'components', 'pages', 'api', 'utils', 'hooks', 'styles', 'public', 'assets']
        
        for dir_name in common_dirs:
            if (path / dir_name).is_dir():
                structure.append(dir_name)
        
        return structure
    
    @classmethod
    def _build_tech_stack(cls, language: str, framework: str, dependencies: Dict[str, str]) -> str:
        """Build comprehensive tech stack description."""
        if language == 'unknown' and framework == 'unknown':
            return 'unknown'
        
        stack_parts = []
        
        if framework != 'unknown':
            # Add version if available
            framework_key = framework.lower().replace('.js', '').replace('.', '')
            version = dependencies.get(framework_key, dependencies.get(framework.lower(), ''))
            if version and version != 'latest':
                stack_parts.append(f"{framework} {version}")
            else:
                stack_parts.append(framework)
        
        # Add TypeScript if detected
        if 'typescript' in dependencies:
            stack_parts.append('TypeScript')
        
        # Add key dependencies
        key_deps = ['tailwindcss', 'prisma', 'mongoose', 'axios', 'redux', 'zustand']
        for dep in key_deps:
            if dep in dependencies:
                stack_parts.append(dep.title())
        
        return ' + '.join(stack_parts) if stack_parts else language
    
    @classmethod
    def _detect_domain(cls, dependencies: Dict[str, str], structure: List[str], config_files: List[str]) -> str:
        """Detect project domain based on dependencies and structure."""
        # Game Development
        if any(f in config_files for f in ['ProjectSettings.asset', '*.uproject', 'project.godot']):
            return 'game_development'
        if any(dep in dependencies for dep in ['unity', 'unreal', 'godot', 'pygame', 'phaser']):
            return 'game_development'
            
        # Desktop Applications
        if any(f in config_files for f in ['tauri.conf.json', 'electron-builder.json', 'main.cpp', 'App.xaml']):
            return 'desktop'
        if any(dep in dependencies for dep in ['electron', 'tauri', 'qt', 'tkinter', 'pyqt']):
            return 'desktop'
            
        # Mobile Development
        if 'pubspec.yaml' in config_files or any(f in config_files for f in ['android/app/build.gradle', 'ios/Podfile']):
            return 'mobile'
        if any(dep in dependencies for dep in ['flutter', 'react-native', 'expo', 'ionic', 'xamarin', 'capacitor']):
            return 'mobile'
            
        # Data Science/ML
        if any(dep in dependencies for dep in ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'jupyter', 'matplotlib', 'keras', 'opencv']):
            return 'data_science'
        if any(dir_name in structure for dir_name in ['notebooks', 'data', 'models']):
            return 'data_science'
            
        # Blockchain/Web3
        if any(f in config_files for f in ['hardhat.config.js', 'truffle-config.js', 'foundry.toml']):
            return 'blockchain'
        if any(dep in dependencies for dep in ['hardhat', 'truffle', 'web3', 'ethers', 'solidity']):
            return 'blockchain'
            
        # Web Backend
        if any(f in config_files for f in ['manage.py', 'artisan', 'wp-config.php']):
            return 'web_backend'
        if any(dep in dependencies for dep in ['express', 'fastapi', 'django', 'flask', 'laravel', 'spring-boot', 'rails', 'gin', 'fiber']):
            return 'web_backend'
        if any(dir_name in structure for dir_name in ['api', 'routes', 'controllers', 'models']):
            return 'web_backend'
            
        # Web Frontend
        if any(f in config_files for f in ['next.config.js', 'nuxt.config.js', 'vue.config.js', 'angular.json']):
            return 'web_frontend'
        if any(dep in dependencies for dep in ['react', 'vue', 'angular', 'svelte', 'next', 'nuxt', 'gatsby', 'remix']):
            return 'web_frontend'
        if any(dir_name in structure for dir_name in ['components', 'pages', 'styles', 'public']):
            return 'web_frontend'
            
        # DevOps/Cloud
        if any(f in config_files for f in ['Dockerfile', 'docker-compose.yml', 'terraform', 'Jenkinsfile']):
            return 'devops'
        if any(dir_name in structure for dir_name in ['terraform', 'ansible', 'k8s', 'docker']):
            return 'devops'
            
        # Testing
        if any(f in config_files for f in ['jest.config.js', 'cypress.config.js', 'pytest.ini']):
            return 'testing'
        if any(dep in dependencies for dep in ['jest', 'mocha', 'pytest', 'junit', 'cypress', 'selenium', 'playwright']):
            return 'testing'
            
        # CLI Tools
        if any(dep in dependencies for dep in ['rich', 'click', 'argparse', 'typer', 'commander', 'yargs']):
            return 'cli_tools'
            
        return 'general'