"""CI/CD integrations for AgentOps.

Provides integrations with GitHub Actions, GitLab CI, and Jenkins.
"""

import os
import json
import subprocess
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IntegrationConfig:
    """Configuration for CI integrations."""
    project_root: str
    auto_approve: bool = False
    notification_channels: List[str] = None


class BaseCIIntegration(ABC):
    """Base class for CI integrations."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize CI integration.
        
        Args:
            config: Integration configuration
        """
        self.config = config

    @abstractmethod
    def get_changed_files(self, event_data: Dict[str, Any]) -> List[str]:
        """Get list of changed files from CI event.
        
        Args:
            event_data: CI event data
            
        Returns:
            List of changed file paths
        """
        pass

    @abstractmethod
    def get_event_type(self, event_data: Dict[str, Any]) -> str:
        """Get event type from CI event data.
        
        Args:
            event_data: CI event data
            
        Returns:
            Event type string
        """
        pass

    @abstractmethod
    def get_branch_info(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """Get branch information from CI event.
        
        Args:
            event_data: CI event data
            
        Returns:
            Branch information
        """
        pass


class GitHubActionsIntegration(BaseCIIntegration):
    """GitHub Actions integration for AgentOps."""

    def get_changed_files(self, event_data: Dict[str, Any]) -> List[str]:
        """Get changed files from GitHub Actions event.
        
        Args:
            event_data: GitHub Actions event data
            
        Returns:
            List of changed file paths
        """
        changed_files = []
        
        # Try to get files from event data
        if 'files' in event_data:
            for file_info in event_data['files']:
                if file_info.get('status') in ['added', 'modified']:
                    changed_files.append(file_info['filename'])
        
        # Fallback: use git diff
        if not changed_files:
            changed_files = self._get_changed_files_from_git()
        
        return changed_files

    def _get_changed_files_from_git(self) -> List[str]:
        """Get changed files using git commands.
        
        Returns:
            List of changed file paths
        """
        try:
            # Get files changed in the last commit
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                return result.stdout.strip().split('\n')
            
            # If no changes in last commit, check unstaged changes
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                return result.stdout.strip().split('\n')
                
        except subprocess.CalledProcessError:
            pass
        
        return []

    def get_event_type(self, event_data: Dict[str, Any]) -> str:
        """Get event type from GitHub Actions event.
        
        Args:
            event_data: GitHub Actions event data
            
        Returns:
            Event type string
        """
        # GitHub Actions sets GITHUB_EVENT_NAME environment variable
        return os.environ.get('GITHUB_EVENT_NAME', 'unknown')

    def get_branch_info(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """Get branch information from GitHub Actions event.
        
        Args:
            event_data: GitHub Actions event data
            
        Returns:
            Branch information
        """
        return {
            'ref': os.environ.get('GITHUB_REF', ''),
            'head_ref': os.environ.get('GITHUB_HEAD_REF', ''),
            'base_ref': os.environ.get('GITHUB_BASE_REF', ''),
            'sha': os.environ.get('GITHUB_SHA', ''),
            'repository': os.environ.get('GITHUB_REPOSITORY', '')
        }

    def get_pull_request_info(self) -> Optional[Dict[str, Any]]:
        """Get pull request information if available.
        
        Returns:
            Pull request information or None
        """
        try:
            # Read GitHub event file
            event_file = os.environ.get('GITHUB_EVENT_PATH')
            if event_file and os.path.exists(event_file):
                with open(event_file, 'r') as f:
                    event_data = json.load(f)
                
                if 'pull_request' in event_data:
                    return event_data['pull_request']
        except Exception:
            pass
        
        return None


class GitLabCIIntegration(BaseCIIntegration):
    """GitLab CI integration for AgentOps."""

    def get_changed_files(self, event_data: Dict[str, Any]) -> List[str]:
        """Get changed files from GitLab CI event.
        
        Args:
            event_data: GitLab CI event data
            
        Returns:
            List of changed file paths
        """
        changed_files = []
        
        # Try to get files from event data
        if 'changes' in event_data:
            for change in event_data['changes']:
                if change.get('new_file', False) or change.get('modified_file', False):
                    changed_files.append(change['new_path'])
        
        # Fallback: use git diff
        if not changed_files:
            changed_files = self._get_changed_files_from_git()
        
        return changed_files

    def _get_changed_files_from_git(self) -> List[str]:
        """Get changed files using git commands.
        
        Returns:
            List of changed file paths
        """
        try:
            # Get files changed between current and previous commit
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                return result.stdout.strip().split('\n')
            
            # Check unstaged changes
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                return result.stdout.strip().split('\n')
                
        except subprocess.CalledProcessError:
            pass
        
        return []

    def get_event_type(self, event_data: Dict[str, Any]) -> str:
        """Get event type from GitLab CI event.
        
        Args:
            event_data: GitLab CI event data
            
        Returns:
            Event type string
        """
        # GitLab CI sets CI_PIPELINE_SOURCE environment variable
        return os.environ.get('CI_PIPELINE_SOURCE', 'unknown')

    def get_branch_info(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """Get branch information from GitLab CI event.
        
        Args:
            event_data: GitLab CI event data
            
        Returns:
            Branch information
        """
        return {
            'ref': os.environ.get('CI_COMMIT_REF_NAME', ''),
            'sha': os.environ.get('CI_COMMIT_SHA', ''),
            'repository': os.environ.get('CI_PROJECT_PATH', ''),
            'project_id': os.environ.get('CI_PROJECT_ID', ''),
            'pipeline_id': os.environ.get('CI_PIPELINE_ID', '')
        }

    def get_merge_request_info(self) -> Optional[Dict[str, Any]]:
        """Get merge request information if available.
        
        Returns:
            Merge request information or None
        """
        mr_iid = os.environ.get('CI_MERGE_REQUEST_IID')
        if mr_iid:
            return {
                'iid': mr_iid,
                'title': os.environ.get('CI_MERGE_REQUEST_TITLE', ''),
                'source_branch': os.environ.get('CI_MERGE_REQUEST_SOURCE_BRANCH_NAME', ''),
                'target_branch': os.environ.get('CI_MERGE_REQUEST_TARGET_BRANCH_NAME', '')
            }
        return None


class JenkinsIntegration(BaseCIIntegration):
    """Jenkins integration for AgentOps."""

    def get_changed_files(self, event_data: Dict[str, Any]) -> List[str]:
        """Get changed files from Jenkins event.
        
        Args:
            event_data: Jenkins event data
            
        Returns:
            List of changed file paths
        """
        changed_files = []
        
        # Try to get files from event data
        if 'changes' in event_data:
            for change in event_data['changes']:
                changed_files.extend(change.get('affectedPaths', []))
        
        # Fallback: use git diff
        if not changed_files:
            changed_files = self._get_changed_files_from_git()
        
        return changed_files

    def _get_changed_files_from_git(self) -> List[str]:
        """Get changed files using git commands.
        
        Returns:
            List of changed file paths
        """
        try:
            # Get files changed in the last commit
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                return result.stdout.strip().split('\n')
            
            # Check unstaged changes
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                return result.stdout.strip().split('\n')
                
        except subprocess.CalledProcessError:
            pass
        
        return []

    def get_event_type(self, event_data: Dict[str, Any]) -> str:
        """Get event type from Jenkins event.
        
        Args:
            event_data: Jenkins event data
            
        Returns:
            Event type string
        """
        return event_data.get('event_type', 'build')

    def get_branch_info(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """Get branch information from Jenkins event.
        
        Args:
            event_data: Jenkins event data
            
        Returns:
            Branch information
        """
        return {
            'ref': os.environ.get('GIT_BRANCH', ''),
            'sha': os.environ.get('GIT_COMMIT', ''),
            'repository': os.environ.get('GIT_URL', ''),
            'build_number': os.environ.get('BUILD_NUMBER', ''),
            'job_name': os.environ.get('JOB_NAME', '')
        }

    def get_build_info(self) -> Dict[str, Any]:
        """Get Jenkins build information.
        
        Returns:
            Build information
        """
        return {
            'build_number': os.environ.get('BUILD_NUMBER', ''),
            'job_name': os.environ.get('JOB_NAME', ''),
            'build_url': os.environ.get('BUILD_URL', ''),
            'workspace': os.environ.get('WORKSPACE', ''),
            'executor_number': os.environ.get('EXECUTOR_NUMBER', '')
        } 