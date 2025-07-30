#!/usr/bin/env python3
"""
Commenter Service for DevOps-in-a-Box R2D Action
================================================

This service provides centralized comment and label management for GitHub issues
created by the R2D workflow. It handles template rendering, comment posting,
and automatic label management based on deployment status.

Key Features:
- Template-based comment generation with variable substitution
- Automatic GitHub label management
- Status tracking with label updates
- Integration with RunRegistry for state management
- Consistent formatting and messaging

Usage:
    from diagram_to_iac.services.commenter import Commenter
    
    commenter = Commenter()
    commenter.post_resume_comment(issue_id=123, sha="abc1234", run_key="run-123")
    commenter.update_labels(issue_id=123, status="in_progress")
"""

import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from diagram_to_iac.agents.git_langgraph.agent import GitAgent, GitAgentInput, GitAgentOutput
from diagram_to_iac.core.registry import RunRegistry, RunStatus


@dataclass
class CommentTemplate:
    """Represents a comment template with metadata."""
    name: str
    template_path: Path
    required_vars: List[str] = field(default_factory=list)
    optional_vars: List[str] = field(default_factory=list)


@dataclass
class LabelRule:
    """Represents a label management rule."""
    status: str
    labels_to_add: List[str] = field(default_factory=list)
    labels_to_remove: List[str] = field(default_factory=list)
    close_issue: bool = False


