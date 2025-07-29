"""Shared state management for AgentOps multi-agent system.

This module defines the AgentState class that maintains shared state across all agents
in the workflow. The state includes code analysis results, requirements, test strategies,
and quality metrics.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AgentState:
    """Shared state for all agents in the AgentOps workflow.
    
    This class maintains the state that is passed between agents during the
    requirements-driven test generation process. Each agent can read from and
    write to this state as needed.
    
    Attributes:
        file_path: Path to the source file being analyzed
        code: Raw source code content
        analysis: Code analysis results from CodeAnalyzer agent
        requirements: List of extracted requirements from RequirementsEngineer agent
        test_strategy: Test strategy from TestArchitect agent
        test_code: Generated test code from TestGenerator agent
        quality_score: Quality assessment from QualityAssurance agent
        errors: List of errors encountered during processing
        metadata: Additional metadata for the workflow
        agent_logs: Logs of agent interactions and decisions
    """
    
    # Input data
    file_path: str
    code: Optional[str] = None
    
    # Agent outputs
    analysis: Optional[Dict[str, Any]] = None
    requirements: List[Dict[str, Any]] = field(default_factory=list)
    test_strategy: Optional[Dict[str, Any]] = None
    test_code: Optional[str] = None
    quality_score: Optional[float] = None
    
    # Workflow state
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    agent_logs: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        """Add an error to the state.
        
        Args:
            error: Error message to add
        """
        self.errors.append(error)
    
    def add_log(self, agent_name: str, action: str, details: Any = None) -> None:
        """Add a log entry for agent interaction.
        
        Args:
            agent_name: Name of the agent
            action: Action performed by the agent
            details: Additional details about the action
        """
        self.agent_logs.append({
            "agent": agent_name,
            "action": action,
            "details": details,
            "timestamp": None  # Could add actual timestamp if needed
        })
    
    def has_errors(self) -> bool:
        """Check if there are any errors in the state.
        
        Returns:
            True if there are errors, False otherwise
        """
        return len(self.errors) > 0
    
    def get_last_error(self) -> Optional[str]:
        """Get the most recent error.
        
        Returns:
            The most recent error message, or None if no errors
        """
        return self.errors[-1] if self.errors else None
    
    def is_complete(self) -> bool:
        """Check if the workflow is complete.
        
        Returns:
            True if all required outputs are present, False otherwise
        """
        return (
            self.analysis is not None
            and len(self.requirements) > 0
            and self.test_strategy is not None
            and self.test_code is not None
            and self.quality_score is not None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization.
        
        Returns:
            Dictionary representation of the state
        """
        return {
            "file_path": self.file_path,
            "code": self.code,
            "analysis": self.analysis,
            "requirements": self.requirements,
            "test_strategy": self.test_strategy,
            "test_code": self.test_code,
            "quality_score": self.quality_score,
            "errors": self.errors,
            "metadata": self.metadata,
            "agent_logs": self.agent_logs,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        """Create state from dictionary.
        
        Args:
            data: Dictionary containing state data
            
        Returns:
            AgentState instance
        """
        return cls(**data) 