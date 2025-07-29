"""Notification system for AgentOps.

Provides a generic notification system for informing users about syntax errors,
import issues, and other problems without being tied to specific project logic.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .config import get_config


class NotificationManager:
    """Manages notifications and user feedback for AgentOps."""
    
    def __init__(self):
        """Initialize the notification manager."""
        self.config = get_config()
        self.console = Console()
        self.notifications: List[Dict[str, Any]] = []
    
    def notify_syntax_error(self, file_path: str, error: str, line_number: Optional[int] = None) -> None:
        """Notify about a syntax error in generated code.
        
        Args:
            file_path: Path to the file with the error
            error: Error message
            line_number: Line number where the error occurred
        """
        if not self.config.notification.syntax_error_notifications:
            return
        
        notification = {
            "type": "syntax_error",
            "file_path": file_path,
            "error": error,
            "line_number": line_number,
            "timestamp": datetime.now().isoformat(),
            "message": f"Syntax error in {file_path}: {error}"
        }
        
        self.notifications.append(notification)
        
        if self.config.notification.console_output:
            self._print_syntax_error_notification(notification)
        
        if self.config.notification.log_file:
            self._log_notification(notification)
    
    def notify_import_validation_issue(self, file_path: str, issues: List[str]) -> None:
        """Notify about import validation issues.
        
        Args:
            file_path: Path to the file with import issues
            issues: List of import validation issues
        """
        if not self.config.notification.import_validation_warnings:
            return
        
        notification = {
            "type": "import_validation",
            "file_path": file_path,
            "issues": issues,
            "timestamp": datetime.now().isoformat(),
            "message": f"Import validation issues in {file_path}: {', '.join(issues)}"
        }
        
        self.notifications.append(notification)
        
        if self.config.notification.console_output:
            self._print_import_validation_notification(notification)
        
        if self.config.notification.log_file:
            self._log_notification(notification)
    
    def notify_test_generation_summary(self, file_path: str, success: bool, 
                                     test_count: int = 0, errors: List[str] = None) -> None:
        """Notify about test generation summary.
        
        Args:
            file_path: Path to the source file
            success: Whether test generation was successful
            test_count: Number of tests generated
            errors: List of errors encountered
        """
        if not self.config.notification.test_generation_summary:
            return
        
        notification = {
            "type": "test_generation_summary",
            "file_path": file_path,
            "success": success,
            "test_count": test_count,
            "errors": errors or [],
            "timestamp": datetime.now().isoformat(),
            "message": f"Test generation for {file_path}: {'Success' if success else 'Failed'}"
        }
        
        self.notifications.append(notification)
        
        if self.config.notification.console_output:
            self._print_test_generation_summary(notification)
        
        if self.config.notification.log_file:
            self._log_notification(notification)
    
    def _print_syntax_error_notification(self, notification: Dict[str, Any]) -> None:
        """Print syntax error notification to console."""
        message = Text()
        message.append("⚠️  ", style="yellow")
        message.append("Syntax Error Detected\n", style="bold yellow")
        message.append(f"File: {notification['file_path']}\n", style="cyan")
        message.append(f"Error: {notification['error']}\n", style="red")
        
        if notification.get('line_number'):
            message.append(f"Line: {notification['line_number']}\n", style="cyan")
        
        message.append("\nThe generated test code contains syntax errors that need to be fixed manually.\n", style="dim")
        message.append("TODO comments have been added to the test file to help identify the issues.", style="green")
        
        self.console.print(Panel(message, title="Syntax Error", border_style="yellow"))
    
    def _print_import_validation_notification(self, notification: Dict[str, Any]) -> None:
        """Print import validation notification to console."""
        message = Text()
        message.append("🔍 ", style="blue")
        message.append("Import Validation Issues\n", style="bold blue")
        message.append(f"File: {notification['file_path']}\n", style="cyan")
        
        for issue in notification['issues']:
            message.append(f"• {issue}\n", style="yellow")
        
        message.append("\nThese issues may affect test execution but are not critical.", style="dim")
        
        self.console.print(Panel(message, title="Import Validation", border_style="blue"))
    
    def _print_test_generation_summary(self, notification: Dict[str, Any]) -> None:
        """Print test generation summary to console."""
        if notification['success']:
            message = Text()
            message.append("✅ ", style="green")
            message.append("Test Generation Complete\n", style="bold green")
            message.append(f"File: {notification['file_path']}\n", style="cyan")
            message.append(f"Tests Generated: {notification['test_count']}\n", style="green")
            
            self.console.print(Panel(message, title="Success", border_style="green"))
        else:
            message = Text()
            message.append("❌ ", style="red")
            message.append("Test Generation Failed\n", style="bold red")
            message.append(f"File: {notification['file_path']}\n", style="cyan")
            
            for error in notification['errors']:
                message.append(f"• {error}\n", style="red")
            
            self.console.print(Panel(message, title="Failure", border_style="red"))
    
    def _log_notification(self, notification: Dict[str, Any]) -> None:
        """Log notification to file."""
        if not self.config.notification.log_file:
            return
        
        log_path = Path(self.config.notification.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps(notification) + '\n')
        except Exception as e:
            # Fallback to console if logging fails
            self.console.print(f"Warning: Failed to log notification: {e}", style="yellow")
    
    def get_notifications(self, notification_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all notifications or filter by type.
        
        Args:
            notification_type: Optional type filter
            
        Returns:
            List of notifications
        """
        if notification_type:
            return [n for n in self.notifications if n['type'] == notification_type]
        return self.notifications.copy()
    
    def clear_notifications(self) -> None:
        """Clear all notifications."""
        self.notifications.clear()


# Global notification manager instance
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


def notify_syntax_error(file_path: str, error: str, line_number: Optional[int] = None) -> None:
    """Convenience function to notify about syntax errors."""
    get_notification_manager().notify_syntax_error(file_path, error, line_number)


def notify_import_validation_issue(file_path: str, issues: List[str]) -> None:
    """Convenience function to notify about import validation issues."""
    get_notification_manager().notify_import_validation_issue(file_path, issues)


def notify_test_generation_summary(file_path: str, success: bool, 
                                 test_count: int = 0, errors: List[str] = None) -> None:
    """Convenience function to notify about test generation summary."""
    get_notification_manager().notify_test_generation_summary(file_path, success, test_count, errors) 