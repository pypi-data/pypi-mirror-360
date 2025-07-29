"""AgentOps Multi-Agent System.

This package implements a multi-agent AI system using LangGraph for requirements-driven
test automation. The system consists of specialized agents that work together to
analyze code, extract requirements, design test strategies, generate tests, and
ensure quality.

Agents:
- Orchestrator: Coordinates all agents and manages workflow
- CodeAnalyzer: Deep code structure and dependency analysis
- RequirementsEngineer: Functional requirement extraction and refinement
- TestArchitect: Test strategy and framework design
- TestGenerator: Actual test code creation
- QualityAssurance: Test validation and improvement
- IntegrationSpecialist: CI/CD and tool integration

The system uses LangGraph for agent coordination and state management.
"""

from .state import AgentState
from .orchestrator import AgentOrchestrator
from .agents import (
    CodeAnalyzerAgent,
    RequirementsEngineerAgent,
    TestArchitectAgent,
    TestGeneratorAgent,
    QualityAssuranceAgent,
    IntegrationSpecialistAgent,
)

__all__ = [
    "AgentState",
    "AgentOrchestrator",
    "CodeAnalyzerAgent",
    "RequirementsEngineerAgent",
    "TestArchitectAgent",
    "TestGeneratorAgent",
    "QualityAssuranceAgent",
    "IntegrationSpecialistAgent",
] 