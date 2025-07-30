# CliOps - Command Line Interface for Prompt Optimization

A powerful CLI tool for structured, pattern-based prompt optimization and state management.

## Features

- **Pattern-based optimization**: Apply proven prompt engineering patterns
- **State management**: Persistent CLI state for project context
- **Rich terminal UI**: Beautiful output with syntax highlighting
- **Extensible**: Add custom patterns and presets
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Initialize configuration
cliops init

# Set project context
cliops state set ARCHITECTURE "React + Node.js"
cliops state set FOCUS "API development"

# Optimize a prompt
cliops "Create a user authentication endpoint"

# Analyze a prompt
cliops analyze "Make this code better"

# List available patterns
cliops patterns
```

## Usage

### Basic Commands

- `cliops optimize <prompt>` - Optimize a prompt using patterns
- `cliops analyze <prompt>` - Analyze prompt for improvements
- `cliops patterns` - List available optimization patterns
- `cliops state set <key> <value>` - Set persistent state
- `cliops init` - Initialize configuration

### Examples

```bash
# Direct prompt optimization
cliops "Fix this bug in my React component"

# With specific pattern
cliops optimize "Refactor this function" --pattern surgical_refactor

# With overrides
cliops optimize "Create API" --context "Express.js backend" --constraints "RESTful design"

# Dry run to see what would be generated
cliops optimize "Test prompt" --dry-run
```

## Testing

```bash
python run_tests.py
```

## License

MIT License