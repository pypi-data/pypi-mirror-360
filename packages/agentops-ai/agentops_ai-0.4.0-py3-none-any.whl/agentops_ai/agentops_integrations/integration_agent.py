"""Integration Agent for AgentOps.

Orchestrates integrations with CI/CD systems, IDEs, and external tools.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from ..agentops_core.workflow import AgentOpsWorkflow
from ..agentops_core.requirement_store import RequirementStore
from .ci_integrations import GitHubActionsIntegration, GitLabCIIntegration, JenkinsIntegration
from .ide_integrations import VSCodeIntegration, PyCharmIntegration
from .webhook_handler import WebhookHandler


@dataclass
class IntegrationConfig:
    """Configuration for integration agent."""
    project_root: str
    ci_provider: Optional[str] = None
    ide_provider: Optional[str] = None
    webhook_enabled: bool = False
    webhook_port: int = 8080
    auto_approve: bool = False
    notification_channels: List[str] = None


class IntegrationAgent:
    """Main integration agent for AgentOps.
    
    Handles CI/CD integration, IDE plugins, webhooks, and external tool connections.
    """

    def __init__(self, config: IntegrationConfig):
        """Initialize the integration agent.
        
        Args:
            config: Integration configuration
        """
        self.config = config
        self.workflow = AgentOpsWorkflow()
        self.requirement_store = RequirementStore()
        
        # Initialize integrations
        self.ci_integrations = {}
        self.ide_integrations = {}
        self.webhook_handler = None
        
        self._setup_integrations()
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging for integration agent."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('.agentops/integration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('agentops.integration')

    def _setup_integrations(self):
        """Set up available integrations based on configuration."""
        # CI/CD Integrations
        if self.config.ci_provider == 'github':
            self.ci_integrations['github'] = GitHubActionsIntegration(self.config)
        elif self.config.ci_provider == 'gitlab':
            self.ci_integrations['gitlab'] = GitLabCIIntegration(self.config)
        elif self.config.ci_provider == 'jenkins':
            self.ci_integrations['jenkins'] = JenkinsIntegration(self.config)
        
        # IDE Integrations
        if self.config.ide_provider == 'vscode':
            self.ide_integrations['vscode'] = VSCodeIntegration(self.config)
        elif self.config.ide_provider == 'pycharm':
            self.ide_integrations['pycharm'] = PyCharmIntegration(self.config)
        
        # Webhook Handler
        if self.config.webhook_enabled:
            self.webhook_handler = WebhookHandler(self.config, self)

    def process_ci_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process CI/CD event (push, pull request, etc.).
        
        Args:
            event_data: Event data from CI system
            
        Returns:
            Processing result
        """
        try:
            self.logger.info(f"Processing CI event: {event_data.get('event_type', 'unknown')}")
            
            # Determine changed files
            changed_files = self._get_changed_files(event_data)
            if not changed_files:
                return {"success": True, "message": "No Python files changed"}
            
            # Process each changed file
            results = []
            for file_path in changed_files:
                if file_path.endswith('.py'):
                    result = self._process_file_change(file_path, event_data)
                    results.append(result)
            
            # Generate summary
            summary = self._generate_ci_summary(results, event_data)
            
            # Send notifications
            self._send_notifications(summary, event_data)
            
            return {
                "success": True,
                "processed_files": len(results),
                "summary": summary,
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"Error processing CI event: {str(e)}")
            return {"success": False, "error": str(e)}

    def _get_changed_files(self, event_data: Dict[str, Any]) -> List[str]:
        """Extract changed files from CI event data.
        
        Args:
            event_data: CI event data
            
        Returns:
            List of changed file paths
        """
        changed_files = []
        
        # GitHub Actions
        if 'github' in self.ci_integrations:
            changed_files = self.ci_integrations['github'].get_changed_files(event_data)
        
        # GitLab CI
        elif 'gitlab' in self.ci_integrations:
            changed_files = self.ci_integrations['gitlab'].get_changed_files(event_data)
        
        # Jenkins
        elif 'jenkins' in self.ci_integrations:
            changed_files = self.ci_integrations['jenkins'].get_changed_files(event_data)
        
        return changed_files

    def _process_file_change(self, file_path: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single file change.
        
        Args:
            file_path: Path to changed file
            event_data: CI event context
            
        Returns:
            Processing result
        """
        try:
            # Use non-interactive mode for CI
            result = self.workflow.process_file_change(
                file_path, 
                interactive=False
            )
            
            if result["success"]:
                # Auto-approve if configured
                if self.config.auto_approve:
                    self._auto_approve_requirement(result["requirement_id"])
                
                return {
                    "file": file_path,
                    "success": True,
                    "requirement_id": result.get("requirement_id"),
                    "test_file": result.get("test_file"),
                    "confidence": result.get("confidence")
                }
            else:
                return {
                    "file": file_path,
                    "success": False,
                    "error": result.get("error")
                }
                
        except Exception as e:
            return {
                "file": file_path,
                "success": False,
                "error": str(e)
            }

    def _auto_approve_requirement(self, requirement_id: str):
        """Auto-approve a requirement if configured.
        
        Args:
            requirement_id: ID of requirement to approve
        """
        try:
            self.requirement_store.approve_requirement(requirement_id)
            self.logger.info(f"Auto-approved requirement {requirement_id}")
        except Exception as e:
            self.logger.error(f"Failed to auto-approve requirement {requirement_id}: {str(e)}")

    def _generate_ci_summary(self, results: List[Dict[str, Any]], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for CI event.
        
        Args:
            results: Processing results
            event_data: CI event data
            
        Returns:
            Summary data
        """
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_data.get("event_type", "unknown"),
            "total_files": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "failed_files": [r["file"] for r in failed],
            "requirements_generated": len(successful),
            "tests_generated": len([r for r in successful if r.get("test_file")])
        }

    def _send_notifications(self, summary: Dict[str, Any], event_data: Dict[str, Any]):
        """Send notifications about processing results.
        
        Args:
            summary: Processing summary
            event_data: CI event data
        """
        if not self.config.notification_channels:
            return
            
        notification_data = {
            "summary": summary,
            "event": event_data,
            "project": self.config.project_root
        }
        
        for channel in self.config.notification_channels:
            try:
                if channel == "slack":
                    self._send_slack_notification(notification_data)
                elif channel == "email":
                    self._send_email_notification(notification_data)
                elif channel == "webhook":
                    self._send_webhook_notification(notification_data)
            except Exception as e:
                self.logger.error(f"Failed to send {channel} notification: {str(e)}")

    def _send_slack_notification(self, data: Dict[str, Any]):
        """Send Slack notification."""
        # TODO: Implement Slack integration
        self.logger.info("Slack notification would be sent here")

    def _send_email_notification(self, data: Dict[str, Any]):
        """Send email notification."""
        # TODO: Implement email integration
        self.logger.info("Email notification would be sent here")

    def _send_webhook_notification(self, data: Dict[str, Any]):
        """Send webhook notification."""
        # TODO: Implement webhook integration
        self.logger.info("Webhook notification would be sent here")

    def start_webhook_server(self):
        """Start webhook server for real-time integration."""
        if self.webhook_handler:
            self.webhook_handler.start_server()
        else:
            raise ValueError("Webhook handler not configured")

    def stop_webhook_server(self):
        """Stop webhook server."""
        if self.webhook_handler:
            self.webhook_handler.stop_server()

    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations.
        
        Returns:
            Integration status information
        """
        return {
            "ci_integrations": list(self.ci_integrations.keys()),
            "ide_integrations": list(self.ide_integrations.keys()),
            "webhook_enabled": self.config.webhook_enabled,
            "auto_approve": self.config.auto_approve,
            "notification_channels": self.config.notification_channels or []
        }

    def generate_ci_config(self, ci_provider: str) -> str:
        """Generate CI configuration for specified provider.
        
        Args:
            ci_provider: CI provider (github, gitlab, jenkins)
            
        Returns:
            CI configuration content
        """
        if ci_provider == 'github':
            return self._generate_github_actions_config()
        elif ci_provider == 'gitlab':
            return self._generate_gitlab_ci_config()
        elif ci_provider == 'jenkins':
            return self._generate_jenkins_config()
        else:
            raise ValueError(f"Unsupported CI provider: {ci_provider}")

    def _generate_github_actions_config(self) -> str:
        """Generate GitHub Actions configuration."""
        return """name: AgentOps CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  agentops:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install AgentOps
        run: |
          pip install agentops-ai
          
      - name: Set up OpenAI API key
        run: |
          echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> $GITHUB_ENV
          
      - name: Initialize AgentOps
        run: |
          agentops init
          
      - name: Process changes with AgentOps
        run: |
          agentops infer --all
          agentops approve --all
          agentops generate-tests
          agentops run --all
          
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: agentops-results
          path: .agentops/
"""

    def _generate_gitlab_ci_config(self) -> str:
        """Generate GitLab CI configuration."""
        return """.agentops:
  image: python:3.11
  before_script:
    - pip install agentops-ai
    - export OPENAI_API_KEY=$OPENAI_API_KEY
    - agentops init
  script:
    - agentops infer --all
    - agentops approve --all
    - agentops generate-tests
    - agentops run --all
  artifacts:
    paths:
      - .agentops/
    expire_in: 1 week
"""

    def _generate_jenkins_config(self) -> str:
        """Generate Jenkins configuration."""
        return """pipeline {
    agent any
    
    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install agentops-ai'
                sh 'agentops init'
            }
        }
        
        stage('Process Changes') {
            steps {
                sh 'agentops infer --all'
                sh 'agentops approve --all'
                sh 'agentops generate-tests'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'agentops run --all'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: '.agentops/**/*', fingerprint: true
        }
    }
}
""" 