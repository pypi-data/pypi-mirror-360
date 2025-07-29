"""IDE integrations for AgentOps.

Provides integrations with VSCode and PyCharm.
"""

import os
import json
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IntegrationConfig:
    """Configuration for IDE integrations."""
    project_root: str
    auto_approve: bool = False
    notification_channels: List[str] = None


class BaseIDEIntegration(ABC):
    """Base class for IDE integrations."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize IDE integration.
        
        Args:
            config: Integration configuration
        """
        self.config = config

    @abstractmethod
    def get_workspace_info(self) -> Dict[str, Any]:
        """Get workspace information.
        
        Returns:
            Workspace information
        """
        pass

    @abstractmethod
    def get_open_files(self) -> List[str]:
        """Get list of currently open files.
        
        Returns:
            List of open file paths
        """
        pass

    @abstractmethod
    def get_file_content(self, file_path: str) -> Optional[str]:
        """Get content of a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content or None
        """
        pass


class VSCodeIntegration(BaseIDEIntegration):
    """VSCode integration for AgentOps."""

    def get_workspace_info(self) -> Dict[str, Any]:
        """Get VSCode workspace information.
        
        Returns:
            Workspace information
        """
        workspace_info = {
            'ide': 'vscode',
            'project_root': self.config.project_root,
            'workspace_file': self._find_workspace_file(),
            'settings': self._get_vscode_settings()
        }
        
        return workspace_info

    def _find_workspace_file(self) -> Optional[str]:
        """Find VSCode workspace file.
        
        Returns:
            Path to workspace file or None
        """
        workspace_file = os.path.join(self.config.project_root, '.vscode', 'settings.json')
        if os.path.exists(workspace_file):
            return workspace_file
        
        # Look for .code-workspace file
        for file in os.listdir(self.config.project_root):
            if file.endswith('.code-workspace'):
                return os.path.join(self.config.project_root, file)
        
        return None

    def _get_vscode_settings(self) -> Dict[str, Any]:
        """Get VSCode settings.
        
        Returns:
            VSCode settings
        """
        settings_file = os.path.join(self.config.project_root, '.vscode', 'settings.json')
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {}

    def get_open_files(self) -> List[str]:
        """Get list of currently open files in VSCode.
        
        Returns:
            List of open file paths
        """
        # VSCode doesn't provide a direct way to get open files via CLI
        # This would typically be handled by a VSCode extension
        return []

    def get_file_content(self, file_path: str) -> Optional[str]:
        """Get content of a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content or None
        """
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception:
            return None

    def generate_extension_config(self) -> str:
        """Generate VSCode extension configuration.
        
        Returns:
            Extension configuration JSON
        """
        return json.dumps({
            "name": "agentops",
            "displayName": "AgentOps",
            "description": "AI-powered requirements-driven test automation",
            "version": "0.1.0",
            "publisher": "agentops",
            "engines": {
                "vscode": "^1.60.0"
            },
            "categories": [
                "Testing",
                "Other"
            ],
            "activationEvents": [
                "onCommand:agentops.infer",
                "onCommand:agentops.approve",
                "onCommand:agentops.generate-tests",
                "onCommand:agentops.run-tests"
            ],
            "main": "./out/extension.js",
            "contributes": {
                "commands": [
                    {
                        "command": "agentops.infer",
                        "title": "AgentOps: Infer Requirements"
                    },
                    {
                        "command": "agentops.approve",
                        "title": "AgentOps: Approve Requirements"
                    },
                    {
                        "command": "agentops.generate-tests",
                        "title": "AgentOps: Generate Tests"
                    },
                    {
                        "command": "agentops.run-tests",
                        "title": "AgentOps: Run Tests"
                    }
                ],
                "configuration": {
                    "title": "AgentOps",
                    "properties": {
                        "agentops.autoApprove": {
                            "type": "boolean",
                            "default": false,
                            "description": "Auto-approve requirements"
                        },
                        "agentops.openaiApiKey": {
                            "type": "string",
                            "default": "",
                            "description": "OpenAI API key"
                        }
                    }
                }
            }
        }, indent=2)

    def generate_launch_config(self) -> str:
        """Generate VSCode launch configuration.
        
        Returns:
            Launch configuration JSON
        """
        return json.dumps({
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "AgentOps: Run Tests",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/.agentops/run_tests.py",
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}"
                }
            ]
        }, indent=2)


