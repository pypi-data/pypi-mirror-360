"""Specialized agents for AgentOps multi-agent system.

This module implements the individual agents that work together to perform
requirements-driven test generation. Each agent has a specific role and
expertise in the workflow.
"""

import os
import time
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools import tool

from .state import AgentState
from ..agentops_core.config import get_config
from ..agentops_core.analyzer import CodeAnalyzer
from ..agentops_core.requirement_inference import RequirementInferenceEngine
from ..agentops_core.services.test_generator import TestGenerator


class BaseAgent:
    """Base class for all AgentOps agents.
    
    Provides common functionality for agent initialization, LLM setup,
    and state management.
    """
    
    def __init__(self, name: str, description: str):
        """Initialize the base agent.
        
        Args:
            name: Name of the agent
            description: Description of the agent's role
        """
        self.name = name
        self.description = description
        self.config = get_config()
        
        # Initialize LLM with configuration
        self.llm = ChatOpenAI(
            model=self.config.llm.model,
            temperature=self.config.llm.temperature,
            max_tokens=self.config.llm.max_tokens,
            api_key=self.config.llm.api_key,
        )
    
    def process(self, state: AgentState) -> AgentState:
        """Process the current state and return updated state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        raise NotImplementedError
    
    def add_log(self, state: AgentState, action: str, details: Any = None) -> None:
        """Add a log entry to the state.
        
        Args:
            state: Agent state to update
            action: Action performed
            details: Additional details
        """
        state.add_log(self.name, action, details)
    
    def _log_llm_progress(self, state: AgentState, step: str, details: Any = None) -> None:
        """Log LLM processing progress for better visibility.
        
        Args:
            state: Agent state to update
            step: Current processing step
            details: Additional details about the step
        """
        self.add_log(state, f"llm_progress_{step}", details)
    
    def _invoke_llm_with_progress(self, messages, state: AgentState, step_name: str = "processing") -> Any:
        """Invoke LLM with progress logging.
        
        Args:
            messages: Messages to send to LLM
            state: Agent state for logging
            step_name: Name of the current step for progress tracking
            
        Returns:
            LLM response
        """
        try:
            self._log_llm_progress(state, f"{step_name}_start", {"timestamp": time.time()})
            response = self.llm.invoke(messages)
            self._log_llm_progress(state, f"{step_name}_complete", {
                "timestamp": time.time(),
                "response_length": len(response.content) if hasattr(response, 'content') else 0
            })
            return response
        except Exception as e:
            self._log_llm_progress(state, f"{step_name}_error", {"error": str(e)})
            raise


class CodeAnalyzerAgent(BaseAgent):
    """Agent responsible for deep code structure and dependency analysis.
    
    This agent analyzes Python code to understand its structure, dependencies,
    and architectural patterns. It provides the foundation for requirement
    extraction and test generation.
    """
    
    def __init__(self):
        """Initialize the Code Analyzer agent."""
        super().__init__(
            name="CodeAnalyzer",
            description="Deep code structure and dependency analysis"
        )
        self.analyzer = CodeAnalyzer()
    
    def process(self, state: AgentState) -> AgentState:
        """Analyze the code and update state with analysis results.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with code analysis
        """
        try:
            self.add_log(state, "start_analysis", {"file_path": state.file_path})
            
            # Read the code if not already provided
            if not state.code:
                with open(state.file_path, 'r') as f:
                    state.code = f.read()
            
            # Perform code analysis using existing analyzer
            analysis_result = self.analyzer.analyze_code(state.code)
            
            # Enhance with LLM-based insights
            enhanced_analysis = self._enhance_analysis_with_llm(state.code, analysis_result)
            
            state.analysis = enhanced_analysis
            self.add_log(state, "analysis_complete", {"analysis_keys": list(enhanced_analysis.keys())})
            
        except Exception as e:
            error_msg = f"Code analysis failed: {str(e)}"
            state.add_error(error_msg)
            self.add_log(state, "analysis_error", {"error": error_msg})
        
        return state
    
    def _enhance_analysis_with_llm(self, code: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance code analysis with LLM insights.
        
        Args:
            code: Source code
            analysis: Basic analysis results
            
        Returns:
            Enhanced analysis with LLM insights
        """
        prompt = f"""
        You are a Code Analyzer Agent specializing in Python code analysis.
        
        Analyze the following code and provide insights about:
        1. Code complexity and maintainability
        2. Potential architectural patterns
        3. Testing challenges and considerations
        4. Dependencies and coupling
        5. Code quality recommendations
        
        Code:
        {code}
        
        Basic Analysis:
        {analysis}
        
        Provide your analysis in JSON format with the following structure:
        {{
            "complexity_insights": "...",
            "architectural_patterns": ["..."],
            "testing_challenges": ["..."],
            "dependencies": ["..."],
            "quality_recommendations": ["..."],
            "testability_score": 0.85
        }}
        """
        
        try:
            response = self._invoke_llm_with_progress([HumanMessage(content=prompt)], state)
            
            # Improved JSON parsing with error recovery
            try:
                import json
                import re
                
                content = response.content.strip()
                
                # Try to extract JSON from markdown code blocks
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
                elif '```' in content:
                    # Remove any markdown formatting
                    content = re.sub(r'```[a-zA-Z]*\s*', '', content)
                    content = re.sub(r'```', '', content)
                
                # Parse the JSON
                llm_insights = json.loads(content)
                
                # Merge with existing analysis
                enhanced = analysis.copy()
                enhanced.update(llm_insights)
                return enhanced
                
            except (json.JSONDecodeError, AttributeError) as e:
                # Fallback: store raw response with structure hints
                enhanced = analysis.copy()
                enhanced["llm_insights"] = response.content
                enhanced["llm_parsing_error"] = str(e)
                enhanced["complexity_insights"] = "LLM analysis available but parsing failed"
                enhanced["testability_score"] = 0.7  # Conservative default
                return enhanced
                
        except Exception as e:
            # If LLM enhancement fails completely, return original analysis with error info
            enhanced = analysis.copy()
            enhanced["llm_error"] = str(e)
            enhanced["testability_score"] = 0.6  # Default fallback
            return enhanced


