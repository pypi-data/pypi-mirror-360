"""AgentOps workflow module.

Implements the main orchestration logic for requirements-driven test automation.
"""

import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
import time
from rich.console import Console
from rich.panel import Panel
from datetime import datetime

from .requirement_inference import RequirementInferenceEngine
from .requirement_store import RequirementStore, Requirement
from .analyzer import analyze_file_with_parents, ProjectAnalyzer, analyze_project_structure
from .terminal_ui import TerminalUI
from .services.test_generator import TestGenerator
from .config import get_config


class AgentOpsWorkflow:
    """Main workflow orchestrator for AgentOps MVP."""

    def __init__(self):
        """Initialize the workflow with all components."""
        config = get_config()
        self.inference_engine = RequirementInferenceEngine()
        self.requirement_store = RequirementStore()
        self.terminal_ui = TerminalUI()
        self.test_generator = TestGenerator()
        self.project_analyzer: Optional[ProjectAnalyzer] = None
        self.config = config

    def _ensure_project_analyzed(self):
        """Ensure the project has been analyzed for structure and imports."""
        if self.project_analyzer is None:
            self.project_analyzer = analyze_project_structure(self.config.project.project_root)
            # Also set the analyzer in the test generator
            self.test_generator.project_analyzer = self.project_analyzer

    def process_file_change(self, file_path: str, interactive: bool = True) -> Dict[str, Any]:
        """Process a file change through the complete workflow.

        This is the main entry point for the Infer -> Approve -> Test workflow.

        Args:
            file_path: Path to the changed Python file
            interactive: Whether to use interactive approval workflow

        Returns:
            Dictionary with workflow results
        """
        # Step 1: Infer requirement from file changes
        inference_result = self.inference_engine.infer_requirement_from_file(file_path)

        if not inference_result["success"]:
            return {
                "success": False,
                "step": "inference",
                "error": inference_result["error"],
            }

        if interactive:
            # Step 2: HITL approval
            approval_result = self._handle_requirement_approval(
                inference_result["requirement"],
                file_path,
                inference_result["confidence"],
                inference_result.get("metadata", {}),
            )

            if not approval_result["success"]:
                return {
                    "success": False,
                    "step": "approval",
                    "error": approval_result.get("error", "User cancelled"),
                }

            # Step 3: Store approved requirement
            requirement = self.requirement_store.create_requirement_from_inference(
                approval_result["requirement_text"],
                file_path,
                inference_result["confidence"],
                inference_result.get("metadata", {}),
            )

            requirement.status = "approved"
            requirement_id = self.requirement_store.store_requirement(requirement)

            # Step 4: Generate tests based on approved requirement
            test_result = self._generate_tests_from_requirement(requirement)

            if not test_result["success"]:
                return {
                    "success": False,
                    "step": "test_generation",
                    "error": test_result["error"],
                }

            return {
                "success": True,
                "requirement_id": requirement_id,
                "requirement_text": approval_result["requirement_text"],
                "test_file": test_result["test_file"],
                "confidence": inference_result["confidence"],
            }
        else:
            # Non-interactive mode: Store as pending requirement
            requirement = self.requirement_store.create_requirement_from_inference(
                inference_result["requirement"],
                file_path,
                inference_result["confidence"],
                inference_result.get("metadata", {}),
            )

            requirement.status = "pending"
            requirement_id = self.requirement_store.store_requirement(requirement)

            return {
                "success": True,
                "requirement_id": requirement_id,
                "requirement_text": inference_result["requirement"],
                "confidence": inference_result["confidence"],
                "requirements_count": 1,
            }

    def _handle_requirement_approval(
        self,
        requirement_text: str,
        file_path: str,
        confidence: float,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle the human-in-the-loop requirement approval process.

        Args:
            requirement_text: Inferred requirement text
            file_path: Path to the file
            confidence: Confidence score
            metadata: Additional metadata

        Returns:
            Approval result dictionary
        """
        while True:
            # Show approval dialog
            choice = self.terminal_ui.show_requirement_approval(
                requirement_text, file_path, confidence, metadata
            )

            if choice == "approve":
                # Confirm approval
                if self.terminal_ui.show_approval_confirmation(requirement_text):
                    self.terminal_ui.show_success_message("approved", requirement_text)
                    return {
                        "success": True,
                        "requirement_text": requirement_text,
                        "action": "approved",
                    }
                else:
                    continue  # Go back to main approval dialog

            elif choice == "edit":
                # Edit requirement text
                edited_text = self.terminal_ui.edit_requirement_text(requirement_text)
                if edited_text:
                    # Confirm the edited requirement
                    if self.terminal_ui.show_approval_confirmation(edited_text):
                        self.terminal_ui.show_success_message("edited", edited_text)
                        return {
                            "success": True,
                            "requirement_text": edited_text,
                            "action": "edited",
                        }
                    else:
                        requirement_text = (
                            edited_text  # Keep the edit for next iteration
                        )
                        continue
                else:
                    continue  # No edit made, go back to main dialog

            elif choice == "reject":
                # Confirm rejection
                if self.terminal_ui.show_rejection_confirmation(requirement_text):
                    self.terminal_ui.show_success_message("rejected", requirement_text)
                    return {
                        "success": False,
                        "requirement_text": requirement_text,
                        "action": "rejected",
                    }
                else:
                    continue  # Go back to main approval dialog

            elif choice == "quit":
                return {"success": False, "action": "quit"}

    def _generate_tests_from_requirement(
        self, requirement: Requirement, force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """Generate tests from a specific requirement.

        Args:
            requirement: The requirement to generate tests for
            force_regenerate: Force regeneration of existing tests

        Returns:
            Dictionary with generation results
        """
        try:
            # Check if test file already exists
            test_file_path = self._get_test_file_path(requirement.file_path)
            
            if os.path.exists(test_file_path) and not force_regenerate:
                return {
                    "success": True,
                    "test_file": test_file_path,
                    "message": "Test file already exists (use --force-regenerate to overwrite)",
                }

            # Ensure project is analyzed
            self._ensure_project_analyzed()
            
            # Use the requirement-based test generation with requirement ID
            result = self.test_generator.generate_tests_from_requirement(
                requirement.file_path,
                requirement.requirement_text,
                requirement.confidence,
                requirement.id  # Pass requirement ID for traceability
            )

            if result["success"]:
                # Determine test file path
                test_file_path = self._get_test_file_path(requirement.file_path)

                # Ensure test directory exists
                os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

                # Write test file (always overwrite when force_regenerate is True)
                with open(test_file_path, "w") as f:
                    f.write(result["code"])

                return {
                    "success": True,
                    "test_file": test_file_path,
                    "code": result["code"],
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Test generation failed"),
                }

        except Exception as e:
            return {"success": False, "error": f"Test generation error: {str(e)}"}

    def _get_test_file_path(self, file_path: str) -> str:
        """Get the test file path for a given source file.

        Args:
            file_path: Path to the source file

        Returns:
            Path to the corresponding test file
        """
        # Convert to Path object for easier manipulation
        source_path = Path(file_path)

        # Create test file path in .agentops/tests directory that mirrors source structure
        relative_path = (
            source_path.relative_to(Path.cwd())
            if source_path.is_absolute()
            else source_path
        )
        test_file_name = f"test_{source_path.name}"

        # Mirror the source directory structure in .agentops/tests/
        test_path = Path(".agentops") / "tests" / relative_path.parent / test_file_name

        return str(test_path)

    def run_tests_with_rca(self, test_file: str = None) -> Dict[str, Any]:
        """Run tests and provide root cause analysis for failures.

        Args:
            test_file: Optional specific test file to run

        Returns:
            Test results with root cause analysis
        """
        import subprocess
        import json

        # Determine test target
        if test_file:
            test_target = test_file
        else:
            test_target = ".agentops/tests"

        # Run pytest with JSON output
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    test_target,
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=.agentops/test_results.json",
                ],
                capture_output=True,
                text=True,
            )

            # Parse test results
            results_file = ".agentops/test_results.json"
            if os.path.exists(results_file):
                with open(results_file) as f:
                    test_results = json.load(f)
            else:
                test_results = {"tests": []}

            # Analyze failures
            failures = []
            for test in test_results.get("tests", []):
                if test.get("outcome") == "failed":
                    failures.append(
                        {
                            "test_name": test.get("nodeid", "unknown"),
                            "failure_message": test.get("call", {}).get(
                                "longrepr", "Unknown failure"
                            ),
                        }
                    )

            if failures:
                # Show root cause analysis for failures
                self._show_root_cause_analysis_for_failures(failures)

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "failures": failures,
                "total_tests": len(test_results.get("tests", [])),
                "failed_tests": len(failures),
            }

        except Exception as e:
            return {"success": False, "error": f"Test execution failed: {str(e)}"}

    def run_tests_for_file(self, file_path: str) -> Dict[str, Any]:
        """Run tests for a specific source file.

        Args:
            file_path: Path to the source file

        Returns:
            Test results with root cause analysis
        """
        # Get the test file path for this source file
        test_file = self._get_test_file_path(file_path)

        # Check if test file exists
        if not os.path.exists(test_file):
            return {
                "success": False,
                "error": f"No tests found for {file_path}. Run 'agentops infer {file_path}' first.",
            }

        # Run tests for this specific file
        return self.run_tests_with_rca(test_file)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests in the .agentops/tests directory.

        Returns:
            Test results with root cause analysis
        """
        return self.run_tests_with_rca()

    def _show_root_cause_analysis_for_failures(self, failures: List[Dict[str, Any]]):
        """Show root cause analysis for test failures.

        Args:
            failures: List of test failures
        """
        for failure in failures:
            # Try to find the corresponding requirement
            test_name = failure["test_name"]

            # Extract file path from test name
            if "::" in test_name:
                test_file = test_name.split("::")[0]
                # Convert test file back to source file
                source_file = self._get_source_file_from_test(test_file)

                if source_file:
                    # Get approved requirements for this file
                    requirements = self.requirement_store.get_requirements_for_file(
                        source_file, status="approved"
                    )

                    if requirements:
                        # Show RCA for the most recent requirement
                        requirement = requirements[0]
                        self.terminal_ui.show_root_cause_analysis(
                            requirement, failure["failure_message"]
                        )

    def _get_source_file_from_test(self, test_file: str) -> Optional[str]:
        """Get the source file path from a test file path.

        Args:
            test_file: Path to the test file

        Returns:
            Path to the source file or None
        """
        # Convert test file path back to source file path
        test_path = Path(test_file)

        # Remove .agentops/tests prefix
        if test_path.parts[:2] == (".agentops", "tests"):
            relative_path = Path(*test_path.parts[2:])

            # Remove test_ prefix from filename
            if relative_path.name.startswith("test_"):
                source_name = relative_path.name[5:]  # Remove "test_"
                source_path = relative_path.parent / source_name

                # Try to find the source file in the current directory
                if source_path.exists():
                    return str(source_path)
                
                # If not found, try looking in the current working directory
                cwd_source_path = Path.cwd() / source_path
                if cwd_source_path.exists():
                    return str(cwd_source_path)
                
                # Try looking for the file with .py extension if not present
                if not source_path.suffix:
                    source_path = source_path.with_suffix('.py')
                    if source_path.exists():
                        return str(source_path)
                    
                    cwd_source_path = Path.cwd() / source_path
                    if cwd_source_path.exists():
                        return str(cwd_source_path)

        return None

    def process_pending_requirements(self) -> Dict[str, Any]:
        """Process all pending requirements through the approval workflow.

        Returns:
            Summary of processing results
        """
        pending_requirements = self.requirement_store.get_pending_requirements()

        if not pending_requirements:
            self.terminal_ui.show_pending_requirements([])
            return {"success": True, "processed": 0}

        # Show pending requirements
        self.terminal_ui.show_pending_requirements(pending_requirements)

        approved_count = 0
        rejected_count = 0

        for requirement in pending_requirements:
            # Process each pending requirement
            approval_result = self._handle_requirement_approval(
                requirement.requirement_text,
                requirement.file_path,
                requirement.confidence,
                requirement.metadata,
            )

            if approval_result["success"]:
                # Update requirement status
                if approval_result["action"] == "approved":
                    self.requirement_store.approve_requirement(requirement.id)
                    approved_count += 1

                    # Generate tests
                    test_result = self._generate_tests_from_requirement(requirement)
                    if not test_result["success"]:
                        self.terminal_ui.show_error_message(
                            f"Failed to generate tests: {test_result['error']}"
                        )
                elif approval_result["action"] == "edited":
                    # Update requirement text and approve
                    self.requirement_store.update_requirement_text(
                        requirement.id, approval_result["requirement_text"]
                    )
                    self.requirement_store.approve_requirement(requirement.id)
                    approved_count += 1

                    # Generate tests with updated requirement
                    updated_requirement = self.requirement_store.get_requirement(
                        requirement.id
                    )
                    test_result = self._generate_tests_from_requirement(
                        updated_requirement
                    )
                    if not test_result["success"]:
                        self.terminal_ui.show_error_message(
                            f"Failed to generate tests: {test_result['error']}"
                        )
            else:
                if approval_result["action"] == "rejected":
                    self.requirement_store.reject_requirement(requirement.id)
                    rejected_count += 1

        return {
            "success": True,
            "processed": len(pending_requirements),
            "approved": approved_count,
            "rejected": rejected_count,
        }

    def show_stats(self):
        """Show requirement statistics."""
        stats = self.requirement_store.get_stats()
        self.terminal_ui.show_requirement_stats(stats)

    def export_requirements_for_editing(self) -> Dict[str, Any]:
        """Export all requirements to an editable Gherkin format file.

        Returns:
            Dictionary with success status, file path, and count
        """
        try:
            # Get all requirements
            all_requirements = self.requirement_store.get_all_requirements()

            if not all_requirements:
                return {
                    "success": False,
                    "error": "No requirements found to export. Run 'agentops infer' first.",
                }

            # Create requirements file in Gherkin format
            requirements_file = ".agentops/requirements.gherkin"

            with open(requirements_file, "w") as f:
                f.write("# AgentOps Requirements File\n")
                f.write(
                    "# Edit this file to modify requirements, then run 'agentops import-requirements'\n\n"
                )

                # Group requirements by file
                files_requirements = {}
                for req in all_requirements:
                    if req.file_path not in files_requirements:
                        files_requirements[req.file_path] = []
                    files_requirements[req.file_path].append(req)

                # Write requirements in Gherkin format
                for file_path, requirements in files_requirements.items():
                    f.write(f"# File: {file_path}\n")
                    f.write(f"Feature: {os.path.basename(file_path)} functionality\n\n")

                    for req in requirements:
                        f.write(f"  # Requirement ID: {req.id}\n")
                        f.write(f"  # Status: {req.status}\n")
                        f.write(f"  # Confidence: {req.confidence:.1%}\n")
                        f.write(f"  Scenario: {req.requirement_text}\n")
                        f.write(f"    Given the {os.path.basename(file_path)} module\n")
                        f.write("    When I use the functionality\n")
                        f.write(
                            f"    Then it should {req.requirement_text.lower()}\n\n"
                        )

                    f.write("\n")

            return {
                "success": True,
                "file_path": requirements_file,
                "count": len(all_requirements),
            }

        except Exception as e:
            return {"success": False, "error": f"Export failed: {str(e)}"}

    def import_and_clarify_requirements(self, requirements_file: str) -> Dict[str, Any]:
        """Import edited requirements file and run clarification workflow.

        Args:
            requirements_file: Path to the edited Gherkin requirements file

        Returns:
            Dictionary with import results
        """
        try:
            # Parse the Gherkin file
            parsed_requirements = self._parse_gherkin_requirements(requirements_file)

            if not parsed_requirements:
                return {
                    "success": False,
                    "error": "No valid requirements found in the file",
                }

            imported_count = 0
            clarified_count = 0
            updated_count = 0

            # Process each parsed requirement
            for req_data in parsed_requirements:
                # Check if requirement exists (by ID if present)
                if req_data.get("id"):
                    existing_req = self.requirement_store.get_requirement(
                        req_data["id"]
                    )
                    if existing_req:
                        # Update existing requirement if text changed
                        if (
                            existing_req.requirement_text
                            != req_data["requirement_text"]
                        ):
                            self.requirement_store.update_requirement_text(
                                req_data["id"], req_data["requirement_text"]
                            )
                            updated_count += 1
                        continue

                # Create new requirement
                requirement = self.requirement_store.create_requirement_from_inference(
                    requirement_text=req_data["requirement_text"],
                    file_path=req_data["file_path"],
                    confidence=req_data.get("confidence", 0.9),
                    metadata=req_data.get("metadata", {}),
                )

                # Run clarification if needed
                clarification_result = self._run_clarification_workflow(requirement)
                if clarification_result["clarified"]:
                    requirement.requirement_text = clarification_result[
                        "clarified_text"
                    ]
                    clarified_count += 1

                # Store the requirement as approved (since it was manually edited)
                requirement.status = "approved"
                self.requirement_store.store_requirement(requirement)
                imported_count += 1

            return {
                "success": True,
                "imported_count": imported_count,
                "clarified_count": clarified_count,
                "updated_count": updated_count,
            }

        except Exception as e:
            return {"success": False, "error": f"Import failed: {str(e)}"}

    def generate_tests_from_requirements(self) -> Dict[str, Any]:
        """Generate tests from all approved requirements.

        Returns:
            Dictionary with generation results
        """
        try:
            # Get all approved requirements
            approved_requirements = self.requirement_store.get_approved_requirements()

            if not approved_requirements:
                return {
                    "success": False,
                    "error": "No approved requirements found. Run 'agentops import-requirements' first.",
                }

            processed_count = 0
            test_files_created = 0
            test_files = []

            # Group requirements by file
            files_requirements = {}
            for req in approved_requirements:
                if req.file_path not in files_requirements:
                    files_requirements[req.file_path] = []
                files_requirements[req.file_path].append(req)

            # Generate tests for each file
            for file_path, requirements in files_requirements.items():
                for requirement in requirements:
                    test_result = self._generate_tests_from_requirement(requirement)
                    if test_result["success"]:
                        if test_result.get("test_file") not in test_files:
                            test_files.append(test_result["test_file"])
                            test_files_created += 1
                    processed_count += 1

            return {
                "success": True,
                "processed_count": processed_count,
                "test_files_created": test_files_created,
                "test_files": test_files,
            }

        except Exception as e:
            return {"success": False, "error": f"Test generation failed: {str(e)}"}

    def generate_tests_from_requirements_filtered(
        self, include_patterns: List[str] = None, exclude_patterns: List[str] = None, force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """Generate tests from approved requirements with folder filtering.

        Args:
            include_patterns: Only generate tests for files matching these patterns
            exclude_patterns: Exclude files matching these patterns from test generation
            force_regenerate: Force regeneration of existing tests

        Returns:
            Dictionary with generation results
        """
        try:
            # Get all approved requirements
            approved_requirements = self.requirement_store.get_approved_requirements()

            if not approved_requirements:
                return {
                    "success": False,
                    "error": "No approved requirements found. Run 'agentops import-requirements' first.",
                }

            # Filter requirements based on include/exclude patterns
            filtered_requirements = []
            for req in approved_requirements:
                file_path = req.file_path
                
                # Check exclude patterns first
                if exclude_patterns:
                    if any(pattern in file_path for pattern in exclude_patterns):
                        continue
                
                # Check include patterns
                if include_patterns:
                    if not any(pattern in file_path for pattern in include_patterns):
                        continue
                
                filtered_requirements.append(req)

            if not filtered_requirements:
                return {
                    "success": False,
                    "error": f"No approved requirements match the specified patterns. "
                            f"Include patterns: {include_patterns}, Exclude patterns: {exclude_patterns}",
                }

            processed_count = 0
            test_files_created = 0
            test_files = []

            # Group requirements by file
            files_requirements = {}
            for req in filtered_requirements:
                if req.file_path not in files_requirements:
                    files_requirements[req.file_path] = []
                files_requirements[req.file_path].append(req)

            # Generate tests for each file
            for file_path, requirements in files_requirements.items():
                for requirement in requirements:
                    test_result = self._generate_tests_from_requirement(requirement, force_regenerate=force_regenerate)
                    if test_result["success"]:
                        if test_result.get("test_file") not in test_files:
                            test_files.append(test_result["test_file"])
                            test_files_created += 1
                    processed_count += 1

            return {
                "success": True,
                "processed_count": processed_count,
                "test_files_created": test_files_created,
                "test_files": test_files,
            }

        except Exception as e:
            return {"success": False, "error": f"Test generation failed: {str(e)}"}

    def _parse_gherkin_requirements(
        self, requirements_file: str
    ) -> List[Dict[str, Any]]:
        """Parse the Gherkin requirements file.

        Args:
            requirements_file: Path to the Gherkin file

        Returns:
            List of parsed requirement dictionaries
        """
        requirements = []
        current_file = None
        current_req = {}

        try:
            with open(requirements_file, "r") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    # Extract metadata from comments
                    if line.startswith("# File:"):
                        current_file = line.replace("# File:", "").strip()
                    elif line.startswith("# Requirement ID:"):
                        current_req["id"] = int(
                            line.replace("# Requirement ID:", "").strip()
                        )
                    elif line.startswith("# Confidence:"):
                        conf_str = (
                            line.replace("# Confidence:", "").strip().replace("%", "")
                        )
                        current_req["confidence"] = float(conf_str) / 100.0
                    continue

                # Parse Gherkin elements
                if line.startswith("Feature:"):
                    continue
                elif line.startswith("Scenario:"):
                    # Extract requirement text from scenario
                    requirement_text = line.replace("Scenario:", "").strip()
                    current_req["requirement_text"] = requirement_text
                    current_req["file_path"] = current_file
                elif (
                    line.startswith("Given")
                    or line.startswith("When")
                    or line.startswith("Then")
                ):
                    # End of scenario - save requirement
                    if current_req.get("requirement_text") and current_req.get(
                        "file_path"
                    ):
                        requirements.append(current_req.copy())
                        current_req = {}

            return requirements

        except Exception as e:
            raise Exception(f"Failed to parse Gherkin file: {str(e)}")

    def _run_clarification_workflow(self, requirement: "Requirement") -> Dict[str, Any]:
        """Run LLM-based clarification for a requirement.

        Args:
            requirement: Requirement object to clarify

        Returns:
            Dictionary with clarification results
        """
        try:
            # Load clarification prompt from file
            clarification_prompt = self._load_prompt(
                "requirement_clarification.txt"
            ).format(
                requirement_text=requirement.requirement_text,
                file_path=requirement.file_path,
            )

            # Use the requirement inference engine to clarify
            clarified_text = self.requirement_inference.infer_requirement(
                requirement.file_path, clarification_prompt
            )

            # Check if clarification actually improved the requirement
            if (
                clarified_text
                and clarified_text.strip() != requirement.requirement_text.strip()
            ):
                # Show clarification to user for approval
                approval = self.terminal_ui.show_clarification_approval(
                    original=requirement.requirement_text,
                    clarified=clarified_text,
                    file_path=requirement.file_path,
                )

                if approval:
                    return {"clarified": True, "clarified_text": clarified_text}

            return {"clarified": False, "clarified_text": requirement.requirement_text}

        except Exception:
            # If clarification fails, use original text
            return {"clarified": False, "clarified_text": requirement.requirement_text}

    def _load_prompt(self, prompt_file: str) -> str:
        """Load a prompt from the prompts directory.

        Args:
            prompt_file: Name of the prompt file

        Returns:
            Prompt content as string
        """
        prompt_path = Path(__file__).parent.parent / "prompts" / prompt_file
        try:
            with open(prompt_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            # Fallback to hardcoded prompt if file not found
            return (
                "Please review and clarify this requirement for better test generation."
            )

    def approve_all_pending_requirements(self) -> Dict[str, Any]:
        """Approve all pending requirements without interactive review.

        This method automatically approves all pending requirements and generates
        tests for them. This is useful for bulk processing when the user trusts
        the inferred requirements.

        Returns:
            Summary of processing results
        """
        pending_requirements = self.requirement_store.get_pending_requirements()

        if not pending_requirements:
            return {"success": True, "processed": 0, "approved": 0, "rejected": 0}

        total_requirements = len(pending_requirements)
        approved_count = 0
        rejected_count = 0
        start_time = time.time()

        print(f"\n[AgentOps] Starting bulk approval of {total_requirements} pending requirements...")
        print(f"[AgentOps] This may take a while depending on the number of requirements and test generation time.\n")

        for i, requirement in enumerate(pending_requirements, 1):
            try:
                requirement_start_time = time.time()
                print(f"[AgentOps] Processing requirement {i}/{total_requirements}: {requirement.file_path}")
                print(f"  Text: {requirement.requirement_text[:100]}{'...' if len(requirement.requirement_text) > 100 else ''}")
                
                # Auto-approve the requirement
                self.requirement_store.approve_requirement(requirement.id)
                approved_count += 1
                print(f"  ✓ Approved requirement {requirement.id}")

                # Generate tests for the approved requirement
                print(f"  Generating tests...")
                test_result = self._generate_tests_from_requirement(requirement)
                if test_result["success"]:
                    print(f"  ✓ Tests generated successfully: {test_result.get('test_file', 'Unknown')}")
                else:
                    print(f"  ⚠ Warning: Failed to generate tests: {test_result['error']}")

                requirement_time = time.time() - requirement_start_time
                elapsed_time = time.time() - start_time
                avg_time_per_req = elapsed_time / i
                estimated_remaining = avg_time_per_req * (total_requirements - i)
                
                print(f"  Progress: {i}/{total_requirements} ({i/total_requirements*100:.1f}%)")
                print(f"  Time: {requirement_time:.1f}s | Elapsed: {elapsed_time:.1f}s | ETA: {estimated_remaining:.1f}s\n")

            except Exception as e:
                print(f"  ✗ Error processing requirement {requirement.id}: {str(e)}")
                rejected_count += 1
                elapsed_time = time.time() - start_time
                print(f"  Progress: {i}/{total_requirements} ({i/total_requirements*100:.1f}%)")
                print(f"  Elapsed time: {elapsed_time:.1f}s\n")

        total_time = time.time() - start_time
        print(f"[AgentOps] Bulk approval completed!")
        print(f"  Total processed: {total_requirements}")
        print(f"  Successfully approved: {approved_count}")
        print(f"  Failed/rejected: {rejected_count}")
        print(f"  Success rate: {approved_count/total_requirements*100:.1f}%")
        print(f"  Total time: {total_time:.1f}s")
        print(f"  Average time per requirement: {total_time/total_requirements:.1f}s")

        return {
            "success": True,
            "processed": total_requirements,
            "approved": approved_count,
            "rejected": rejected_count,
        }

    def approve_all_pending_requirements_fast(self) -> Dict[str, Any]:
        """Approve all pending requirements efficiently without individual test generation.

        This method approves all requirements first, then generates tests in batch.
        This is much faster than the interactive version.

        Returns:
            Summary of processing results
        """
        pending_requirements = self.requirement_store.get_pending_requirements()

        if not pending_requirements:
            return {"success": True, "processed": 0, "approved": 0, "rejected": 0}

        total_requirements = len(pending_requirements)
        approved_count = 0
        rejected_count = 0
        start_time = time.time()

        print(f"\n[AgentOps] Starting fast bulk approval of {total_requirements} pending requirements...")
        print(f"[AgentOps] Approving all requirements first, then generating tests in batch.\n")

        # Step 1: Approve all requirements quickly
        print("[AgentOps] Step 1: Approving all requirements...")
        for i, requirement in enumerate(pending_requirements, 1):
            try:
                self.requirement_store.approve_requirement(requirement.id)
                approved_count += 1
                print(f"  ✓ Approved requirement {requirement.id} ({i}/{total_requirements})")
            except Exception as e:
                print(f"  ✗ Error approving requirement {requirement.id}: {str(e)}")
                rejected_count += 1

        approval_time = time.time() - start_time
        print(f"[AgentOps] Requirements approval completed in {approval_time:.1f}s")
        print(f"[AgentOps] Approved: {approved_count}, Failed: {rejected_count}\n")

        # Step 2: Generate tests in batch (optional - can be done separately)
        print("[AgentOps] Step 2: Test generation can be done separately with step 4")
        print("[AgentOps] Use 'agentops generate-tests' or run step 4 in the runner script\n")

        total_time = time.time() - start_time
        print(f"[AgentOps] Fast bulk approval completed!")
        print(f"  Total processed: {total_requirements}")
        print(f"  Successfully approved: {approved_count}")
        print(f"  Failed/rejected: {rejected_count}")
        print(f"  Success rate: {approved_count/total_requirements*100:.1f}%")
        print(f"  Total time: {total_time:.1f}s")

        return {
            "success": True,
            "processed": total_requirements,
            "approved": approved_count,
            "rejected": rejected_count,
        }

    def generate_traceability_matrix(self, output_format: str = "markdown") -> Dict[str, Any]:
        """Generate a traceability matrix linking requirements to test cases.

        Args:
            output_format: Output format ('markdown', 'csv', 'json')

        Returns:
            Dictionary with success status and file path
        """
        try:
            # Get all approved requirements
            approved_requirements = self.requirement_store.get_approved_requirements()
            
            if not approved_requirements:
                return {
                    "success": False,
                    "error": "No approved requirements found. Run 'agentops infer' first.",
                }

            # Build traceability matrix
            traceability_data = []
            
            for requirement in approved_requirements:
                # Get test file path for this requirement
                test_file_path = self._get_test_file_path(requirement.file_path)
                
                # Check if test file exists
                test_exists = os.path.exists(test_file_path)
                
                # Extract test functions if file exists
                test_functions = []
                if test_exists:
                    try:
                        with open(test_file_path, 'r') as f:
                            test_content = f.read()
                        
                        # Extract test function names using regex
                        import re
                        test_function_matches = re.findall(r'def (test_\w+)', test_content)
                        test_functions = test_function_matches
                    except Exception as e:
                        test_functions = [f"Error reading test file: {str(e)}"]
                
                # Add to traceability data
                traceability_data.append({
                    "requirement_id": requirement.id,
                    "requirement_text": requirement.requirement_text,
                    "source_file": requirement.file_path,
                    "test_file": test_file_path,
                    "test_exists": test_exists,
                    "test_functions": test_functions,
                    "confidence": requirement.confidence,
                    "status": requirement.status,
                    "created_at": requirement.created_at
                })

            # Generate output based on format
            if output_format == "markdown":
                return self._export_traceability_markdown(traceability_data)
            elif output_format == "csv":
                return self._export_traceability_csv(traceability_data)
            elif output_format == "json":
                return self._export_traceability_json(traceability_data)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported output format: {output_format}. Use 'markdown', 'csv', or 'json'."
                }

        except Exception as e:
            return {"success": False, "error": f"Traceability matrix generation failed: {str(e)}"}

    def _export_traceability_markdown(self, traceability_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export traceability matrix as Markdown table.

        Args:
            traceability_data: List of traceability entries

        Returns:
            Dictionary with success status and file path
        """
        try:
            output_file = ".agentops/traceability_matrix.md"
            
            with open(output_file, 'w') as f:
                f.write("# AgentOps Traceability Matrix\n\n")
                f.write("This matrix shows the bidirectional links between requirements and test cases.\n\n")
                
                # Summary statistics
                total_requirements = len(traceability_data)
                requirements_with_tests = sum(1 for item in traceability_data if item["test_exists"])
                total_test_functions = sum(len(item["test_functions"]) for item in traceability_data)
                
                f.write("## Summary\n\n")
                f.write(f"- **Total Requirements**: {total_requirements}\n")
                f.write(f"- **Requirements with Tests**: {requirements_with_tests}\n")
                f.write(f"- **Test Coverage**: {requirements_with_tests/total_requirements*100:.1f}%\n")
                f.write(f"- **Total Test Functions**: {total_test_functions}\n\n")
                
                # Main traceability table
                f.write("## Requirements to Test Cases Traceability\n\n")
                f.write("| Req ID | Requirement | Source File | Test File | Test Functions | Status |\n")
                f.write("|--------|-------------|-------------|-----------|----------------|--------|\n")
                
                for item in traceability_data:
                    req_id = item["requirement_id"]
                    req_text = item["requirement_text"][:50] + "..." if len(item["requirement_text"]) > 50 else item["requirement_text"]
                    source_file = item["source_file"]
                    test_file = item["test_file"]
                    test_functions = ", ".join(item["test_functions"][:3])  # Show first 3 test functions
                    if len(item["test_functions"]) > 3:
                        test_functions += f" (+{len(item['test_functions']) - 3} more)"
                    status = "✅" if item["test_exists"] else "❌"
                    
                    f.write(f"| {req_id} | {req_text} | {source_file} | {test_file} | {test_functions} | {status} |\n")
                
                # Test cases to requirements mapping
                f.write("\n## Test Cases to Requirements Mapping\n\n")
                f.write("| Test File | Test Functions | Requirements |\n")
                f.write("|-----------|----------------|--------------|\n")
                
                # Group by test file
                test_file_groups = {}
                for item in traceability_data:
                    if item["test_exists"]:
                        test_file = item["test_file"]
                        if test_file not in test_file_groups:
                            test_file_groups[test_file] = []
                        test_file_groups[test_file].append(item)
                
                for test_file, items in test_file_groups.items():
                    all_test_functions = []
                    all_requirements = []
                    
                    for item in items:
                        all_test_functions.extend(item["test_functions"])
                        all_requirements.append(f"Req {item['requirement_id']}: {item['requirement_text'][:30]}...")
                    
                    test_functions_str = ", ".join(all_test_functions[:5])
                    if len(all_test_functions) > 5:
                        test_functions_str += f" (+{len(all_test_functions) - 5} more)"
                    
                    requirements_str = "; ".join(all_requirements[:3])
                    if len(all_requirements) > 3:
                        requirements_str += f" (+{len(all_requirements) - 3} more)"
                    
                    f.write(f"| {test_file} | {test_functions_str} | {requirements_str} |\n")
                
                # Navigation links
                f.write("\n## Navigation\n\n")
                f.write("### Quick Links\n\n")
                f.write("- [View all requirements](.agentops/requirements.gherkin)\n")
                f.write("- [View all test files](.agentops/tests/)\n")
                f.write("- [View test results](.agentops/test_results.json)\n\n")
                
                f.write("### How to Use This Matrix\n\n")
                f.write("1. **From Requirements**: Find a requirement ID and see which test functions validate it\n")
                f.write("2. **From Test Cases**: Find a test file and see which requirements it covers\n")
                f.write("3. **Coverage Analysis**: Identify requirements without tests (❌ status)\n")
                f.write("4. **Test Function Details**: Click on test file paths to view actual test implementations\n\n")
                
                f.write("---\n")
                f.write(f"*Generated by AgentOps on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

            return {
                "success": True,
                "file_path": output_file,
                "format": "markdown",
                "requirements_count": len(traceability_data),
                "test_coverage": f"{requirements_with_tests/total_requirements*100:.1f}%"
            }

        except Exception as e:
            return {"success": False, "error": f"Markdown export failed: {str(e)}"}

    def _export_traceability_csv(self, traceability_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export traceability matrix as CSV.

        Args:
            traceability_data: List of traceability entries

        Returns:
            Dictionary with success status and file path
        """
        try:
            import csv
            
            output_file = ".agentops/traceability_matrix.csv"
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    "Requirement ID",
                    "Requirement Text", 
                    "Source File",
                    "Test File",
                    "Test Functions",
                    "Test Exists",
                    "Confidence",
                    "Status",
                    "Created At"
                ])
                
                # Write data
                for item in traceability_data:
                    writer.writerow([
                        item["requirement_id"],
                        item["requirement_text"],
                        item["source_file"],
                        item["test_file"],
                        "; ".join(item["test_functions"]),
                        item["test_exists"],
                        item["confidence"],
                        item["status"],
                        item["created_at"]
                    ])

            return {
                "success": True,
                "file_path": output_file,
                "format": "csv",
                "requirements_count": len(traceability_data)
            }

        except Exception as e:
            return {"success": False, "error": f"CSV export failed: {str(e)}"}

    def _export_traceability_json(self, traceability_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export traceability matrix as JSON.

        Args:
            traceability_data: List of traceability entries

        Returns:
            Dictionary with success status and file path
        """
        try:
            import json
            
            output_file = ".agentops/traceability_matrix.json"
            
            # Add metadata
            export_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_requirements": len(traceability_data),
                    "requirements_with_tests": sum(1 for item in traceability_data if item["test_exists"]),
                    "total_test_functions": sum(len(item["test_functions"]) for item in traceability_data)
                },
                "traceability_matrix": traceability_data
            }
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)

            return {
                "success": True,
                "file_path": output_file,
                "format": "json",
                "requirements_count": len(traceability_data)
            }

        except Exception as e:
            return {"success": False, "error": f"JSON export failed: {str(e)}"}

    def get_requirement_for_test_function(self, test_file: str, test_function: str) -> Optional[Requirement]:
        """Get the requirement that corresponds to a specific test function.

        Args:
            test_file: Path to the test file
            test_function: Name of the test function

        Returns:
            Requirement object or None if not found
        """
        try:
            # Convert test file back to source file
            source_file = self._get_source_file_from_test(test_file)
            
            if not source_file:
                return None
            
            # Get requirements for this source file
            requirements = self.requirement_store.get_requirements_for_file(source_file, status="approved")
            
            if not requirements:
                return None
            
            # For now, return the most recent requirement
            # In a more sophisticated implementation, we could parse the test function
            # to determine which specific requirement it tests
            return requirements[0]
            
        except Exception as e:
            print(f"Error getting requirement for test function: {str(e)}")
            return None

    def get_test_functions_for_requirement(self, requirement_id: int) -> List[str]:
        """Get all test functions that validate a specific requirement.

        Args:
            requirement_id: ID of the requirement

        Returns:
            List of test function names
        """
        try:
            # Get the requirement
            requirement = self.requirement_store.get_requirement(requirement_id)
            
            if not requirement:
                return []
            
            # Get test file path
            test_file_path = self._get_test_file_path(requirement.file_path)
            
            if not os.path.exists(test_file_path):
                return []
            
            # Extract test functions from the test file
            with open(test_file_path, 'r') as f:
                test_content = f.read()
            
            import re
            test_function_matches = re.findall(r'def (test_\w+)', test_content)
            return test_function_matches
            
        except Exception as e:
            print(f"Error getting test functions for requirement: {str(e)}")
            return []
