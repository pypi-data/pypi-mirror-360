"""Comprehensive Analyzer module for AgentOps.

Provides both single-file and project-wide analysis capabilities for:
- Function and class extraction from individual files
- Project structure and import hierarchy analysis
- Dependency relationship mapping
- Import path resolution for test generation
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque


@dataclass
class FunctionInfo:
    """Stores detailed information about a function in the codebase."""
    name: str
    parameters: List[Dict[str, Any]]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False


@dataclass
class ClassInfo:
    """Stores detailed information about a class in the codebase."""
    name: str
    methods: List[FunctionInfo] = field(default_factory=list)
    docstring: Optional[str] = None
    bases: List[str] = field(default_factory=list)


@dataclass
class ModuleInfo:
    """Information about a Python module in the project."""
    file_path: str
    module_name: str
    imports: List[str] = field(default_factory=list)
    from_imports: List[Tuple[str, List[str]]] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    is_package: bool = False
    has_init: bool = False
    # Detailed analysis for single-file use cases
    function_details: List[FunctionInfo] = field(default_factory=list)
    class_details: List[ClassInfo] = field(default_factory=list)


class CodeAnalyzer:
    """Performs static analysis on Python code to extract structure and metadata."""

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file and extract function and class information."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.analyze_code(content, file_path)

    def analyze_code(self, code: str, file_path: str = None) -> Dict[str, Any]:
        """Analyze Python code and extract function and class information."""
        tree = ast.parse(code)
        _add_parents(tree)
        
        return {
            "imports": self._extract_imports(tree)[0],  # Just the import names
            "functions": self._extract_functions(tree),
            "classes": self._extract_classes(tree),
        }

    def _extract_imports(self, tree: ast.AST) -> Tuple[List[str], List[Tuple[str, List[str]]]]:
        """Extract import statements from AST."""
        imports = []
        from_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                from_imports.append((module, names))
        
        return imports, from_imports

    def _extract_functions(self, tree: ast.AST) -> List[FunctionInfo]:
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and isinstance(
                node.parent, ast.Module
            ):
                functions.append(self._function_info_from_node(node))
        return functions

    def _extract_classes(self, tree: ast.AST) -> List[ClassInfo]:
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [
                    self._function_info_from_node(n)
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                bases = [self._get_name(base) for base in node.bases]
                docstring = ast.get_docstring(node)
                classes.append(
                    ClassInfo(
                        name=node.name,
                        methods=methods,
                        docstring=docstring,
                        bases=bases,
                    )
                )
        return classes

    def _function_info_from_node(self, node: ast.AST) -> FunctionInfo:
        params = []
        for arg in node.args.args:
            param = {"name": arg.arg}
            if arg.annotation:
                param["type"] = self._get_name(arg.annotation)
            else:
                param["type"] = None
            params.append(param)
        return_type = (
            self._get_name(node.returns) if getattr(node, "returns", None) else None
        )
        decorators = [self._get_name(d) for d in getattr(node, "decorator_list", [])]
        docstring = ast.get_docstring(node)
        is_async = isinstance(node, ast.AsyncFunctionDef)
        return FunctionInfo(
            name=node.name,
            parameters=params,
            return_type=return_type,
            docstring=docstring,
            decorators=decorators,
            is_async=is_async,
        )

    def _get_name(self, node):
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[{self._get_name(node.slice)}]"
        elif isinstance(node, ast.Index):
            return self._get_name(node.value)
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Tuple):
            return ", ".join(self._get_name(elt) for elt in node.elts)
        return str(ast.dump(node))


class ProjectAnalyzer:
    """Analyzes Python project structure and import hierarchies."""
    
    def __init__(self, project_root: str = "."):
        """Initialize the project analyzer.
        
        Args:
            project_root: Root directory of the Python project
        """
        self.project_root = Path(project_root).resolve()
        self.modules: Dict[str, ModuleInfo] = {}
        self.package_structure: Dict[str, List[str]] = defaultdict(list)
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_import_graph: Dict[str, Set[str]] = defaultdict(set)
        self.code_analyzer = CodeAnalyzer()
        
    def analyze_project(self) -> Dict[str, Any]:
        """Analyze the entire project structure and import relationships.
        
        Returns:
            Dictionary containing project analysis results
        """
        # Find all Python files
        python_files = self._find_python_files()
        
        # Analyze each file
        for file_path in python_files:
            self._analyze_file(file_path)
        
        # Build import dependency graph
        self._build_import_graph()
        
        # Analyze package structure
        self._analyze_package_structure()
        
        return {
            "modules": self.modules,
            "package_structure": dict(self.package_structure),
            "import_graph": dict(self.import_graph),
            "reverse_import_graph": dict(self.reverse_import_graph),
            "project_root": str(self.project_root)
        }
    
    def _find_python_files(self) -> List[str]:
        """Find all Python files in the project."""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip common directories that shouldn't be analyzed
            dirs[:] = [d for d in dirs if not self._should_skip_directory(d)]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
        
        return python_files
    
    def _should_skip_directory(self, dir_name: str) -> bool:
        """Check if a directory should be skipped during analysis."""
        skip_patterns = {
            '__pycache__', '.pytest_cache', '.git', 'venv', 'env', '.venv',
            'node_modules', 'build', 'dist', '.tox', '.mypy_cache',
            'tests', 'test', '.agentops'
        }
        return dir_name in skip_patterns or dir_name.startswith('.')
    
    def _analyze_file(self, file_path: str):
        """Analyze a single Python file."""
        try:
            # Check if file exists and is readable
            if not os.path.exists(file_path):
                print(f"Warning: File does not exist: {file_path}")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            _add_parents(tree)
            
            # Get module name
            module_name = self._get_module_name(file_path)
            
            # Extract imports
            imports, from_imports = self.code_analyzer._extract_imports(tree)
            
            # Extract functions and classes (both simple and detailed)
            functions = [f.name for f in self.code_analyzer._extract_functions(tree)]
            classes = [c.name for c in self.code_analyzer._extract_classes(tree)]
            function_details = self.code_analyzer._extract_functions(tree)
            class_details = self.code_analyzer._extract_classes(tree)
            
            # Check if this is a package
            is_package = self._is_package(file_path)
            has_init = os.path.basename(file_path) == '__init__.py'
            
            # Create module info
            module_info = ModuleInfo(
                file_path=file_path,
                module_name=module_name,
                imports=imports,
                from_imports=from_imports,
                functions=functions,
                classes=classes,
                is_package=is_package,
                has_init=has_init,
                function_details=function_details,
                class_details=class_details
            )
            
            self.modules[module_name] = module_info
            
        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")
            # Try to add a basic module entry even if analysis fails
            try:
                module_name = self._get_module_name(file_path)
                if module_name not in self.modules:
                    self.modules[module_name] = ModuleInfo(
                        file_path=file_path,
                        module_name=module_name,
                        is_package=self._is_package(file_path),
                        has_init=os.path.basename(file_path) == '__init__.py'
                    )
            except Exception:
                pass  # Give up if even basic module creation fails
    
    def _get_module_name(self, file_path: str) -> str:
        """Get the module name from a file path."""
        try:
            # Resolve both paths to handle symlinks and different representations
            file_path_resolved = Path(file_path).resolve()
            project_root_resolved = self.project_root.resolve()
            
            # Try to get relative path
            try:
                rel_path = file_path_resolved.relative_to(project_root_resolved)
            except ValueError:
                # If the file is not in the project root, try alternative approaches
                # This can happen on macOS with /var/folders vs /private/var/folders
                if str(file_path_resolved).startswith('/var/folders') and str(project_root_resolved).startswith('/private/var/folders'):
                    # Handle macOS temporary directory path differences
                    alt_path = str(file_path_resolved).replace('/var/folders', '/private/var/folders')
                    alt_file_path = Path(alt_path)
                    if alt_file_path.exists():
                        rel_path = alt_file_path.relative_to(project_root_resolved)
                    else:
                        # Fallback: use the filename as module name
                        return Path(file_path).stem
                else:
                    # Fallback: use the filename as module name
                    return Path(file_path).stem
            
            # Remove .py extension
            if rel_path.suffix == '.py':
                rel_path = rel_path.with_suffix('')
            
            # Convert path to module name
            parts = list(rel_path.parts)
            
            # Handle __init__.py files
            if parts and parts[-1] == '__init__':
                parts = parts[:-1]
            
            module_name = '.'.join(parts) if parts else '__main__'
            
            # Debug print for example_math.py
            if 'example_math' in str(file_path):
                print(f"DEBUG: File path: {file_path}")
                print(f"DEBUG: Project root: {project_root_resolved}")
                print(f"DEBUG: Relative path: {rel_path}")
                print(f"DEBUG: Module name: {module_name}")
            
            return module_name
            
        except Exception as e:
            # Fallback: use the filename as module name
            return Path(file_path).stem
    
    def _is_package(self, file_path: str) -> bool:
        """Check if a file is part of a package."""
        dir_path = Path(file_path).parent
        return (dir_path / '__init__.py').exists()
    
    def _build_import_graph(self):
        """Build the import dependency graph."""
        for module_name, module_info in self.modules.items():
            # Process regular imports
            for import_name in module_info.imports:
                self._add_dependency(module_name, import_name)
            
            # Process from imports
            for module, names in module_info.from_imports:
                if module:  # Skip relative imports for now
                    self._add_dependency(module_name, module)
    
    def _add_dependency(self, dependent: str, dependency: str):
        """Add a dependency relationship to the graph."""
        # Only add if dependency is in our project
        if dependency in self.modules:
            self.import_graph[dependent].add(dependency)
            self.reverse_import_graph[dependency].add(dependent)
    
    def _analyze_package_structure(self):
        """Analyze the package structure of the project."""
        for module_name, module_info in self.modules.items():
            if module_info.is_package:
                package_name = module_name
                self.package_structure[package_name].append(module_info.file_path)
    
    def get_module_dependencies(self, module_name: str) -> Set[str]:
        """Get all modules that the given module depends on."""
        return self.import_graph.get(module_name, set())
    
    def get_module_dependents(self, module_name: str) -> Set[str]:
        """Get all modules that depend on the given module."""
        return self.reverse_import_graph.get(module_name, set())
    
    def get_import_path(self, from_module: str, to_module: str) -> Optional[str]:
        """Get the correct import path from one module to another."""
        if to_module not in self.modules:
            return None
        
        from_parts = from_module.split('.')
        to_parts = to_module.split('.')
        
        # Find common prefix
        common_prefix_len = 0
        for i, (from_part, to_part) in enumerate(zip(from_parts, to_parts)):
            if from_part == to_part:
                common_prefix_len = i + 1
            else:
                break
        if common_prefix_len > 0:
            if len(from_parts) == common_prefix_len and len(to_parts) == common_prefix_len:
                return None
            relative_parts = to_parts[common_prefix_len:]
            up_levels = len(from_parts) - common_prefix_len
            # Special case: parent-to-child, use absolute import
            if up_levels == 1 and from_parts[-1] != '__init__':
                return '.'.join(relative_parts)
            if up_levels > 0:
                dots = '.' * up_levels
                return dots + ('.'.join(relative_parts) if relative_parts else '')
            else:
                return '.'.join(relative_parts)
        else:
            return to_module
    
    def get_test_imports(self, source_module: str, test_module: str) -> List[str]:
        """Get the correct imports needed for a test file."""
        imports = []
        
        # Get the source module info
        if source_module not in self.modules:
            return imports
        
        source_info = self.modules[source_module]
        
        # Import the source module itself
        import_path = self.get_import_path(test_module, source_module)
        if import_path:
            if import_path.startswith('.'):
                # Relative import
                imports.append(f"from {import_path} import *")
            else:
                # Absolute import
                imports.append(f"import {import_path}")
        
        # Import dependencies that might be needed for testing
        for dependency in source_info.dependencies:
            if dependency in self.modules:
                dep_import_path = self.get_import_path(test_module, dependency)
                if dep_import_path:
                    imports.append(f"import {dep_import_path}")
        
        return imports
    
    def validate_imports(self, test_code: str, source_module: str, test_module: str) -> Tuple[bool, List[str]]:
        """Validate that test code has correct imports."""
        issues = []
        
        # Parse test code to extract imports
        try:
            tree = ast.parse(test_code)
            test_imports, test_from_imports = self.code_analyzer._extract_imports(tree)
        except SyntaxError as e:
            issues.append(f"Syntax error in test code: {e}")
            return False, issues
        
        # Check if source module is imported
        source_imported = False
        for import_name in test_imports:
            if import_name == source_module or import_name.endswith(f'.{source_module.split(".")[-1]}'):
                source_imported = True
                break
        
        for module, names in test_from_imports:
            if module == source_module or module.endswith(f'.{source_module.split(".")[-1]}'):
                source_imported = True
                break
        
        if not source_imported:
            issues.append(f"Source module '{source_module}' is not imported")
        
        return len(issues) == 0, issues


# Patch ast nodes to add parent references for easier traversal
def _add_parents(node, parent=None):
    # If parent is None, this is the root (module), so use node as parent for its children
    actual_parent = parent if parent is not None else node
    for child in ast.iter_child_nodes(node):
        child.parent = actual_parent
        _add_parents(child, child)


def analyze_tree_with_parents(tree) -> dict:
    """Analyze an AST tree and extract parent relationships.

    Args:
        tree (ast.AST): The AST tree to analyze.
    """
    analyzer = CodeAnalyzer()
    return {
        "imports": analyzer._extract_imports(tree)[0],  # Just the import names
        "functions": analyzer._extract_functions(tree),
        "classes": analyzer._extract_classes(tree),
    }


def analyze_file_with_parents(file_path: str) -> dict:
    """Analyze a Python file and extract parent relationships from its AST.

    Args:
        file_path (str): Path to the Python file.
    """
    with open(file_path, "r") as f:
        content = f.read()
    tree = ast.parse(content)
    _add_parents(tree)
    return analyze_tree_with_parents(tree)


def analyze_project_structure(project_root: str = ".") -> ProjectAnalyzer:
    """Convenience function to analyze a project."""
    analyzer = ProjectAnalyzer(project_root)
    analyzer.analyze_project()
    return analyzer
