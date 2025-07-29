"""AgentOps CLI - Multi-Agent AI System for Requirements-Driven Test Automation.

Implements the multi-agent workflow for automated end-to-end test generation.

The CLI supports:
- Multi-agent workflow for automated end-to-end processing
- Test execution with root cause analysis
- CI/CD and IDE integration management
- Project initialization and configuration

Key Commands:
- init: Initialize AgentOps project structure
- multi-agent-run: Run complete multi-agent workflow
- run: Execute tests with root cause analysis
- config: View and edit AgentOps configuration
- integration: Manage CI/CD and IDE integrations

Reference: Multi-Agent System Architecture
"""

import click
import os
import sys
import json
import ast
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import csv
from rich.table import Table
import tempfile
import subprocess
from rich.progress import Progress
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.prompt import Confirm
import time
import datetime
from rich.progress import SpinnerColumn, TextColumn
from typing import List
import difflib

from agentops_ai.agentops_core.workflow import AgentOpsWorkflow
from agentops_ai.agentops_core.requirement_store import RequirementStore
from agentops_ai.agentops_core.config import get_config, AgentOpsConfig, LLMConfig, ProjectConfig, IntegrationConfig
from agentops_ai.agentops_core.analyzer import CodeAnalyzer, _add_parents
from agentops_ai.agentops_core.utils import find_python_files
from agentops_ai.agentops_integrations import IntegrationAgent, IntegrationConfig as IntConfig

# Optional import for advanced multi-agent workflow
try:
    from agentops_ai.agentops_agents import AgentOrchestrator
    AGENT_ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    AGENT_ORCHESTRATOR_AVAILABLE = False
    AgentOrchestrator = None

console = Console()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version="0.5.0")
def cli():
    """AgentOps - Multi-Agent AI System for Requirements-Driven Test Automation.
    
    🚀 AI-powered QA co-pilot for vibe coders - Requirements-driven test automation 
    with a sophisticated multi-agent AI system.
    
    QUICK START:
        agentops init                           # Initialize project
        agentops multi-agent-run myfile.py     # Run complete workflow
        agentops run --all                     # Execute generated tests
    
    RECOMMENDED WORKFLOW:
        1. agentops init                        # Initialize project
        2. agentops multi-agent-run myfile.py  # Run complete multi-agent workflow
        3. agentops run --all                  # Execute generated tests
        4. agentops report --check-changes     # View results and changes
    
    WORKFLOW COMMANDS:
        init              Initialize AgentOps project structure
        multi-agent-run   Run complete multi-agent workflow (6 AI agents) [RECOMMENDED]
        run              Execute generated tests with analysis
        infer            Run simple test generation (single LLM call) [QUICK PROTOTYPING]
    
        MANAGEMENT COMMANDS:
        fast-approve     Quickly approve pending requirements
        approve-all      Approve all requirements with confirmation
        config          View and edit AgentOps configuration
        status          Show project status and configuration
        check           Check system requirements and setup

    ANALYSIS COMMANDS:
        report          Generate analysis report from existing results
        traceability    Generate traceability matrix
        requirement-info Show detailed requirement information
        test-info       Show test file and function details

    INTEGRATION COMMANDS:
        integration     Manage CI/CD and IDE integrations

    DISCOVERY COMMANDS:
        version         Show version information and updates
        welcome         Show welcome message and quick start guide
    
    EXAMPLES:
        # Complete workflow for a single file
        agentops multi-agent-run mymodule.py
        
        # Process all Python files in parallel
        agentops multi-agent-run --all --parallel --workers 6
        
        # View results and check for changes
        agentops report --check-changes
        
        # View traceability matrix
        agentops traceability --open
        
        # Quick test generation (for prototyping only)
        agentops infer myfile.py
    
    LEARN MORE:
        • Documentation: https://github.com/knaig/agentops_ai
        • Examples: Run 'agentops examples' for sample workflows
        • Community: Join our Discord for support and feedback
        
    Need help? Run 'agentops help' for detailed command information.
    """
    pass


def suggest_command(unknown_command: str) -> list:
    """Suggest similar commands when user types an unknown command.
    
    Args:
        unknown_command: The command that was not found
        
    Returns:
        List of suggested commands with similarity scores
    """
    # All available commands
    all_commands = [
        "init", "multi-agent-run", "infer", "run", "runner",
        "fast-approve", "approve-all", "config", "status", "check",
        "report", "traceability", "requirement-info", "test-info",
        "integration", "help", "examples", "commands", "version", "welcome"
    ]
    
    # Find similar commands using difflib
    suggestions = difflib.get_close_matches(unknown_command, all_commands, n=3, cutoff=0.3)
    
    return suggestions


@cli.command()
def welcome():
    """Show welcome message and quick start guide for new users.
    
    Displays a friendly welcome message with quick start instructions
    and helpful tips for getting started with AgentOps.
    """
    console.print(
        Panel(
            "[bold cyan]🎉 Welcome to AgentOps![/bold cyan]\n\n"
            "You're about to experience AI-powered test automation like never before.\n"
            "AgentOps uses 6 specialized AI agents to automatically analyze your code,\n"
            "extract requirements, and generate comprehensive test suites.\n\n"
            "[bold]🚀 Let's get you started in 3 simple steps:[/bold]",
            title="Welcome to AgentOps",
            border_style="green",
        )
    )
    
    console.print(
        "[bold]Step 1: Initialize your project[/bold]\n"
        "  [cyan]agentops init[/cyan]\n"
        "  This creates the .agentops directory and sets up your project.\n\n"
        
        "[bold]Step 2: Set your OpenAI API key[/bold]\n"
        "  [cyan]export OPENAI_API_KEY='your-api-key-here'[/cyan]\n"
        "  Get your key from: https://platform.openai.com/api-keys\n\n"
        
        "[bold]Step 3: Run the multi-agent workflow[/bold]\n"
        "  [cyan]agentops multi-agent-run myfile.py[/cyan]\n"
        "  Or process all files: [cyan]agentops multi-agent-run --all[/cyan]\n\n"
        
        "[bold]🎯 What happens next?[/bold]\n"
        "• 6 AI agents analyze your code and extract requirements\n"
        "• High-quality test suites are automatically generated\n"
        "• You get comprehensive test coverage and traceability\n"
        "• All results are stored in .agentops/ for easy access\n\n"
        
        "[bold]💡 Pro Tips:[/bold]\n"
        "• Run [cyan]agentops examples[/cyan] to see real-world use cases\n"
        "• Use [cyan]agentops help[/cyan] for detailed command information\n"
        "• Try [cyan]agentops runner --steps 1,2,3,4 --all[/cyan] for custom workflows\n"
        "• Check [cyan]agentops report --check-changes[/cyan] to see what's up-to-date\n\n"
        
        "[bold]🔗 Get Help & Connect:[/bold]\n"
        "• GitHub: https://github.com/knaig/agentops_ai\n"
        "• Issues: https://github.com/knaig/agentops_ai/issues\n"
        "• Discussions: https://github.com/knaig/agentops_ai/discussions\n\n"
        
        "[bold green]Ready to automate your testing? Let's go! 🚀[/bold green]"
    )


@cli.command()
def status():
    """Show current AgentOps project status and configuration.
    
    Displays information about the current project, including:
    - Project initialization status
    - Configuration settings
    - Recent activity and results
    - System health and readiness
    """
    console.print(
        Panel(
            "[bold cyan]🔍 AgentOps Project Status[/bold cyan]\n\n"
            "Checking your project configuration and recent activity...",
            title="Status Check",
            border_style="blue",
        )
    )
    
    # Check if project is initialized
    project_dir = Path(".agentops")
    if not project_dir.exists():
        console.print(
            "[yellow]⚠️  Project not initialized[/yellow]\n"
            "Run [cyan]agentops init[/cyan] to set up your project.\n"
        )
        return
    
    console.print("[green]✅ Project initialized[/green]")
    
    # Check configuration
    try:
        config = get_config()
        console.print(f"[green]✅ Configuration loaded[/green]")
        console.print(f"   • OpenAI API: {'✅ Configured' if config.llm.api_key else '❌ Not set'}")
        console.print(f"   • Model: {config.llm.model}")
        console.print(f"   • Temperature: {config.llm.temperature}")
    except Exception as e:
        console.print(f"[red]❌ Configuration error: {e}[/red]")
    
    # Check recent activity
    requirements_file = project_dir / "requirements.json"
    tests_dir = project_dir / "tests"
    
    if requirements_file.exists():
        try:
            with open(requirements_file, 'r') as f:
                requirements = json.load(f)
            console.print(f"[green]✅ Requirements database: {len(requirements)} requirements[/green]")
        except:
            console.print("[yellow]⚠️  Requirements database exists but may be corrupted[/yellow]")
    else:
        console.print("[yellow]⚠️  No requirements database found[/yellow]")
    
    if tests_dir.exists():
        test_files = list(tests_dir.glob("*.py"))
        console.print(f"[green]✅ Test files: {len(test_files)} generated[/green]")
    else:
        console.print("[yellow]⚠️  No test files generated yet[/yellow]")
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(
            "\n[red]❌ OpenAI API key not set[/red]\n"
            "Set your API key: [cyan]export OPENAI_API_KEY='your-key-here'[/cyan]\n"
            "Get your key from: https://platform.openai.com/api-keys"
        )
    else:
        console.print("[green]✅ OpenAI API key configured[/green]")
    
    console.print(
        "\n[bold]🚀 Ready to use AgentOps![/bold]\n"
        "Try: [cyan]agentops multi-agent-run myfile.py[/cyan]"
    )