class PyCharmIntegration(BaseIDEIntegration):
    """PyCharm integration for AgentOps."""

    def get_workspace_info(self) -> Dict[str, Any]:
        """Get PyCharm workspace information.
        
        Returns:
            Workspace information
        """
        workspace_info = {
            'ide': 'pycharm',
            'project_root': self.config.project_root,
            'project_file': self._find_project_file(),
            'settings': self._get_pycharm_settings()
        }
        
        return workspace_info

    def _find_project_file(self) -> Optional[str]:
        """Find PyCharm project file.
        
        Returns:
            Path to project file or None
        """
        # Look for .idea directory
        idea_dir = os.path.join(self.config.project_root, '.idea')
        if os.path.exists(idea_dir):
            return idea_dir
        
        return None

    def _get_pycharm_settings(self) -> Dict[str, Any]:
        """Get PyCharm settings.
        
        Returns:
            PyCharm settings
        """
        settings = {}
        
        # Read workspace.xml
        workspace_file = os.path.join(self.config.project_root, '.idea', 'workspace.xml')
        if os.path.exists(workspace_file):
            try:
                with open(workspace_file, 'r') as f:
                    # Parse XML (simplified)
                    content = f.read()
                    settings['workspace'] = content
            except Exception:
                pass
        
        return settings

    def get_open_files(self) -> List[str]:
        """Get list of currently open files in PyCharm.
        
        Returns:
            List of open file paths
        """
        # PyCharm doesn't provide a direct way to get open files via CLI
        # This would typically be handled by a PyCharm plugin
        return []

    def get_file_content(self, file_path: str) -> Optional[str]:
        """Get content of a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content or None
        """
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception:
            return None

    def generate_plugin_config(self) -> str:
        """Generate PyCharm plugin configuration.
        
        Returns:
            Plugin configuration XML
        """
        return """<?xml version="1.0" encoding="UTF-8"?>
<idea-plugin>
    <id>com.agentops.plugin</id>
    <name>AgentOps</name>
    <vendor>AgentOps</vendor>
    <description>AI-powered requirements-driven test automation</description>
    
    <depends>com.intellij.modules.platform</depends>
    <depends>com.intellij.modules.python</depends>
    
    <extensions defaultExtensionNs="com.intellij">
        <toolWindow id="AgentOps" secondary="true" icon="AllIcons.General.Modified" anchor="right"
                   factoryClass="com.agentops.plugin.AgentOpsToolWindowFactory"/>
    </extensions>
    
    <actions>
        <action id="AgentOps.InferRequirements" class="com.agentops.plugin.actions.InferRequirementsAction"
                text="Infer Requirements" description="Infer requirements from code changes">
            <add-to-group group-id="ToolsMenu" anchor="last"/>
        </action>
        
        <action id="AgentOps.ApproveRequirements" class="com.agentops.plugin.actions.ApproveRequirementsAction"
                text="Approve Requirements" description="Approve inferred requirements">
            <add-to-group group-id="ToolsMenu" anchor="last"/>
        </action>
        
        <action id="AgentOps.GenerateTests" class="com.agentops.plugin.actions.GenerateTestsAction"
                text="Generate Tests" description="Generate tests from requirements">
            <add-to-group group-id="ToolsMenu" anchor="last"/>
        </action>
        
        <action id="AgentOps.RunTests" class="com.agentops.plugin.actions.RunTestsAction"
                text="Run Tests" description="Run generated tests">
            <add-to-group group-id="ToolsMenu" anchor="last"/>
        </action>
    </actions>
</idea-plugin>"""

    def generate_run_config(self) -> str:
        """Generate PyCharm run configuration.
        
        Returns:
            Run configuration XML
        """
        return """<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="AgentOps: Run Tests" type="PythonConfigurationType" factoryName="Python">
    <module name="agentops" />
    <option name="INTERPRETER_OPTIONS" value="" />
    <option name="PARENT_ENVS" value="true" />
    <envs>
      <env name="PYTHONUNBUFFERED" value="1" />
    </envs>
    <option name="SDK_HOME" value="" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
    <option name="IS_MODULE_SDK" value="true" />
    <option name="ADD_CONTENT_ROOTS" value="true" />
    <option name="ADD_SOURCE_ROOTS" value="true" />
    <option name="SCRIPT_NAME" value="$PROJECT_DIR$/.agentops/run_tests.py" />
    <option name="PARAMETERS" value="" />
    <option name="SHOW_COMMAND_LINE" value="false" />
    <option name="EMULATE_TERMINAL" value="false" />
    <option name="MODULE_MODE" value="false" />
    <option name="REDIRECT_INPUT" value="false" />
    <option name="INPUT_FILE" value="" />
    <method v="2" />
  </configuration>
</component>""" 