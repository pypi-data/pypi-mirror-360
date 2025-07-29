"""
AgentOps - Multi-Agent AI System for Requirements-Driven Test Automation

AgentOps is an AI-powered QA co-pilot that automatically generates comprehensive
test suites from your codebase using a sophisticated multi-agent system.

Quick Start:
    # CLI Usage
    agentops init                    # Initialize project
    agentops multi-agent-run file.py # Run complete workflow
    agentops run --all              # Execute generated tests

    # Python API Usage
    from agentops_ai import AgentOps
    
    agentops = AgentOps("./my_project")
    result = agentops.analyze_file("src/my_module.py")
    result = agentops.generate_tests("src/my_module.py")
    result = agentops.run_tests("src/my_module.py")

For more information, visit: https://github.com/knaig/agentops_ai
"""

__version__ = "0.4.0"
__author__ = "AgentOps Team"
__email__ = "support@agentops.ai"

# Import the main API classes
from .agentops_api import AgentOps, AgentOpsResult, analyze_file, generate_tests, run_tests

# Import CLI components
from .agentops_cli.main import cli as cli_main

# Export the main API
__all__ = [
    "AgentOps",
    "AgentOpsResult", 
    "analyze_file",
    "generate_tests",
    "run_tests",
    "cli_main",
    "__version__"
] 