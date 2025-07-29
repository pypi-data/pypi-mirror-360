"""Orchestrator agent for AgentOps multi-agent system.

This module implements the AgentOrchestrator, which coordinates the workflow
of all specialized agents. The orchestrator manages the state and agent execution order.
"""

from typing import Dict, Any
from .state import AgentState
from .agents import (
    CodeAnalyzerAgent,
    RequirementsEngineerAgent,
    TestArchitectAgent,
    TestGeneratorAgent,
    QualityAssuranceAgent,
    IntegrationSpecialistAgent,
)

# Optional LangGraph import for advanced workflow
try:
    from langgraph.graph import StateGraph
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None

class AgentOrchestrator:
    """Orchestrator for the AgentOps multi-agent workflow.
    
    This class coordinates the execution of all specialized agents using
    LangGraph's StateGraph. It manages the shared state and agent order.
    """
    def __init__(self):
        self.code_analyzer = CodeAnalyzerAgent()
        self.requirements_engineer = RequirementsEngineerAgent()
        self.test_architect = TestArchitectAgent()
        self.test_generator = TestGeneratorAgent()
        self.quality_assurance = QualityAssuranceAgent()
        self.integration_specialist = IntegrationSpecialistAgent()
        
        # Define the agent workflow order
        self.agent_sequence = [
            self.code_analyzer,
            self.requirements_engineer,
            self.test_architect,
            self.test_generator,
            self.quality_assurance,
            self.integration_specialist,
        ]
    
    def run(self, file_path: str) -> AgentState:
        """Run the multi-agent workflow on the given file.
        
        Args:
            file_path: Path to the source file to analyze and generate tests for
        Returns:
            Final AgentState after all agents have processed
        """
        state = AgentState(file_path=file_path)
        
        for i, agent in enumerate(self.agent_sequence):
            try:
                # Log agent start
                state.add_log("orchestrator", f"starting_agent_{agent.name}", {
                    "agent_index": i,
                    "total_agents": len(self.agent_sequence)
                })
                
                # Process with current agent
                state = agent.process(state)
                
                # Check for errors after each agent
                if state.has_errors():
                    # Attempt error recovery
                    recovery_result = self._attempt_error_recovery(state, agent, i)
                    if recovery_result["recovered"]:
                        state.add_log("orchestrator", f"error_recovery_success", {
                            "agent": agent.name,
                            "recovery_method": recovery_result["method"]
                        })
                        # Clear the recovered errors
                        state.errors = [e for e in state.errors if e not in recovery_result["resolved_errors"]]
                    else:
                        state.add_log("orchestrator", f"error_recovery_failed", {
                            "agent": agent.name,
                            "unresolved_errors": state.errors
                        })
                        break
                
                # Log successful completion
                state.add_log("orchestrator", f"completed_agent_{agent.name}", {
                    "agent_index": i,
                    "success": True
                })
                
            except Exception as e:
                error_msg = f"Critical error in {agent.name}: {str(e)}"
                state.add_error(error_msg)
                state.add_log("orchestrator", f"critical_error_{agent.name}", {
                    "error": error_msg,
                    "agent_index": i
                })
                break
        
        # Save requirements to database if they were extracted
        if state.requirements and not state.has_errors():
            try:
                from ..agentops_core.workflow import AgentOpsWorkflow
                workflow = AgentOpsWorkflow()
                
                for req in state.requirements:
                    # Create and store each requirement in the database
                    requirement = workflow.requirement_store.create_requirement_from_inference(
                        req["text"],
                        file_path,
                        req["confidence"],
                        {"source": req.get("source", "multi_agent_workflow")}
                    )
                    # Actually store it in the database
                    req_id = workflow.requirement_store.store_requirement(requirement)
                
                state.add_log("orchestrator", "requirements_saved_to_db", {
                    "file_path": file_path,
                    "requirements_count": len(state.requirements)
                })
            except Exception as e:
                state.add_error(f"Failed to save requirements to database: {str(e)}")
        
        # Write generated test code to file if available
        if state.test_code and not state.has_errors():
            try:
                self._write_test_file(file_path, state.test_code)
                state.add_log("orchestrator", "test_file_written", {
                    "file_path": file_path,
                    "test_code_length": len(state.test_code)
                })
            except Exception as e:
                state.add_error(f"Failed to write test file: {str(e)}")
        
        return state
    
    def run_with_progress(self, file_path: str, progress, task) -> AgentState:
        """Run the multi-agent workflow with progress updates.
        
        Args:
            file_path: Path to the source file to analyze and generate tests for
            progress: Rich progress object for updates
            task: Progress task ID
        Returns:
            Final AgentState after all agents have processed
        """
        state = AgentState(file_path=file_path)
        
        # Agent descriptions for progress updates
        agent_descriptions = {
            "CodeAnalyzer": "Analyzing code structure and dependencies...",
            "RequirementsEngineer": "Extracting functional requirements...",
            "TestArchitect": "Designing comprehensive test strategy...",
            "TestGenerator": "Generating high-quality test code...",
            "QualityAssurance": "Validating test quality and coverage...",
            "IntegrationSpecialist": "Setting up CI/CD and IDE integrations..."
        }
        
        for i, agent in enumerate(self.agent_sequence):
            try:
                # Update progress with current agent
                agent_desc = agent_descriptions.get(agent.name, f"Running {agent.name}...")
                progress.update(task, description=f"[cyan]{agent_desc}[/cyan]")
                
                # Log agent start
                state.add_log("orchestrator", f"starting_agent_{agent.name}", {
                    "agent_index": i,
                    "total_agents": len(self.agent_sequence)
                })
                
                # Process with current agent
                state = agent.process(state)
                
                # Check for errors after each agent
                if state.has_errors():
                    progress.update(task, description=f"[yellow]Recovering from errors in {agent.name}...[/yellow]")
                    
                    # Attempt error recovery
                    recovery_result = self._attempt_error_recovery(state, agent, i)
                    if recovery_result["recovered"]:
                        state.add_log("orchestrator", f"error_recovery_success", {
                            "agent": agent.name,
                            "recovery_method": recovery_result["method"]
                        })
                        # Clear the recovered errors
                        state.errors = [e for e in state.errors if e not in recovery_result["resolved_errors"]]
                        progress.update(task, description=f"[green]✓ Recovered from errors in {agent.name}[/green]")
                    else:
                        state.add_log("orchestrator", f"error_recovery_failed", {
                            "agent": agent.name,
                            "unresolved_errors": state.errors
                        })
                        progress.update(task, description=f"[red]✗ Failed to recover from errors in {agent.name}[/red]")
                        break
                else:
                    progress.update(task, description=f"[green]✓ Completed {agent.name}[/green]")
                
                # Log successful completion
                state.add_log("orchestrator", f"completed_agent_{agent.name}", {
                    "agent_index": i,
                    "success": True
                })
                
            except Exception as e:
                error_msg = f"Critical error in {agent.name}: {str(e)}"
                state.add_error(error_msg)
                state.add_log("orchestrator", f"critical_error_{agent.name}", {
                    "error": error_msg,
                    "agent_index": i
                })
                progress.update(task, description=f"[red]✗ Critical error in {agent.name}[/red]")
                break
        
        # Save requirements to database if they were extracted
        if state.requirements and not state.has_errors():
            try:
                progress.update(task, description="[cyan]Saving requirements to database...[/cyan]")
                from ..agentops_core.workflow import AgentOpsWorkflow
                workflow = AgentOpsWorkflow()
                
                for req in state.requirements:
                    # Create and store each requirement in the database
                    requirement = workflow.requirement_store.create_requirement_from_inference(
                        req["text"],
                        file_path,
                        req["confidence"],
                        {"source": req.get("source", "multi_agent_workflow")}
                    )
                    # Actually store it in the database
                    req_id = workflow.requirement_store.store_requirement(requirement)
                
                state.add_log("orchestrator", "requirements_saved_to_db", {
                    "file_path": file_path,
                    "requirements_count": len(state.requirements)
                })
                progress.update(task, description="[green]✓ Requirements saved to database[/green]")
            except Exception as e:
                state.add_error(f"Failed to save requirements to database: {str(e)}")
                progress.update(task, description="[red]✗ Failed to save requirements to database[/red]")
        
        # Write generated test code to file if available
        if state.test_code and not state.has_errors():
            try:
                progress.update(task, description="[cyan]Writing test file...[/cyan]")
                self._write_test_file(file_path, state.test_code)
                state.add_log("orchestrator", "test_file_written", {
                    "file_path": file_path,
                    "test_code_length": len(state.test_code)
                })
                progress.update(task, description="[green]✓ Test file written successfully[/green]")
            except Exception as e:
                state.add_error(f"Failed to write test file: {str(e)}")
                progress.update(task, description="[red]✗ Failed to write test file[/red]")
        
        return state
    
    def run_with_graph(self, file_path: str) -> AgentState:
        """Run the multi-agent workflow using LangGraph's StateGraph.
        
        Args:
            file_path: Path to the source file
        Returns:
            Final AgentState
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError(
                "LangGraph is required for run_with_graph method. "
                "Install with: pip install langgraph"
            )
        
        state = AgentState(file_path=file_path)
        graph = StateGraph(AgentState)
        
        # Add each agent as a node in the graph
        for agent in self.agent_sequence:
            graph.add_node(agent.name, agent.process)
        
        # Define the workflow sequence
        for i in range(len(self.agent_sequence) - 1):
            graph.add_edge(self.agent_sequence[i].name, self.agent_sequence[i+1].name)
        
        # Set the entry point
        graph.set_entry_point(self.agent_sequence[0].name)
        
        # Run the graph
        final_state = graph.run(state)
        
        # Write generated test code to file if available
        if final_state.test_code and not final_state.has_errors():
            self._write_test_file(file_path, final_state.test_code)
        
        return final_state
    
    def _write_test_file(self, source_file_path: str, test_code: str):
        """Write generated test code to a file.
        
        Args:
            source_file_path: Path to the source file
            test_code: Generated test code to write
        """
        from pathlib import Path
        import os
        
        # Create test file path that mirrors source directory structure
        source_path = Path(source_file_path)
        relative_path = (
            source_path.relative_to(Path.cwd())
            if source_path.is_absolute()
            else source_path
        )
        test_file_name = f"test_{source_path.name}"
        
        # Mirror the source directory structure in .agentops/tests/
        test_path = Path(".agentops") / "tests" / relative_path.parent / test_file_name
        
        # Ensure test directory exists (including subdirectories)
        os.makedirs(test_path.parent, exist_ok=True)
        
        # Write test code to file
        with open(test_path, "w") as f:
            f.write(test_code)
        
        print(f"DEBUG: Test file written to: {test_path}")

    def _attempt_error_recovery(self, state: AgentState, failed_agent, agent_index: int) -> Dict[str, Any]:
        """Attempt to recover from errors using systematic error analysis.
        
        Args:
            state: Current agent state with errors
            failed_agent: The agent that encountered errors
            agent_index: Index of the failed agent in the sequence
            
        Returns:
            Dictionary with recovery results
        """
        recovery_methods = []
        resolved_errors = []
        
        for error in state.errors:
            recovery_method = self._analyze_and_recover_error(error, state, failed_agent)
            if recovery_method["success"]:
                recovery_methods.append(recovery_method["method"])
                resolved_errors.append(error)
        
        return {
            "recovered": len(resolved_errors) > 0,
            "method": recovery_methods,
            "resolved_errors": resolved_errors,
            "remaining_errors": [e for e in state.errors if e not in resolved_errors]
        }
    
    def _analyze_and_recover_error(self, error: str, state: AgentState, failed_agent) -> Dict[str, Any]:
        """Analyze a specific error and attempt recovery using deterministic methods.
        
        Args:
            error: Error message to analyze
            state: Current agent state
            failed_agent: Agent that generated the error
            
        Returns:
            Recovery result
        """
        error_lower = error.lower()
        
        # Pattern 1: LLM API errors (rate limits, network issues)
        if any(keyword in error_lower for keyword in ["rate limit", "api", "openai", "network", "timeout"]):
            return self._recover_llm_api_error(error, state, failed_agent)
        
        # Pattern 2: JSON parsing errors
        if any(keyword in error_lower for keyword in ["json", "parse", "decode"]):
            return self._recover_json_parsing_error(error, state, failed_agent)
        
        # Pattern 3: File system errors
        if any(keyword in error_lower for keyword in ["file", "permission", "not found", "directory"]):
            return self._recover_filesystem_error(error, state, failed_agent)
        
        # Pattern 4: Code analysis errors
        if any(keyword in error_lower for keyword in ["syntax", "ast", "parse"]):
            return self._recover_code_analysis_error(error, state, failed_agent)
        
        # Pattern 5: Import resolution errors
        if any(keyword in error_lower for keyword in ["import", "module", "dependency"]):
            return self._recover_import_error(error, state, failed_agent)
        
        return {"success": False, "method": "no_recovery_pattern_found"}
    
    def _recover_llm_api_error(self, error: str, state: AgentState, failed_agent) -> Dict[str, Any]:
        """Recover from LLM API errors using fallback strategies."""
        # For API errors, we can provide fallback behavior
        if hasattr(failed_agent, '_generate_fallback_strategy'):
            # TestArchitectAgent has fallback strategy
            if state.analysis and state.requirements:
                fallback_strategy = failed_agent._generate_fallback_strategy(state.analysis, state.requirements)
                state.test_strategy = fallback_strategy
                return {"success": True, "method": "fallback_strategy_generated"}
        
        return {"success": False, "method": "no_llm_fallback_available"}
    
    def _recover_json_parsing_error(self, error: str, state: AgentState, failed_agent) -> Dict[str, Any]:
        """Recover from JSON parsing errors by providing default structures."""
        agent_name = failed_agent.name
        
        if agent_name == "TestArchitect" and not state.test_strategy:
            # Provide minimal test strategy
            state.test_strategy = {
                "framework": "pytest",
                "test_types": ["unit"],
                "coverage_targets": {"unit": 0.80},
                "fixture_strategy": "basic",
                "mocking_strategy": "minimal",
                "priority_order": ["high", "medium"],
                "error_recovery": True
            }
            return {"success": True, "method": "default_test_strategy"}
        
        elif agent_name == "CodeAnalyzer" and not state.analysis:
            # Provide minimal analysis
            state.analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "complexity_insights": "Analysis failed - using defaults",
                "testability_score": 0.5,
                "error_recovery": True
            }
            return {"success": True, "method": "default_code_analysis"}
        
        return {"success": False, "method": "no_json_recovery_available"}
    
    def _recover_filesystem_error(self, error: str, state: AgentState, failed_agent) -> Dict[str, Any]:
        """Recover from file system errors."""
        if "permission" in error.lower():
            # Try to create directories with appropriate permissions
            try:
                import os
                from pathlib import Path
                
                test_dir = Path(".agentops/tests")
                test_dir.mkdir(parents=True, exist_ok=True)
                return {"success": True, "method": "directory_creation_retry"}
            except Exception:
                pass
        
        return {"success": False, "method": "filesystem_error_unrecoverable"}
    
    def _recover_code_analysis_error(self, error: str, state: AgentState, failed_agent) -> Dict[str, Any]:
        """Recover from code analysis errors."""
        if not state.code and state.file_path:
            # Try to reload the file
            try:
                with open(state.file_path, 'r', encoding='utf-8') as f:
                    state.code = f.read()
                return {"success": True, "method": "file_reload"}
            except Exception:
                pass
        
        # Provide minimal analysis if code exists but parsing failed
        if state.code and not state.analysis:
            state.analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "complexity_insights": "Syntax error in source - using minimal analysis",
                "testability_score": 0.3,
                "syntax_error_recovery": True
            }
            return {"success": True, "method": "minimal_analysis_fallback"}
        
        return {"success": False, "method": "code_analysis_unrecoverable"}
    
    def _recover_import_error(self, error: str, state: AgentState, failed_agent) -> Dict[str, Any]:
        """Recover from import resolution errors."""
        # For import errors, we can often continue with basic imports
        if failed_agent.name == "TestGenerator" and state.test_code:
            # Add basic imports if test code exists but has import issues
            basic_imports = "import pytest\nimport unittest\nfrom unittest.mock import Mock, patch\n\n"
            
            if not state.test_code.startswith(("import", "from")):
                state.test_code = basic_imports + state.test_code
                return {"success": True, "method": "basic_imports_added"}
        
        return {"success": False, "method": "import_error_unrecoverable"} 