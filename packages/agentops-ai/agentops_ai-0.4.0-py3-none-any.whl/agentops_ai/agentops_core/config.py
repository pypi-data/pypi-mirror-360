"""Configuration module for AgentOps.

Handles all configuration including LLM providers, API keys, and project settings.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    
    provider: str = "openai"
    api_key: Optional[str] = None
    model: str = "gpt-4o-mini"
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 2000
    
    def __post_init__(self):
        """Set default values from environment variables."""
        if self.api_key is None:
            self.api_key = os.environ.get("OPENAI_API_KEY")
        if self.model == "gpt-4o-mini" and os.environ.get("AGENTOPS_MODEL"):
            self.model = os.environ.get("AGENTOPS_MODEL")


@dataclass
class ProjectConfig:
    """Configuration for project settings."""
    
    project_root: str = "."
    test_framework: str = "pytest"
    test_output_dir: str = ".agentops/tests"
    requirements_file: str = ".agentops/requirements.gherkin"
    exclude_patterns: list = field(default_factory=lambda: [
        "tests", "__pycache__", ".pytest_cache", ".agentops", "venv", "env",
        ".venv", ".env", ".git", ".idea", ".vscode", "build", "dist",
        "*.egg-info", "node_modules", "coverage", ".coverage"
    ])
    include_patterns: list = field(default_factory=list)


@dataclass
class IntegrationConfig:
    """Configuration for integrations."""
    
    ci_provider: Optional[str] = None
    ide_provider: Optional[str] = None
    webhook_enabled: bool = False
    webhook_port: int = 8080
    webhook_secret: Optional[str] = None
    auto_approve: bool = False
    notification_channels: list = field(default_factory=list)


@dataclass
class NotificationConfig:
    """Configuration for notifications and user feedback."""
    
    syntax_error_notifications: bool = True
    import_validation_warnings: bool = True
    test_generation_summary: bool = True
    console_output: bool = True
    log_file: Optional[str] = None
    notification_level: str = "info"  # debug, info, warning, error


@dataclass
class AgentOpsConfig:
    """Main configuration class for AgentOps."""
    
    llm: LLMConfig = field(default_factory=LLMConfig)
    project: ProjectConfig = field(default_factory=ProjectConfig)
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)
    notification: NotificationConfig = field(default_factory=NotificationConfig)
    config_file: str = ".agentops/config.json"
    
    def __post_init__(self):
        """Load configuration from file if it exists."""
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                self._update_from_dict(config_data)
            except Exception as e:
                print(f"Warning: Failed to load config from {config_file}: {e}")
    
    def save_config(self) -> None:
        """Save configuration to file."""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "base_url": self.llm.base_url,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
            },
            "project": {
                "test_framework": self.project.test_framework,
                "test_output_dir": self.project.test_output_dir,
                "requirements_file": self.project.requirements_file,
                "exclude_patterns": self.project.exclude_patterns,
                "include_patterns": self.project.include_patterns,
            },
            "integration": {
                "ci_provider": self.integration.ci_provider,
                "ide_provider": self.integration.ide_provider,
                "webhook_enabled": self.integration.webhook_enabled,
                "webhook_port": self.integration.webhook_port,
                "webhook_secret": self.integration.webhook_secret,
                "auto_approve": self.integration.auto_approve,
                "notification_channels": self.integration.notification_channels,
            },
            "notification": {
                "syntax_error_notifications": self.notification.syntax_error_notifications,
                "import_validation_warnings": self.notification.import_validation_warnings,
                "test_generation_summary": self.notification.test_generation_summary,
                "console_output": self.notification.console_output,
                "log_file": self.notification.log_file,
                "notification_level": self.notification.notification_level,
            }
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config to {config_file}: {e}")
    
    def _update_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if "llm" in config_data:
            llm_data = config_data["llm"]
            for key, value in llm_data.items():
                if hasattr(self.llm, key):
                    setattr(self.llm, key, value)
        
        if "project" in config_data:
            project_data = config_data["project"]
            for key, value in project_data.items():
                if hasattr(self.project, key):
                    setattr(self.project, key, value)
        
        if "integration" in config_data:
            integration_data = config_data["integration"]
            for key, value in integration_data.items():
                if hasattr(self.integration, key):
                    setattr(self.integration, key, value)
        
        if "notification" in config_data:
            notification_data = config_data["notification"]
            for key, value in notification_data.items():
                if hasattr(self.notification, key):
                    setattr(self.notification, key, value)
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.llm.api_key:
            print("Warning: No LLM API key configured")
            return False
        return True
    
    def initialize_project(self, project_root: str = ".") -> None:
        """Initialize project configuration."""
        self.project.project_root = project_root
        
        # Create necessary directories
        test_dir = Path(project_root) / self.project.test_output_dir
        test_dir.mkdir(parents=True, exist_ok=True)
        
        requirements_dir = Path(project_root) / Path(self.project.requirements_file).parent
        requirements_dir.mkdir(parents=True, exist_ok=True)
        
        config_dir = Path(project_root) / Path(self.config_file).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        self.save_config()


# Global configuration instance
_config: Optional[AgentOpsConfig] = None


def get_config() -> AgentOpsConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AgentOpsConfig()
    return _config


def set_config(config: AgentOpsConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset the global configuration instance."""
    global _config
    _config = None 