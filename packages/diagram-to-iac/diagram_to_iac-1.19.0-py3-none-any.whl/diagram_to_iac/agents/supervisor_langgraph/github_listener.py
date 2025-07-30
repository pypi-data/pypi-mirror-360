#!/usr/bin/env python3
"""
GitHub Comment Listener for DevOps-in-a-Box R2D Action
======================================================

This module provides GitHub comment monitoring and retry dispatch functionality.
It polls umbrella issues for retry commands and dispatches appropriate actions
based on commit SHA matching and available secrets.

Key Features:
- Poll GitHub issues for retry keywords (retry, run again, continue)
- SHA-based decision making: resume existing or start new pipeline  
- PAT detection and automatic workflow resumption
- Integration with RunRegistry for state management
- Webhook-style comment handling for real-time responses

Usage:
    from diagram_to_iac.agents.supervisor_langgraph.github_listener import GitHubListener
    
    listener = GitHubListener(github_token=token)
    listener.start_polling(issue_id=123, repo_url="https://github.com/user/repo")
"""

import re
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

from diagram_to_iac.core.registry import RunRegistry, RunMetadata, RunStatus
from diagram_to_iac.agents.git_langgraph.agent import GitAgent, GitAgentInput, GitAgentOutput


class RetryCommand(str, Enum):
    """Supported retry command keywords."""
    RETRY = "retry"
    RUN_AGAIN = "run again"
    CONTINUE = "continue"
    RESUME = "resume"


@dataclass
class CommentEvent:
    """Represents a GitHub issue comment event."""
    comment_id: int
    author: str
    body: str
    created_at: datetime
    issue_id: int
    repo_url: str


@dataclass
class RetryContext:
    """Context information for retry operations."""
    command: RetryCommand
    comment_event: CommentEvent
    target_sha: Optional[str] = None
    is_manual_request: bool = False
    should_resume: bool = False
    existing_run: Optional[RunMetadata] = None


