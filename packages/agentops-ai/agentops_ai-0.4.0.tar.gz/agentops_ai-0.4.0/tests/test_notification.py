"""Tests for the notification system."""

import pytest
from unittest.mock import patch, MagicMock
from agentops_ai.agentops_core.notification import (
    NotificationManager, 
    notify_syntax_error, 
    notify_import_validation_issue,
    notify_test_generation_summary
)


class TestNotificationManager:
    """Test the NotificationManager class."""
    
    def test_notify_syntax_error(self):
        """Test syntax error notification."""
        with patch('agentops_ai.agentops_core.notification.Console') as mock_console:
            manager = NotificationManager()
            manager.config.notification.syntax_error_notifications = True
            manager.config.notification.console_output = True
            
            manager.notify_syntax_error("test.py", "invalid syntax", 10)
            
            assert len(manager.notifications) == 1
            notification = manager.notifications[0]
            assert notification["type"] == "syntax_error"
            assert notification["file_path"] == "test.py"
            assert notification["error"] == "invalid syntax"
            assert notification["line_number"] == 10
            
            # Verify console output was called
            mock_console.return_value.print.assert_called_once()
    
    def test_notify_import_validation_issue(self):
        """Test import validation notification."""
        with patch('agentops_ai.agentops_core.notification.Console') as mock_console:
            manager = NotificationManager()
            manager.config.notification.import_validation_warnings = True
            manager.config.notification.console_output = True
            
            issues = ["Missing import: module1", "Invalid import: module2"]
            manager.notify_import_validation_issue("test.py", issues)
            
            assert len(manager.notifications) == 1
            notification = manager.notifications[0]
            assert notification["type"] == "import_validation"
            assert notification["file_path"] == "test.py"
            assert notification["issues"] == issues
            
            # Verify console output was called
            mock_console.return_value.print.assert_called_once()
    
    def test_notify_test_generation_summary_success(self):
        """Test test generation summary notification for success."""
        with patch('agentops_ai.agentops_core.notification.Console') as mock_console:
            manager = NotificationManager()
            manager.config.notification.test_generation_summary = True
            manager.config.notification.console_output = True
            
            manager.notify_test_generation_summary("test.py", True, 5)
            
            assert len(manager.notifications) == 1
            notification = manager.notifications[0]
            assert notification["type"] == "test_generation_summary"
            assert notification["file_path"] == "test.py"
            assert notification["success"] is True
            assert notification["test_count"] == 5
            
            # Verify console output was called
            mock_console.return_value.print.assert_called_once()
    
    def test_notify_test_generation_summary_failure(self):
        """Test test generation summary notification for failure."""
        with patch('agentops_ai.agentops_core.notification.Console') as mock_console:
            manager = NotificationManager()
            manager.config.notification.test_generation_summary = True
            manager.config.notification.console_output = True
            
            errors = ["API key not found", "Network error"]
            manager.notify_test_generation_summary("test.py", False, 0, errors)
            
            assert len(manager.notifications) == 1
            notification = manager.notifications[0]
            assert notification["type"] == "test_generation_summary"
            assert notification["file_path"] == "test.py"
            assert notification["success"] is False
            assert notification["test_count"] == 0
            assert notification["errors"] == errors
            
            # Verify console output was called
            mock_console.return_value.print.assert_called_once()
    
    def test_notification_disabled(self):
        """Test that notifications are not sent when disabled."""
        manager = NotificationManager()
        manager.config.notification.syntax_error_notifications = False
        manager.config.notification.console_output = True
        
        manager.notify_syntax_error("test.py", "invalid syntax")
        
        assert len(manager.notifications) == 0
    
    def test_get_notifications_filtered(self):
        """Test getting notifications filtered by type."""
        manager = NotificationManager()
        manager.config.notification.syntax_error_notifications = True
        manager.config.notification.import_validation_warnings = True
        
        manager.notify_syntax_error("test1.py", "error1")
        manager.notify_import_validation_issue("test2.py", ["issue1"])
        manager.notify_syntax_error("test3.py", "error2")
        
        syntax_errors = manager.get_notifications("syntax_error")
        assert len(syntax_errors) == 2
        
        import_issues = manager.get_notifications("import_validation")
        assert len(import_issues) == 1
        
        all_notifications = manager.get_notifications()
        assert len(all_notifications) == 3
    
    def test_clear_notifications(self):
        """Test clearing notifications."""
        manager = NotificationManager()
        manager.config.notification.syntax_error_notifications = True
        
        manager.notify_syntax_error("test.py", "error")
        assert len(manager.notifications) == 1
        
        manager.clear_notifications()
        assert len(manager.notifications) == 0


class TestConvenienceFunctions:
    """Test the convenience functions."""
    
    @patch('agentops_ai.agentops_core.notification.get_notification_manager')
    def test_notify_syntax_error_function(self, mock_get_manager):
        """Test the notify_syntax_error convenience function."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        
        notify_syntax_error("test.py", "error", 5)
        
        mock_manager.notify_syntax_error.assert_called_once_with("test.py", "error", 5)
    
    @patch('agentops_ai.agentops_core.notification.get_notification_manager')
    def test_notify_import_validation_issue_function(self, mock_get_manager):
        """Test the notify_import_validation_issue convenience function."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        
        issues = ["issue1", "issue2"]
        notify_import_validation_issue("test.py", issues)
        
        mock_manager.notify_import_validation_issue.assert_called_once_with("test.py", issues)
    
    @patch('agentops_ai.agentops_core.notification.get_notification_manager')
    def test_notify_test_generation_summary_function(self, mock_get_manager):
        """Test the notify_test_generation_summary convenience function."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        
        errors = ["error1"]
        notify_test_generation_summary("test.py", False, 0, errors)
        
        mock_manager.notify_test_generation_summary.assert_called_once_with("test.py", False, 0, errors) 