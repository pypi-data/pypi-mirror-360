"""Terminal UI module for AgentOps.

Provides interactive terminal user interface for human-in-the-loop approval and RCA.
"""

from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.layout import Layout
from rich.columns import Columns
from rich.box import ROUNDED

from .requirement_store import Requirement


class TerminalUI:
    """Terminal-based UI for requirement approval workflow."""

    def __init__(self):
        """Initialize the terminal UI."""
        self.console = Console()

    def show_requirement_approval(
        self,
        requirement_text: str,
        file_path: str,
        confidence: float,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Show requirement approval dialog.

        Args:
            requirement_text: The inferred requirement text
            file_path: Path to the file
            confidence: Confidence score (0.0 to 1.0)
            metadata: Additional metadata

        Returns:
            User choice: 'approve', 'edit', 'reject'
        """
        # Clear screen for focused interaction
        self.console.clear()

        # Create main panel with requirement
        requirement_panel = self._create_requirement_panel(
            requirement_text, file_path, confidence, metadata
        )

        self.console.print(requirement_panel)
        self.console.print()

        # Show action options
        actions_table = Table(show_header=False, box=None, padding=(0, 2))
        actions_table.add_column("Key", style="bold cyan")
        actions_table.add_column("Action", style="white")

        actions_table.add_row("[A]", "Approve requirement")
        actions_table.add_row("[E]", "Edit requirement text")
        actions_table.add_row("[R]", "Reject requirement")
        actions_table.add_row("[Q]", "Quit without saving")

        self.console.print(Panel(actions_table, title="Actions", border_style="blue"))
        self.console.print()

        # Get user input
        while True:
            choice = Prompt.ask(
                "[bold]Choose action[/bold]",
                choices=["a", "e", "r", "q", "A", "E", "R", "Q"],
                default="a",
                show_default=True,
            ).lower()

            if choice == "a":
                return "approve"
            elif choice == "e":
                return "edit"
            elif choice == "r":
                return "reject"
            elif choice == "q":
                return "quit"

    def edit_requirement_text(self, original_text: str) -> Optional[str]:
        """Allow user to edit requirement text.

        Args:
            original_text: Original requirement text

        Returns:
            Edited text or None if cancelled
        """
        self.console.print(
            Panel(
                f"[bold]Original requirement:[/bold]\n{original_text}",
                title="Edit Requirement",
                border_style="yellow",
            )
        )
        self.console.print()

        # Get edited text
        new_text = Prompt.ask(
            "[bold]Enter new requirement text[/bold]", default=original_text
        )

        if new_text.strip() == original_text.strip():
            self.console.print("[yellow]No changes made[/yellow]")
            return None

        # Confirm the edit
        self.console.print(
            Panel(
                f"[bold]New requirement:[/bold]\n{new_text}",
                title="Confirm Edit",
                border_style="green",
            )
        )

        if Confirm.ask("[bold]Confirm this edit?[/bold]", default=True):
            return new_text.strip()

        return None

    def show_approval_confirmation(self, requirement_text: str) -> bool:
        """Show final approval confirmation.

        Args:
            requirement_text: The requirement text to approve

        Returns:
            True if confirmed, False otherwise
        """
        self.console.print(
            Panel(
                f"[bold green]✓ Approving requirement:[/bold green]\n{requirement_text}",
                title="Confirmation",
                border_style="green",
            )
        )

        return Confirm.ask("[bold]Confirm approval?[/bold]", default=True)

    def show_rejection_confirmation(self, requirement_text: str) -> bool:
        """Show rejection confirmation.

        Args:
            requirement_text: The requirement text to reject

        Returns:
            True if confirmed, False otherwise
        """
        self.console.print(
            Panel(
                f"[bold red]✗ Rejecting requirement:[/bold red]\n{requirement_text}",
                title="Confirmation",
                border_style="red",
            )
        )

        return Confirm.ask("[bold]Confirm rejection?[/bold]", default=False)

    def show_success_message(self, action: str, requirement_text: str):
        """Show success message after action.

        Args:
            action: Action taken ('approved', 'rejected', 'edited')
            requirement_text: The requirement text
        """
        if action == "approved":
            self.console.print(
                Panel(
                    "[bold green]✓ Requirement approved successfully![/bold green]\n\n"
                    "Next: AgentOps will generate tests based on this requirement.\n"
                    "Run [bold cyan]agentops run[/bold cyan] to execute tests.",
                    title="Success",
                    border_style="green",
                )
            )
        elif action == "rejected":
            self.console.print(
                Panel(
                    "[bold red]✗ Requirement rejected[/bold red]\n\n"
                    "No tests will be generated for this change.",
                    title="Rejected",
                    border_style="red",
                )
            )
        elif action == "edited":
            self.console.print(
                Panel(
                    "[bold yellow]✓ Requirement edited and approved[/bold yellow]\n\n"
                    "Tests will be generated based on the edited requirement.",
                    title="Edited & Approved",
                    border_style="yellow",
                )
            )

    def show_error_message(self, error: str):
        """Show error message.

        Args:
            error: Error message to display
        """
        self.console.print(
            Panel(
                f"[bold red]Error:[/bold red] {error}",
                title="Error",
                border_style="red",
            )
        )

    def show_pending_requirements(self, requirements):
        """Show list of pending requirements.

        Args:
            requirements: List of pending requirements
        """
        if not requirements:
            self.console.print(
                Panel(
                    "[bold green]No pending requirements[/bold green]\n\n"
                    "All requirements have been processed.",
                    title="Pending Requirements",
                    border_style="green",
                )
            )
            return

        self.console.print(
            f"\n[bold]Found {len(requirements)} pending requirements:[/bold]\n"
        )

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("File", style="blue", width=30)
        table.add_column("Requirement", style="white", width=50)
        table.add_column("Confidence", style="green", width=10)
        table.add_column("Created", style="yellow", width=20)

        for req in requirements:
            # Truncate long requirement text
            req_text = req.requirement_text
            if len(req_text) > 47:
                req_text = req_text[:44] + "..."

            # Format confidence as percentage
            confidence = f"{req.confidence:.1%}"

            # Format creation date
            created = req.created_at.split("T")[0]  # Just date part

            table.add_row(str(req.id), req.file_path, req_text, confidence, created)

        self.console.print(table)

    def show_requirement_stats(self, stats: Dict[str, Any]):
        """Show requirement statistics.

        Args:
            stats: Statistics dictionary from RequirementStore
        """
        stats_table = Table(show_header=False, box=ROUNDED)
        stats_table.add_column("Metric", style="bold cyan")
        stats_table.add_column("Value", style="white")

        stats_table.add_row("Total Requirements", str(stats["total"]))
        stats_table.add_row("Approved", f"[green]{stats['approved']}[/green]")
        stats_table.add_row("Pending", f"[yellow]{stats['pending']}[/yellow]")
        stats_table.add_row("Rejected", f"[red]{stats['rejected']}[/red]")
        stats_table.add_row("Avg Confidence", f"{stats['avg_confidence']:.1%}")

        self.console.print(
            Panel(stats_table, title="Requirement Statistics", border_style="blue")
        )

    def show_root_cause_analysis(self, requirement: Requirement, test_failure: str):
        """Show root cause analysis for test failure.

        Args:
            requirement: The validated requirement
            test_failure: Test failure log
        """
        # Create layout for side-by-side comparison
        Layout()

        # Left side: Requirement
        requirement_panel = Panel(
            f"[bold]Requirement:[/bold]\n{requirement.requirement_text}\n\n"
            f"[bold]File:[/bold] {requirement.file_path}\n"
            f"[bold]Confidence:[/bold] {requirement.confidence:.1%}\n"
            f"[bold]Status:[/bold] [green]{requirement.status}[/green]",
            title="Validated Requirement",
            border_style="green",
        )

        # Right side: Test failure
        failure_panel = Panel(
            f"[bold red]Test Failure:[/bold red]\n{test_failure}",
            title="Test Failure Log",
            border_style="red",
        )

        # Show both panels
        columns = Columns([requirement_panel, failure_panel], equal=True)
        self.console.print(columns)

        # Analysis
        analysis_panel = Panel(
            "[bold yellow]Root Cause Analysis:[/bold yellow]\n\n"
            "Compare the validated requirement (left) with the test failure (right).\n\n"
            "• If the test failure contradicts the requirement → [bold red]Code Bug[/bold red]\n"
            "• If the test failure aligns with the requirement → [bold blue]Test Issue[/bold blue]\n"
            "• If unclear → Run [bold cyan]agentops regenerate[/bold cyan] to update tests",
            title="Diagnosis",
            border_style="yellow",
        )

        self.console.print(analysis_panel)

    def _create_requirement_panel(
        self,
        requirement_text: str,
        file_path: str,
        confidence: float,
        metadata: Dict[str, Any] = None,
    ) -> Panel:
        """Create a formatted panel for requirement display.

        Args:
            requirement_text: The requirement text
            file_path: Path to the file
            confidence: Confidence score
            metadata: Additional metadata

        Returns:
            Rich Panel with formatted requirement
        """
        # Confidence color based on score
        if confidence >= 0.8:
            confidence_color = "green"
        elif confidence >= 0.6:
            confidence_color = "yellow"
        else:
            confidence_color = "red"

        # Format metadata
        meta_text = ""
        if metadata:
            if "diff_lines" in metadata:
                meta_text += f"Diff lines: {metadata['diff_lines']}\n"
            if "requirement_length" in metadata:
                meta_text += f"Requirement length: {metadata['requirement_length']}\n"

        content = (
            f"[bold]Inferred Requirement:[/bold]\n"
            f"{requirement_text}\n\n"
            f"[bold]File:[/bold] {file_path}\n"
            f"[bold]Confidence:[/bold] [{confidence_color}]{confidence:.1%}[/{confidence_color}]\n"
        )

        if meta_text:
            content += f"\n[bold]Details:[/bold]\n{meta_text}"

        return Panel(
            content,
            title="AgentOps - Requirement Approval",
            border_style="cyan",
            padding=(1, 2),
        )

    def show_clarification_approval(
        self, original: str, clarified: str, file_path: str
    ) -> bool:
        """Show clarification for user approval.

        Args:
            original: Original requirement text
            clarified: LLM-clarified requirement text
            file_path: File path for context

        Returns:
            True if user approves clarification, False otherwise
        """
        self.console.print(
            Panel(
                f"[bold]LLM Clarification Suggestion[/bold]\n\n"
                f"File: {file_path}\n\n"
                f"[yellow]Original:[/yellow]\n{original}\n\n"
                f"[green]Clarified:[/green]\n{clarified}",
                title="Requirement Clarification",
                border_style="blue",
            )
        )

        self.console.print(
            Panel(
                "  [A]    Accept clarification\n" "  [R]    Reject (keep original)\n",
                title="Actions",
                border_style="cyan",
            )
        )

        while True:
            choice = Prompt.ask(
                "[bold cyan]Your choice[/bold cyan]",
                choices=["A", "a", "R", "r"],
                default="A",
            ).upper()

            if choice == "A":
                return True
            elif choice == "R":
                return False
