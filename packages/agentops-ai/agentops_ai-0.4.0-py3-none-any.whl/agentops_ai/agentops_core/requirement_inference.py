"""Requirement inference module for AgentOps.

Uses LLMs to infer requirements from code changes.
"""

import os
import subprocess
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from .config import get_config

load_dotenv()


class RequirementInferenceEngine:
    """Infers functional requirements from code diffs using LLM."""

    def __init__(self, api_key: Optional[str] = None, model: str = None):
        """Initialize the requirement inference engine.

        Args:
            api_key: OpenAI API key (defaults to config)
            model: OpenAI model to use (defaults to config)
        """
        config = get_config()
        self.api_key = api_key or config.llm.api_key
        self.model = model or config.llm.model
        self.client = OpenAI(api_key=self.api_key)

    def get_git_diff(self, file_path: str) -> Optional[str]:
        """Get git diff for a specific file.

        Args:
            file_path: Path to the file to get diff for

        Returns:
            Git diff as string or None if no diff/error
        """
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD", file_path],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout if result.stdout.strip() else None
        except subprocess.CalledProcessError:
            # Try unstaged changes if no staged changes
            try:
                result = subprocess.run(
                    ["git", "diff", file_path],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return result.stdout if result.stdout.strip() else None
            except subprocess.CalledProcessError:
                return None

    def get_file_changes(self, file_path: str) -> Optional[str]:
        """Get recent changes for a file using git or file modification.

        Args:
            file_path: Path to the file

        Returns:
            Code diff or None if no changes detected
        """
        # First try git diff
        diff = self.get_git_diff(file_path)
        if diff:
            return diff

        # If no git diff available, read the whole file as "new"
        # This handles new files or non-git projects
        try:
            with open(file_path, "r") as f:
                content = f.read()
            return f"New file: {file_path}\n\n{content}"
        except Exception:
            return None

    def infer_requirement_from_diff(self, diff: str, file_path: str) -> Dict[str, Any]:
        """Infer a functional requirement from a code diff.

        Args:
            diff: Git diff or code changes
            file_path: Path to the file being analyzed

        Returns:
            Dict with requirement, confidence, and metadata
        """
        if not diff or not diff.strip():
            return {"success": False, "error": "No code changes detected"}

        prompt = self._create_inference_prompt(diff, file_path)

        try:
            # Load system prompt from file
            system_prompt = self._load_prompt("requirement_inference.txt")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=200,
            )

            requirement_text = response.choices[0].message.content.strip()

            # Parse the response to extract requirement and confidence
            return self._parse_inference_response(requirement_text, diff, file_path)

        except Exception as e:
            return {"success": False, "error": f"Failed to infer requirement: {str(e)}"}

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
            return "You are an expert software analyst. Your job is to infer a single, clear functional requirement from code changes."

    def _create_inference_prompt(self, diff: str, file_path: str) -> str:
        """Create a prompt for requirement inference.

        Args:
            diff: Code diff
            file_path: Path to the file

        Returns:
            Formatted prompt for LLM
        """
        # Load the base prompt template
        base_prompt = self._load_prompt("requirement_inference.txt")

        # Format the prompt with the specific diff and file path
        return base_prompt.format(file_path=file_path, diff=diff)

    def _parse_inference_response(
        self, response: str, diff: str, file_path: str
    ) -> Dict[str, Any]:
        """Parse the LLM response and extract requirement details.

        Args:
            response: Raw LLM response
            diff: Original diff
            file_path: File path

        Returns:
            Parsed requirement data
        """
        # Clean up the response
        requirement = response.strip()

        # Remove any markdown formatting
        if requirement.startswith("```"):
            lines = requirement.split("\n")
            requirement = "\n".join(
                line for line in lines if not line.startswith("```")
            )

        # Extract just the requirement statement
        if "\n" in requirement:
            requirement = requirement.split("\n")[0]

        # Basic validation
        if len(requirement) < 10:
            return {
                "success": False,
                "error": "Generated requirement too short or unclear",
            }

        if len(requirement) > 200:
            return {"success": False, "error": "Generated requirement too long"}

        # Calculate confidence based on diff complexity and requirement clarity
        confidence = self._calculate_confidence(diff, requirement)

        return {
            "success": True,
            "requirement": requirement,
            "confidence": confidence,
            "metadata": {
                "file_path": file_path,
                "diff_lines": len(diff.split("\n")),
                "requirement_length": len(requirement),
            },
        }

    def _calculate_confidence(self, diff: str, requirement: str) -> float:
        """Calculate confidence score for the inferred requirement.

        Args:
            diff: Code diff
            requirement: Inferred requirement

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.8  # Base confidence

        # Adjust based on diff complexity
        diff_lines = len(
            [line for line in diff.split("\n") if line.startswith(("+", "-"))]
        )
        if diff_lines > 20:
            confidence -= 0.1  # Complex changes are harder to infer
        elif diff_lines < 5:
            confidence += 0.1  # Simple changes are easier to infer

        # Adjust based on requirement clarity
        if any(
            keyword in requirement.lower() for keyword in ["should", "must", "will"]
        ):
            confidence += 0.05

        if any(
            keyword in requirement.lower()
            for keyword in ["function", "method", "class"]
        ):
            confidence += 0.05

        # Ensure confidence is within bounds
        return max(0.1, min(1.0, confidence))

    def infer_requirement_from_file(self, file_path: str) -> Dict[str, Any]:
        """Infer requirement from a file by getting its changes and analyzing them.

        Args:
            file_path: Path to the Python file

        Returns:
            Requirement inference result
        """
        # Get file changes
        diff = self.get_file_changes(file_path)
        if not diff:
            return {"success": False, "error": "No changes detected in file"}

        # Infer requirement from diff
        return self.infer_requirement_from_diff(diff, file_path)
