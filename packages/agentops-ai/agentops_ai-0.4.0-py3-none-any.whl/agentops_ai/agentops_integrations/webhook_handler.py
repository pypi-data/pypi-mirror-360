"""Webhook handler for AgentOps integrations.

Provides real-time webhook processing for CI/CD and external tool integrations.
"""

import json
import logging
import threading
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import hmac
import hashlib


@dataclass
class IntegrationConfig:
    """Configuration for webhook handler."""
    project_root: str
    webhook_enabled: bool = False
    webhook_port: int = 8080
    webhook_secret: Optional[str] = None
    auto_approve: bool = False


class WebhookRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for webhook endpoints."""

    def __init__(self, *args, integration_agent=None, **kwargs):
        """Initialize request handler.
        
        Args:
            integration_agent: Reference to integration agent
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.integration_agent = integration_agent
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        """Override log message to use our logger."""
        logging.getLogger('agentops.webhook').info(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        """Handle GET requests (health check)."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "service": "agentops-webhook",
            "timestamp": time.time()
        }
        
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle POST requests (webhook events)."""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Read request body
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            event_data = json.loads(post_data.decode('utf-8'))
            
            # Verify webhook signature if secret is configured
            if self.integration_agent and self.integration_agent.config.webhook_secret:
                if not self._verify_signature(post_data):
                    self.send_error(401, "Invalid signature")
                    return
            
            # Process the webhook event
            if self.integration_agent:
                result = self.integration_agent.process_ci_event(event_data)
            else:
                result = {"success": False, "error": "Integration agent not available"}
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "success": result.get("success", False),
                "message": result.get("message", "Webhook processed"),
                "timestamp": time.time()
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            logging.getLogger('agentops.webhook').error(f"Webhook processing error: {str(e)}")
            self.send_error(500, "Internal server error")

    def _verify_signature(self, payload: bytes) -> bool:
        """Verify webhook signature.
        
        Args:
            payload: Request payload
            
        Returns:
            True if signature is valid
        """
        if not self.integration_agent or not self.integration_agent.config.webhook_secret:
            return True
        
        signature = self.headers.get('X-Hub-Signature-256')
        if not signature:
            return False
        
        # Remove 'sha256=' prefix
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        # Calculate expected signature
        expected_signature = hmac.new(
            self.integration_agent.config.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)


class WebhookHandler:
    """Webhook handler for AgentOps integrations."""

    def __init__(self, config: IntegrationConfig, integration_agent):
        """Initialize webhook handler.
        
        Args:
            config: Integration configuration
            integration_agent: Reference to integration agent
        """
        self.config = config
        self.integration_agent = integration_agent
        self.server = None
        self.server_thread = None
        self.logger = logging.getLogger('agentops.webhook')

    def start_server(self):
        """Start webhook server."""
        if self.server:
            self.logger.warning("Webhook server already running")
            return
        
        try:
            # Create custom request handler with integration agent reference
            class CustomHandler(WebhookRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, integration_agent=self.integration_agent, **kwargs)
            
            # Create server
            self.server = HTTPServer(('localhost', self.config.webhook_port), CustomHandler)
            
            # Start server in background thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            self.logger.info(f"Webhook server started on port {self.config.webhook_port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start webhook server: {str(e)}")
            raise

    def _run_server(self):
        """Run the webhook server."""
        try:
            self.server.serve_forever()
        except Exception as e:
            self.logger.error(f"Webhook server error: {str(e)}")

    def stop_server(self):
        """Stop webhook server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            self.server_thread = None
            self.logger.info("Webhook server stopped")

    def get_webhook_url(self) -> str:
        """Get webhook URL for external configuration.
        
        Returns:
            Webhook URL
        """
        return f"http://localhost:{self.config.webhook_port}/webhook"

    def generate_github_webhook_config(self) -> Dict[str, Any]:
        """Generate GitHub webhook configuration.
        
        Returns:
            GitHub webhook configuration
        """
        return {
            "url": self.get_webhook_url(),
            "content_type": "json",
            "secret": self.config.webhook_secret or "your-webhook-secret",
            "events": [
                "push",
                "pull_request",
                "pull_request_review",
                "pull_request_review_comment"
            ],
            "active": True
        }

    def generate_gitlab_webhook_config(self) -> Dict[str, Any]:
        """Generate GitLab webhook configuration.
        
        Returns:
            GitLab webhook configuration
        """
        return {
            "url": self.get_webhook_url(),
            "push_events": True,
            "merge_requests_events": True,
            "tag_push_events": False,
            "note_events": False,
            "confidential_note_events": False,
            "pipeline_events": False,
            "wiki_page_events": False,
            "deployment_events": False,
            "job_events": False,
            "releases_events": False,
            "enable_ssl_verification": False,
            "token": self.config.webhook_secret or "your-webhook-token"
        }

    def generate_jenkins_webhook_config(self) -> Dict[str, Any]:
        """Generate Jenkins webhook configuration.
        
        Returns:
            Jenkins webhook configuration
        """
        return {
            "url": self.get_webhook_url(),
            "events": [
                "build_started",
                "build_completed",
                "build_failed"
            ],
            "authentication": {
                "type": "token",
                "token": self.config.webhook_secret or "your-webhook-token"
            }
        }

    def process_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook event data.
        
        Args:
            event_data: Webhook event data
            
        Returns:
            Processing result
        """
        try:
            # Determine event type
            event_type = self._determine_event_type(event_data)
            
            # Add event type to data
            event_data['event_type'] = event_type
            
            # Process with integration agent
            if self.integration_agent:
                return self.integration_agent.process_ci_event(event_data)
            else:
                return {"success": False, "error": "Integration agent not available"}
                
        except Exception as e:
            self.logger.error(f"Error processing webhook event: {str(e)}")
            return {"success": False, "error": str(e)}

    def _determine_event_type(self, event_data: Dict[str, Any]) -> str:
        """Determine event type from webhook data.
        
        Args:
            event_data: Webhook event data
            
        Returns:
            Event type string
        """
        # Check for GitHub-style events
        if 'ref' in event_data and 'repository' in event_data:
            if 'pull_request' in event_data:
                return 'pull_request'
            elif event_data.get('ref', '').startswith('refs/heads/'):
                return 'push'
            elif event_data.get('ref', '').startswith('refs/tags/'):
                return 'tag_push'
        
        # Check for GitLab-style events
        if 'object_kind' in event_data:
            return event_data['object_kind']
        
        # Check for Jenkins-style events
        if 'build' in event_data:
            return 'build'
        
        # Default
        return 'unknown'

    def get_webhook_status(self) -> Dict[str, Any]:
        """Get webhook server status.
        
        Returns:
            Status information
        """
        return {
            "running": self.server is not None,
            "port": self.config.webhook_port,
            "url": self.get_webhook_url() if self.server else None,
            "secret_configured": bool(self.config.webhook_secret)
        } 