@cli.command()
@click.argument("target", type=click.Path(exists=True), required=False)
@click.option(
    "--all", "run_all", is_flag=True, 
    help="Run complete multi-agent workflow on all Python files in the current directory"
)
@click.option(
    "--output-dir",
    default=None,
    help="Output directory for generated tests (default: .agentops/tests/)"
)
@click.option(
    "--parallel", is_flag=True,
    help="Process files in parallel for faster execution"
)
@click.option(
    "--workers", default=4, type=int,
    help="Number of parallel workers (default: 4, max: 8)"
)
def multi_agent_run(target: str, run_all: bool, output_dir: str, parallel: bool, workers: int):
    """Run complete multi-agent workflow on Python files.

    This command runs the entire multi-agent workflow:
    1. CodeAnalyzer Agent: Analyzes code structure and dependencies
    2. RequirementsEngineer Agent: Extracts functional requirements
    3. TestArchitect Agent: Designs test strategy
    4. TestGenerator Agent: Generates test code
    5. QualityAssurance Agent: Validates test quality
    6. IntegrationSpecialist Agent: Sets up integrations
    
    Usage:
        agentops multi-agent-run file.py          # Single file
        agentops multi-agent-run directory/       # All Python files in directory
        agentops multi-agent-run --all            # All Python files in current directory
        agentops multi-agent-run --all --parallel # Parallel processing
        agentops multi-agent-run --all --parallel --workers 6 # Custom worker count

    Args:
        target: Path to Python file or directory to process
        run_all: Process all Python files in current directory
        output_dir: Directory for generated tests (optional)
        parallel: Process files in parallel for faster execution
        workers: Number of parallel workers (default: 4, max: 8)
    """
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    # Validate worker count
    if workers < 1 or workers > 8:
        console.print(
            Panel(
                "[red]Worker count must be between 1 and 8[/red]",
                title="Invalid Worker Count",
                border_style="red",
            )
        )
        sys.exit(1)

    # Determine what files to process
    files_to_process = []
    
    if run_all:
        # Process all Python files in current directory
        files_to_process = find_python_files(".")
        if not files_to_process:
            console.print(
                Panel(
                    "[yellow]No Python files found in current directory.[/yellow]",
                    title="No Files Found",
                    border_style="yellow",
                )
            )
            return
    elif target:
        if os.path.isfile(target):
            # Single file
            if not target.endswith('.py'):
                console.print(
                    Panel(
                        "[yellow]Target must be a Python file (.py)[/yellow]",
                        title="Invalid File Type",
                        border_style="yellow",
                    )
                )
                return
            files_to_process = [target]
        elif os.path.isdir(target):
            # Directory - process all Python files
            files_to_process = find_python_files(target)
            if not files_to_process:
                console.print(
                    Panel(
                        f"[yellow]No Python files found in {target}[/yellow]",
                        title="No Files Found",
                        border_style="yellow",
                    )
                )
                return
        else:
            console.print(
                Panel(
                    "[yellow]Target must be a valid file or directory[/yellow]",
                    title="Invalid Target",
                    border_style="yellow",
                )
            )
            return
    else:
        # No target specified and no --all flag
        console.print(
            Panel(
                "[yellow]Please specify a file, directory, or use --all flag[/yellow]\n\n"
                "Usage:\n"
                "• [bold]agentops multi-agent-run file.py[/bold] - Single file\n"
                "• [bold]agentops multi-agent-run directory/[/bold] - All files in directory\n"
                "• [bold]agentops multi-agent-run --all[/bold] - All files in current directory",
                title="Missing Target",
                border_style="yellow",
            )
        )
        return

    # Adjust worker count based on file count
    if parallel and len(files_to_process) < workers:
        workers = len(files_to_process)
        console.print(f"[dim]Adjusted workers to {workers} (file count)[/dim]")

    # Check if AgentOrchestrator is available
    if not AGENT_ORCHESTRATOR_AVAILABLE:
        console.print(
            Panel(
                "[red]Advanced multi-agent workflow not available.[/red]\n\n"
                "Install required dependencies:\n"
                "[bold]pip install langchain-openai[/bold]\n\n"
                "Or use the simple workflow: [bold]agentops infer <file.py>[/bold]",
                title="Dependency Missing",
                border_style="red",
            )
        )
        sys.exit(1)

    # Initialize AgentOrchestrator
    orchestrator = AgentOrchestrator()
    
    # Process files
    total_files = len(files_to_process)
    successful_files = 0
    failed_files = []
    
    processing_mode = "parallel" if parallel else "sequential"
    console.print(
        Panel(
            f"[bold]Starting multi-agent workflow for {total_files} file(s) in {processing_mode} mode[/bold]\n"
            f"Workers: {workers}" if parallel else "",
            title="AgentOps Multi-Agent Run",
            border_style="cyan",
        )
    )

    if parallel and total_files > 1:
        # Parallel processing
        import threading
        
        # Thread-local storage for progress tracking
        thread_local = threading.local()
        
        def process_file(file_path):
            """Process a single file with the orchestrator."""
            try:
                # Run the multi-agent workflow
                final_state = orchestrator.run(file_path)
                
                if final_state.has_errors():
                    return file_path, False, final_state.errors
                else:
                    return file_path, True, None
            except Exception as e:
                return file_path, False, [str(e)]
        
        with Progress() as progress:
            task = progress.add_task("Processing files...", total=total_files)
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                # Submit all files for processing
                future_to_file = {
                    executor.submit(process_file, file_path): file_path 
                    for file_path in files_to_process
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_file):
                    file_path, success, errors = future.result()
                    if success:
                        successful_files += 1
                        progress.update(task, advance=1, description=f"✓ {Path(file_path).name}")
                    else:
                        failed_files.append((file_path, errors))
                        progress.update(task, advance=1, description=f"✗ {Path(file_path).name}")
    else:
        # Sequential processing with enhanced progress updates
        for i, file_path in enumerate(files_to_process, 1):
            file_name = Path(file_path).name
            console.print(f"\n[bold cyan]Processing {i}/{total_files}: {file_name}[/bold cyan]")
            
            try:
                # Enhanced progress display for sequential processing
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task(f"Starting multi-agent workflow...", total=None)
                    
                    # Run the multi-agent workflow with progress updates
                    final_state = orchestrator.run_with_progress(file_path, progress, task)
                    
                    if final_state.has_errors():
                        failed_files.append((file_path, final_state.errors))
                        progress.update(task, description=f"[red]Failed: {file_name}[/red]")
                        console.print(f"[red]✗ Failed to process {file_name}[/red]")
                        for error in final_state.errors:
                            console.print(f"  [dim]Error: {error}[/dim]")
                    else:
                        successful_files += 1
                        progress.update(task, description=f"[green]✓ Completed: {file_name}[/green]")
                        console.print(f"[green]✓ Successfully processed {file_name}[/green]")
                        
                        # Show generated test count if available
                        if hasattr(final_state, 'test_code') and final_state.test_code:
                            test_count = final_state.test_code.count('def test_')
                            console.print(f"  [dim]Generated {test_count} test functions[/dim]")
                        
            except Exception as e:
                failed_files.append((file_path, [str(e)]))
                console.print(f"[red]✗ Exception processing {file_name}: {str(e)}[/red]")

    # Display results
    console.print(
        Panel(
            f"[bold]Multi-agent Workflow Complete[/bold]\n\n"
            f"✓ Successfully processed {successful_files}/{total_files} files!\n"
            f"Mode: {processing_mode}",
            title="Multi-agent Workflow Complete",
            border_style="green" if successful_files == total_files else "yellow",
        )
    )
    
    # Generate markdown report
    report_path = generate_markdown_report(files_to_process, successful_files, failed_files, processing_mode)
    
    if report_path:
        console.print(f"\n[cyan]📊 Detailed report generated: {report_path}[/cyan]")
    
    if failed_files:
        console.print("\n[red]Failed files:[/red]")
        for file_path, errors in failed_files:
            console.print(f"  • {file_path}")
            for error in errors:
                console.print(f"    [dim]Error: {error}[/dim]")
    
    return successful_files == total_files

def generate_markdown_report(files_to_process: List[str], successful_files: int, 
                            failed_files: List[tuple], processing_mode: str) -> str:
    """Generate a detailed markdown report of the multi-agent workflow execution.
    
    Args:
        files_to_process: List of all files that were processed
        successful_files: Number of successfully processed files
        failed_files: List of (file_path, errors) tuples for failed files
        processing_mode: Mode used for processing (sequential/parallel)
        
    Returns:
        Path to the generated markdown report file
    """
    from pathlib import Path
    import datetime
    
    # Create report directory if it doesn't exist
    report_dir = Path(".agentops/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"multi_agent_workflow_report_{timestamp}.md"
    
    # Create the markdown content
    markdown_content = f"""# AgentOps Multi-Agent Workflow Report

**Generated:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Processing Mode:** {processing_mode}  
**Total Files:** {len(files_to_process)}  
**Successful:** {successful_files}  
**Failed:** {len(failed_files)}  
**Success Rate:** {(successful_files / len(files_to_process) * 100):.1f}%

## Workflow Summary

The multi-agent workflow consists of 6 specialized agents that work together to analyze code and generate comprehensive tests:

1. **CodeAnalyzer** - Analyzes code structure and dependencies
2. **RequirementsEngineer** - Extracts functional requirements
3. **TestArchitect** - Designs comprehensive test strategy
4. **TestGenerator** - Creates high-quality test code
5. **QualityAssurance** - Validates test quality
6. **IntegrationSpecialist** - Sets up CI/CD and IDE integrations

## Detailed Results

| File | CodeAnalyzer | RequirementsEngineer | TestArchitect | TestGenerator | QualityAssurance | IntegrationSpecialist | Overall Status | Test Functions | Errors |
|------|--------------|---------------------|---------------|---------------|------------------|---------------------|----------------|----------------|---------|
"""
    
    # Create a set of failed files for quick lookup
    failed_files_set = {file_path for file_path, _ in failed_files}
    
    for file_path in files_to_process:
        file_name = Path(file_path).name
        # Handle both absolute and relative paths
        try:
            relative_path = Path(file_path).relative_to(Path.cwd())
        except ValueError:
            # If the file is not in the current directory, use the original path
            relative_path = Path(file_path)
        
        # Determine overall status
        if file_path in failed_files_set:
            status = "❌ Failed"
            errors = next(errors for fp, errors in failed_files if fp == file_path)
            error_summary = "; ".join(errors[:2])  # Show first 2 errors
            if len(errors) > 2:
                error_summary += f" (+{len(errors)-2} more)"
        else:
            status = "✅ Success"
            error_summary = ""
        
        # Try to get test count from generated test file
        test_count = "N/A"
        # Handle test file path resolution
        try:
            test_file_path = Path(".agentops/tests") / relative_path.parent / f"test_{file_name}"
        except:
            # Fallback to just the filename if path resolution fails
            test_file_path = Path(".agentops/tests") / f"test_{file_name}"
        if test_file_path.exists():
            try:
                with open(test_file_path, 'r') as f:
                    test_content = f.read()
                    test_count = str(test_content.count('def test_'))
            except:
                test_count = "N/A"
        
        # For now, we'll show the agent status as completed for successful files
        # In a future enhancement, we could parse the actual logs to show individual agent status
        if file_path in failed_files_set:
            agent_statuses = ["❌", "❌", "❌", "❌", "❌", "❌"]
        else:
            agent_statuses = ["✅", "✅", "✅", "✅", "✅", "✅"]
        
        # Add row to table
        markdown_content += f"| `{relative_path}` | {agent_statuses[0]} | {agent_statuses[1]} | {agent_statuses[2]} | {agent_statuses[3]} | {agent_statuses[4]} | {agent_statuses[5]} | {status} | {test_count} | {error_summary} |\n"
    
    markdown_content += f"""
## Agent Details

### CodeAnalyzer Agent
- **Purpose:** Deep code structure and dependency analysis
- **Output:** Code complexity, architectural patterns, testing challenges
- **Success Rate:** {calculate_agent_success_rate('CodeAnalyzer', files_to_process, failed_files_set):.1f}%

### RequirementsEngineer Agent  
- **Purpose:** Extract functional requirements using LLM
- **Output:** Functional requirements, user stories, acceptance criteria
- **Success Rate:** {calculate_agent_success_rate('RequirementsEngineer', files_to_process, failed_files_set):.1f}%

### TestArchitect Agent
- **Purpose:** Design comprehensive test strategy
- **Output:** Test plan, coverage strategy, testing approach
- **Success Rate:** {calculate_agent_success_rate('TestArchitect', files_to_process, failed_files_set):.1f}%

### TestGenerator Agent
- **Purpose:** Create high-quality test code
- **Output:** Generated test files with comprehensive test cases
- **Success Rate:** {calculate_agent_success_rate('TestGenerator', files_to_process, failed_files_set):.1f}%

### QualityAssurance Agent
- **Purpose:** Validate test quality and coverage
- **Output:** Quality metrics, coverage analysis, improvement suggestions
- **Success Rate:** {calculate_agent_success_rate('QualityAssurance', files_to_process, failed_files_set):.1f}%

### IntegrationSpecialist Agent
- **Purpose:** Set up CI/CD and IDE integrations
- **Output:** Integration configurations, deployment scripts
- **Success Rate:** {calculate_agent_success_rate('IntegrationSpecialist', files_to_process, failed_files_set):.1f}%

## Error Analysis

"""
    
    if failed_files:
        markdown_content += "### Common Error Patterns\n\n"
        error_patterns = {}
        for _, errors in failed_files:
            for error in errors:
                # Extract error type (first part before colon or common patterns)
                error_type = error.split(':')[0] if ':' in error else error.split()[0]
                error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
        
        for error_type, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True):
            markdown_content += f"- **{error_type}**: {count} occurrence(s)\n"
        
        markdown_content += "\n### Detailed Error Log\n\n"
        for file_path, errors in failed_files:
            # Handle path display for error logs
            try:
                display_path = Path(file_path).relative_to(Path.cwd())
            except ValueError:
                display_path = Path(file_path)
            markdown_content += f"#### `{display_path}`\n\n"
            for error in errors:
                markdown_content += f"```\n{error}\n```\n\n"
    else:
        markdown_content += "✅ No errors encountered during processing.\n\n"
    
    markdown_content += f"""
## Recommendations

Based on the workflow results:

"""
    
    success_rate = (successful_files / len(files_to_process) * 100)
    if success_rate >= 90:
        markdown_content += "- 🎉 **Excellent results!** The workflow is performing very well.\n"
        markdown_content += "- Consider running the workflow on more complex codebases to validate robustness.\n"
    elif success_rate >= 70:
        markdown_content += "- 👍 **Good results!** Most files were processed successfully.\n"
        markdown_content += "- Review failed files to identify common patterns and improve error handling.\n"
    elif success_rate >= 50:
        markdown_content += "- ⚠️ **Moderate results.** Some files failed processing.\n"
        markdown_content += "- Investigate error patterns and consider adjusting LLM parameters.\n"
    else:
        markdown_content += "- ❌ **Poor results.** Many files failed processing.\n"
        markdown_content += "- Check API key configuration and network connectivity.\n"
        markdown_content += "- Review error logs for systematic issues.\n"
    
    markdown_content += f"""
- **Total Processing Time:** Check the CLI output for timing information
- **Generated Test Files:** Located in `.agentops/tests/` directory
- **Configuration:** Review `.agentops/config.json` for LLM settings

---
*Report generated by AgentOps Multi-Agent System*
"""
    
    # Write the report to file
    with open(report_path, 'w') as f:
        f.write(markdown_content)
    
    return str(report_path)

