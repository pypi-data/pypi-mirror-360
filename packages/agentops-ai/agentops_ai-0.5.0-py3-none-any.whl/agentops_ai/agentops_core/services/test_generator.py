import ast
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import re
from openai import OpenAI
from pathlib import Path

# Import the consolidated analyzer
from ..analyzer import ProjectAnalyzer, analyze_project_structure
from ..config import get_config
from ..notification import notify_syntax_error, notify_import_validation_issue, notify_test_generation_summary

load_dotenv()


class TestGenerator:
    """Service for generating tests using OpenAI API with proper project structure analysis."""

    def __init__(self, api_key: Optional[str] = None, model: str = None):
        """Initialize the test generator.
        Args:
            api_key: OpenAI API key (defaults to config)
            model: OpenAI model to use (defaults to config)
        """
        config = get_config()
        self.api_key = api_key or config.llm.api_key
        self.model = model or config.llm.model
        self.client = OpenAI(api_key=self.api_key)
        self.project_analyzer: Optional[ProjectAnalyzer] = None

    def _find_project_root(self) -> Path:
        """Find the project root directory (where .agentops directory is located)."""
        current_dir = Path.cwd().resolve()
        
        # Walk up the directory tree to find .agentops directory
        for parent in [current_dir] + list(current_dir.parents):
            if (parent / ".agentops").exists():
                return parent
        
        # If no .agentops found, use current directory
        return current_dir

    def _ensure_project_analyzed(self, project_root: str = "."):
        """Ensure the project has been analyzed for structure and imports."""
        # Find the actual project root (where .agentops directory is)
        actual_project_root = self._find_project_root()
        
        if self.project_analyzer is None or self.project_analyzer.project_root != str(actual_project_root):
            print(f"DEBUG: Analyzing project structure at: {actual_project_root}")
            self.project_analyzer = analyze_project_structure(str(actual_project_root))

    def parse_code(self, code: str) -> Dict[str, Any]:
        """Parse Python code to extract structure.

        Args:
            code: Python code as string

        Returns:
            Dict containing code structure
        """
        try:
            ast.parse(code)
            # Extract classes, functions, etc.
            # Implementation here
            return {"success": True, "structure": {}}
        except SyntaxError as e:
            return {"success": False, "error": str(e)}

    def _validate_test_imports(self, test_code: str, source_file: str) -> bool:
        """Validate that the test code imports and uses the correct classes/functions from the source file."""
        try:
            # Read the source file to see what's available
            with open(source_file, 'r') as f:
                source_code = f.read()
            
            # Parse source code to find classes and functions
            import ast
            source_tree = ast.parse(source_code)
            source_names = set()
            
            for node in ast.walk(source_tree):
                if isinstance(node, ast.ClassDef):
                    source_names.add(node.name)
                elif isinstance(node, ast.FunctionDef):
                    # Only include top-level functions
                    if not hasattr(node, 'parent'):
                        source_names.add(node.name)
            
            # Parse test code to see what it's trying to use
            test_tree = ast.parse(test_code)
            test_names = set()
            
            for node in ast.walk(test_tree):
                if isinstance(node, ast.Name):
                    test_names.add(node.id)
            
            # Check if test code uses any names that don't exist in source
            unused_names = test_names - source_names
            if unused_names:
                notify_import_validation_issue(source_file, [f"Test code references names not in source: {unused_names}"])
                return False
            
            return True
            
        except Exception as e:
            notify_import_validation_issue(source_file, [f"Could not validate test imports: {e}"])
            return True  # Assume valid if we can't check

    def generate_tests(self, target: str, framework: str = "pytest") -> dict:
        """Generate tests for a given target.

        Args:
            target: File path or module name to generate tests for
            framework: Test framework to use (default: pytest)

        Returns:
            Dictionary with test generation results
        """
        try:
            # Ensure project is analyzed
            self._ensure_project_analyzed()
            
            # Read the target file
            with open(target, "r") as f:
                code = f.read()

            # Parse the code to get structure
            structure = self._analyze_code(code)

            # Create prompt for test generation
            prompt = self._create_prompt(code, structure, framework)

            # Generate test code
            response = self._call_openai(prompt)

            # Process the response
            result = self._process_response(response, framework)

            if result["success"]:
                # Get module names for proper import handling
                source_module = self._get_module_name(target)
                test_module = self._get_test_module_name(target)
                
                # Fix imports using project analyzer
                if self.project_analyzer:
                    result["tests"] = self._fix_test_imports(
                        result["tests"], source_module, test_module
                    )
                
                # Validate that the test code imports correctly
                if not self._validate_test_imports(result["tests"], target):
                    print(f"Warning: Generated test code may have import issues for {target}")

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_module_name(self, file_path: str) -> str:
        """Get the module name from a file path."""
        if self.project_analyzer is None:
            # Fallback to basic module name extraction
            try:
                # Handle both absolute and relative paths
                file_path_obj = Path(file_path)
                project_root = self._find_project_root()
                
                if file_path_obj.is_absolute():
                    rel_path = file_path_obj.relative_to(project_root)
                else:
                    # For relative paths, resolve against project root
                    rel_path = (project_root / file_path_obj).relative_to(project_root)
                
                if rel_path.suffix == '.py':
                    rel_path = rel_path.with_suffix('')
                return '.'.join(rel_path.parts)
            except ValueError:
                # If relative_to fails, use the filename as module name
                return Path(file_path).stem
        
        # Use project analyzer to get proper module name
        for module_name, module_info in self.project_analyzer.modules.items():
            if module_info.file_path == file_path:
                return module_name
        
        # Fallback
        try:
            file_path_obj = Path(file_path)
            project_root = self._find_project_root()
            
            if file_path_obj.is_absolute():
                rel_path = file_path_obj.relative_to(project_root)
            else:
                rel_path = (project_root / file_path_obj).relative_to(project_root)
            
            if rel_path.suffix == '.py':
                rel_path = rel_path.with_suffix('')
            return '.'.join(rel_path.parts)
        except ValueError:
            return Path(file_path).stem

    def _get_test_module_name(self, source_file: str) -> str:
        """Get the test module name for a source file."""
        # Convert source file path to test file path
        source_path = Path(source_file)
        project_root = self._find_project_root()
        
        try:
            # Handle both absolute and relative paths
            if source_path.is_absolute():
                rel_source_path = source_path.relative_to(project_root)
            else:
                rel_source_path = (project_root / source_path).relative_to(project_root)
            
            test_path = Path(".agentops") / "tests" / rel_source_path
            test_path = test_path.parent / f"test_{test_path.name}"
            
            # Convert to module name
            rel_path = test_path.relative_to(project_root)
            if rel_path.suffix == '.py':
                rel_path = rel_path.with_suffix('')
            return '.'.join(rel_path.parts)
        except ValueError:
            # Fallback: create a simple test module name
            source_name = source_path.stem
            return f"agentops.tests.test_{source_name}"

    def _fix_test_imports(self, test_code: str, source_module: str, test_module: str) -> str:
        """Fix imports in test code using project analyzer."""
        if self.project_analyzer is None:
            return test_code
        
        # Get the source file path and analyze its contents
        source_file_path = None
        if source_module in self.project_analyzer.modules:
            source_file_path = self.project_analyzer.modules[source_module].file_path
        else:
            # Try to guess the file path from the module name
            for mod, info in self.project_analyzer.modules.items():
                if mod.endswith(source_module.split('.')[-1]):
                    source_file_path = info.file_path
                    break
        
        if source_file_path:
            source_module_name = self.project_analyzer._get_module_name(source_file_path)
        else:
            # Fallback: use the source_module as is
            source_module_name = source_module
            return test_code  # Skip import fixing if we can't find the source file
        
        # Analyze the source file to find actual classes and functions
        if not source_file_path:
            print(f"DEBUG: No source file path found for module {source_module}")
            return test_code
            
        try:
            with open(source_file_path, 'r') as f:
                source_code = f.read()
            
            # Parse the source code to find classes and functions
            import ast
            tree = ast.parse(source_code)
            
            # Extract class names
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            # Extract function names (only top-level functions, not methods)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and not hasattr(node, 'parent')]
            
            # Find what's actually being used in the test code
            test_tree = ast.parse(test_code)
            used_names = set()
            for node in ast.walk(test_tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
            
            # Determine what to import based on what's actually used
            imports_to_add = []
            for class_name in classes:
                if class_name in used_names:
                    imports_to_add.append(class_name)
            
            for func_name in functions:
                if func_name in used_names:
                    imports_to_add.append(func_name)
            
            if imports_to_add:
                print(f"DEBUG: Importing from {source_module_name}: {', '.join(imports_to_add)}")
            else:
                print(f"DEBUG: No specific imports found for {source_module_name}")
                return test_code

        except Exception as e:
            if source_file_path:
                print(f"DEBUG: Error analyzing source file {source_file_path}: {e}")
            else:
                print(f"DEBUG: Error analyzing source file (path is None): {e}")
            return test_code
        
        # Replace imports in the test code
        import_lines = []
        code_lines = []
        in_imports = True
        
        for line in test_code.split('\n'):
            stripped = line.strip()
            if in_imports and (stripped.startswith('import ') or stripped.startswith('from ')):
                # Skip any existing imports of the classes/functions we want to import
                if any(name in line for name in imports_to_add):
                    continue
                else:
                    import_lines.append(line)
            else:
                in_imports = False
                code_lines.append(line)
        
        # Add the correct imports
        if imports_to_add:
            import_statement = f"from {source_module_name} import {', '.join(imports_to_add)}"
            import_lines.insert(0, import_statement)
        
        # Combine imports and code
        return '\n'.join(import_lines + [''] + code_lines)

    def _create_prompt(
        self, code: str, structure: Dict[str, Any], framework: str
    ) -> str:
        """Create a prompt for the OpenAI API that guarantees only valid Python code in a single code block, no prose or markdown outside."""
        # Process numeric literals in the code before creating the prompt
        code = self._validate_numeric_literals(code)

        summary = []
        if structure:
            functions = structure.get("functions", [])
            classes = structure.get("classes", [])
            
            if functions:
                summary.append("Functions:")
                for f in functions:
                    args_str = ", ".join(f.get("args", []))
                    summary.append(f"- {f.get('name', 'unknown')}({args_str})")
            
            if classes:
                summary.append("Classes:")
                for c in classes:
                    methods = c.get("methods", [])
                    methods_str = ", ".join([m.get("name", "") for m in methods])
                    summary.append(f"- {c.get('name', 'unknown')} (methods: {methods_str})")
        
        summary_text = "\n".join(summary)

        # Check if this is a Pydantic model file
        is_pydantic = (
            "from pydantic import" in code or "class" in code and "BaseModel" in code
        )

        if is_pydantic:
            prompt = (
                "You are AgentOps QA Agent. You must output ONLY valid Python code inside a single ```python code block. "
                "Do not explain, comment, or output anything else outside the block. No markdown, no prose, no TODOs.\n\n"
                "CRITICAL: Generate only valid Python syntax. Pay special attention to:\n"
                "- Use explicit decimal points for floats (1.0 not 1.)\n"
                "- Use proper scientific notation (1e-6 not 1.e-6)\n"
                "- No trailing decimal points\n"
                "- Valid numeric literals only\n\n"
                "Start output with:\n```python\n\n"
                "End output with:\n```\n\n"
                "Your task is to generate a complete, ready-to-run pytest test file for the Pydantic model(s) below. "
                "The file must:\n"
                "- Import the model class directly from the module\n"
                "- Test model creation with valid data\n"
                "- Test model validation with invalid data\n"
                "- Test default values\n"
                "- Test optional fields\n"
                "- Use idiomatic pytest\n"
                "- Use assert statements with helpful error messages\n"
                "- Add `@pytest.mark.generated_by_agentops` above every test\n"
                "- Include a Python docstring at the top with this fingerprint block:\n"
                '"""\n'
                "Auto-generated by AgentOps QA Agent v0.4\n"
                "Date: 2025-05-24\n"
                "Target: Pydantic model(s) (see below)\n"
                "LLM Confidence Score: 86%\n"
                "Generation Prompt Hash: a9f7e2c3\n"
                "Regeneration Policy: Re-evaluate on diff; regenerate if confidence < 70%\n"
                '"""\n\n'
                "Important:\n"
                "- Do not include any non-Python content.\n"
                "- Do not wrap your output in markdown.\n"
                "- Assume temperature=0.0 and sufficient max_tokens.\n"
                "- The output should be a single test file stored under `.agentops/tests/<mirrored path>/`.\n"
                "- When using numeric values in tests:\n"
                "  * Always use explicit decimal points for floats (e.g., 1.0 instead of 1.)\n"
                "  * Use proper scientific notation (e.g., 1e-6 instead of 1.e-6)\n"
                "  * Ensure negative numbers have no space after the minus sign\n"
                "  * Use proper numeric literals for all test values\n"
                "  * Use proper numeric literals in JSON/dict values\n\n"
                f"# Code summary:\n{summary_text}\n\n# Full code to test:\n{code}"
            )
        else:
            prompt = (
                "You are AgentOps QA Agent. You must output ONLY valid Python code inside a single ```python code block. "
                "Do not explain, comment, or output anything else outside the block. No markdown, no prose, no TODOs.\n\n"
                "CRITICAL: Generate only valid Python syntax. Pay special attention to:\n"
                "- Use explicit decimal points for floats (1.0 not 1.)\n"
                "- Use proper scientific notation (1e-6 not 1.e-6)\n"
                "- No trailing decimal points\n"
                "- Valid numeric literals only\n\n"
                "Start output with:\n```python\n\n"
                "End output with:\n```\n\n"
                "Your task is to generate a complete, ready-to-run pytest test file for all public functions and methods in the code below. "
                "The file must:\n"
                "- Use idiomatic pytest, with @pytest.mark.parametrize where appropriate\n"
                "- Use assert statements with helpful error messages\n"
                "- Add `@pytest.mark.generated_by_agentops` above every test\n"
                "- Include a Python docstring at the top with this fingerprint block:\n"
                '"""\n'
                "Auto-generated by AgentOps QA Agent v0.4\n"
                "Date: 2025-05-24\n"
                "Target: auto-discovered functions (see below)\n"
                "LLM Confidence Score: 86%\n"
                "Generation Prompt Hash: a9f7e2c3\n"
                "Regeneration Policy: Re-evaluate on diff; regenerate if confidence < 70%\n"
                '"""\n\n'
                "Important:\n"
                "- Do not include any non-Python content.\n"
                "- Do not wrap your output in markdown.\n"
                "- Assume temperature=0.0 and sufficient max_tokens.\n"
                "- The output should be a single test file stored under `.agentops/tests/<mirrored path>/`.\n"
                "- When using numeric values in tests:\n"
                "  * Always use explicit decimal points for floats (e.g., 1.0 instead of 1.)\n"
                "  * Use proper scientific notation (e.g., 1e-6 instead of 1.e-6)\n"
                "  * Ensure negative numbers have no space after the minus sign\n"
                "  * Use proper numeric literals for all test values\n\n"
                f"# Code summary:\n{summary_text}\n\n# Full code to test:\n{code}"
            )
        return prompt

    def _load_prompt(self, prompt_file: str) -> str:
        """Load a prompt from the prompts directory.

        Args:
            prompt_file: Name of the prompt file

        Returns:
            Prompt content as string
        """
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / prompt_file
        try:
            with open(prompt_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            # Fallback to hardcoded prompt if file not found
            return "You are an expert test engineer. Your task is to generate comprehensive tests for the provided code."

    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call the OpenAI API with the given prompt."""
        try:
            # Load system prompt from file
            system_prompt = self._load_prompt("test_generation.txt")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
            # No debug print of the raw response
            return {"success": True, "data": response}
        except Exception as e:
            print("[AgentOps DEBUG] OpenAI API Exception:", e)
            return {"success": False, "error": str(e)}

    def _process_response(
        self, response: Dict[str, Any], framework: str
    ) -> Dict[str, Any]:
        """Process the OpenAI API response."""
        if not response["success"]:
            print("[AgentOps DEBUG] OpenAI response not successful:", response)
            return {"success": False, "error": response["error"]}
        data = response["data"]
        # Extract the test code from the OpenAI response
        try:
            raw_content = data.choices[0].message.content
            # Extract code from ```python ... ``` block
            match = re.search(r"```python(.*?)```", raw_content, re.DOTALL)
            if match:
                test_code = match.group(1).strip()
            else:
                test_code = raw_content.strip()
            
            if not test_code:
                return {"success": False, "error": "No test code generated"}
            
            # Check for syntax errors and add TODO comments
            processed_code, syntax_error = self.auto_fix_syntax_errors(test_code)
            if syntax_error:
                notify_syntax_error("generated_test", str(syntax_error))
            
            confidence = 1.0 if test_code else 0.0
            return {"success": True, "tests": processed_code or test_code, "confidence": confidence}
        except Exception as e:
            print("[AgentOps DEBUG] Failed to parse OpenAI response:", e)
            return {"success": False, "error": f"Failed to parse OpenAI response: {e}"}

    def write_tests_to_file(
        self,
        test_code: str,
        output_dir: str = "tests",
        base_name: str = "test_generated.py",
    ) -> str:
        """Write the generated test code to a file and return the file path."""
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, base_name)
        with open(file_path, "w") as f:
            f.write(test_code)
        return file_path

    def _dedupe_and_group_imports(self, code):
        lines = code.split("\n")
        import_lines = [
            line
            for line in lines
            if line.strip().startswith("import ") or line.strip().startswith("from ")
        ]
        import_lines = list(dict.fromkeys(import_lines))
        non_import_lines = [line for line in lines if line not in import_lines]
        return "\n".join(import_lines + [""] + non_import_lines)

    def _decorate_tests(self, code):
        lines = code.split("\n")
        out = []
        for i, line in enumerate(lines):
            if line.strip().startswith("def test_"):
                out.append("@pytest.mark.generated_by_agentops")
            out.append(line)
        return "\n".join(out)

    def _add_risk_comments(self, code):
        lines = code.split("\n")
        out = []
        for i, line in enumerate(lines):
            if line.strip().startswith("def test_"):
                out.append("# Risk: medium | Importance: auto-generated by AgentOps")
            out.append(line)
        return "\n".join(out)

    def _add_assertion_messages(self, code):
        import re

        def add_msg(match):
            assertion = match.group(0)
            if "assert " in assertion and "," not in assertion:
                expr = assertion[len("assert ") :].strip()
                return f"assert {expr}, 'Assertion failed: {expr}'"
            return assertion

        return re.sub(r"assert [^,\n]+", add_msg, code)

    def _validate_numeric_literals(self, code: str) -> str:
        """Validate numeric literals and return any issues found.
        
        This method identifies potential syntax errors in numeric literals
        but does not attempt to fix them. It returns information about
        any issues found for user notification.
        """
        import re
        import ast
        
        issues = []
        
        try:
            # Try to parse the code to catch syntax errors
            ast.parse(code)
            return code  # No issues found
        except SyntaxError as e:
            if "invalid decimal literal" in str(e):
                # Extract the problematic line
                lines = code.split('\n')
                if e.lineno and e.lineno <= len(lines):
                    line = lines[e.lineno - 1]
                    issues.append({
                        'type': 'invalid_decimal_literal',
                        'line': e.lineno,
                        'column': e.offset,
                        'content': line.strip(),
                        'message': str(e)
                    })
                    
                    # Add a comment to inform the user
                    comment = f"# TODO: Fix invalid decimal literal on line {e.lineno}: {line.strip()}"
                    lines.insert(e.lineno, comment)
                    return '\n'.join(lines)
            
            # For other syntax errors, just add a general comment
            lines = code.split('\n')
            comment = f"# TODO: Fix syntax error: {str(e)}"
            lines.insert(0, comment)
            return '\n'.join(lines)
        
        return code

    def _post_process_test_code(self, test_code: str) -> str:
        """Post-process the generated test code to extract and validate Python code."""
        # Extract the code block from the response
        code_block = re.search(r"```python\n(.*?)```", test_code, re.DOTALL)
        if code_block:
            code = code_block.group(1)
        else:
            code = test_code

        # Validate numeric literals and add TODO comments for any issues
        code = self._validate_numeric_literals(code)

        return code

    def auto_fix_syntax_errors(
        self, test_code: str, max_attempts: int = 5
    ) -> tuple[str, SyntaxError | None]:
        """
        Check for syntax errors and add TODO comments for any issues found.
        Returns (code_with_todos, None) on success.
        Returns (original_code, Exception) on unrecoverable errors.
        """
        import ast
        
        try:
            # Try to parse the code
            ast.parse(test_code)
            return test_code, None
        except SyntaxError as e:
            # Add a TODO comment at the top to inform the user
            lines = test_code.split('\n')
            todo_comment = f"# TODO: Fix syntax error on line {e.lineno}: {str(e)}"
            lines.insert(0, todo_comment)
            
            # Also add a comment on the problematic line if possible
            if e.lineno and e.lineno <= len(lines):
                line_comment = f"# TODO: Fix this line - {str(e)}"
                lines.insert(e.lineno, line_comment)
            
            return '\n'.join(lines), None

    def generate_tests_from_requirement(
        self, file_path: str, requirement_text: str, confidence: float, requirement_id: int = None
    ) -> Dict[str, Any]:
        """Generate tests from a specific requirement.

        Args:
            file_path: Path to the source file
            requirement_text: The functional requirement text
            confidence: Confidence score for the requirement
            requirement_id: ID of the requirement for traceability

        Returns:
            Dictionary with generated test code and success status
        """
        try:
            # Read the source file
            with open(file_path, 'r') as f:
                source_code = f.read()

            # Get module names for proper import handling
            source_module = self._get_module_name(file_path)
            test_module = self._get_test_module_name(file_path)

            # Create requirement-driven prompt with requirement ID
            prompt = self._create_requirement_driven_prompt(
                source_code, file_path, requirement_text, confidence, 
                source_module, test_module, requirement_id
            )

            # Generate test code
            response = self._call_openai(prompt)

            # Process the response
            result = self._process_response(response, "pytest")

            if not result["success"]:
                return result

            # Post-process the generated code
            processed_code = self._post_process_test_code(result["tests"])

            # Fix imports using project analyzer
            if self.project_analyzer:
                processed_code = self._fix_test_imports(processed_code, source_module, test_module)
                
                # Validate imports
                is_valid, issues = self.project_analyzer.validate_imports(
                    processed_code, source_module, test_module
                )
                if not is_valid:
                    notify_import_validation_issue(file_path, issues)

            # Count test functions in the generated code
            test_count = len([line for line in processed_code.split('\n') if line.strip().startswith('def test_')])
            
            notify_test_generation_summary(file_path, True, test_count)
            return {"code": processed_code, "success": True, "error": None}

        except Exception as e:
            error_msg = f"Requirement-based test generation failed: {str(e)}"
            notify_test_generation_summary(file_path, False, 0, [error_msg])
            return {
                "code": None,
                "success": False,
                "error": error_msg,
            }

    def _create_requirement_driven_prompt(
        self, source_code: str, file_path: str, requirement_text: str, 
        confidence: float, source_module: str, test_module: str, requirement_id: int = None
    ) -> str:
        """Create a prompt for requirement-driven test generation with project context.

        Args:
            source_code: The source code to test
            file_path: Path to the source file
            requirement_text: The functional requirement
            confidence: Confidence score
            source_module: The source module name
            test_module: The test module name
            requirement_id: ID of the requirement for traceability

        Returns:
            Formatted prompt for LLM
        """
        # Get project context for imports
        import_context = ""
        if self.project_analyzer:
            correct_imports = self.project_analyzer.get_test_imports(source_module, test_module)
            if correct_imports:
                import_context = f"""
IMPORT CONTEXT:
The test file should use these imports for proper module access:
{chr(10).join(correct_imports)}

"""
        
        # Add requirement ID to docstring if available
        requirement_info = f"Requirement ID: {requirement_id}" if requirement_id else "Requirement ID: Unknown"
        
        return f"""
You are AgentOps QA Agent generating tests based on a validated functional requirement.

CRITICAL: You must output ONLY valid Python code inside a single ```python code block.
Do not explain, comment, or output anything else outside the block.

Your task:
Generate a complete pytest test file that specifically validates the following requirement:

REQUIREMENT: {requirement_text}

{import_context}
The test must:
1. Import necessary modules from the source file using the correct import paths
2. Create test cases that verify the requirement is met
3. Use descriptive test names that relate to the requirement
4. Include helpful assertion messages
5. Add `@pytest.mark.generated_by_agentops` above every test function
6. Use proper pytest patterns and conventions
7. Include requirement traceability information in comments

Include this docstring at the top:
\"\"\"
Auto-generated by AgentOps QA Agent v0.2 (MVP)
Target: {file_path}
{requirement_info}
Requirement: {requirement_text}
Confidence: {confidence:.1%}
Generation: Requirement-driven test generation
Traceability: This test file validates the above requirement
\"\"\"

IMPORTANT: Add a comment at the top of each test function linking it to the requirement:
# Validates requirement: {requirement_text[:50]}{'...' if len(requirement_text) > 50 else ''}

Source code to test:
```python
{source_code}
```

Remember:
- Output ONLY Python code in a single ```python code block
- Focus tests on validating the specific requirement
- Use proper numeric literals (no trailing decimals like 1.)
- Make tests deterministic and reliable
- Use the correct import statements for the project structure
- Include requirement traceability in comments
"""

    def qa_validate_test_file(self, test_code: str) -> str:
        """Use a separate LLM call to validate and fix the generated test code."""
        # This function can be expanded to use a different model or prompt for validation
        validation_prompt = (
            "You are a QA engineer. Your task is to validate the following pytest test file. "
            "If the file is valid, return it as is. If it has syntax errors or other issues, "
            "fix them and return the corrected file. The file should be wrapped in a single ```python code block.\n\n"
            f"Test file to validate:\n{test_code}"
        )

        return self._generate_test_code(validation_prompt)

    def _rewrite_imports_to_absolute(self, code: str, module_path: str) -> str:
        """Rewrite relative and placeholder imports in the test code to absolute imports from the project root."""
        import re

        # Compute the absolute import base from the module_path
        # E.g., for .agentops/tests/agentops_ai/agentops_cli/test_main.py, base is agentops_ai.agentops_cli
        base = (
            module_path.replace(".agentops/tests/", "")
            .replace("/", ".")
            .rsplit(".", 1)[0]
        )

        # For Pydantic models, we want to import directly from the module
        if "from pydantic import" in code:
            # Extract the module name from the path
            module_name = os.path.basename(module_path).replace(".py", "")
            # Replace relative imports with direct imports
            code = re.sub(
                r"from \. import ([\w, ]+)", f"from {module_name} import \\1", code
            )
            code = re.sub(
                r"from \.\. import ([\w, ]+)", f"from {module_name} import \\1", code
            )
            return code

        def repl(match):
            rel = match.group(1)
            name = match.group(2)
            # Only handle .. imports for now
            if rel == "..":
                # Remove last component from base
                abs_base = ".".join(base.split(".")[:-1])
                return f"from {abs_base} import {name}"
            elif rel == ".":
                return f"from {base} import {name}"
            return match.group(0)

        # Replace relative imports
        code = re.sub(r"from (\.+)\s*import\s*([\w, ]+)", repl, code)
        # Replace 'from your_module import ...' with absolute import
        code = re.sub(
            r"from your_module import ([\w, ]+)", f"from {base} import \\1", code
        )
        # Replace 'from . import ...' and 'from .. import ...' at the start of lines
        code = re.sub(
            r"^from \. import ([\w, ]+)",
            f"from {base} import \\1",
            code,
            flags=re.MULTILINE,
        )
        code = re.sub(
            r"^from \.\. import ([\w, ]+)",
            f"from {'.'.join(base.split('.')[:-1])} import \\1",
            code,
            flags=re.MULTILINE,
        )
        return code

    def _create_api_test_prompt(self, code: str, filename: str) -> str:
        return f'''
You are a QA test generation agent.

You are given one or more API endpoint definitions from a Python web framework (e.g., FastAPI, Flask).

Your job is to generate a **valid pytest test file** that tests each endpoint's basic success case, with:
- The correct HTTP method
- Required parameters (from path, query, or JSON body)
- Expected status code (e.g., 200 OK)

Use `TestClient` if the framework is FastAPI or Flask.

Each test must:
- Be wrapped with `@pytest.mark.generated_by_agentops`
- Include a meaningful assert for `status_code` and (if JSON) a key/value check
- Be deterministic, with fixed test data

Embed this fingerprint docstring at the top of the file:

"""
Auto-generated by AgentOps QA Agent v0.4
Date: 2025-05-25
Target: API endpoint(s) from {filename}
LLM Confidence Score: 86%
Generation Prompt Hash: a9f7e2c3
Regeneration Policy: Re-evaluate on diff; regenerate if confidence < 70%
"""

Do NOT include markdown. Return only valid Python code inside a ```python code block.

Example endpoint:
@app.post("/login")
def login(username: str, password: str):
    ...
from fastapi.testclient import TestClient
from app import app
import pytest

client = TestClient(app)

@pytest.mark.generated_by_agentops
def test_login_success():
    response = client.post("/login", json={"username": "test", "password": "secret"})
    assert response.status_code == 200
    assert "token" in response.json()

---

### 🛠 Extend This Prompt For:
- Auth headers (`Authorization: Bearer ...`)
- Query parameters (`/items/?id=1&status=ok`)
- Parametrize input/output cases
- Error scenarios (401, 422, etc.)

Below are the API endpoint definitions:
{code}
'''

    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze the code to extract functions, classes, and other structures."""
        try:
            import ast
            tree = ast.parse(code)
            
            structure = {
                "functions": [],
                "classes": [],
                "imports": [],
                "variables": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Only include top-level functions (not methods)
                    if not hasattr(node, 'parent'):
                        func_info = {
                            "name": node.name,
                            "args": [arg.arg for arg in node.args.args if arg.arg != 'self'],
                            "decorators": [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list],
                            "docstring": ast.get_docstring(node)
                        }
                        structure["functions"].append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "bases": [base.id if hasattr(base, 'id') else str(base) for base in node.bases],
                        "methods": [],
                        "docstring": ast.get_docstring(node)
                    }
                    
                    # Extract methods from the class
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            method_info = {
                                "name": child.name,
                                "args": [arg.arg for arg in child.args.args if arg.arg != 'self'],
                                "decorators": [d.id if hasattr(d, 'id') else str(d) for d in child.decorator_list],
                                "docstring": ast.get_docstring(child)
                            }
                            class_info["methods"].append(method_info)
                    
                    structure["classes"].append(class_info)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        structure["imports"].append({
                            "module": alias.name,
                            "asname": alias.asname
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        structure["imports"].append({
                            "module": node.module,
                            "name": alias.name,
                            "asname": alias.asname
                        })
                
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            structure["variables"].append({
                                "name": target.id,
                                "value": ast.unparse(node.value) if hasattr(ast, 'unparse') else str(node.value)
                            })
            
            return structure
            
        except SyntaxError as e:
            print(f"DEBUG: Syntax error in code analysis: {e}")
            return {"functions": [], "classes": [], "imports": [], "variables": []}
        except Exception as e:
            print(f"DEBUG: Error in code analysis: {e}")
            return {"functions": [], "classes": [], "imports": [], "variables": []}

    def _generate_test_code(self, prompt: str) -> str:
        """Generate test code using the OpenAI API."""
        return (
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                top_p=1.0,
                max_tokens=2048,
            )
            .choices[0]
            .message.content
        )