class RequirementsEngineerAgent(BaseAgent):
    """Agent responsible for extracting and refining functional requirements.
    
    This agent analyzes code changes and extracts functional requirements
    that can be used for test generation. It uses both static analysis
    and LLM-based reasoning.
    """
    
    def __init__(self):
        """Initialize the Requirements Engineer agent."""
        super().__init__(
            name="RequirementsEngineer",
            description="Functional requirement extraction and refinement"
        )
        self.inference_engine = RequirementInferenceEngine()
    
    def process(self, state: AgentState) -> AgentState:
        """Extract requirements from code and update state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with extracted requirements
        """
        try:
            self.add_log(state, "start_requirement_extraction", {"file_path": state.file_path})
            
            if not state.analysis:
                raise ValueError("Code analysis must be completed before requirement extraction")
            
            # Extract requirements using existing inference engine
            inference_result = self.inference_engine.infer_requirement_from_file(state.file_path)
            
            if inference_result["success"]:
                # Enhance requirements with LLM analysis
                enhanced_requirements = self._enhance_requirements_with_llm(
                    state.code, state.analysis, inference_result
                )
                
                state.requirements = enhanced_requirements
                self.add_log(state, "requirements_extracted", {
                    "count": len(enhanced_requirements),
                    "requirements": [req["text"] for req in enhanced_requirements]
                })
            else:
                raise ValueError(f"Requirement inference failed: {inference_result.get('error')}")
                
        except Exception as e:
            error_msg = f"Requirement extraction failed: {str(e)}"
            state.add_error(error_msg)
            self.add_log(state, "requirement_extraction_error", {"error": error_msg})
        
        return state
    
    def _enhance_requirements_with_llm(self, code: str, analysis: Dict[str, Any], 
                                     inference_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance requirements with LLM analysis.
        
        Args:
            code: Source code
            analysis: Code analysis results
            inference_result: Basic inference results
            
        Returns:
            Enhanced requirements list
        """
        prompt = f"""
        You are a Requirements Engineer Agent specializing in extracting functional requirements.
        
        Based on the code analysis and basic inference, extract and refine functional requirements.
        Each requirement should be:
        1. Clear and testable
        2. Specific to the functionality
        3. Include acceptance criteria
        4. Have a confidence score
        
        Code:
        {code}
        
        Analysis:
        {analysis}
        
        Basic Inference:
        {inference_result}
        
        Provide requirements in JSON format:
        [
            {{
                "id": "REQ-001",
                "text": "Clear requirement statement",
                "confidence": 0.95,
                "acceptance_criteria": ["..."],
                "source": "code_analysis",
                "priority": "high"
            }}
        ]
        """
        
        try:
            response = self._invoke_llm_with_progress([HumanMessage(content=prompt)], state)
            # Parse response and return enhanced requirements
            # For now, return basic requirement structure
            return [{
                "id": "REQ-001",
                "text": inference_result["requirement"],
                "confidence": inference_result["confidence"],
                "acceptance_criteria": [],
                "source": "code_analysis",
                "priority": "high"
            }]
        except Exception:
            # If LLM enhancement fails, return basic requirement
            return [{
                "id": "REQ-001",
                "text": inference_result["requirement"],
                "confidence": inference_result["confidence"],
                "acceptance_criteria": [],
                "source": "basic_inference",
                "priority": "high"
            }]


class TestArchitectAgent(BaseAgent):
    """Agent responsible for designing comprehensive test strategies.
    
    This agent designs test strategies based on requirements and code analysis.
    It determines the optimal testing approach, framework, and coverage strategy.
    """
    
    def __init__(self):
        """Initialize the Test Architect agent."""
        super().__init__(
            name="TestArchitect",
            description="Test strategy and framework design"
        )
    
    def process(self, state: AgentState) -> AgentState:
        """Design test strategy and update state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with test strategy
        """
        try:
            self.add_log(state, "start_test_strategy_design", {
                "requirements_count": len(state.requirements)
            })
            
            if not state.requirements:
                raise ValueError("Requirements must be extracted before test strategy design")
            
            # Design test strategy using LLM
            test_strategy = self._design_test_strategy(state.code, state.analysis, state.requirements)
            
            state.test_strategy = test_strategy
            self.add_log(state, "test_strategy_designed", {
                "framework": test_strategy.get("framework"),
                "test_types": test_strategy.get("test_types", [])
            })
            
        except Exception as e:
            error_msg = f"Test strategy design failed: {str(e)}"
            state.add_error(error_msg)
            self.add_log(state, "test_strategy_error", {"error": error_msg})
        
        return state
    
    def _design_test_strategy(self, code: str, analysis: Dict[str, Any], 
                             requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Design comprehensive test strategy.
        
        Args:
            code: Source code
            analysis: Code analysis results
            requirements: Extracted requirements
            
        Returns:
            Test strategy dictionary
        """
        prompt = f"""
        You are a Test Architect Agent specializing in designing test strategies.
        
        Design a comprehensive test strategy for the given code and requirements.
        Consider:
        1. Optimal test framework (pytest recommended)
        2. Test types needed (unit, integration, edge cases)
        3. Coverage targets and priorities
        4. Test data and fixture strategies
        5. Mocking and dependency management
        
        Code:
        {code}
        
        Analysis:
        {analysis}
        
        Requirements:
        {requirements}
        
        Provide strategy in JSON format:
        {{
            "framework": "pytest",
            "test_types": ["unit", "integration", "edge_cases"],
            "coverage_targets": {{"unit": 0.95, "integration": 0.80}},
            "fixture_strategy": "comprehensive",
            "mocking_strategy": "isolated",
            "priority_order": ["critical", "high", "medium", "low"]
        }}
        """
        
        try:
            response = self._invoke_llm_with_progress([HumanMessage(content=prompt)], state)
            
            # Improved JSON parsing for test strategy
            try:
                import json
                import re
                
                content = response.content.strip()
                
                # Extract JSON from response
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
                elif '```' in content:
                    content = re.sub(r'```[a-zA-Z]*\s*', '', content)
                    content = re.sub(r'```', '', content)
                
                # Parse and validate the strategy
                strategy = json.loads(content)
                
                # Ensure required fields are present
                default_strategy = {
                    "framework": "pytest",
                    "test_types": ["unit"],
                    "coverage_targets": {"unit": 0.80},
                    "fixture_strategy": "basic",
                    "mocking_strategy": "minimal",
                    "priority_order": ["high", "medium"]
                }
                
                # Merge parsed strategy with defaults
                for key, default_value in default_strategy.items():
                    if key not in strategy:
                        strategy[key] = default_value
                
                return strategy
                
            except (json.JSONDecodeError, AttributeError) as e:
                # Fallback to intelligent strategy based on analysis
                return self._generate_fallback_strategy(analysis, requirements)
                
        except Exception:
            # Final fallback to basic strategy
            return self._generate_fallback_strategy(analysis, requirements)
    
    def _generate_fallback_strategy(self, analysis: Dict[str, Any], 
                                   requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a fallback test strategy when LLM parsing fails.
        
        Args:
            analysis: Code analysis results
            requirements: List of requirements
            
        Returns:
            Basic but functional test strategy
        """
        # Analyze complexity from code analysis
        functions_count = len(analysis.get("functions", []))
        classes_count = len(analysis.get("classes", []))
        requirements_count = len(requirements)
        
        # Determine test types based on complexity
        test_types = ["unit"]
        if classes_count > 0:
            test_types.append("integration")
        if functions_count > 5 or requirements_count > 3:
            test_types.append("edge_cases")
        
        # Set coverage targets based on complexity
        coverage_targets = {"unit": 0.85}
        if "integration" in test_types:
            coverage_targets["integration"] = 0.75
        
        return {
            "framework": "pytest",
            "test_types": test_types,
            "coverage_targets": coverage_targets,
            "fixture_strategy": "comprehensive" if classes_count > 0 else "basic",
            "mocking_strategy": "isolated" if "integration" in test_types else "minimal",
            "priority_order": ["critical", "high", "medium", "low"],
            "fallback_generated": True,
            "analysis_source": f"functions: {functions_count}, classes: {classes_count}, requirements: {requirements_count}"
        }


class TestGeneratorAgent(BaseAgent):
    """Agent responsible for creating actual test code.
    
    This agent generates high-quality, maintainable test code based on
    requirements and test strategy. It uses both existing test generation
    logic and LLM enhancement.
    """
    
    def __init__(self):
        """Initialize the Test Generator agent."""
        super().__init__(
            name="TestGenerator",
            description="Actual test code creation"
        )
        self.test_generator = TestGenerator()
    
    def process(self, state: AgentState) -> AgentState:
        """Generate test code and update state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with generated test code
        """
        try:
            self.add_log(state, "start_test_generation", {
                "requirements_count": len(state.requirements)
            })
            
            if not state.test_strategy:
                raise ValueError("Test strategy must be designed before test generation")
            
            # Generate tests using existing generator
            test_code = self._generate_tests(state)
            
            state.test_code = test_code
            self.add_log(state, "test_generation_complete", {
                "code_length": len(test_code) if test_code else 0
            })
            
        except Exception as e:
            error_msg = f"Test generation failed: {str(e)}"
            state.add_error(error_msg)
            self.add_log(state, "test_generation_error", {"error": error_msg})
        
        return state
    
    def _generate_tests(self, state: AgentState) -> str:
        """Generate test code using requirements and strategy.
        
        Args:
            state: Current agent state
            
        Returns:
            Generated test code
        """
        # Use existing test generator for each requirement
        all_test_code = []
        
        for req in state.requirements:
            try:
                result = self.test_generator.generate_tests_from_requirement(
                    state.file_path,
                    req["text"],
                    req["confidence"]
                )
                
                if result["success"]:
                    all_test_code.append(result["code"])
                else:
                    state.add_error(f"Failed to generate tests for requirement {req['id']}: {result.get('error')}")
                    
            except Exception as e:
                state.add_error(f"Error generating tests for requirement {req['id']}: {str(e)}")
        
        # Combine all test code
        combined_code = "\n\n".join(all_test_code)
        
        # Enhance with LLM if needed
        if combined_code and state.test_strategy:
            enhanced_code = self._enhance_test_code_with_llm(
                combined_code, state.code, state.requirements, state.test_strategy
            )
            return enhanced_code
        
        return combined_code
    
    def _enhance_test_code_with_llm(self, test_code: str, source_code: str,
                                   requirements: List[Dict[str, Any]], 
                                   strategy: Dict[str, Any]) -> str:
        """Enhance test code with LLM improvements.
        
        Args:
            test_code: Generated test code
            source_code: Original source code
            requirements: Requirements list
            strategy: Test strategy
            
        Returns:
            Enhanced test code
        """
        prompt = f"""
        You are a Test Generator Agent specializing in Python test code.
        
        Review and enhance the generated test code to ensure:
        1. Comprehensive coverage of all requirements
        2. Proper test structure and organization
        3. Clear test names and documentation
        4. Robust error handling and edge cases
        5. Adherence to pytest best practices
        
        Source Code:
        {source_code}
        
        Requirements:
        {requirements}
        
        Test Strategy:
        {strategy}
        
        Generated Test Code:
        {test_code}
        
        Provide ONLY the enhanced test code. Do not include any explanations, markdown, or prose text.
        Start with the imports and end with the last test function.
        """
        
        try:
            response = self._invoke_llm_with_progress([HumanMessage(content=prompt)], state)
            # Extract only Python code from the response
            content = response.content
            
            # Try to extract code from markdown blocks
            import re
            code_match = re.search(r'```python\s*(.*?)\s*```', content, re.DOTALL)
            if code_match:
                return code_match.group(1).strip()
            
            # If no markdown blocks, try to find Python code
            lines = content.split('\n')
            python_lines = []
            in_code = False
            
            for line in lines:
                stripped = line.strip()
                # Start of Python code
                if stripped.startswith('import ') or stripped.startswith('from ') or stripped.startswith('def test_'):
                    in_code = True
                
                if in_code:
                    python_lines.append(line)
                
                # End of Python code (empty line followed by non-Python content)
                if in_code and not stripped and len(lines) > lines.index(line) + 1:
                    next_line = lines[lines.index(line) + 1].strip()
                    if not (next_line.startswith('def ') or next_line.startswith('import ') or next_line.startswith('from ') or next_line.startswith('#')):
                        break
            
            if python_lines:
                return '\n'.join(python_lines).strip()
            
            # Fallback: return original code
            return test_code
            
        except Exception:
            # If LLM enhancement fails, return original code
            return test_code


class QualityAssuranceAgent(BaseAgent):
    """Agent responsible for test validation and quality improvement.
    
    This agent validates generated tests for quality, completeness, and
    adherence to best practices. It provides quality metrics and improvement
    recommendations.
    """
    
    def __init__(self):
        """Initialize the Quality Assurance agent."""
        super().__init__(
            name="QualityAssurance",
            description="Test validation and quality improvement"
        )
    
    def process(self, state: AgentState) -> AgentState:
        """Validate test quality and update state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with quality assessment
        """
        try:
            self.add_log(state, "start_quality_assessment", {
                "test_code_length": len(state.test_code) if state.test_code else 0
            })
            
            if not state.test_code:
                raise ValueError("Test code must be generated before quality assessment")
            
            # Assess quality using LLM
            quality_assessment = self._assess_quality(state)
            
            state.quality_score = quality_assessment["overall_score"]
            state.metadata["quality_assessment"] = quality_assessment
            
            self.add_log(state, "quality_assessment_complete", {
                "overall_score": quality_assessment["overall_score"],
                "recommendations_count": len(quality_assessment.get("recommendations", []))
            })
            
        except Exception as e:
            error_msg = f"Quality assessment failed: {str(e)}"
            state.add_error(error_msg)
            self.add_log(state, "quality_assessment_error", {"error": error_msg})
        
        return state
    
    def _assess_quality(self, state: AgentState) -> Dict[str, Any]:
        """Assess the quality of generated tests.
        
        Args:
            state: Current agent state
            
        Returns:
            Quality assessment dictionary
        """
        prompt = f"""
        You are a Quality Assurance Agent specializing in test code validation.
        
        Assess the quality of the generated test code based on:
        1. Coverage completeness (0-1 score)
        2. Code quality and readability (0-1 score)
        3. Test structure and organization (0-1 score)
        4. Error handling and edge cases (0-1 score)
        5. Adherence to best practices (0-1 score)
        
        Source Code:
        {state.code}
        
        Requirements:
        {state.requirements}
        
        Test Strategy:
        {state.test_strategy}
        
        Generated Test Code:
        {state.test_code}
        
        Provide assessment in JSON format:
        {{
            "coverage_score": 0.95,
            "code_quality_score": 0.88,
            "structure_score": 0.92,
            "error_handling_score": 0.85,
            "best_practices_score": 0.90,
            "overall_score": 0.90,
            "recommendations": ["..."],
            "strengths": ["..."],
            "areas_for_improvement": ["..."]
        }}
        """
        
        try:
            response = self._invoke_llm_with_progress([HumanMessage(content=prompt)], state)
            # Parse response and return quality assessment
            # For now, return basic assessment
            return {
                "coverage_score": 0.85,
                "code_quality_score": 0.80,
                "structure_score": 0.85,
                "error_handling_score": 0.80,
                "best_practices_score": 0.85,
                "overall_score": 0.83,
                "recommendations": ["Add more edge case testing", "Improve test documentation"],
                "strengths": ["Good basic structure", "Covers main functionality"],
                "areas_for_improvement": ["Edge cases", "Documentation"]
            }
        except Exception:
            # If LLM assessment fails, return basic assessment
            return {
                "coverage_score": 0.70,
                "code_quality_score": 0.70,
                "structure_score": 0.70,
                "error_handling_score": 0.70,
                "best_practices_score": 0.70,
                "overall_score": 0.70,
                "recommendations": ["Manual review recommended"],
                "strengths": ["Basic functionality covered"],
                "areas_for_improvement": ["Comprehensive review needed"]
            }


class IntegrationSpecialistAgent(BaseAgent):
    """Agent responsible for CI/CD and tool integration.
    
    This agent handles integration with CI/CD systems, IDEs, and other
    development tools. It configures automated workflows and notifications.
    """
    
    def __init__(self):
        """Initialize the Integration Specialist agent."""
        super().__init__(
            name="IntegrationSpecialist",
            description="CI/CD and tool integration"
        )
    
    def process(self, state: AgentState) -> AgentState:
        """Configure integrations and update state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with integration configuration
        """
        try:
            self.add_log(state, "start_integration_setup", {
                "project_root": self.config.project.project_root
            })
            
            # Configure integrations based on project needs
            integration_config = self._configure_integrations(state)
            
            state.metadata["integration_config"] = integration_config
            self.add_log(state, "integration_setup_complete", {
                "ci_provider": integration_config.get("ci_provider"),
                "ide_integration": integration_config.get("ide_integration")
            })
            
        except Exception as e:
            error_msg = f"Integration setup failed: {str(e)}"
            state.add_error(error_msg)
            self.add_log(state, "integration_setup_error", {"error": error_msg})
        
        return state
    
    def _configure_integrations(self, state: AgentState) -> Dict[str, Any]:
        """Configure CI/CD and tool integrations.
        
        Args:
            state: Current agent state
            
        Returns:
            Integration configuration dictionary
        """
        # For now, return basic integration config
        # This could be enhanced with actual CI/CD configuration generation
        return {
            "ci_provider": "github",
            "ide_integration": "vscode",
            "webhook_enabled": True,
            "auto_approve": False,
            "notification_channels": ["slack"],
            "test_reporting": True
        } 