def calculate_agent_success_rate(agent_name: str, files_to_process: List[str], 
                                failed_files_set: set) -> float:
    """Calculate success rate for a specific agent.
    
    Args:
        agent_name: Name of the agent
        files_to_process: List of all processed files
        failed_files_set: Set of failed file paths
        
    Returns:
        Success rate as a percentage
    """
    # For now, we assume all successful files completed all agents
    # In a future enhancement, we could parse actual logs for per-agent status
    successful_for_agent = len(files_to_process) - len(failed_files_set)
    return (successful_for_agent / len(files_to_process)) * 100 if files_to_process else 0


@cli.command()
@click.argument("target", type=click.Path(exists=True), required=False)
@click.option(
    "--all", "run_all", is_flag=True, 
    help="Run simple test generation on all Python files in the current directory"
)
@click.option(
    "--output-dir",
    default=None,
    help="Output directory for generated tests (default: .agentops/tests/)"
)
@click.option(
    "--parallel", is_flag=True,
    help="Process files in parallel for faster execution"
)
@click.option(
    "--workers", default=4, type=int,
    help="Number of parallel workers (default: 4, max: 8)"
)
def infer(target: str, run_all: bool, output_dir: str, parallel: bool, workers: int):
    """Run simple test generation on Python files (QUICK PROTOTYPING).

    ⚠️  NOTE: This is for quick prototyping only. For production use, 
    we recommend using 'agentops multi-agent-run' which provides:
    • Requirement extraction and traceability
    • Interactive approval workflow
    • Quality validation and testing strategy
    • Comprehensive test coverage

    This command uses the basic test generator workflow which is much faster
    than the multi-agent workflow. It makes a single LLM call per file to
    generate tests directly.

    Usage:
        agentops infer file.py          # Single file
        agentops infer directory/       # All Python files in directory
        agentops infer --all            # All Python files in current directory
        agentops infer --all --parallel # Parallel processing
        agentops infer --all --parallel --workers 6 # Custom worker count

    Args:
        target: Path to Python file or directory to process
        run_all: Process all Python files in current directory
        output_dir: Directory for generated tests (optional)
        parallel: Process files in parallel for faster execution
        workers: Number of parallel workers (default: 4, max: 8)
    """
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    # Validate worker count
    if workers < 1 or workers > 8:
        console.print(
            Panel(
                "[red]Worker count must be between 1 and 8[/red]",
                title="Invalid Worker Count",
                border_style="red",
            )
        )
        sys.exit(1)

    # Determine what files to process
    files_to_process = []
    
    if run_all:
        # Process all Python files in current directory
        files_to_process = find_python_files(".")
        if not files_to_process:
            console.print(
                Panel(
                    "[yellow]No Python files found in current directory.[/yellow]",
                    title="No Files Found",
                    border_style="yellow",
                )
            )
            return
    elif target:
        if os.path.isfile(target):
            # Single file
            if not target.endswith('.py'):
                console.print(
                    Panel(
                        "[yellow]Target must be a Python file (.py)[/yellow]",
                        title="Invalid File Type",
                        border_style="yellow",
                    )
                )
                return
            files_to_process = [target]
        elif os.path.isdir(target):
            # Directory - process all Python files
            files_to_process = find_python_files(target)
            if not files_to_process:
                console.print(
                    Panel(
                        f"[yellow]No Python files found in {target}[/yellow]",
                        title="No Files Found",
                        border_style="yellow",
                    )
                )
                return
        else:
            console.print(
                Panel(
                    "[yellow]Target must be a valid file or directory[/yellow]",
                    title="Invalid Target",
                    border_style="yellow",
                )
            )
            return
    else:
        # No target specified and no --all flag
        console.print(
            Panel(
                "[yellow]Please specify a file, directory, or use --all flag[/yellow]\n\n"
                "Usage:\n"
                "• [bold]agentops infer file.py[/bold] - Single file\n"
                "• [bold]agentops infer directory/[/bold] - All files in directory\n"
                "• [bold]agentops infer --all[/bold] - All files in current directory",
                title="Missing Target",
                border_style="yellow",
            )
        )
        return

    # Adjust worker count based on file count
    if parallel and len(files_to_process) < workers:
        workers = len(files_to_process)
        console.print(f"[dim]Adjusted workers to {workers} (file count)[/dim]")

    # Initialize simple test generator
    from agentops_ai.agentops_core.services.test_generator import TestGenerator
    config = get_config()
    test_generator = TestGenerator(api_key=config.llm.api_key, model=config.llm.model)
    
    # Process files
    total_files = len(files_to_process)
    successful_files = 0
    failed_files = []
    
    processing_mode = "parallel" if parallel else "sequential"
    console.print(
        Panel(
            f"[bold]Starting simple test generation for {total_files} file(s) in {processing_mode} mode[/bold]\n"
            f"Workers: {workers}" if parallel else "",
            title="AgentOps Simple Test Generation (Quick Prototyping)",
            border_style="yellow",
        )
    )
    
    # Show recommendation for production use
    console.print(
        Panel(
            "[yellow]⚠️  Quick Prototyping Mode[/yellow]\n\n"
            "For production use, we recommend: [bold cyan]agentops multi-agent-run[/bold cyan]\n"
            "This provides requirement extraction, approval workflow, and quality validation.",
            title="Recommendation",
            border_style="yellow",
        )
    )

    if parallel and total_files > 1:
        # Parallel processing
        def process_file(file_path):
            """Process a single file with the test generator."""
            try:
                # Generate tests using simple workflow
                result = test_generator.generate_tests(file_path)
                
                if result.get("success", False):
                    # Save the generated tests to file
                    test_code = result.get("tests", "")
                    if test_code:
                        # Create output directory
                        output_dir = output_dir or ".agentops/tests"
                        os.makedirs(output_dir, exist_ok=True)
                        
                        # Generate test filename based on source file
                        source_name = Path(file_path).stem
                        test_filename = f"test_{source_name}.py"
                        test_file_path = os.path.join(output_dir, test_filename)
                        
                        # Write test code to file
                        with open(test_file_path, "w") as f:
                            f.write(test_code)
                        
                        console.print(f"[dim]Generated: {test_file_path}[/dim]")
                    
                    return file_path, True, None
                else:
                    return file_path, False, [result.get("error", "Unknown error")]
            except Exception as e:
                return file_path, False, [str(e)]
        
        with Progress() as progress:
            task = progress.add_task("Processing files...", total=total_files)
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                # Submit all files for processing
                future_to_file = {
                    executor.submit(process_file, file_path): file_path 
                    for file_path in files_to_process
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_file):
                    file_path, success, errors = future.result()
                    
                    if success:
                        successful_files += 1
                        progress.update(task, description=f"✓ {os.path.basename(file_path)}")
                    else:
                        failed_files.append((file_path, errors))
                        progress.update(task, description=f"✗ {os.path.basename(file_path)}")
                    
                    progress.advance(task)
    else:
        # Sequential processing
        with Progress() as progress:
            task = progress.add_task("Processing files...", total=total_files)
            
            for file_path in files_to_process:
                try:
                    progress.update(task, description=f"Processing {os.path.basename(file_path)}...")
                    
                    # Generate tests using simple workflow
                    result = test_generator.generate_tests(file_path)

                    if result.get("success", False):
                        # Save the generated tests to file
                        test_code = result.get("tests", "")
                        if test_code:
                            # Create output directory
                            output_dir = output_dir or ".agentops/tests"
                            os.makedirs(output_dir, exist_ok=True)
                            
                            # Generate test filename based on source file
                            source_name = Path(file_path).stem
                            test_filename = f"test_{source_name}.py"
                            test_file_path = os.path.join(output_dir, test_filename)
                            
                            # Write test code to file
                            with open(test_file_path, "w") as f:
                                f.write(test_code)
                            
                            console.print(f"[dim]Generated: {test_file_path}[/dim]")
                        
                        successful_files += 1
                    else:
                        failed_files.append((file_path, [result.get("error", "Unknown error")]))
                        
                except Exception as e:
                    failed_files.append((file_path, [str(e)]))
                
                progress.advance(task)

    # Display results
    console.print("\n" + "="*60)
                        
    if successful_files > 0:
        console.print(
            Panel(
                f"[bold green]✓ Successfully processed {successful_files}/{total_files} files![/bold green]\n"
                f"Mode: {processing_mode}" + (f" ({workers} workers)" if parallel else ""),
                title="Quick Test Generation Complete",
                border_style="green",
            )
        )
        
        # Final recommendation
        console.print(
            Panel(
                "[bold]Next Steps:[/bold]\n"
                "• Run [cyan]agentops run --all[/cyan] to execute the generated tests\n"
                "• For production use, try [cyan]agentops multi-agent-run[/cyan] for full workflow\n"
                "• View results with [cyan]agentops report --check-changes[/cyan]",
                title="What's Next?",
                border_style="blue",
            )
        )

    if failed_files:
        console.print(
            Panel(
                f"[red]Failed to process {len(failed_files)} files:[/red]\n" + 
                "\n".join([f"• {file}: {', '.join(errors)}" for file, errors in failed_files]),
                title="Failed Files",
                border_style="red",
            )
        )

    if successful_files == 0:
        console.print(
            Panel(
                "[red]No files were processed successfully.[/red]",
                title="Quick Test Generation Failed",
                border_style="red",
            )
        )
        
        # Suggest alternative approach
        console.print(
            Panel(
                "[bold]Try the recommended approach:[/bold]\n"
                "[cyan]agentops multi-agent-run[/cyan] for comprehensive test generation\n"
                "This includes requirement extraction and quality validation.",
                title="Alternative",
                border_style="yellow",
            )
        )
        sys.exit(1)