class Commenter:
    """
    Service for managing GitHub comments and labels for R2D deployments.
    
    Provides template-based comment generation with automatic variable substitution
    and consistent label management based on deployment status.
    """
    
    # Standard R2D labels
    LABEL_R2D_DEPLOYMENT = "r2d-deployment"
    LABEL_R2D_IN_PROGRESS = "r2d-in-progress"
    LABEL_R2D_SUCCEEDED = "r2d-succeeded"
    LABEL_NEEDS_SECRET = "needs-secret"
    LABEL_AUTOMATED = "automated"
    LABEL_INFRASTRUCTURE = "infrastructure"
    
    def __init__(self, git_agent: Optional[GitAgent] = None, registry: Optional[RunRegistry] = None):
        """
        Initialize the Commenter service.
        
        Args:
            git_agent: GitAgent instance for GitHub operations (optional)
            registry: RunRegistry for state management (optional)
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize Git agent for GitHub operations
        self.git_agent = git_agent or GitAgent()
        
        # Initialize registry for state tracking
        from diagram_to_iac.core.registry import get_default_registry
        self.registry = registry or get_default_registry()
        
        # Find templates directory
        self.templates_dir = Path(__file__).parent.parent / "templates" / "issue_comments"
        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")
        
        # Load available templates
        self.templates = self._load_templates()
        
        # Define label management rules
        self.label_rules = self._setup_label_rules()
        
        self.logger.info(f"Commenter initialized with {len(self.templates)} templates")

    def _load_templates(self) -> Dict[str, CommentTemplate]:
        """Load all comment templates from the templates directory."""
        templates = {}
        
        template_configs = {
            "resume": {
                "required_vars": ["sha", "run_key", "previous_status", "timestamp"],
                "optional_vars": []
            },
            "new_commit": {
                "required_vars": ["sha", "previous_issue_id", "timestamp"],
                "optional_vars": ["pr_number"]
            },
            "need_pat": {
                "required_vars": ["sha", "timestamp"],
                "optional_vars": ["workspace_name"]
            },
            "fix_proposed": {
                "required_vars": ["error_type", "fix_description", "timestamp", "sha"],
                "optional_vars": ["fix_details"]
            },
            "success": {
                "required_vars": ["sha", "timestamp", "terraform_summary"],
                "optional_vars": ["duration", "resource_count"]
            }
        }
        
        for template_name, config in template_configs.items():
            template_path = self.templates_dir / f"{template_name}.txt"
            if template_path.exists():
                templates[template_name] = CommentTemplate(
                    name=template_name,
                    template_path=template_path,
                    required_vars=config["required_vars"],
                    optional_vars=config["optional_vars"]
                )
                self.logger.debug(f"Loaded template: {template_name}")
            else:
                self.logger.warning(f"Template file not found: {template_path}")
        
        return templates

    def _setup_label_rules(self) -> Dict[str, LabelRule]:
        """Setup label management rules for different deployment statuses."""
        return {
            "created": LabelRule(
                status="created",
                labels_to_add=[self.LABEL_R2D_DEPLOYMENT, self.LABEL_AUTOMATED, self.LABEL_INFRASTRUCTURE],
                labels_to_remove=[]
            ),
            "in_progress": LabelRule(
                status="in_progress",
                labels_to_add=[self.LABEL_R2D_IN_PROGRESS],
                labels_to_remove=[self.LABEL_NEEDS_SECRET]
            ),
            "needs_secret": LabelRule(
                status="needs_secret",
                labels_to_add=[self.LABEL_NEEDS_SECRET],
                labels_to_remove=[self.LABEL_R2D_IN_PROGRESS]
            ),
            "succeeded": LabelRule(
                status="succeeded",
                labels_to_add=[self.LABEL_R2D_SUCCEEDED],
                labels_to_remove=[self.LABEL_R2D_IN_PROGRESS, self.LABEL_NEEDS_SECRET],
                close_issue=True
            ),
            "error": LabelRule(
                status="error",
                labels_to_add=[],
                labels_to_remove=[self.LABEL_R2D_IN_PROGRESS]
            ),
            "waiting_for_pat": LabelRule(
                status="waiting_for_pat",
                labels_to_add=[self.LABEL_NEEDS_SECRET],
                labels_to_remove=[self.LABEL_R2D_IN_PROGRESS]
            ),
            "waiting_for_pr": LabelRule(
                status="waiting_for_pr",
                labels_to_add=[],
                labels_to_remove=[self.LABEL_R2D_IN_PROGRESS, self.LABEL_NEEDS_SECRET]
            ),
            "completed": LabelRule(
                status="completed",
                labels_to_add=[self.LABEL_R2D_SUCCEEDED],
                labels_to_remove=[self.LABEL_R2D_IN_PROGRESS, self.LABEL_NEEDS_SECRET],
                close_issue=True
            ),
            "failed": LabelRule(
                status="failed",
                labels_to_add=[],
                labels_to_remove=[self.LABEL_R2D_IN_PROGRESS]
            ),
            "cancelled": LabelRule(
                status="cancelled",
                labels_to_add=[],
                labels_to_remove=[self.LABEL_R2D_IN_PROGRESS, self.LABEL_NEEDS_SECRET],
                close_issue=True
            )
        }

    def _render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render a comment template with the provided variables.
        
        Args:
            template_name: Name of the template to render
            variables: Dictionary of variables to substitute
            
        Returns:
            Rendered template content
            
        Raises:
            ValueError: If template not found or required variables missing
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        
        # Add default values for common variables
        default_vars = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "workspace_name": "default",
            "pr_number": "N/A",
            "duration": "N/A",
            "resource_count": "N/A",
            "fix_details": "See above for details"
        }
        
        # Merge variables with defaults (user variables take precedence)
        final_vars = {**default_vars, **variables}
        
        # Check for required variables (after applying defaults)
        missing_vars = [var for var in template.required_vars if var not in final_vars]
        if missing_vars:
            raise ValueError(f"Missing required variables for template '{template_name}': {missing_vars}")
        
        # Load template content
        try:
            with open(template.template_path, 'r') as f:
                content = f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to load template '{template_name}': {e}")
        
        # Render template
        try:
            rendered = content.format(**final_vars)
            self.logger.debug(f"Successfully rendered template '{template_name}'")
            return rendered
        except KeyError as e:
            raise ValueError(f"Template variable not found: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to render template '{template_name}': {e}")

    def _post_comment(self, issue_id: int, comment_body: str, repo_url: Optional[str] = None) -> bool:
        """
        Post a comment to a GitHub issue.
        
        Args:
            issue_id: GitHub issue ID
            comment_body: Comment content to post
            repo_url: Repository URL (optional, for context)
            
        Returns:
            True if comment posted successfully, False otherwise
        """
        try:
            # Use GitAgent to post the comment
            git_input = GitAgentInput(
                query=f"comment on issue {issue_id}: {comment_body}",
                issue_id=issue_id
            )
            
            result = self.git_agent.run(git_input)
            
            if not result.success:
                error_msg = result.artifacts.get("error_message", "Unknown error")
                self.logger.error(f"Failed to post comment to issue #{issue_id}: {error_msg}")
                return False
            
            self.logger.info(f"Successfully posted comment to issue #{issue_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error posting comment to issue #{issue_id}: {e}")
            return False

    def update_labels(self, issue_id: int, status: str, repo_url: Optional[str] = None) -> bool:
        """
        Update GitHub issue labels based on deployment status.
        
        Args:
            issue_id: GitHub issue ID
            status: Deployment status (maps to RunStatus values)
            repo_url: Repository URL (optional, for context)
            
        Returns:
            True if labels updated successfully, False otherwise
        """
        if status not in self.label_rules:
            self.logger.warning(f"No label rule defined for status: {status}")
            return False
        
        rule = self.label_rules[status]
        
        try:
            # Add labels
            for label in rule.labels_to_add:
                git_input = GitAgentInput(
                    query=f"add label {label} to issue {issue_id}",
                    issue_id=issue_id
                )
                result = self.git_agent.run(git_input)
                
                if not result.success:
                    error_msg = result.artifacts.get("error_message", "Unknown error")
                    self.logger.warning(f"Failed to add label '{label}' to issue #{issue_id}: {error_msg}")
                else:
                    self.logger.debug(f"Added label '{label}' to issue #{issue_id}")
            
            # Remove labels  
            for label in rule.labels_to_remove:
                git_input = GitAgentInput(
                    query=f"remove label {label} from issue {issue_id}",
                    issue_id=issue_id
                )
                result = self.git_agent.run(git_input)
                
                if not result.success:
                    error_msg = result.artifacts.get("error_message", "Unknown error")
                    self.logger.warning(f"Failed to remove label '{label}' from issue #{issue_id}: {error_msg}")
                else:
                    self.logger.debug(f"Removed label '{label}' from issue #{issue_id}")
            
            # Close issue if required
            if rule.close_issue:
                git_input = GitAgentInput(
                    query=f"close issue {issue_id}",
                    issue_id=issue_id
                )
                result = self.git_agent.run(git_input)
                
                if not result.success:
                    error_msg = result.artifacts.get("error_message", "Unknown error")
                    self.logger.warning(f"Failed to close issue #{issue_id}: {error_msg}")
                else:
                    self.logger.info(f"Closed issue #{issue_id}")
            
            self.logger.info(f"Successfully updated labels for issue #{issue_id} with status '{status}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating labels for issue #{issue_id}: {e}")
            return False

    # Template-specific comment methods

    def post_resume_comment(self, issue_id: int, sha: str, run_key: str, 
                          previous_status: str = "unknown", repo_url: Optional[str] = None) -> bool:
        """
        Post a resume deployment comment.
        
        Args:
            issue_id: GitHub issue ID
            sha: Commit SHA being resumed
            run_key: Registry run key
            previous_status: Previous deployment status
            repo_url: Repository URL (optional)
            
        Returns:
            True if comment posted successfully, False otherwise
        """
        variables = {
            "sha": sha,
            "run_key": run_key,
            "previous_status": previous_status
        }
        
        try:
            comment_body = self._render_template("resume", variables)
            success = self._post_comment(issue_id, comment_body, repo_url)
            
            if success:
                # Update labels to in-progress
                self.update_labels(issue_id, "in_progress", repo_url)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error posting resume comment: {e}")
            return False

    def post_new_commit_comment(self, issue_id: int, sha: str, previous_issue_id: int,
                              pr_number: Optional[int] = None, repo_url: Optional[str] = None) -> bool:
        """
        Post a new commit deployment comment.
        
        Args:
            issue_id: GitHub issue ID
            sha: New commit SHA
            previous_issue_id: Previous umbrella issue ID
            pr_number: Pull request number (optional)
            repo_url: Repository URL (optional)
            
        Returns:
            True if comment posted successfully, False otherwise
        """
        variables = {
            "sha": sha,
            "previous_issue_id": previous_issue_id
        }
        
        if pr_number:
            variables["pr_number"] = pr_number
        
        try:
            comment_body = self._render_template("new_commit", variables)
            return self._post_comment(issue_id, comment_body, repo_url)
            
        except Exception as e:
            self.logger.error(f"Error posting new commit comment: {e}")
            return False

    def post_need_pat_comment(self, issue_id: int, sha: str, workspace_name: str = "default",
                            repo_url: Optional[str] = None) -> bool:
        """
        Post a PAT required comment.
        
        Args:
            issue_id: GitHub issue ID
            sha: Commit SHA waiting for PAT
            workspace_name: Terraform workspace name
            repo_url: Repository URL (optional)
            
        Returns:
            True if comment posted successfully, False otherwise
        """
        variables = {
            "sha": sha,
            "workspace_name": workspace_name
        }
        
        try:
            comment_body = self._render_template("need_pat", variables)
            success = self._post_comment(issue_id, comment_body, repo_url)
            
            if success:
                # Update labels to waiting for secret
                self.update_labels(issue_id, "waiting_for_pat", repo_url)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error posting need PAT comment: {e}")
            return False

    def post_fix_proposed_comment(self, issue_id: int, sha: str, error_type: str,
                                fix_description: str, fix_details: str = "",
                                repo_url: Optional[str] = None) -> bool:
        """
        Post a fix proposed comment.
        
        Args:
            issue_id: GitHub issue ID
            sha: Commit SHA being fixed
            error_type: Type of error being fixed
            fix_description: Description of the fix
            fix_details: Detailed fix information
            repo_url: Repository URL (optional)
            
        Returns:
            True if comment posted successfully, False otherwise
        """
        variables = {
            "sha": sha,
            "error_type": error_type,
            "fix_description": fix_description,
            "fix_details": fix_details or "Automatic fix applied"
        }
        
        try:
            comment_body = self._render_template("fix_proposed", variables)
            return self._post_comment(issue_id, comment_body, repo_url)
            
        except Exception as e:
            self.logger.error(f"Error posting fix proposed comment: {e}")
            return False

    def post_success_comment(self, issue_id: int, sha: str, terraform_summary: str,
                           duration: str = "N/A", resource_count: str = "N/A",
                           repo_url: Optional[str] = None) -> bool:
        """
        Post a deployment success comment.
        
        Args:
            issue_id: GitHub issue ID
            sha: Completed commit SHA
            terraform_summary: Summary of Terraform operations
            duration: Deployment duration
            resource_count: Number of resources deployed
            repo_url: Repository URL (optional)
            
        Returns:
            True if comment posted successfully, False otherwise
        """
        variables = {
            "sha": sha,
            "terraform_summary": terraform_summary,
            "duration": duration,
            "resource_count": resource_count
        }
        
        try:
            comment_body = self._render_template("success", variables)
            success = self._post_comment(issue_id, comment_body, repo_url)
            
            if success:
                # Update labels to succeeded and close issue
                self.update_labels(issue_id, "completed", repo_url)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error posting success comment: {e}")
            return False

    # Utility methods

    def get_template_variables(self, template_name: str) -> Dict[str, List[str]]:
        """
        Get required and optional variables for a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Dictionary with 'required' and 'optional' variable lists
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        return {
            "required": template.required_vars,
            "optional": template.optional_vars
        }

    def list_available_templates(self) -> List[str]:
        """
        Get list of available comment templates.
        
        Returns:
            List of template names
        """
        return list(self.templates.keys())

    def get_label_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all label management rules.
        
        Returns:
            Dictionary of status -> rule mappings
        """
        return {
            status: {
                "labels_to_add": rule.labels_to_add,
                "labels_to_remove": rule.labels_to_remove,
                "close_issue": rule.close_issue
            }
            for status, rule in self.label_rules.items()
        }


# Convenience functions for backwards compatibility
def post_resume_comment(issue_id: int, sha: str, run_key: str, **kwargs) -> bool:
    """Convenience function to post a resume comment."""
    commenter = Commenter()
    return commenter.post_resume_comment(issue_id, sha, run_key, **kwargs)


def post_success_comment(issue_id: int, sha: str, terraform_summary: str, **kwargs) -> bool:
    """Convenience function to post a success comment."""
    commenter = Commenter()
    return commenter.post_success_comment(issue_id, sha, terraform_summary, **kwargs)


def update_issue_labels(issue_id: int, status: str, **kwargs) -> bool:
    """Convenience function to update issue labels."""
    commenter = Commenter()
    return commenter.update_labels(issue_id, status, **kwargs)
