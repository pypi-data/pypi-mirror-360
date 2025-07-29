"""Utility functions for AgentOps.

Common utilities used across the codebase.
"""

import os
from pathlib import Path
from typing import List, Optional


def find_python_files(directory: str = ".", exclude_patterns: Optional[List[str]] = None, 
                     include_patterns: Optional[List[str]] = None) -> List[str]:
    """Find all Python files in the directory tree.

    Recursively searches for .py files while excluding common patterns like
    test directories, cache folders, virtual environments, and packaging artifacts.

    Args:
        directory: Root directory to search (default: current directory)
        exclude_patterns: List of patterns to exclude from search
        include_patterns: List of patterns to include (if specified, only these are processed)

    Returns:
        List of Python file paths, sorted alphabetically

    Example:
        >>> find_python_files(".", ["tests", "venv"])
        ["./src/main.py", "./src/utils.py"]
    """
    if exclude_patterns is None:
        # Default exclusions cover common patterns that shouldn't be processed
        exclude_patterns = [
            # Python-specific
            "tests",
            "__pycache__",
            ".pytest_cache",
            ".agentops",
            "venv",
            "env",
            ".venv",
            ".env",
            
            # Version control
            ".git",
            ".svn",
            ".hg",
            
            # IDE and editor
            ".idea",
            ".vscode",
            ".vs",
            "*.swp",
            "*.swo",
            
            # OS-specific
            ".DS_Store",
            "Thumbs.db",
            
            # Build and packaging
            "build",
            "dist",
            "*.egg-info",
            ".eggs",
            "develop-eggs",
            "downloads",
            "eggs",
            "lib",
            "lib64",
            "parts",
            "sdist",
            "var",
            "wheels",
            "share",
            "pyvenv.cfg",
            
            # Node.js and frontend
            "node_modules",
            "npm-debug.log",
            "yarn-error.log",
            ".npm",
            ".yarn",
            
            # Java and other languages
            "target",
            "bin",
            "obj",
            ".gradle",
            ".mvn",
            
            # Documentation and generated files
            "docs/_build",
            "site",
            ".sphinx_cache",
            "coverage",
            ".coverage",
            "htmlcov",
            ".tox",
            ".nox",
            ".hypothesis",
            ".mypy_cache",
            ".dmypy.json",
            
            # Temporary and cache
            "tmp",
            "temp",
            ".cache",
            "*.log",
            "*.tmp",
            
            # Docker and containers
            ".docker",
            "docker-compose.override.yml",
            
            # CI/CD
            ".github/workflows",
            ".gitlab-ci",
            ".travis.yml",
            ".circleci",
            
            # Database
            "*.db",
            "*.sqlite",
            "*.sqlite3",
            
            # Backup and archive
            "*.bak",
            "*.backup",
            "*.old",
            "*.orig",
            "*.rej",
        ]

    python_files = []

    for root, dirs, files in os.walk(directory):
        # Modify dirs in-place to prevent walking into excluded directories
        dirs[:] = [
            d for d in dirs if d not in exclude_patterns and not d.startswith(".")
        ]

        for file in files:
            if file.endswith(".py") and not file.startswith("."):
                file_path = os.path.join(root, file)
                
                # Check if file should be excluded - use more precise matching
                excluded = False
                for pattern in exclude_patterns:
                    # Only match against directory or file name, not full path
                    rel_path = os.path.relpath(file_path, directory)
                    rel_parts = os.path.normpath(rel_path).split(os.sep)
                    file_stem = os.path.splitext(os.path.basename(file_path))[0]
                    if (
                        pattern == os.path.basename(file_path)
                        or pattern in rel_parts
                        or pattern == file_stem
                    ):
                        excluded = True
                        break
                
                if excluded:
                    continue
                
                # If include_patterns is specified, only process matching files
                if include_patterns:
                    if not any(pattern in file_path for pattern in include_patterns):
                        continue
                
                python_files.append(file_path)

    return sorted(python_files)


def ensure_directory(path: str) -> None:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_relative_path(file_path: str, base_path: str = ".") -> str:
    """Get the relative path of a file from a base path.
    
    Args:
        file_path: Absolute or relative file path
        base_path: Base path to make relative to (default: current directory)
        
    Returns:
        Relative path string
    """
    return os.path.relpath(file_path, base_path)


def is_python_file(file_path: str) -> bool:
    """Check if a file is a Python file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is a Python file, False otherwise
    """
    return file_path.endswith('.py') and os.path.isfile(file_path)


def get_file_size(file_path: str) -> int:
    """Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0 