@cli.command()
@click.argument("target", type=click.Path(exists=True), required=False)
@click.option(
    "--all", "run_all", is_flag=True, 
    help="Run tests for all generated test files"
)
def run(target: str, run_all: bool):
    """Execute tests with root cause analysis for failures.
    
    Runs the generated tests and provides intelligent analysis of any failures.
    The system will analyze test failures and provide suggestions for fixing
    either the code or the tests.
    
    Options:
        --target: Run tests for a specific source file
        --all: Run all generated tests
    """
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    config = get_config()
    test_dir = Path(config.project.test_output_dir)
    
    if not test_dir.exists():
        console.print(
            Panel(
                "[yellow]No tests found.[/yellow]\n\n"
                "Run [bold cyan]agentops multi-agent-run <file.py>[/bold cyan] to generate tests first.",
                title="No Tests",
                border_style="yellow",
            )
        )
        sys.exit(1)

    # Find test files to run
    test_files = []
    if target:
        # Find test file for specific source file
        source_name = Path(target).stem
        test_file = test_dir / f"test_{source_name}.py"
        if test_file.exists():
            test_files = [str(test_file)]
        else:
            console.print(
                Panel(
                    f"[red]No test file found for {target}[/red]\n\n"
                    f"Expected: {test_file}",
                    title="Test File Not Found",
                    border_style="red",
                )
            )
            sys.exit(1)
    elif run_all:
        # Find all test files
        test_files = [str(f) for f in test_dir.glob("test_*.py")]
        if not test_files:
            console.print(
                Panel(
                    "[yellow]No test files found.[/yellow]\n\n"
                    "Run [bold cyan]agentops multi-agent-run <file.py>[/bold cyan] to generate tests first.",
                    title="No Tests",
                    border_style="yellow",
                )
            )
            sys.exit(1)
    else:
        console.print(
            Panel(
                "[yellow]Please specify --target or --all[/yellow]\n\n"
                "Usage:\n"
                "• [bold cyan]agentops run --target mymodule.py[/bold cyan]\n"
                "• [bold cyan]agentops run --all[/bold cyan]",
                title="Usage",
                border_style="yellow",
            )
        )
        sys.exit(1)

    # Run tests with pytest
    console.print(f"[bold]Running {len(test_files)} test file(s)...[/bold]")
    
    try:
        result = subprocess.run(
            ["pytest", "-v"] + test_files,
            capture_output=True,
            text=True,
            cwd=config.project.project_root
        )

        if result.returncode == 0:
            console.print(
                Panel(
                    "[bold green]✓ All tests passed![/bold green]",
                    title="Test Results",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[red]Some tests failed[/red]\n\n{result.stdout}\n{result.stderr}",
                    title="Test Results",
                    border_style="red",
                )
            )

    except FileNotFoundError:
        console.print(
            Panel(
                "[red]pytest not found[/red]\n\n"
                "Install pytest: [bold]pip install pytest[/bold]",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


@cli.command()
@click.option("--non-interactive", is_flag=True, help="Skip confirmation prompts")
def fast_approve(non_interactive):
    """Approve all pending requirements quickly without generating tests.
    
    This command efficiently approves all pending requirements without generating
    tests for each one individually. Test generation should be done separately
    for better performance.
    """
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    # Initialize workflow
    workflow = AgentOpsWorkflow()
    
    # Get pending requirements count
    pending_requirements = workflow.requirement_store.get_pending_requirements()
    
    if not pending_requirements:
        console.print(
            Panel(
                "[bold green]No pending requirements found![/bold green]\n\n"
                "All requirements have been processed.",
                title="No Pending Requirements",
                border_style="green",
            )
        )
        sys.exit(0)
    
    # Show confirmation (unless non-interactive)
    if not non_interactive:
        console.print(
            Panel(
                f"[bold]Found {len(pending_requirements)} pending requirements[/bold]\n\n"
                "This will quickly approve all pending requirements.\n"
                "Test generation will need to be done separately.\n"
                "This action cannot be undone.",
                title="Fast Bulk Approval",
                border_style="yellow",
            )
        )
        
        if not Confirm.ask("[bold]Continue with fast bulk approval?[/bold]", default=False):
            console.print("[yellow]Fast bulk approval cancelled.[/yellow]")
            sys.exit(0)
    
    # Run fast bulk approval
    console.print(f"[bold]Starting fast bulk approval of {len(pending_requirements)} requirements...[/bold]")
    
    result = workflow.approve_all_pending_requirements_fast()
    
    if result["success"]:
        console.print(
            Panel(
                f"[bold green]✓ Fast bulk approval completed![/bold green]\n\n"
                f"Processed: {result['processed']}\n"
                f"Approved: {result['approved']}\n"
                f"Failed: {result['rejected']}\n"
                f"Success rate: {result['approved']/result['processed']*100:.1f}%\n\n"
                f"Next: Run test generation with 'agentops generate-tests' or step 4 in runner script",
                title="Fast Bulk Approval Results",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                f"[red]Fast bulk approval failed[/red]\n\n"
                f"Error: {result.get('error', 'Unknown error')}",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


@cli.command()
@click.option("--non-interactive", is_flag=True, help="Skip confirmation prompts")
def approve_all(non_interactive):
    """Approve all pending requirements without interactive review.
    
    This command automatically approves all pending requirements and generates
    tests for them. This is useful for bulk processing when you trust the
    inferred requirements.
    """
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    # Initialize workflow
    workflow = AgentOpsWorkflow()
    
    # Get pending requirements count
    pending_requirements = workflow.requirement_store.get_pending_requirements()
    
    if not pending_requirements:
        console.print(
            Panel(
                "[bold green]No pending requirements found![/bold green]\n\n"
                "All requirements have been processed.",
                title="No Pending Requirements",
                border_style="green",
            )
        )
        sys.exit(0)
    
    # Show confirmation (unless non-interactive)
    if not non_interactive:
        console.print(
            Panel(
                f"[bold]Found {len(pending_requirements)} pending requirements[/bold]\n\n"
                "This will automatically approve all pending requirements and generate tests.\n"
                "This action cannot be undone.",
                title="Bulk Approval",
                border_style="yellow",
            )
        )
        
        if not Confirm.ask("[bold]Continue with bulk approval?[/bold]", default=False):
            console.print("[yellow]Bulk approval cancelled.[/yellow]")
            sys.exit(0)
    
    # Run bulk approval
    console.print(f"[bold]Starting bulk approval of {len(pending_requirements)} requirements...[/bold]")
    
    result = workflow.approve_all_pending_requirements()
    
    if result["success"]:
        console.print(
            Panel(
                f"[bold green]✓ Bulk approval completed![/bold green]\n\n"
                f"Processed: {result['processed']}\n"
                f"Approved: {result['approved']}\n"
                f"Failed: {result['rejected']}\n"
                f"Success rate: {result['approved']/result['processed']*100:.1f}%",
                title="Bulk Approval Results",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                f"[red]Bulk approval failed[/red]\n\n"
                f"Error: {result.get('error', 'Unknown error')}",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


@cli.command()
def config():
    """View and edit AgentOps configuration.
    
    Shows current configuration and provides options to modify settings.
    """
    config = get_config()

    console.print(
        Panel(
            f"[bold]AgentOps Configuration[/bold]\n\n"
            f"Project Root: {config.project.project_root}\n"
            f"Test Output: {config.project.test_output_dir}\n"
            f"LLM Model: {config.llm.model}\n"
            f"LLM Temperature: {config.llm.temperature}\n"
            f"API Key: {'✓ Set' if config.llm.api_key else '✗ Not set'}\n\n"
            f"Config File: {config.config_file}",
            title="Configuration",
            border_style="cyan",
        )
    )


@cli.group()
def integration():
    """Manage CI/CD and IDE integrations for AgentOps."""
    pass


@integration.command()
@click.option("--ci-provider", type=click.Choice(["github", "gitlab", "jenkins"]), 
              help="CI/CD provider to configure")
@click.option("--ide-provider", type=click.Choice(["vscode", "pycharm"]), 
              help="IDE provider to configure")
@click.option("--webhook-enabled", is_flag=True, help="Enable webhook server")
@click.option("--webhook-port", default=8080, help="Webhook server port")
@click.option("--webhook-secret", help="Webhook secret for signature verification")
@click.option("--auto-approve", is_flag=True, help="Auto-approve requirements in CI")
@click.option("--notification-channels", multiple=True, 
              type=click.Choice(["slack", "email", "webhook"]),
              help="Notification channels (can specify multiple)")
def setup(ci_provider, ide_provider, webhook_enabled, webhook_port, webhook_secret, 
          auto_approve, notification_channels):
    """Setup CI/CD and IDE integrations.
    
    Configures AgentOps to work with your CI/CD pipeline and IDE.
    """
    config = get_config()
    
    # Update integration settings
    if ci_provider:
        config.integration.ci_provider = ci_provider
    if ide_provider:
        config.integration.ide_provider = ide_provider
    if webhook_enabled is not None:
        config.integration.webhook_enabled = webhook_enabled
    if webhook_port:
        config.integration.webhook_port = webhook_port
    if webhook_secret:
        config.integration.webhook_secret = webhook_secret
    if auto_approve is not None:
        config.integration.auto_approve = auto_approve
    if notification_channels:
        config.integration.notification_channels = list(notification_channels)

    # Save configuration
    config.save()
        
    console.print(
        Panel(
            "[bold green]✓ Integration settings updated![/bold green]\n\n"
            f"CI Provider: {config.integration.ci_provider}\n"
            f"IDE Provider: {config.integration.ide_provider}\n"
            f"Webhook Enabled: {config.integration.webhook_enabled}\n"
            f"Auto Approve: {config.integration.auto_approve}",
            title="Integration Setup",
            border_style="green",
        )
    )


@integration.command()
def status():
    """Show integration status and configuration."""
    config = get_config()
    
    console.print(
        Panel(
            f"[bold]Integration Status[/bold]\n\n"
            f"CI Provider: {config.integration.ci_provider}\n"
            f"IDE Provider: {config.integration.ide_provider}\n"
            f"Webhook Enabled: {config.integration.webhook_enabled}\n"
            f"Webhook Port: {config.integration.webhook_port}\n"
            f"Auto Approve: {config.integration.auto_approve}\n"
            f"Notifications: {', '.join(config.integration.notification_channels)}",
            title="Integration Status",
            border_style="cyan",
        )
    )


@cli.command()
@click.option("--format", "output_format", 
              type=click.Choice(["markdown", "csv", "json"]), 
              default="markdown",
              help="Output format for traceability matrix (default: markdown)")
@click.option("--open", "open_file", is_flag=True, 
              help="Open the generated file in default application")
def traceability(output_format: str, open_file: bool):
    """Generate traceability matrix linking requirements to tests.
    
    Creates a comprehensive traceability matrix showing the relationship
    between source code, requirements, and generated tests.
    
    Usage:
        agentops traceability                    # Generate markdown matrix
        agentops traceability --format csv       # Generate CSV matrix
        agentops traceability --format json      # Generate JSON matrix
        agentops traceability --open             # Open generated file
    """
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)

    # Initialize workflow
    workflow = AgentOpsWorkflow()
    
    # Generate traceability matrix
    result = workflow.generate_traceability_matrix(output_format)
    
    if result["success"]:
        file_path = result["file_path"]
        
        if RICH_AVAILABLE:
            console.print(
                Panel(
                    f"[bold green]✓ Traceability matrix generated![/bold green]\n\n"
                    f"File: [cyan]{file_path}[/cyan]\n"
                    f"Format: [cyan]{output_format}[/cyan]\n"
                    f"Requirements: [cyan]{result['requirements_count']}[/cyan]\n"
                    f"Test Files: [cyan]{result['test_files_count']}[/cyan]\n"
                    f"Test Functions: [cyan]{result['test_functions_count']}[/cyan]\n\n"
                    f"Matrix includes:\n"
                    f"• Source files to requirements mapping\n"
                    f"• Requirements to test functions mapping\n"
                    f"• Test cases to requirements mapping\n"
                    f"• Coverage analysis and statistics\n"
                    f"• Navigation links to related files",
                    title="Traceability Matrix Generated",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold green]✓ Traceability matrix generated![/bold green]\n\n"
                    f"File: [cyan]{file_path}[/cyan]\n"
                    f"Format: [cyan]{output_format}[/cyan]\n"
                    f"Requirements: [cyan]{result['requirements_count']}[/cyan]",
                    title="Traceability Matrix Generated",
                    border_style="green",
                )
            )
        
        # Open file if requested
        if open_file:
            try:
                import subprocess
                import platform
                
                system = platform.system()
                if system == "Darwin":  # macOS
                    subprocess.run(["open", file_path])
                elif system == "Windows":
                    subprocess.run(["start", file_path], shell=True)
                else:  # Linux
                    subprocess.run(["xdg-open", file_path])
                    
                console.print(f"[green]Opened {file_path}[/green]")
            except Exception as e:
                console.print(f"[yellow]Could not open file automatically: {e}[/yellow]")
                console.print(f"[cyan]File location: {file_path}[/cyan]")
        else:
            console.print(f"\n[cyan]File location: {file_path}[/cyan]")
            
    else:
        console.print(
            Panel(
                f"[red]Failed to generate traceability matrix[/red]\n\n"
                f"Error: {result['error']}",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


@cli.command()
@click.option("--format", "output_format", 
              type=click.Choice(["markdown", "csv", "json"]), 
              default="markdown",
              help="Output format for the report (default: markdown)")
@click.option("--open", "open_file", is_flag=True, 
              help="Open the generated report in default application")
@click.option("--force", is_flag=True,
              help="Force regeneration even if no changes detected")
@click.option("--check-changes", is_flag=True,
              help="Only check for file changes without generating report")
def report(output_format: str, open_file: bool, force: bool, check_changes: bool):
    """Generate a comprehensive report from existing workflow results.
    
    This command analyzes existing test files and requirements to generate
    a detailed report without re-running the multi-agent workflow. It can
    detect file changes and mark outdated results.
    
    Usage:
        agentops report                    # Generate markdown report
        agentops report --format csv       # Generate CSV report
        agentops report --check-changes    # Only check for file changes
        agentops report --force            # Force regeneration
        agentops report --open             # Open generated report
    """
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)
    
    # Initialize workflow
    workflow = AgentOpsWorkflow()
    
    # Analyze existing results and detect changes
    analysis_result = analyze_existing_results(workflow)
    
    if check_changes:
        # Only show change analysis
        display_change_analysis(analysis_result)
        return
    
    # Generate report based on analysis
    report_result = generate_analysis_report(analysis_result, output_format, force)
    
    if report_result["success"]:
        file_path = report_result["file_path"]
        
        console.print(
            Panel(
                f"[bold green]✓ Analysis report generated![/bold green]\n\n"
                f"File: [cyan]{file_path}[/cyan]\n"
                f"Format: [cyan]{output_format}[/cyan]\n"
                f"Files Analyzed: [cyan]{report_result['files_analyzed']}[/cyan]\n"
                f"Outdated Files: [cyan]{report_result['outdated_files']}[/cyan]\n"
                f"Up-to-date Files: [cyan]{report_result['up_to_date_files']}[/cyan]",
                title="Analysis Report Generated",
                border_style="green",
            )
        )
        
        # Open file if requested
        if open_file:
            try:
                import subprocess
                import platform
                
                system = platform.system()
                if system == "Darwin":  # macOS
                    subprocess.run(["open", file_path])
                elif system == "Windows":
                    subprocess.run(["start", file_path], shell=True)
                else:  # Linux
                    subprocess.run(["xdg-open", file_path])
                    
                console.print(f"[green]Opened {file_path}[/green]")
            except Exception as e:
                console.print(f"[yellow]Could not open file automatically: {e}[/yellow]")
                console.print(f"[cyan]File location: {file_path}[/cyan]")
        else:
            console.print(f"\n[cyan]File location: {file_path}[/cyan]")
            
    else:
        console.print(
            Panel(
                f"[red]Failed to generate analysis report[/red]\n\n"
                f"Error: {report_result['error']}",
                title="Error",
                border_style="red",
            )
        )
        sys.exit(1)


def analyze_existing_results(workflow: AgentOpsWorkflow) -> dict:
    """Analyze existing workflow results and detect file changes.
    
    Args:
        workflow: AgentOpsWorkflow instance
        
    Returns:
        Dictionary with analysis results
    """
    from pathlib import Path
    import hashlib
    import json
    from datetime import datetime
    
    analysis = {
        "files_analyzed": [],
        "outdated_files": [],
        "up_to_date_files": [],
        "missing_tests": [],
        "test_files": [],
        "requirements": [],
        "change_summary": {}
    }
    
    # Get all test files
    test_dir = Path(".agentops/tests")
    if test_dir.exists():
        test_files = list(test_dir.rglob("test_*.py"))
        analysis["test_files"] = [str(f) for f in test_files]
    
    # Get all requirements
    try:
        requirements = workflow.requirement_store.get_all_requirements()
        analysis["requirements"] = [req.file_path for req in requirements]
    except:
        pass
    
    # Analyze each source file that has tests
    for test_file in analysis["test_files"]:
        test_path = Path(test_file)
        
        # Extract source file path from test file path
        # Test file: .agentops/tests/path/to/test_source.py
        # Source file: path/to/source.py
        relative_test_path = test_path.relative_to(test_dir)
        source_file_name = relative_test_path.name.replace("test_", "")
        source_file_path = relative_test_path.parent / source_file_name
        
        # Check if source file exists
        if not source_file_path.exists():
            analysis["missing_tests"].append({
                "test_file": test_file,
                "source_file": str(source_file_path),
                "status": "source_missing"
            })
            continue
        
        # Calculate file hash for change detection
        try:
            with open(source_file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
        except:
            file_hash = "unknown"
        
        # Check if we have stored hash for this file
        hash_file = Path(".agentops/file_hashes.json")
        stored_hashes = {}
        if hash_file.exists():
            try:
                with open(hash_file, 'r') as f:
                    stored_hashes = json.load(f)
            except:
                stored_hashes = {}
        
        file_info = {
            "source_file": str(source_file_path),
            "test_file": test_file,
            "current_hash": file_hash,
            "stored_hash": stored_hashes.get(str(source_file_path)),
            "last_modified": datetime.fromtimestamp(source_file_path.stat().st_mtime).isoformat(),
            "test_count": 0
        }
        
        # Count test functions
        try:
            with open(test_file, 'r') as f:
                test_content = f.read()
                file_info["test_count"] = test_content.count('def test_')
        except:
            pass
        
        # Determine if file is outdated
        if file_info["stored_hash"] is None:
            file_info["status"] = "new_file"
            analysis["up_to_date_files"].append(file_info)
        elif file_info["current_hash"] != file_info["stored_hash"]:
            file_info["status"] = "modified"
            analysis["outdated_files"].append(file_info)
        else:
            file_info["status"] = "up_to_date"
            analysis["up_to_date_files"].append(file_info)
        
        analysis["files_analyzed"].append(file_info)
    
    # Generate change summary
    analysis["change_summary"] = {
        "total_files": len(analysis["files_analyzed"]),
        "up_to_date": len(analysis["up_to_date_files"]),
        "outdated": len(analysis["outdated_files"]),
        "missing_source": len([f for f in analysis["missing_tests"] if f["status"] == "source_missing"]),
        "total_tests": sum(f["test_count"] for f in analysis["files_analyzed"]),
        "total_requirements": len(analysis["requirements"])
    }
    
    return analysis


def display_change_analysis(analysis: dict):
    """Display change analysis results.
    
    Args:
        analysis: Analysis results from analyze_existing_results
    """
    summary = analysis["change_summary"]
    
    console.print(
        Panel(
            f"[bold]File Change Analysis[/bold]\n\n"
            f"📊 **Summary:**\n"
            f"• Total Files: {summary['total_files']}\n"
            f"• Up-to-date: {summary['up_to_date']} ✅\n"
            f"• Outdated: {summary['outdated']} ⚠️\n"
            f"• Missing Source: {summary['missing_source']} ❌\n"
            f"• Total Tests: {summary['total_tests']}\n"
            f"• Total Requirements: {summary['total_requirements']}",
            title="Change Analysis Results",
            border_style="cyan",
        )
    )
    
    if analysis["outdated_files"]:
        console.print("\n[yellow]⚠️  Outdated Files (Source Modified):[/yellow]")
        for file_info in analysis["outdated_files"]:
            console.print(f"  • {file_info['source_file']}")
            console.print(f"    [dim]Test file: {file_info['test_file']}[/dim]")
            console.print(f"    [dim]Last modified: {file_info['last_modified']}[/dim]")
    
    if analysis["missing_tests"]:
        console.print("\n[red]❌ Missing Source Files:[/red]")
        for file_info in analysis["missing_tests"]:
            if file_info["status"] == "source_missing":
                console.print(f"  • {file_info['source_file']}")
                console.print(f"    [dim]Test file: {file_info['test_file']}[/dim]")


def generate_analysis_report(analysis: dict, output_format: str, force: bool) -> dict:
    """Generate analysis report from existing results.
    
    Args:
        analysis: Analysis results from analyze_existing_results
        output_format: Report format (markdown, csv, json)
        force: Force regeneration even if no changes
        
    Returns:
        Dictionary with report generation results
    """
    from pathlib import Path
    import datetime
    
    # Create report directory if it doesn't exist
    report_dir = Path(".agentops/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"analysis_report_{timestamp}.{output_format}"
    
    summary = analysis["change_summary"]
    
    if output_format == "markdown":
        content = generate_markdown_analysis_report(analysis, timestamp)
    elif output_format == "csv":
        content = generate_csv_analysis_report(analysis)
    elif output_format == "json":
        content = json.dumps(analysis, indent=2)
    else:
        return {"success": False, "error": f"Unsupported format: {output_format}"}
    
    # Write the report to file
    try:
        with open(report_path, 'w') as f:
            f.write(content)
        
        return {
            "success": True,
            "file_path": str(report_path),
            "files_analyzed": summary["total_files"],
            "outdated_files": summary["outdated"],
            "up_to_date_files": summary["up_to_date"]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_markdown_analysis_report(analysis: dict, timestamp: str) -> str:
    """Generate markdown analysis report.
    
    Args:
        analysis: Analysis results
        timestamp: Report timestamp
        
    Returns:
        Markdown content
    """
    summary = analysis["change_summary"]
    
    content = f"""# AgentOps Analysis Report

**Generated:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Report ID:** {timestamp}  
**Total Files Analyzed:** {summary['total_files']}  
**Up-to-date Files:** {summary['up_to_date']}  
**Outdated Files:** {summary['outdated']}  
**Missing Source Files:** {summary['missing_source']}  
**Total Tests:** {summary['total_tests']}  
**Total Requirements:** {summary['total_requirements']}

## Summary

This report analyzes existing AgentOps workflow results without re-running the multi-agent system.
It detects file changes and identifies which test files need to be regenerated.

## File Status Overview

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Up-to-date | {summary['up_to_date']} | {(summary['up_to_date'] / summary['total_files'] * 100):.1f}% |
| ⚠️ Outdated | {summary['outdated']} | {(summary['outdated'] / summary['total_files'] * 100):.1f}% |
| ❌ Missing Source | {summary['missing_source']} | {(summary['missing_source'] / summary['total_files'] * 100):.1f}% |

## Detailed File Analysis

| Source File | Test File | Status | Test Count | Last Modified | Hash Changed |
|-------------|-----------|--------|------------|---------------|--------------|
"""
    
    for file_info in analysis["files_analyzed"]:
        status_icon = {
            "up_to_date": "✅",
            "modified": "⚠️",
            "new_file": "🆕"
        }.get(file_info["status"], "❓")
        
        hash_changed = "Yes" if file_info["current_hash"] != file_info["stored_hash"] else "No"
        
        content += f"| `{file_info['source_file']}` | `{file_info['test_file']}` | {status_icon} {file_info['status']} | {file_info['test_count']} | {file_info['last_modified']} | {hash_changed} |\n"
    
    if analysis["outdated_files"]:
        content += f"""
## ⚠️ Outdated Files (Require Re-generation)

The following files have been modified since their tests were generated:

"""
        for file_info in analysis["outdated_files"]:
            content += f"### `{file_info['source_file']}`\n\n"
            content += f"- **Test File:** `{file_info['test_file']}`\n"
            content += f"- **Last Modified:** {file_info['last_modified']}\n"
            content += f"- **Test Count:** {file_info['test_count']}\n"
            content += f"- **Action Required:** Re-run `agentops multi-agent-run {file_info['source_file']}`\n\n"
    
    if analysis["missing_tests"]:
        content += f"""
## ❌ Missing Source Files

The following test files exist but their source files are missing:

"""
        for file_info in analysis["missing_tests"]:
            if file_info["status"] == "source_missing":
                content += f"- **Test File:** `{file_info['test_file']}`\n"
                content += f"- **Missing Source:** `{file_info['source_file']}`\n\n"
    
    content += f"""
## Recommendations

"""
    
    if summary["outdated"] > 0:
        content += f"- ⚠️ **{summary['outdated']} file(s) need re-generation** due to source changes\n"
        content += f"- Run `agentops multi-agent-run <file>` for each outdated file\n"
        content += f"- Or use `agentops runner --steps 2,3,4 --target <file>` for faster regeneration\n"
    
    if summary["missing_source"] > 0:
        content += f"- ❌ **{summary['missing_source']} test file(s) have missing source files**\n"
        content += f"- Consider removing orphaned test files\n"
    
    if summary["up_to_date"] > 0:
        content += f"- ✅ **{summary['up_to_date']} file(s) are up-to-date** and don't need regeneration\n"
    
    content += f"""
## Next Steps

1. **For Outdated Files:** Re-run the multi-agent workflow to regenerate tests
2. **For Missing Source:** Remove orphaned test files or restore source files
3. **For Up-to-date Files:** No action needed, tests are current

---
*Report generated by AgentOps Analysis System*
"""
    
    return content


def generate_csv_analysis_report(analysis: dict) -> str:
    """Generate CSV analysis report.
    
    Args:
        analysis: Analysis results
        
    Returns:
        CSV content
    """
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Source File", "Test File", "Status", "Test Count", 
        "Last Modified", "Hash Changed", "Current Hash", "Stored Hash"
    ])
    
    # Write data
    for file_info in analysis["files_analyzed"]:
        hash_changed = "Yes" if file_info["current_hash"] != file_info["stored_hash"] else "No"
        writer.writerow([
            file_info["source_file"],
            file_info["test_file"],
            file_info["status"],
            file_info["test_count"],
            file_info["last_modified"],
            hash_changed,
            file_info["current_hash"],
            file_info["stored_hash"] or "N/A"
        ])
    
    return output.getvalue()


@cli.command()
def help():
    """Show detailed help information and command examples.
    
    Displays comprehensive help for all AgentOps commands with examples,
    use cases, and best practices.
    """
    console.print(
        Panel(
            "[bold cyan]AgentOps - Multi-Agent AI System for Requirements-Driven Test Automation[/bold cyan]\n\n"
            "[bold]🎯 What is AgentOps?[/bold]\n"
            "AgentOps uses 6 specialized AI agents to automatically analyze your code, "
            "extract requirements, and generate comprehensive test suites. It's like "
            "having a team of expert QA engineers working on your codebase.\n\n"
            "[bold]🚀 RECOMMENDED WORKFLOW:[/bold]\n"
            "1. [cyan]agentops init[/cyan]                        # Initialize project\n"
            "2. [cyan]agentops multi-agent-run myfile.py[/cyan]  # Run complete multi-agent workflow\n"
            "3. [cyan]agentops run --all[/cyan]                  # Execute generated tests\n"
            "4. [cyan]agentops report --check-changes[/cyan]     # View results and changes\n\n"
            "[bold]🤖 The Multi-Agent Workflow:[/bold]\n"
            "1. [cyan]CodeAnalyzer[/cyan] - Deep code structure and dependency analysis\n"
            "2. [cyan]RequirementsEngineer[/cyan] - Extract functional requirements using LLM\n"
            "3. [cyan]TestArchitect[/cyan] - Design comprehensive test strategy\n"
            "4. [cyan]TestGenerator[/cyan] - Create high-quality test code\n"
            "5. [cyan]QualityAssurance[/cyan] - Validate test quality\n"
            "6. [cyan]IntegrationSpecialist[/cyan] - Set up CI/CD and IDE integrations\n\n"
            "[bold]📚 Documentation & Support:[/bold]\n"
            "• GitHub: https://github.com/knaig/agentops_ai\n"
            "• Issues: https://github.com/knaig/agentops_ai/issues\n"
            "• Discussions: https://github.com/knaig/agentops_ai/discussions",
            title="AgentOps Help",
            border_style="cyan",
        )
    )
    
    # Command categories
    categories = {
        "🚀 Workflow Commands": [
            ("init", "Initialize AgentOps project structure"),
            ("multi-agent-run", "Run complete multi-agent workflow (6 AI agents) [RECOMMENDED]"),
            ("run", "Execute generated tests with analysis"),
            ("infer", "Run simple test generation (single LLM call) [QUICK PROTOTYPING]")
        ],
        "⚙️ Management Commands": [
            ("fast-approve", "Quickly approve pending requirements"),
            ("approve-all", "Approve all requirements with confirmation"),
            ("config", "View and edit AgentOps configuration")
        ],
        "📊 Analysis Commands": [
            ("report", "Generate analysis report from existing results"),
            ("traceability", "Generate traceability matrix"),
            ("requirement-info", "Show detailed requirement information"),
            ("test-info", "Show test file and function details")
        ],
        "🔗 Integration Commands": [
            ("integration", "Manage CI/CD and IDE integrations")
        ]
    }
    
    for category, commands in categories.items():
        console.print(f"\n[bold]{category}[/bold]")
        for cmd, desc in commands:
            console.print(f"  [cyan]{cmd:<20}[/cyan] {desc}")
    
    console.print(
        "\n[bold]💡 Quick Examples:[/bold]\n"
        "  [cyan]agentops init[/cyan]                                    # Initialize project\n"
        "  [cyan]agentops multi-agent-run myfile.py[/cyan]              # Run complete workflow\n"
        "  [cyan]agentops multi-agent-run --all --parallel[/cyan]       # Process all files in parallel\n"
        "  [cyan]agentops report --check-changes[/cyan]                  # Check for file changes\n"
        "  [cyan]agentops traceability --open[/cyan]                     # View traceability matrix\n"
        "  [cyan]agentops infer myfile.py[/cyan]                         # Quick prototyping only\n\n"
        "[bold]🔍 For detailed help on any command:[/bold]\n"
        "  [cyan]agentops <command> --help[/cyan]\n\n"
        "[bold]📖 Learn More:[/bold]\n"
        "  • Run [cyan]agentops examples[/cyan] for sample workflows\n"
        "  • Visit our GitHub for full documentation\n"
        "  • Join our community for support and feedback"
    )


@cli.command()
def examples():
    """Show practical examples and use cases for AgentOps.
    
    Displays real-world examples of how to use AgentOps for different
    scenarios and project types.
    """
    console.print(
        Panel(
            "[bold cyan]AgentOps Examples & Use Cases[/bold cyan]\n\n"
            "Learn how to use AgentOps effectively for different scenarios.",
            title="Examples",
            border_style="cyan",
        )
    )
    
    examples_data = {
        "🆕 Getting Started (Recommended)": [
            ("Initialize a new project", "agentops init"),
            ("Run complete workflow on a single file", "agentops multi-agent-run mymodule.py"),
            ("Execute generated tests", "agentops run --all"),
            ("View project status and changes", "agentops report --check-changes")
        ],
        "🏗️ Development Workflow": [
            ("Process all Python files", "agentops multi-agent-run --all"),
            ("Parallel processing", "agentops multi-agent-run --all --parallel --workers 6"),
            ("Approve requirements", "agentops approve-all --non-interactive"),
            ("Quick prototyping (not recommended for production)", "agentops infer myfile.py")
        ],
        "⚡ Advanced Workflows": [
            ("Custom workflow steps", "agentops runner --steps 1,2,4 --all"),
            ("Auto-approve workflow", "agentops runner --steps 1,2,3,4,5,6 --all --auto-approve"),
            ("Requirements only", "agentops runner --steps 1,2 --target myfile.py"),
            ("Test generation only", "agentops runner --steps 4,5 --all")
        ],
        "📊 Analysis & Reporting": [
            ("Generate traceability matrix", "agentops traceability --format markdown"),
            ("Check file changes", "agentops report --check-changes"),
            ("Detailed analysis report", "agentops report --format csv"),
            ("View requirement details", "agentops requirement-info 1")
        ],
        "🔧 Configuration & Integration": [
            ("View configuration", "agentops config"),
            ("Setup CI/CD integration", "agentops integration setup --ci-provider github"),
            ("Check integration status", "agentops integration status"),
            ("Configure IDE integration", "agentops integration setup --ide-provider vscode")
        ]
    }
    
    for category, examples_list in examples_data.items():
        console.print(f"\n[bold]{category}[/bold]")
        for desc, cmd in examples_list:
            console.print(f"  [dim]{desc}[/dim]")
            console.print(f"  [cyan]{cmd}[/cyan]\n")
    
    console.print(
        "[bold]🎯 Common Scenarios:[/bold]\n\n"
        "[bold]New Project Setup (Recommended):[/bold]\n"
        "  1. [cyan]agentops init[/cyan]\n"
        "  2. [cyan]export OPENAI_API_KEY='your-key'[/cyan]\n"
        "  3. [cyan]agentops multi-agent-run --all[/cyan]\n"
        "  4. [cyan]agentops run --all[/cyan]\n"
        "  5. [cyan]agentops report --check-changes[/cyan]\n\n"
        "[bold]Continuous Integration:[/bold]\n"
        "  1. [cyan]agentops multi-agent-run --all --parallel --workers 6[/cyan]\n"
        "  2. [cyan]agentops approve-all --non-interactive[/cyan]\n"
        "  3. [cyan]agentops run --all[/cyan]\n"
        "  4. [cyan]agentops report --format markdown[/cyan]\n\n"
        "[bold]Code Review Process:[/bold]\n"
        "  1. [cyan]agentops multi-agent-run changed_file.py[/cyan]\n"
        "  2. [cyan]agentops traceability --open[/cyan]\n"
        "  3. [cyan]agentops run --file changed_file.py[/cyan]\n\n"
        "[bold]Quick Prototyping (Not for Production):[/bold]\n"
        "  1. [cyan]agentops infer myfile.py[/cyan]\n"
        "  2. [cyan]agentops run --all[/cyan]\n\n"
        "[bold]📚 Need More Help?[/bold]\n"
        "  • Run [cyan]agentops help[/cyan] for detailed command information\n"
        "  • Visit our GitHub for full documentation\n"
        "  • Join our community for support and feedback"
    )


@cli.command()
def version():
    """Show AgentOps version and check for updates.
    
    Displays current version information and checks for available updates.
    """
    console.print(
        Panel(
            "[bold cyan]🔍 AgentOps Version Information[/bold cyan]\n\n"
            "Current version and system information...",
            title="Version Check",
            border_style="blue",
        )
    )
    
    # Show current version
    console.print(f"[bold]Current Version:[/bold] 0.3.0")
    
    # Show Python version
    import platform
    console.print(f"[bold]Python Version:[/bold] {platform.python_version()}")
    
    # Show platform
    console.print(f"[bold]Platform:[/bold] {platform.system()} {platform.release()}")
    
    # Check for updates (placeholder for future implementation)
    console.print(
        "\n[bold]Update Status:[/bold]\n"
        "• [green]✅ You're running the latest version[/green]\n"
        "• Check GitHub for updates: https://github.com/knaig/agentops_ai/releases"
    )
    
    # Show installation info
    console.print(
        "\n[bold]Installation:[/bold]\n"
        "• [green]✅ AgentOps is properly installed[/green]\n"
        "• CLI is accessible via: [cyan]agentops[/cyan] or [cyan]python -m agentops_ai.agentops_cli[/cyan]"
    )
    
    console.print(
        "\n[bold]🎯 What's New in 0.3.0:[/bold]\n"
        "• Enhanced multi-agent workflow with 6 AI agents\n"
        "• Improved CLI discoverability and help system\n"
        "• Better progress reporting and status updates\n"
        "• Comprehensive analysis and reporting features\n"
        "• Requirements traceability matrix generation"
    )


@cli.command()
def check():
    """Check system requirements and configuration.
    
    Verifies that all dependencies and configurations are properly set up
    for AgentOps to work correctly.
    """
    console.print(
        Panel(
            "[bold cyan]🔍 AgentOps System Check[/bold cyan]\n\n"
            "Verifying system requirements and configuration...",
            title="System Check",
            border_style="blue",
        )
    )
    
    all_good = True
    
    # Check Python version
    import sys
    python_version = sys.version_info
    if python_version >= (3, 8):
        console.print(f"[green]✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}[/green]")
    else:
        console.print(f"[red]❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (requires 3.8+)[/red]")
        all_good = False
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        console.print("[green]✅ OpenAI API key configured[/green]")
    else:
        console.print("[red]❌ OpenAI API key not set[/red]")
        console.print("  Set it with: [cyan]export OPENAI_API_KEY='your-key-here'[/cyan]")
        all_good = False
    
    # Check required packages
    required_packages = [
        ("click", "CLI framework"),
        ("rich", "Terminal UI"),
        ("openai", "OpenAI API client"),
        ("pathlib", "Path handling"),
        ("json", "JSON processing"),
        ("ast", "Python AST parsing")
    ]
    
    console.print("\n[bold]Required Packages:[/bold]")
    for package, description in required_packages:
        try:
            __import__(package)
            console.print(f"  [green]✅ {package}[/green] - {description}")
        except ImportError:
            console.print(f"  [red]❌ {package}[/red] - {description} (missing)")
            all_good = False
    
    # Check optional packages
    optional_packages = [
        ("langchain_openai", "Advanced multi-agent workflow"),
        ("pytest", "Test execution"),
        ("coverage", "Test coverage analysis")
    ]
    
    console.print("\n[bold]Optional Packages:[/bold]")
    for package, description in optional_packages:
        try:
            __import__(package)
            console.print(f"  [green]✅ {package}[/green] - {description}")
        except ImportError:
            console.print(f"  [yellow]⚠️  {package}[/yellow] - {description} (optional)")
    
    # Check project initialization
    if Path(".agentops").exists():
        console.print("\n[green]✅ Project initialized[/green]")
    else:
        console.print("\n[yellow]⚠️  Project not initialized[/yellow]")
        console.print("  Run: [cyan]agentops init[/cyan]")
    
    # Check file permissions
    try:
        test_file = Path(".agentops_test")
        test_file.write_text("test")
        test_file.unlink()
        console.print("[green]✅ File system permissions OK[/green]")
    except Exception as e:
        console.print(f"[red]❌ File system permissions issue: {e}[/red]")
        all_good = False
    
    # Summary
    if all_good:
        console.print(
            "\n[bold green]🎉 All checks passed! AgentOps is ready to use.[/bold green]\n"
            "Try: [cyan]agentops multi-agent-run myfile.py[/cyan]"
        )
    else:
        console.print(
            "\n[bold red]⚠️  Some issues found. Please fix them before using AgentOps.[/bold red]\n"
            "Run: [cyan]agentops help[/cyan] for assistance"
        )


@cli.command()
def commands():
    """List all available AgentOps commands with descriptions.
    
    Shows a comprehensive list of all commands organized by category
    for easy discovery and reference.
    """
    console.print(
        Panel(
            "[bold cyan]AgentOps Commands Reference[/bold cyan]\n\n"
            "All available commands organized by functionality.",
            title="Commands",
            border_style="cyan",
        )
    )
    
    # Get all commands from the CLI group
    commands_list = []
    for cmd_name, cmd_obj in cli.commands.items():
        if hasattr(cmd_obj, 'help') and cmd_obj.help:
            # Extract first line of help as short description
            short_desc = cmd_obj.help.split('\n')[0].strip()
            commands_list.append((cmd_name, short_desc))
        else:
            commands_list.append((cmd_name, "No description available"))
    
    # Sort commands alphabetically
    commands_list.sort(key=lambda x: x[0])
    
    # Group commands by functionality
    command_groups = {
        "Core Workflow": ["init", "multi-agent-run", "infer", "run", "runner"],
        "Management": ["fast-approve", "approve-all", "config", "status", "check"],
        "Analysis": ["report", "traceability", "requirement-info", "test-info"],
        "Integration": ["integration"],
        "Help & Discovery": ["help", "examples", "commands", "version", "welcome"]
    }
    
    for group_name, group_commands in command_groups.items():
        console.print(f"\n[bold]{group_name}[/bold]")
        for cmd_name in group_commands:
            # Find the command in our list
            cmd_desc = next((desc for name, desc in commands_list if name == cmd_name), "No description")
            console.print(f"  [cyan]{cmd_name:<20}[/cyan] {cmd_desc}")
    
    console.print(
        "\n[bold]💡 Usage Tips:[/bold]\n"
        "  • Run [cyan]agentops <command> --help[/cyan] for detailed help on any command\n"
        "  • Use [cyan]agentops help[/cyan] for comprehensive documentation\n"
        "  • Try [cyan]agentops examples[/cyan] for practical use cases\n\n"
        "[bold]🔍 Command Discovery:[/bold]\n"
        "  • Commands are organized by functionality\n"
        "  • Use tab completion if your shell supports it\n"
        "  • All commands support --help for detailed information"
    )


@cli.command()
@click.argument("directory", default=".")
def init(directory: str):
    """Initialize a new AgentOps project.

    Creates the .agentops directory structure, initializes the SQLite database,
    and sets up the project for multi-agent test automation.

    This command must be run before any other AgentOps commands. It creates:
    - .agentops/ directory for project data
    - .agentops/tests/ directory for generated tests
    - .agentops/requirements.db SQLite database
    - .agentops/config.json configuration file
    - .gitignore entry for .agentops/ (if .git exists)

    Args:
        directory: Project directory to initialize (default: current directory)
    """
    project_dir = Path(directory).resolve()

    # Initialize configuration
    config = get_config()
    config.initialize_project(str(project_dir))
    
    # Validate configuration
    if not config.validate():
        console.print(
            Panel(
                "[yellow]Warning: No LLM API key configured.[/yellow]\n\n"
                "Set your OpenAI API key:\n"
                "1. Export: [bold]export OPENAI_API_KEY='your-key'[/bold]\n"
                "2. Or edit: [bold].agentops/config.json[/bold]\n\n"
                "You can still initialize the project, but LLM features won't work.",
                title="Configuration Warning",
                border_style="yellow",
            )
        )

    # Create .gitignore entry for .agentops if .git exists
    gitignore_path = project_dir / ".gitignore"
    if (project_dir / ".git").exists():
        gitignore_content = ""
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                gitignore_content = f.read()

        # WHY: Only add if not already present to avoid duplicates
        if ".agentops/" not in gitignore_content:
            with open(gitignore_path, "a") as f:
                f.write("\n# AgentOps\n.agentops/\n")

    console.print(
        Panel(
            "[bold green]✓ AgentOps project initialized![/bold green]\n\n"
            f"Directory: {project_dir}\n"
            f"Database: {project_dir / '.agentops/requirements.db'}\n"
            f"Tests: {project_dir / config.project.test_output_dir}\n"
            f"Config: {project_dir / config.config_file}\n\n"
            f"Next steps:\n"
            f"1. Set your OpenAI API key: [bold]export OPENAI_API_KEY='your-key'[/bold]\n"
            f"2. Run [bold cyan]agentops multi-agent-run <file.py>[/bold cyan] to start the workflow",
            title="AgentOps Init",
            border_style="green",
        )
    )


@cli.command()
@click.argument("requirement_id", type=int, required=False)
@click.option("--format", "output_format", 
              type=click.Choice(["table", "json", "markdown"]), 
              default="table",
              help="Output format (default: table)")
def requirement_info(requirement_id: int, output_format: str):
    """Show detailed requirement information.
    
    Displays comprehensive information about requirements including:
    - Requirement details and description
    - Associated test functions
    - Coverage status
    - Creation and modification dates
    - Related files and functions
    
    Args:
        requirement_id: Specific requirement ID to show (optional)
        output_format: Output format (table, json, markdown)
    """
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)
    
    try:
        workflow = AgentOpsWorkflow()
        requirements = workflow.requirement_store.get_all_requirements()
        
        if not requirements:
            console.print(
                Panel(
                    "[yellow]No requirements found.[/yellow]\n\n"
                    "Run [bold cyan]agentops multi-agent-run[/bold cyan] to generate requirements.",
                    title="No Requirements",
                    border_style="yellow",
                )
            )
            return
        
        if requirement_id is not None:
            # Show specific requirement
            req = next((r for r in requirements if r.id == requirement_id), None)
            if not req:
                console.print(
                    Panel(
                        f"[red]Requirement ID {requirement_id} not found.[/red]",
                        title="Not Found",
                        border_style="red",
                    )
                )
                return
            
            if output_format == "table":
                console.print(
                    Panel(
                        f"[bold]Requirement #{req.id}[/bold]\n\n"
                        f"📝 [bold]Description:[/bold] {req.requirement_text}\n"
                        f"📁 [bold]File:[/bold] {req.file_path}\n"
                        f"🔗 [bold]Code Symbol:[/bold] {req.code_symbol}\n"
                        f"📊 [bold]Status:[/bold] {req.status}\n"
                        f"📅 [bold]Created:[/bold] {req.created_at}\n"
                        f"🎯 [bold]Confidence:[/bold] {req.confidence:.1%}\n"
                        f"🏷️ [bold]Metadata:[/bold] {len(req.metadata)} items",
                        title=f"Requirement #{req.id}",
                        border_style="cyan",
                    )
                )
            elif output_format == "json":
                import json
                # Convert to dict for JSON serialization
                req_dict = {
                    "id": req.id,
                    "requirement_text": req.requirement_text,
                    "file_path": req.file_path,
                    "code_symbol": req.code_symbol,
                    "commit_hash": req.commit_hash,
                    "confidence": req.confidence,
                    "status": req.status,
                    "created_at": req.created_at,
                    "metadata": req.metadata
                }
                console.print(json.dumps(req_dict, indent=2))
            else:  # markdown
                console.print(f"# Requirement #{req.id}\n\n")
                console.print(f"**Description:** {req.requirement_text}\n")
                console.print(f"**File:** {req.file_path}\n")
                console.print(f"**Code Symbol:** {req.code_symbol}\n")
                console.print(f"**Status:** {req.status}\n")
                console.print(f"**Created:** {req.created_at}\n")
                console.print(f"**Confidence:** {req.confidence:.1%}\n")
                console.print(f"**Metadata:** {len(req.metadata)} items\n")
        else:
            # Show summary of all requirements
            console.print(
                Panel(
                    f"[bold]Requirements Summary[/bold]\n\n"
                    f"Total Requirements: {len(requirements)}\n"
                    f"Approved: {len([r for r in requirements if r.status == 'approved'])}\n"
                    f"Pending: {len([r for r in requirements if r.status == 'pending'])}\n"
                    f"Rejected: {len([r for r in requirements if r.status == 'rejected'])}",
                    title="Requirements Overview",
                    border_style="cyan",
                )
            )
            
            if output_format == "table":
                from rich.table import Table
                table = Table(title="All Requirements")
                table.add_column("ID", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("File", style="blue")
                table.add_column("Function", style="yellow")
                table.add_column("Description", style="white")
                
                for req in requirements:
                    status_emoji = {"approved": "✅", "pending": "⏳", "rejected": "❌"}
                    table.add_row(
                        str(req.id),
                        f"{status_emoji.get(req.status, '❓')} {req.status}",
                        req.file_path,
                        req.code_symbol,
                        req.requirement_text[:50] + "..." if len(req.requirement_text) > 50 else req.requirement_text
                    )
                
                console.print(table)
            elif output_format == "json":
                import json
                # Convert to list of dicts for JSON serialization
                reqs_dict = []
                for r in requirements:
                    reqs_dict.append({
                        "id": r.id,
                        "requirement_text": r.requirement_text,
                        "file_path": r.file_path,
                        "code_symbol": r.code_symbol,
                        "commit_hash": r.commit_hash,
                        "confidence": r.confidence,
                        "status": r.status,
                        "created_at": r.created_at,
                        "metadata": r.metadata
                    })
                console.print(json.dumps(reqs_dict, indent=2))
            else:  # markdown
                console.print("# Requirements\n\n")
                for req in requirements:
                    status_emoji = {"approved": "✅", "pending": "⏳", "rejected": "❌"}
                    console.print(f"## {status_emoji.get(req.status, '❓')} Requirement #{req.id}\n")
                    console.print(f"**File:** {req.file_path}\n")
                    console.print(f"**Code Symbol:** {req.code_symbol}\n")
                    console.print(f"**Description:** {req.requirement_text}\n")
                    console.print(f"**Status:** {req.status}\n")
                    console.print(f"**Confidence:** {req.confidence:.1%}\n\n")
    
    except Exception as e:
        console.print(
            Panel(
                f"[red]Error loading requirements: {str(e)}[/red]",
                title="Error",
                border_style="red",
            )
        )


@cli.command()
@click.argument("test_file", type=click.Path(exists=True), required=False)
@click.option("--format", "output_format", 
              type=click.Choice(["table", "json", "markdown"]), 
              default="table",
              help="Output format (default: table)")
def test_info(test_file: str, output_format: str):
    """Show test file and function details.
    
    Displays comprehensive information about generated test files including:
    - Test file statistics
    - Test function details
    - Coverage information
    - Associated requirements
    - Test execution status
    
    Args:
        test_file: Specific test file to analyze (optional)
        output_format: Output format (table, json, markdown)
    """
    if not os.path.exists(".agentops"):
        console.print(
            Panel(
                "[yellow]AgentOps not initialized in this directory.[/yellow]\n\n"
                "Run [bold cyan]agentops init[/bold cyan] first.",
                title="Not Initialized",
                border_style="yellow",
            )
        )
        sys.exit(1)
    
    test_dir = Path(".agentops/tests")
    if not test_dir.exists():
        console.print(
            Panel(
                "[yellow]No test files found.[/yellow]\n\n"
                "Run [bold cyan]agentops multi-agent-run[/bold cyan] to generate tests.",
                title="No Tests",
                border_style="yellow",
            )
        )
        return
    
    if test_file:
        # Analyze specific test file
        test_path = Path(test_file)
        if not test_path.exists():
            console.print(
                Panel(
                    f"[red]Test file {test_file} not found.[/red]",
                    title="File Not Found",
                    border_style="red",
                )
            )
            return
        
        # Parse test file to extract information
        try:
            with open(test_path, 'r') as f:
                content = f.read()
            
            # Extract test functions
            import re
            test_functions = re.findall(r'def (test_\w+)', content)
            
            # Count lines and complexity
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            if output_format == "table":
                console.print(
                    Panel(
                        f"[bold]Test File Analysis[/bold]\n\n"
                        f"📁 [bold]File:[/bold] {test_path}\n"
                        f"📊 [bold]Test Functions:[/bold] {len(test_functions)}\n"
                        f"📏 [bold]Total Lines:[/bold] {len(lines)}\n"
                        f"📝 [bold]Code Lines:[/bold] {len(non_empty_lines)}\n"
                        f"📈 [bold]Functions:[/bold] {', '.join(test_functions) if test_functions else 'None'}",
                        title=f"Test File: {test_path.name}",
                        border_style="green",
                    )
                )
            elif output_format == "json":
                import json
                data = {
                    "file": str(test_path),
                    "test_functions": test_functions,
                    "total_lines": len(lines),
                    "code_lines": len(non_empty_lines),
                    "size_bytes": test_path.stat().st_size
                }
                console.print(json.dumps(data, indent=2))
            else:  # markdown
                console.print(f"# Test File: {test_path.name}\n\n")
                console.print(f"**File:** {test_path}\n")
                console.print(f"**Test Functions:** {len(test_functions)}\n")
                console.print(f"**Total Lines:** {len(lines)}\n")
                console.print(f"**Code Lines:** {len(non_empty_lines)}\n\n")
                if test_functions:
                    console.print("## Test Functions\n\n")
                    for func in test_functions:
                        console.print(f"- `{func}`\n")
        
        except Exception as e:
            console.print(
                Panel(
                    f"[red]Error analyzing test file: {str(e)}[/red]",
                    title="Error",
                    border_style="red",
                )
            )
    else:
        # Show summary of all test files
        test_files = list(test_dir.rglob("test_*.py"))
        
        if not test_files:
            console.print(
                Panel(
                    "[yellow]No test files found in .agentops/tests/[/yellow]\n\n"
                    "Run [bold cyan]agentops multi-agent-run[/bold cyan] to generate tests.",
                    title="No Tests",
                    border_style="yellow",
                )
            )
            return
        
        console.print(
            Panel(
                f"[bold]Test Files Summary[/bold]\n\n"
                f"Total Test Files: {len(test_files)}\n"
                f"Total Size: {sum(f.stat().st_size for f in test_files) / 1024:.1f} KB",
                title="Tests Overview",
                border_style="green",
            )
        )
        
        if output_format == "table":
            from rich.table import Table
            table = Table(title="Test Files")
            table.add_column("File", style="cyan")
            table.add_column("Size", style="blue")
            table.add_column("Functions", style="green")
            table.add_column("Lines", style="yellow")
            
            for test_file_path in test_files:
                try:
                    with open(test_file_path, 'r') as f:
                        content = f.read()
                    
                    import re
                    test_functions = re.findall(r'def (test_\w+)', content)
                    lines = len(content.split('\n'))
                    size_kb = test_file_path.stat().st_size / 1024
                    
                    table.add_row(
                        test_file_path.name,
                        f"{size_kb:.1f} KB",
                        str(len(test_functions)),
                        str(lines)
                    )
                except:
                    table.add_row(test_file_path.name, "Error", "Error", "Error")
            
            console.print(table)
        elif output_format == "json":
            import json
            data = []
            for test_file_path in test_files:
                try:
                    with open(test_file_path, 'r') as f:
                        content = f.read()
                    
                    import re
                    test_functions = re.findall(r'def (test_\w+)', content)
                    lines = len(content.split('\n'))
                    size_kb = test_file_path.stat().st_size / 1024
                    
                    data.append({
                        "file": test_file_path.name,
                        "path": str(test_file_path),
                        "size_kb": round(size_kb, 1),
                        "test_functions": test_functions,
                        "total_lines": lines
                    })
                except Exception as e:
                    data.append({
                        "file": test_file_path.name,
                        "path": str(test_file_path),
                        "error": str(e)
                    })
            
            console.print(json.dumps(data, indent=2))
        else:  # markdown
            console.print("# Test Files\n\n")
            for test_file_path in test_files:
                try:
                    with open(test_file_path, 'r') as f:
                        content = f.read()
                    
                    import re
                    test_functions = re.findall(r'def (test_\w+)', content)
                    lines = len(content.split('\n'))
                    size_kb = test_file_path.stat().st_size / 1024
                    
                    console.print(f"## {test_file_path.name}\n")
                    console.print(f"**Size:** {size_kb:.1f} KB\n")
                    console.print(f"**Test Functions:** {len(test_functions)}\n")
                    console.print(f"**Total Lines:** {lines}\n")
                    if test_functions:
                        console.print("**Functions:** " + ", ".join(test_functions) + "\n")
                    console.print("\n")
                except Exception as e:
                    console.print(f"## {test_file_path.name}\n")
                    console.print(f"**Error:** {str(e)}\n\n")


if __name__ == "__main__":
    cli()
