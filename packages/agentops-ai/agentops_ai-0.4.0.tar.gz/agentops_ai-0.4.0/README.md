# AgentOps 🤖

[![PyPI version](https://badge.fury.io/py/agentops-ai.svg)](https://badge.fury.io/py/agentops-ai)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/knaig/agentops_ai?style=social)](https://github.com/knaig/agentops_ai)

**The world's first AI-powered QA co-pilot** that automatically generates comprehensive test suites from your code using a sophisticated multi-agent AI system. Think of it as having a team of expert QA engineers working on your codebase 24/7.

## ✨ Features

- 🤖 **6 AI Agents** working in harmony for comprehensive analysis
- 📝 **Automated Requirements Extraction** from code changes
- 🧪 **Intelligent Test Generation** with edge case detection
- 🔄 **Delta-Based Updates** - only analyze what changed
- 📊 **Requirements Traceability** matrix for full coverage
- 🚀 **90% Time Savings** compared to manual test writing
- 🎯 **Zero Configuration** setup with sensible defaults
- 🔧 **Rich CLI** with progressive help and examples

## 🚀 Quick Start

### CLI Usage

```bash
# Install AgentOps
pip install agentops-ai

# Set up your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Initialize and run the multi-agent workflow
agentops init
agentops multi-agent-run examples/demo-project/calc.py
agentops run --all
```

### Python API Usage

```python
from agentops_ai import AgentOps

# Initialize AgentOps for your project
agentops = AgentOps("./my_project")

# Analyze a Python file
result = agentops.analyze_file("src/my_module.py")

# Generate tests
result = agentops.generate_tests("src/my_module.py")

# Run tests
result = agentops.run_tests("src/my_module.py")
```

📖 **For detailed API documentation, see [docs/api-reference.md](docs/api-reference.md)**

## 🎯 What's New (v0.3.0)

### ✅ Enhanced Discoverability
- **Rich CLI Help System** with progressive disclosure and examples
- **Interactive Onboarding** with `agentops welcome` command
- **System Health Checks** with `agentops check` command
- **Project Status Monitoring** with `agentops status` command
- **Version Information** with `agentops version` command

### ✅ Multi-Agent AI System
AgentOps uses a **multi-agent AI system** that automatically handles the entire workflow:
- **CodeAnalyzer Agent**: Deep code structure analysis
- **RequirementsEngineer Agent**: LLM-powered requirement extraction  
- **TestArchitect Agent**: Comprehensive test strategy design
- **TestGenerator Agent**: High-quality test code generation
- **QualityAssurance Agent**: Test validation and scoring
- **IntegrationSpecialist Agent**: CI/CD and IDE integration

### ✅ Enhanced Reliability
- **Import Issues Fixed**: Resolved CLI import errors for cross-project usage
- **Error Recovery**: Robust error handling with automatic recovery mechanisms
- **Type Safety**: Enhanced type annotations and IDE support

### ✅ Simplified Workflow
- **One Command**: `agentops multi-agent-run` replaces the old multi-step process
- **Automatic**: No manual approval steps required
- **Intelligent**: AI agents handle all decision-making

## 🎯 What's New (December 2024)

### ✅ Multi-Agent AI System
AgentOps now uses a **multi-agent AI system** that automatically handles the entire workflow:
- **CodeAnalyzer Agent**: Deep code structure analysis
- **RequirementsEngineer Agent**: LLM-powered requirement extraction  
- **TestArchitect Agent**: Comprehensive test strategy design
- **TestGenerator Agent**: High-quality test code generation
- **QualityAssurance Agent**: Test validation and scoring
- **IntegrationSpecialist Agent**: CI/CD and IDE integration

### ✅ Enhanced Reliability
- **Import Issues Fixed**: Resolved CLI import errors for cross-project usage
- **Error Recovery**: Robust error handling with automatic recovery mechanisms
- **Type Safety**: Enhanced type annotations and IDE support

### ✅ Simplified Workflow
- **One Command**: `agentops multi-agent-run` replaces the old multi-step process
- **Automatic**: No manual approval steps required
- **Intelligent**: AI agents handle all decision-making

## 📁 Project Structure

```
AgentOps/
├── agentops_ai/              # Main package
│   ├── agentops_agents/      # Multi-agent system
│   ├── agentops_cli/         # Command-line interface
│   ├── agentops_core/        # Core business logic
│   ├── docs/                 # Documentation
│   ├── prompts/              # LLM prompt templates
│   └── .tours/               # CodeTour files
├── examples/                 # Example projects
│   └── demo-project/         # Demo project
├── .github/                  # CI/CD workflows
├── .private/                 # Internal documentation
└── docs/                     # Project documentation
```

## 🛠️ Development

### Prerequisites

- Python 3.11+
- Poetry
- OpenAI API key

### Setup

```bash
# Clone and install
git clone <repository-url>
cd AgentOps
pip install -e .

# Set environment variables
export OPENAI_API_KEY="your-api-key"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentops_ai

# Run linting
ruff check agentops_ai
black --check agentops_ai
```

### Documentation

```bash
# Start documentation server
cd agentops_ai/docs
mkdocs serve
```

## 📚 Documentation

- **[Documentation Overview](docs/README.md)** - Complete documentation structure and navigation
- **[Quick Start Guide](docs/user-guides/01_QUICK_START.md)** - Get up and running with multi-agent system
- **[AgentOps Runner Guide](docs/user-guides/AGENTOPS_RUNNER_GUIDE.md)** - Complete guide for the runner script
- **[Architecture Overview](docs/developer-guides/02_ARCHITECTURE_OVERVIEW.md)** - Multi-agent system design
- **[Multi-Agent Differences](docs/developer-guides/04_MULTI_AGENT_DIFF.md)** - Legacy vs. new system comparison
- **[API Reference](docs/api-reference/)** - Complete API docs
- **[Readiness Checklist](docs/developer-guides/06_READINESS_CHECKLIST.md)** - Engineer onboarding
- **[Recent Improvements](docs/changelog/IMPORT_FIX_AND_IMPROVEMENTS.md)** - Latest fixes and enhancements

## 🎯 Multi-Agent Workflow

AgentOps now follows a **single-command automation** workflow:

```bash
# Initialize project
agentops init

# Run complete multi-agent workflow
agentops multi-agent-run path/to/your_file.py

# Execute generated tests
agentops run --all
```

### What Each Agent Does
1. **CodeAnalyzer**: Analyzes code structure and dependencies
2. **RequirementsEngineer**: Extracts functional requirements using LLM
3. **TestArchitect**: Designs comprehensive test strategy
4. **TestGenerator**: Creates high-quality test code
5. **QualityAssurance**: Validates and scores test quality
6. **IntegrationSpecialist**: Sets up CI/CD and IDE integrations

## 🔧 CLI Commands

### Core Workflow
```bash
agentops init                    # Initialize project structure
agentops multi-agent-run <file>  # Run complete multi-agent workflow
agentops run --file <file>       # Run tests for specific file
agentops run --all               # Run all generated tests
```

### Discovery & Help
```bash
agentops welcome                 # Interactive welcome and quick start guide
agentops help                    # Comprehensive help documentation
agentops examples                # Practical examples and use cases
agentops commands                # List all available commands
agentops version                 # Show version and system information
agentops check                   # Verify system requirements and setup
agentops status                  # Show project status and configuration
```

### Management & Analysis
```bash
agentops config                  # View and edit configuration
agentops report --check-changes  # Generate analysis report
agentops traceability --open     # View requirements-to-tests matrix
agentops integration setup       # Configure CI/CD and IDE integrations
```

### Getting Started
```bash
# First time? Start here:
agentops welcome                 # Interactive onboarding
agentops check                   # Verify your setup
agentops init                    # Initialize your project
agentops multi-agent-run myfile.py  # Run your first workflow
```

## 🏗️ Architecture

AgentOps uses a modern multi-agent architecture:

- **Multi-Agent Layer**: Specialized AI agents for each task
- **LangGraph Orchestration**: Modern AI workflow management
- **CLI Layer**: Command-line interface with Click
- **Core Engine**: Business logic and state management
- **Service Layer**: LLM-based analysis and generation
- **Storage Layer**: SQLite database for requirements

## 🛡️ Error Recovery

The system includes robust error recovery mechanisms:
- **LLM API Errors**: Automatic fallback strategies
- **JSON Parsing Errors**: Default structure provision
- **File System Errors**: Directory creation retry
- **Code Analysis Errors**: File reload and minimal analysis
- **Import Resolution Errors**: Basic import addition

## 🤝 Contributing

1. Read the [Architecture Overview](agentops_ai/docs/02_ARCHITECTURE_OVERVIEW.md)
2. Complete the [Readiness Checklist](agentops_ai/docs/06_READINESS_CHECKLIST.md)
3. Review [Recent Improvements](docs/IMPORT_FIX_AND_IMPROVEMENTS.md)
4. Explore the CodeTours in `.tours/`
5. Follow the development workflow

## 🔍 Discoverability Features

AgentOps is designed to be **highly discoverable** with multiple ways to learn and explore:

### 🎯 Interactive Onboarding
```bash
agentops welcome    # Start here for new users
agentops check      # Verify your system setup
agentops status     # Check your project status
```

### 📚 Progressive Help System
```bash
agentops --help     # Main help with command categories
agentops help       # Comprehensive documentation
agentops examples   # Real-world use cases
agentops commands   # All commands organized by function
```

### 🚀 Command Discovery
- **Tab Completion**: Works with bash, zsh, fish shells
- **Command Suggestions**: Get help when you make typos
- **Progressive Disclosure**: Essential info first, details on demand
- **Rich Examples**: Every command includes practical examples

### 📊 System Monitoring
- **Health Checks**: Verify dependencies and configuration
- **Status Monitoring**: Track project progress and health
- **Version Information**: Check updates and compatibility
- **Error Diagnostics**: Clear error messages with solutions

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built for vibe coders who want to ship fast without sacrificing quality! 🚀**

**Latest**: Multi-agent AI system with enhanced discoverability and CLI experience ✅

## 🌟 Star Us!

If AgentOps helps you ship faster, please [star us on GitHub](https://github.com/knaig/agentops_ai) ⭐ 