class GitHubListener:
    """
    GitHub comment listener for retry dispatch functionality.
    
    Monitors GitHub issues for retry commands and coordinates with the
    RunRegistry to determine appropriate actions (resume vs new run).
    """
    
    def __init__(self, github_token: Optional[str] = None, registry: Optional[RunRegistry] = None):
        """
        Initialize the GitHub listener.
        
        Args:
            github_token: GitHub personal access token
            registry: RunRegistry instance for state management
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.github_token = github_token
        self.registry = registry or RunRegistry()
        self.git_agent = GitAgent()
        
        # Compile retry command patterns
        self.retry_patterns = [
            re.compile(r'\b(retry)\b', re.IGNORECASE),
            re.compile(r'\b(run\s+again)\b', re.IGNORECASE),
            re.compile(r'\b(continue)\b', re.IGNORECASE),
            re.compile(r'\b(resume)\b', re.IGNORECASE),
        ]
        
        # Callbacks for different actions
        self.resume_callback: Optional[Callable[[RetryContext], bool]] = None
        self.new_run_callback: Optional[Callable[[RetryContext], bool]] = None
        
        self.logger.info("GitHub listener initialized")
    
    def set_callbacks(self, 
                     resume_callback: Optional[Callable[[RetryContext], bool]] = None,
                     new_run_callback: Optional[Callable[[RetryContext], bool]] = None):
        """
        Set callback functions for handling retry actions.
        
        Args:
            resume_callback: Function to call when resuming existing run
            new_run_callback: Function to call when starting new run
        """
        self.resume_callback = resume_callback
        self.new_run_callback = new_run_callback
        self.logger.info("Retry callbacks configured")
    
    def detect_retry_command(self, comment_body: str) -> Optional[RetryCommand]:
        """
        Detect retry commands in a comment body.
        
        Args:
            comment_body: The text content of the comment
            
        Returns:
            RetryCommand if found, None otherwise
        """
        for pattern in self.retry_patterns:
            match = pattern.search(comment_body)
            if match:
                command_text = match.group(1).lower().replace(" ", "_")
                try:
                    return RetryCommand(command_text)
                except ValueError:
                    # Handle "run again" case
                    if "run" in command_text and "again" in comment_body.lower():
                        return RetryCommand.RUN_AGAIN
        return None
    
    def extract_sha_from_comment(self, comment_body: str) -> Optional[str]:
        """
        Extract commit SHA from comment if specified.
        
        Args:
            comment_body: The text content of the comment
            
        Returns:
            Commit SHA if found, None otherwise
        """
        # Look for SHA patterns (7+ hex characters)
        sha_pattern = re.compile(r'\b([a-f0-9]{7,40})\b', re.IGNORECASE)
        match = sha_pattern.search(comment_body)
        if match:
            return match.group(1).lower()
        return None
    
    def get_latest_commit_sha(self, repo_url: str) -> Optional[str]:
        """
        Get the latest commit SHA from the repository.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Latest commit SHA if available, None otherwise
        """
        try:
            # Use GitAgent to get latest commit info
            result = self.git_agent.run(GitAgentInput(
                query=f"get latest commit SHA for repository {repo_url}",
                thread_id="github_listener"
            ))
            
            if result.success and result.answer:
                # Extract SHA from the response
                sha_match = re.search(r'\b([a-f0-9]{7,40})\b', result.answer, re.IGNORECASE)
                if sha_match:
                    return sha_match.group(1).lower()
            
            self.logger.warning(f"Could not retrieve latest commit SHA for {repo_url}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting latest commit SHA: {e}")
            return None
    
    def analyze_retry_context(self, comment_event: CommentEvent, command: RetryCommand) -> RetryContext:
        """
        Analyze retry context to determine appropriate action.
        
        Args:
            comment_event: The comment that triggered the retry
            command: The detected retry command
            
        Returns:
            RetryContext with analysis results
        """
        context = RetryContext(
            command=command,
            comment_event=comment_event
        )
        
        # Extract SHA from comment or get latest
        target_sha = self.extract_sha_from_comment(comment_event.body)
        if not target_sha:
            target_sha = self.get_latest_commit_sha(comment_event.repo_url)
        
        context.target_sha = target_sha
        
        if not target_sha:
            self.logger.warning("Could not determine target SHA for retry")
            return context
        
        # Find existing runs for this repo and SHA
        existing_runs = self.registry.find_by_commit_and_repo(
            comment_event.repo_url, target_sha
        )
        
        if existing_runs:
            # Same SHA - check if we can resume
            latest_run = existing_runs[0]  # Already sorted by creation time
            context.existing_run = latest_run
            
            # Check if run can be resumed (waiting for PAT, etc.)
            if latest_run.can_be_resumed():
                context.should_resume = True
                self.logger.info(f"Found resumable run for SHA {target_sha[:7]}: {latest_run.run_key}")
            else:
                # Run exists but can't be resumed - check if it's completed/failed
                if latest_run.status in [RunStatus.COMPLETED, RunStatus.FAILED]:
                    context.is_manual_request = True
                    self.logger.info(f"Found completed run for SHA {target_sha[:7]}, treating as manual request")
                else:
                    self.logger.warning(f"Found non-resumable run for SHA {target_sha[:7]}: {latest_run.status}")
        else:
            # No existing runs for this SHA - treat as manual request
            context.is_manual_request = True
            self.logger.info(f"No existing runs found for SHA {target_sha[:7]}, treating as manual request")
        
        return context
    
    def add_resumption_comment(self, issue_id: int, repo_url: str, commit_sha: str) -> bool:
        """
        Add a comment to the issue indicating resumption.
        
        Args:
            issue_id: GitHub issue ID
            repo_url: Repository URL
            commit_sha: Commit SHA being resumed
            
        Returns:
            True if comment was added successfully, False otherwise
        """
        try:
            short_sha = commit_sha[:7]
            comment_text = f"🔄 **Resuming action on commit `{short_sha}`**\n\nPipeline resumption requested. Checking for updated secrets and continuing from previous state."
            
            result = self.git_agent.run(GitAgentInput(
                query=f"add comment to issue {issue_id} in repository {repo_url}: {comment_text}",
                issue_id=issue_id,
                thread_id="github_listener"
            ))
            
            if result.success:
                self.logger.info(f"Added resumption comment to issue #{issue_id}")
                return True
            else:
                self.logger.warning(f"Failed to add resumption comment: {result.error_message}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding resumption comment: {e}")
            return False
    
    def handle_retry_command(self, comment_event: CommentEvent) -> bool:
        """
        Handle a detected retry command.
        
        Args:
            comment_event: The comment event containing the retry command
            
        Returns:
            True if retry was handled successfully, False otherwise
        """
        # Detect the retry command
        command = self.detect_retry_command(comment_event.body)
        if not command:
            return False
        
        self.logger.info(f"Detected retry command '{command.value}' from {comment_event.author}")
        
        # Analyze the retry context
        context = self.analyze_retry_context(comment_event, command)
        
        if context.should_resume and context.existing_run:
            # Resume existing run
            self.logger.info(f"Resuming run {context.existing_run.run_key} for SHA {context.target_sha[:7]}")
            
            # Add resumption comment
            self.add_resumption_comment(
                comment_event.issue_id, 
                comment_event.repo_url, 
                context.target_sha
            )
            
            # Call resume callback if set
            if self.resume_callback:
                return self.resume_callback(context)
            else:
                self.logger.warning("No resume callback configured")
                return False
                
        elif context.is_manual_request:
            # Start new run
            self.logger.info(f"Starting new run for SHA {context.target_sha[:7]} (manual request)")
            
            # Call new run callback if set
            if self.new_run_callback:
                return self.new_run_callback(context)
            else:
                self.logger.warning("No new run callback configured")
                return False
        else:
            self.logger.warning(f"Could not determine appropriate action for retry command")
            return False
    
    def poll_issue_comments(self, issue_id: int, repo_url: str, 
                           poll_interval: int = 30, max_polls: Optional[int] = None) -> None:
        """
        Poll an issue for new comments containing retry commands.
        
        Args:
            issue_id: GitHub issue ID to monitor
            repo_url: Repository URL
            poll_interval: Seconds between polls
            max_polls: Maximum number of polls (None for infinite)
        """
        self.logger.info(f"Starting comment polling for issue #{issue_id} in {repo_url}")
        
        last_check = datetime.utcnow()
        poll_count = 0
        
        while max_polls is None or poll_count < max_polls:
            try:
                # Get recent comments
                result = self.git_agent.run(GitAgentInput(
                    query=f"get recent comments for issue {issue_id} in repository {repo_url} since {last_check.isoformat()}",
                    thread_id="github_listener"
                ))
                
                if result.success and result.answer:
                    # Parse comments from response (this would need actual GitHub API integration)
                    # For now, simulate comment detection
                    self.logger.debug(f"Checked for new comments on issue #{issue_id}")
                
                last_check = datetime.utcnow()
                poll_count += 1
                
                if max_polls is None or poll_count < max_polls:
                    time.sleep(poll_interval)
                    
            except KeyboardInterrupt:
                self.logger.info("Polling interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Error during comment polling: {e}")
                time.sleep(poll_interval)
                poll_count += 1
        
        self.logger.info(f"Comment polling completed after {poll_count} polls")
    
    def simulate_comment_event(self, issue_id: int, repo_url: str, 
                              comment_body: str, author: str = "test-user") -> CommentEvent:
        """
        Simulate a comment event for testing purposes.
        
        Args:
            issue_id: GitHub issue ID
            repo_url: Repository URL  
            comment_body: Comment text content
            author: Comment author
            
        Returns:
            Simulated CommentEvent
        """
        return CommentEvent(
            comment_id=12345,
            author=author,
            body=comment_body,
            created_at=datetime.utcnow(),
            issue_id=issue_id,
            repo_url=repo_url
        )


# Helper functions for integration
def create_github_listener(github_token: Optional[str] = None, 
                          registry: Optional[RunRegistry] = None) -> GitHubListener:
    """Create a configured GitHub listener instance."""
    return GitHubListener(github_token=github_token, registry=registry)


def handle_webhook_comment(webhook_payload: Dict[str, Any], 
                          listener: GitHubListener) -> bool:
    """
    Handle a GitHub webhook comment event.
    
    Args:
        webhook_payload: GitHub webhook payload
        listener: Configured GitHubListener instance
        
    Returns:
        True if comment was handled successfully, False otherwise
    """
    try:
        # Extract comment information from webhook payload
        comment_data = webhook_payload.get('comment', {})
        issue_data = webhook_payload.get('issue', {})
        repo_data = webhook_payload.get('repository', {})
        
        comment_event = CommentEvent(
            comment_id=comment_data.get('id', 0),
            author=comment_data.get('user', {}).get('login', 'unknown'),
            body=comment_data.get('body', ''),
            created_at=datetime.fromisoformat(comment_data.get('created_at', datetime.utcnow().isoformat())),
            issue_id=issue_data.get('number', 0),
            repo_url=repo_data.get('html_url', '')
        )
        
        return listener.handle_retry_command(comment_event)
        
    except Exception as e:
        logging.error(f"Error handling webhook comment: {e}")
        return False
