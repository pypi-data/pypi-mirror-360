"""
AgentOps Core Module.

Core components for requirements-driven test automation.
Implements the Infer -> Approve -> Test workflow.
"""

from .workflow import AgentOpsWorkflow
from .requirement_inference import RequirementInferenceEngine
from .requirement_store import RequirementStore, Requirement
from .terminal_ui import TerminalUI

import hashlib
import os
from pathlib import Path
from typing import Optional, Tuple


def _calculate_directory_hash(directory: str) -> str:
    """Calculate SHA-256 hash of all Python files in the directory."""
    sha256_hash = hashlib.sha256()

    # Get all Python files
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    # Sort files to ensure consistent hashing
    python_files.sort()

    # Hash each file's contents
    for file_path in python_files:
        with open(file_path, "rb") as f:
            sha256_hash.update(f.read())

    return sha256_hash.hexdigest()


def get_version_info() -> Tuple[str, str]:
    """Get AgentOps version and hash.

    Returns:
        Tuple of (version, hash)
    """
    version = "0.2.0"  # Update this when releasing new versions
    package_dir = Path(__file__).parent.parent
    version_hash = _calculate_directory_hash(str(package_dir))
    return version, version_hash


def verify_version(expected_hash: Optional[str] = None) -> bool:
    """Verify that the current AgentOps installation matches the expected version.

    Args:
        expected_hash: Optional hash to verify against. If not provided,
                      will check against the hash in .agentops.yml if it exists.

    Returns:
        bool: True if version matches, False otherwise
    """
    _, current_hash = get_version_info()

    if expected_hash:
        return current_hash == expected_hash

    # Try to get hash from .agentops.yml
    try:
        import yaml

        config_path = Path(".agentops.yml")
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                if "version_hash" in config:
                    return current_hash == config["version_hash"]
    except Exception:
        pass

    return True  # If no hash to verify against, assume it's correct


__version__ = "0.2.0"

__all__ = [
    "AgentOpsWorkflow",
    "RequirementInferenceEngine",
    "RequirementStore",
    "Requirement",
    "TerminalUI",
]
