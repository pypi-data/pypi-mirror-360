"""
AgentOps Public API

This module provides a clean, documented API for using AgentOps programmatically.
It wraps the internal implementation and provides a simple interface for common tasks.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# Import internal components
from .agentops_core.workflow import AgentOpsWorkflow
from .agentops_core.config import AgentOpsConfig, set_config
from .agentops_core.requirement_store import RequirementStore
from .agentops_core.services.test_generator import TestGenerator


@dataclass
class AgentOpsResult:
    """Result object for AgentOps operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentOps:
    """
    Main AgentOps API class for programmatic usage.
    
    This class provides a clean interface to AgentOps functionality,
    handling initialization, configuration, and common workflows.
    
    Example:
        ```python
        from agentops_ai import AgentOps
        
        # Initialize AgentOps for a project
        agentops = AgentOps(project_root="./my_project")
        
        # Analyze a Python file
        result = agentops.analyze_file("src/my_module.py")
        
        # Generate tests
        result = agentops.generate_tests("src/my_module.py")
        
        # Run tests
        result = agentops.run_tests("src/my_module.py")
        ```
    """
    
    def __init__(self, project_root: str = ".", config_file: str = "agentops.yaml"):
        """
        Initialize AgentOps for a project.
        
        Args:
            project_root: Path to the project root directory
            config_file: Name of the configuration file (default: agentops.yaml)
            
        Example:
            ```python
            # Initialize for current directory
            agentops = AgentOps()
            
            # Initialize for specific project
            agentops = AgentOps("./my_project")
            ```
        """
        self.project_root = Path(project_root).resolve()
        self.config_file = config_file
        
        # Initialize internal components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize internal AgentOps components."""
        try:
            # Load configuration
            self.config = AgentOpsConfig()
            
            # Set the config file path and load it
            config_path = self.project_root / self.config_file
            if config_path.exists():
                self.config.config_file = str(config_path)
                self.config.load_config()
            # Set as global config for downstream consumers
            set_config(self.config)
            
            # Initialize workflow and services (no arguments)
            self.workflow = AgentOpsWorkflow()
            self.requirement_store = RequirementStore()
            self.test_generator = TestGenerator()
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize AgentOps: {e}")
    
    def analyze_file(self, file_path: str) -> AgentOpsResult:
        """
        Analyze a Python file and infer requirements.
        
        Args:
            file_path: Path to the Python file to analyze (relative to project root)
            
        Returns:
            AgentOpsResult with analysis results
            
        Example:
            ```python
            result = agentops.analyze_file("src/my_module.py")
            if result.success:
                print(f"Found {len(result.data['requirements'])} requirements")
            else:
                print(f"Analysis failed: {result.error}")
            ```
        """
        try:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                return AgentOpsResult(
                    success=False,
                    message="File not found",
                    error=f"File {file_path} does not exist"
                )
            
            # Run requirement inference
            result = self.workflow.infer_requirements(str(full_path))
            
            if result["success"]:
                return AgentOpsResult(
                    success=True,
                    message=f"Successfully analyzed {file_path}",
                    data={
                        "requirements": result.get("requirements", []),
                        "file_path": str(full_path),
                        "confidence_scores": result.get("confidence_scores", [])
                    }
                )
            else:
                return AgentOpsResult(
                    success=False,
                    message="Analysis failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return AgentOpsResult(
                success=False,
                message="Analysis failed",
                error=str(e)
            )
    
    def generate_tests(self, file_path: str, force_regenerate: bool = False) -> AgentOpsResult:
        """
        Generate tests for a Python file.
        
        Args:
            file_path: Path to the Python file to generate tests for
            force_regenerate: Whether to regenerate tests if they already exist
            
        Returns:
            AgentOpsResult with test generation results
            
        Example:
            ```python
            result = agentops.generate_tests("src/my_module.py")
            if result.success:
                print(f"Tests generated: {result.data['test_file']}")
            else:
                print(f"Test generation failed: {result.error}")
            ```
        """
        try:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                return AgentOpsResult(
                    success=False,
                    message="File not found",
                    error=f"File {file_path} does not exist"
                )
            
            # Generate tests
            result = self.workflow.process_file_change(str(full_path), interactive=False)
            
            if result["success"]:
                return AgentOpsResult(
                    success=True,
                    message=f"Successfully generated tests for {file_path}",
                    data={
                        "test_file": result.get("test_file"),
                        "code": result.get("code"),
                        "file_path": str(full_path)
                    }
                )
            else:
                return AgentOpsResult(
                    success=False,
                    message="Test generation failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return AgentOpsResult(
                success=False,
                message="Test generation failed",
                error=str(e)
            )
    
    def run_tests(self, file_path: str = None) -> AgentOpsResult:
        """
        Run tests for a specific file or all tests.
        
        Args:
            file_path: Path to the Python file to run tests for (optional)
                      If None, runs all tests in the project
            
        Returns:
            AgentOpsResult with test execution results
            
        Example:
            ```python
            # Run tests for specific file
            result = agentops.run_tests("src/my_module.py")
            
            # Run all tests
            result = agentops.run_tests()
            
            if result.success:
                print(f"Tests passed: {result.data['passed']}/{result.data['total']}")
            else:
                print(f"Test execution failed: {result.error}")
            ```
        """
        try:
            if file_path:
                full_path = self.project_root / file_path
                result = self.workflow.run_tests_for_file(str(full_path))
            else:
                result = self.workflow.run_all_tests()
            
            if result["success"]:
                return AgentOpsResult(
                    success=True,
                    message="Tests executed successfully",
                    data={
                        "output": result.get("output", ""),
                        "failures": result.get("failures", []),
                        "total_tests": result.get("total_tests", 0),
                        "failed_tests": result.get("failed_tests", 0),
                        "passed_tests": result.get("total_tests", 0) - result.get("failed_tests", 0)
                    }
                )
            else:
                return AgentOpsResult(
                    success=False,
                    message="Test execution failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return AgentOpsResult(
                success=False,
                message="Test execution failed",
                error=str(e)
            )
    
    def analyze_project(self, include_patterns: List[str] = None, 
                       exclude_patterns: List[str] = None) -> AgentOpsResult:
        """
        Analyze all Python files in the project.
        
        Args:
            include_patterns: List of file patterns to include (e.g., ["src/**/*.py"])
            exclude_patterns: List of file patterns to exclude (e.g., ["tests/**/*.py"])
            
        Returns:
            AgentOpsResult with project analysis results
            
        Example:
            ```python
            result = agentops.analyze_project(
                include_patterns=["src/**/*.py"],
                exclude_patterns=["tests/**/*.py"]
            )
            
            if result.success:
                print(f"Analyzed {result.data['files_analyzed']} files")
                print(f"Found {result.data['total_requirements']} requirements")
            ```
        """
        try:
            # Run multi-agent analysis
            result = self.workflow.multi_agent_analyze(
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns
            )
            
            if result["success"]:
                return AgentOpsResult(
                    success=True,
                    message="Project analysis completed successfully",
                    data={
                        "files_analyzed": result.get("files_analyzed", 0),
                        "total_requirements": result.get("total_requirements", 0),
                        "requirements": result.get("requirements", []),
                        "analysis_time": result.get("analysis_time", 0)
                    }
                )
            else:
                return AgentOpsResult(
                    success=False,
                    message="Project analysis failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return AgentOpsResult(
                success=False,
                message="Project analysis failed",
                error=str(e)
            )
    
    def generate_all_tests(self, force_regenerate: bool = False) -> AgentOpsResult:
        """
        Generate tests for all analyzed files in the project.
        
        Args:
            force_regenerate: Whether to regenerate existing tests
            
        Returns:
            AgentOpsResult with test generation results
            
        Example:
            ```python
            result = agentops.generate_all_tests()
            
            if result.success:
                print(f"Generated tests for {result.data['test_files_created']} files")
            ```
        """
        try:
            result = self.workflow.generate_tests_from_requirements_filtered(
                force_regenerate=force_regenerate
            )
            
            if result["success"]:
                return AgentOpsResult(
                    success=True,
                    message="Test generation completed successfully",
                    data={
                        "processed_count": result.get("processed_count", 0),
                        "test_files_created": result.get("test_files_created", 0),
                        "test_files": result.get("test_files", [])
                    }
                )
            else:
                return AgentOpsResult(
                    success=False,
                    message="Test generation failed",
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            return AgentOpsResult(
                success=False,
                message="Test generation failed",
                error=str(e)
            )
    
    def get_project_status(self) -> AgentOpsResult:
        """
        Get the current status of the AgentOps project.
        
        Returns:
            AgentOpsResult with project status information
            
        Example:
            ```python
            result = agentops.get_project_status()
            
            if result.success:
                status = result.data
                print(f"Requirements: {status['requirements_count']}")
                print(f"Tests: {status['tests_count']}")
                print(f"Coverage: {status['coverage_percentage']}%")
            ```
        """
        try:
            # Get requirements count
            requirements = self.requirement_store.get_all_requirements()
            requirements_count = len(requirements)
            
            # Get tests count
            test_dir = self.project_root / ".agentops" / "tests"
            tests_count = 0
            if test_dir.exists():
                tests_count = len(list(test_dir.rglob("*.py")))
            
            # Calculate coverage
            coverage_percentage = 0
            if requirements_count > 0:
                requirements_with_tests = sum(1 for req in requirements if req.status == "approved")
                coverage_percentage = (requirements_with_tests / requirements_count) * 100
            
            return AgentOpsResult(
                success=True,
                message="Project status retrieved successfully",
                data={
                    "requirements_count": requirements_count,
                    "tests_count": tests_count,
                    "coverage_percentage": round(coverage_percentage, 1),
                    "project_root": str(self.project_root),
                    "config_file": self.config_file
                }
            )
            
        except Exception as e:
            return AgentOpsResult(
                success=False,
                message="Failed to get project status",
                error=str(e)
            )


# Convenience functions for quick usage
def analyze_file(file_path: str, project_root: str = ".") -> AgentOpsResult:
    """
    Quick function to analyze a single file.
    
    Args:
        file_path: Path to the Python file
        project_root: Project root directory
        
    Returns:
        AgentOpsResult with analysis results
    """
    agentops = AgentOps(project_root)
    return agentops.analyze_file(file_path)


def generate_tests(file_path: str, project_root: str = ".") -> AgentOpsResult:
    """
    Quick function to generate tests for a single file.
    
    Args:
        file_path: Path to the Python file
        project_root: Project root directory
        
    Returns:
        AgentOpsResult with test generation results
    """
    agentops = AgentOps(project_root)
    return agentops.generate_tests(file_path)


def run_tests(file_path: str = None, project_root: str = ".") -> AgentOpsResult:
    """
    Quick function to run tests.
    
    Args:
        file_path: Path to the Python file (optional)
        project_root: Project root directory
        
    Returns:
        AgentOpsResult with test execution results
    """
    agentops = AgentOps(project_root)
    return agentops.run_tests(file_path) 