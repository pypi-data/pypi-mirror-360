#!/usr/bin/env python3
"""
Registry System for DevOps-in-a-Box R2D Action
===============================================

This module provides a persistent registry to track deployment runs and manage
issue lifecycle. It ensures proper reuse of umbrella issues for the same SHA
and creates new issues for new commits.

Key Features:
- Persistent storage of run metadata
- SHA-based run identification
- Issue lifecycle management
- Helper functions for lookup and updates

Usage:
    from diagram_to_iac.core.registry import RunRegistry
    
    registry = RunRegistry()
    run_key = registry.create_run(repo_url, commit_sha, job_name)
    run_data = registry.lookup(run_key)
    registry.update(run_key, {"status": "completed"})
"""

import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from .config_loader import get_config_value


class RunStatus(str, Enum):
    """Status values for deployment runs."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_PAT = "waiting_for_pat"
    WAITING_FOR_PR = "waiting_for_pr"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStatus(BaseModel):
    """Status information for individual agents."""
    agent_name: str
    status: str
    last_updated: datetime
    error_message: Optional[str] = None
    artifacts: Optional[Dict[str, Any]] = None


class RunMetadata(BaseModel):
    """Complete metadata for a deployment run."""
    run_key: str = Field(..., description="Unique identifier for this run")
    repo_url: str = Field(..., description="GitHub repository URL")
    commit_sha: str = Field(..., description="Git commit SHA")
    job_name: str = Field(..., description="GitHub Actions job name")
    umbrella_issue_id: Optional[int] = Field(None, description="GitHub issue ID for this run")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Run creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    status: RunStatus = Field(default=RunStatus.CREATED, description="Overall run status")
    agent_statuses: Dict[str, AgentStatus] = Field(default_factory=dict, description="Individual agent statuses")
    wait_reason: Optional[str] = Field(None, description="Reason for waiting (if applicable)")
    linked_pr: Optional[int] = Field(None, description="Pull request ID if created")
    branch_name: Optional[str] = Field(None, description="Target branch name")
    thread_id: Optional[str] = Field(None, description="Conversation thread ID")
    artifacts_path: Optional[str] = Field(None, description="Path to collected artifacts")
    terraform_summary: Optional[str] = Field(None, description="Terraform operation summary")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    predecessor_run: Optional[str] = Field(None, description="Previous run key for same repo/issue")
    
    @field_validator('commit_sha')
    @classmethod
    def validate_commit_sha(cls, v):
        """Validate that commit SHA is a valid git hash."""
        if not v or len(v) < 7:
            raise ValueError("Commit SHA must be at least 7 characters")
        return v.lower()
    
    @field_validator('repo_url')
    @classmethod
    def validate_repo_url(cls, v):
        """Validate that repo URL is a valid GitHub URL."""
        if not v or 'github.com' not in v:
            raise ValueError("Repository URL must be a valid GitHub URL")
        return v
    
    def update_timestamp(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.now(timezone.utc)
    
    def get_sha_prefix(self) -> str:
        """Get the short SHA prefix for display."""
        return self.commit_sha[:7]
    
    def is_same_commit(self, other_sha: str) -> bool:
        """Check if this run is for the same commit."""
        return self.commit_sha.lower() == other_sha.lower()
    
    def can_be_resumed(self) -> bool:
        """Check if this run can be resumed."""
        return self.status in [RunStatus.WAITING_FOR_PAT, RunStatus.WAITING_FOR_PR]


class RunRegistry:
    """
    Registry for managing deployment run metadata and lifecycle.
    
    This class provides persistent storage and management of deployment runs,
    ensuring proper issue reuse for the same commit SHA and creating new
    issues for new commits.
    """
    
    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize the run registry.
        
        Args:
            registry_path: Custom path for the registry file. If None, uses default.
        """
        if registry_path:
            self.registry_path = Path(registry_path)
        else:
            # Get workspace base from config (with fallback)
            workspace_base = get_config_value("system.workspace_base", "/workspace")
            
            # Try multiple locations for registry file
            possible_paths = [
                Path.cwd() / "data" / "state" / "issue_registry.json",  # Development
                Path(workspace_base) / "data" / "state" / "issue_registry.json",  # Container workspace
                Path("/tmp/diagram_to_iac/data/state/issue_registry.json"),  # Container fallback
            ]
            self.registry_path = None
            for path in possible_paths:
                try:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    self.registry_path = path
                    break
                except (PermissionError, OSError):
                    continue
            
            # Final fallback if all locations fail
            if not self.registry_path:
                self.registry_path = Path("/tmp/issue_registry.json")
        
        # Ensure the directory exists
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing registry or create empty one
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load the registry from persistent storage."""
        if self.registry_path.exists() and self.registry_path.stat().st_size > 0:
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                
                # Handle empty JSON file
                if not data:
                    self._initialize_empty_registry()
                    return
                
                # Convert datetime strings back to datetime objects
                self.runs = {}
                for run_key, run_data in data.get('runs', {}).items():
                    # Parse datetime fields
                    if 'created_at' in run_data:
                        run_data['created_at'] = datetime.fromisoformat(run_data['created_at'])
                    if 'updated_at' in run_data:
                        run_data['updated_at'] = datetime.fromisoformat(run_data['updated_at'])
                    
                    # Convert status string back to enum if needed
                    if 'status' in run_data and isinstance(run_data['status'], str):
                        try:
                            run_data['status'] = RunStatus(run_data['status'])
                        except ValueError:
                            # Fallback to CREATED if invalid status
                            run_data['status'] = RunStatus.CREATED
                    
                    # Parse agent statuses
                    if 'agent_statuses' in run_data:
                        agent_statuses = {}
                        for agent_name, status_data in run_data['agent_statuses'].items():
                            if 'last_updated' in status_data:
                                status_data['last_updated'] = datetime.fromisoformat(status_data['last_updated'])
                            agent_statuses[agent_name] = AgentStatus(**status_data)
                        run_data['agent_statuses'] = agent_statuses
                    
                    self.runs[run_key] = RunMetadata(**run_data)
                
                self.metadata = data.get('metadata', {})
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"Warning: Could not load registry from {self.registry_path}: {e}")
                self._initialize_empty_registry()
        else:
            self._initialize_empty_registry()
    
    def _initialize_empty_registry(self) -> None:
        """Initialize an empty registry."""
        self.runs = {}
        self.metadata = {
            'version': '1.0.0',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'description': 'DevOps-in-a-Box R2D Action Run Registry'
        }
        # Save the initialized registry to prevent JSON loading warnings
        self._save_registry()
    
    def _save_registry(self) -> None:
        """Save the registry to persistent storage."""
        data = {
            'metadata': self.metadata,
            'runs': {}
        }
        
        # Convert runs to serializable format
        for run_key, run_metadata in self.runs.items():
            run_dict = run_metadata.model_dump()
            
            # Convert enum values to strings for proper serialization
            if 'status' in run_dict:
                if hasattr(run_dict['status'], 'value'):
                    run_dict['status'] = run_dict['status'].value
                elif isinstance(run_dict['status'], RunStatus):
                    run_dict['status'] = run_dict['status'].value
                elif isinstance(run_dict['status'], str):
                    # Already a string, keep as is
                    pass
            
            # Convert datetime objects to ISO strings
            if 'created_at' in run_dict:
                run_dict['created_at'] = run_dict['created_at'].isoformat()
            if 'updated_at' in run_dict:
                run_dict['updated_at'] = run_dict['updated_at'].isoformat()
            
            # Convert agent statuses
            if 'agent_statuses' in run_dict:
                agent_statuses = {}
                for agent_name, status in run_dict['agent_statuses'].items():
                    status_dict = status.model_dump() if hasattr(status, 'model_dump') else status
                    if 'last_updated' in status_dict:
                        status_dict['last_updated'] = status_dict['last_updated'].isoformat()
                    agent_statuses[agent_name] = status_dict
                run_dict['agent_statuses'] = agent_statuses
            
            data['runs'][run_key] = run_dict
        
        # Write to file atomically
        temp_path = self.registry_path.with_suffix('.tmp')
        try:
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            temp_path.replace(self.registry_path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise RuntimeError(f"Failed to save registry: {e}")
    
    def generate_run_key(self, repo_url: str, commit_sha: str, job_name: str) -> str:
        """
        Generate a unique run key for a deployment.
        
        Args:
            repo_url: GitHub repository URL
            commit_sha: Git commit SHA
            job_name: GitHub Actions job name
            
        Returns:
            Unique run key string
        """
        # Extract repo name from URL
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        short_sha = commit_sha[:7]
        
        # Include microseconds and job name for better uniqueness
        now = datetime.now(timezone.utc)
        timestamp = now.strftime('%Y%m%d-%H%M%S')
        microseconds = f"{now.microsecond:06d}"[:3]  # Use first 3 digits of microseconds
        
        # Sanitize job name for use in key
        safe_job_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in job_name)[:10]
        
        base_key = f"{repo_name}-{short_sha}-{safe_job_name}-{timestamp}-{microseconds}"
        
        # Ensure uniqueness by checking if key already exists
        counter = 0
        unique_key = base_key
        while unique_key in self.runs:
            counter += 1
            unique_key = f"{base_key}-{counter}"
            # Safety break to prevent infinite loop
            if counter > 1000:
                # Fallback to UUID if we somehow have 1000+ collisions
                import uuid
                unique_key = f"{repo_name}-{short_sha}-{uuid.uuid4().hex[:8]}"
                break
        
        return unique_key
    
    def create_run(self, repo_url: str, commit_sha: str, job_name: str, 
                   thread_id: Optional[str] = None, branch_name: Optional[str] = None) -> str:
        """
        Create a new deployment run entry.
        
        Args:
            repo_url: GitHub repository URL
            commit_sha: Git commit SHA
            job_name: GitHub Actions job name
            thread_id: Optional conversation thread ID
            branch_name: Optional target branch name
            
        Returns:
            Unique run key for the created run
        """
        run_key = self.generate_run_key(repo_url, commit_sha, job_name)
        
        run_metadata = RunMetadata(
            run_key=run_key,
            repo_url=repo_url,
            commit_sha=commit_sha.lower(),
            job_name=job_name,
            thread_id=thread_id,
            branch_name=branch_name
        )
        
        self.runs[run_key] = run_metadata
        self._save_registry()
        
        return run_key
    
    def lookup(self, run_key: str) -> Optional[RunMetadata]:
        """
        Look up a run by its key.
        
        Args:
            run_key: The run key to look up
            
        Returns:
            RunMetadata if found, None otherwise
        """
        return self.runs.get(run_key)
    
    def update(self, run_key: str, data: Dict[str, Any]) -> bool:
        """
        Update a run with new data.
        
        Args:
            run_key: The run key to update
            data: Dictionary of fields to update
            
        Returns:
            True if update was successful, False if run not found
        """
        if run_key not in self.runs:
            return False
        
        run_metadata = self.runs[run_key]
        
        # Update fields with proper type conversion
        for field, value in data.items():
            if hasattr(run_metadata, field):
                # Handle RunStatus enum conversion
                if field == 'status' and isinstance(value, str):
                    try:
                        value = RunStatus(value)
                    except ValueError:
                        # If invalid status string, keep as RunStatus enum
                        if not isinstance(value, RunStatus):
                            value = RunStatus.CREATED
                setattr(run_metadata, field, value)
        
        # Always update the timestamp
        run_metadata.update_timestamp()
        
        self._save_registry()
        return True
    
    def find_by_commit_and_repo(self, repo_url: str, commit_sha: str) -> List[RunMetadata]:
        """
        Find all runs for a specific repository and commit SHA.
        
        Args:
            repo_url: GitHub repository URL
            commit_sha: Git commit SHA
            
        Returns:
            List of matching RunMetadata objects
        """
        matches = []
        for run_metadata in self.runs.values():
            if (run_metadata.repo_url == repo_url and 
                run_metadata.is_same_commit(commit_sha)):
                matches.append(run_metadata)
        
        # Sort by creation time, newest first
        return sorted(matches, key=lambda x: x.created_at, reverse=True)
    
    def find_resumable_run(self, repo_url: str, commit_sha: str) -> Optional[RunMetadata]:
        """
        Find a resumable run for the given repository and commit.
        
        Args:
            repo_url: GitHub repository URL
            commit_sha: Git commit SHA
            
        Returns:
            RunMetadata for a resumable run, or None if no resumable run exists
        """
        matching_runs = self.find_by_commit_and_repo(repo_url, commit_sha)
        
        for run in matching_runs:
            if run.can_be_resumed():
                return run
        
        return None
    
    def mark_run_completed(self, run_key: str, terraform_summary: Optional[str] = None) -> bool:
        """
        Mark a run as completed.
        
        Args:
            run_key: The run key to mark as completed
            terraform_summary: Optional summary of Terraform operations
            
        Returns:
            True if update was successful, False if run not found
        """
        update_data = {'status': RunStatus.COMPLETED}
        if terraform_summary:
            update_data['terraform_summary'] = terraform_summary
        
        return self.update(run_key, update_data)
    
    def mark_run_failed(self, run_key: str, error_reason: str) -> bool:
        """
        Mark a run as failed.
        
        Args:
            run_key: The run key to mark as failed
            error_reason: Reason for the failure
            
        Returns:
            True if update was successful, False if run not found
        """
        return self.update(run_key, {
            'status': RunStatus.FAILED,
            'wait_reason': error_reason
        })
    
    def update_agent_status(self, run_key: str, agent_name: str, status: str, 
                           error_message: Optional[str] = None, 
                           artifacts: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update the status of a specific agent within a run.
        
        Args:
            run_key: The run key
            agent_name: Name of the agent
            status: New status for the agent
            error_message: Optional error message
            artifacts: Optional artifacts produced by the agent
            
        Returns:
            True if update was successful, False if run not found
        """
        if run_key not in self.runs:
            return False
        
        agent_status = AgentStatus(
            agent_name=agent_name,
            status=status,
            last_updated=datetime.now(timezone.utc),
            error_message=error_message,
            artifacts=artifacts
        )
        
        run_metadata = self.runs[run_key]
        run_metadata.agent_statuses[agent_name] = agent_status
        run_metadata.update_timestamp()
        
        self._save_registry()
        return True
    
    def get_run_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all runs in the registry.
        
        Returns:
            Dictionary containing various statistics
        """
        if not self.runs:
            return {
                'total_runs': 0,
                'status_breakdown': {},
                'oldest_run': None,
                'newest_run': None
            }
        
        status_counts = {}
        for run in self.runs.values():
            status = run.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        sorted_runs = sorted(self.runs.values(), key=lambda x: x.created_at)
        
        return {
            'total_runs': len(self.runs),
            'status_breakdown': status_counts,
            'oldest_run': sorted_runs[0].created_at.isoformat(),
            'newest_run': sorted_runs[-1].created_at.isoformat(),
            'unique_repositories': len(set(run.repo_url for run in self.runs.values())),
            'unique_commits': len(set(run.commit_sha for run in self.runs.values()))
        }
    
    def cleanup_old_runs(self, days_old: int = 30) -> int:
        """
        Clean up runs older than the specified number of days.
        
        Args:
            days_old: Number of days old to consider for cleanup
            
        Returns:
            Number of runs cleaned up
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
        
        old_runs = [
            run_key for run_key, run_metadata in self.runs.items()
            if run_metadata.created_at < cutoff_date and 
               run_metadata.status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED]
        ]
        
        for run_key in old_runs:
            del self.runs[run_key]
        
        if old_runs:
            self._save_registry()
        
        return len(old_runs)
    
    def find_latest_run_with_issue(self, repo_url: str) -> Optional[RunMetadata]:
        """
        Find the most recent run for a repository that has an associated issue.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            RunMetadata for the most recent run with an issue, or None if none found
        """
        matching_runs = []
        for run_metadata in self.runs.values():
            if (run_metadata.repo_url == repo_url and 
                run_metadata.umbrella_issue_id is not None):
                matching_runs.append(run_metadata)
        
        if not matching_runs:
            return None
        
        # Sort by creation time, newest first
        return sorted(matching_runs, key=lambda x: x.created_at, reverse=True)[0]
    
    def find_previous_umbrella_issue(self, repo_url: str, exclude_sha: Optional[str] = None) -> Optional[int]:
        """
        Find the umbrella issue ID from the most recent run for a repository.
        Optionally exclude runs with a specific commit SHA.
        
        Args:
            repo_url: GitHub repository URL
            exclude_sha: Optional commit SHA to exclude from search
            
        Returns:
            Issue ID if found, None otherwise
        """
        matching_runs = []
        for run_metadata in self.runs.values():
            if (run_metadata.repo_url == repo_url and 
                run_metadata.umbrella_issue_id is not None):
                # Exclude runs with the specified SHA if provided
                if exclude_sha and run_metadata.is_same_commit(exclude_sha):
                    continue
                matching_runs.append(run_metadata)
        
        if not matching_runs:
            return None
        
        # Get the most recent run with an issue
        latest_run = sorted(matching_runs, key=lambda x: x.created_at, reverse=True)[0]
        return latest_run.umbrella_issue_id
    
    def link_predecessor_run(self, current_run_key: str, predecessor_run_key: str) -> bool:
        """
        Link a current run to its predecessor run.
        
        Args:
            current_run_key: The current run key
            predecessor_run_key: The predecessor run key
            
        Returns:
            True if linking was successful, False if either run not found
        """
        if current_run_key not in self.runs or predecessor_run_key not in self.runs:
            return False
        
        return self.update(current_run_key, {'predecessor_run': predecessor_run_key})
    
    def get_run_chain(self, run_key: str) -> List[RunMetadata]:
        """
        Get the complete chain of linked runs starting from the given run.
        
        Args:
            run_key: The starting run key
            
        Returns:
            List of RunMetadata objects in chronological order (oldest first)
        """
        if run_key not in self.runs:
            return []
        
        chain = []
        current_run = self.runs[run_key]
        
        # First, find the root of the chain by following predecessors
        visited = set()
        while current_run.predecessor_run and current_run.predecessor_run not in visited:
            visited.add(current_run.run_key)
            if current_run.predecessor_run in self.runs:
                current_run = self.runs[current_run.predecessor_run]
            else:
                break
        
        # Now collect the chain starting from the root
        chain.append(current_run)
        
        # Find all successors
        def find_successors(run: RunMetadata) -> List[RunMetadata]:
            successors = []
            for other_run in self.runs.values():
                if other_run.predecessor_run == run.run_key:
                    successors.append(other_run)
            return sorted(successors, key=lambda x: x.created_at)
        
        # Recursively build the chain
        current_successors = find_successors(current_run)
        while current_successors:
            next_run = current_successors[0]  # Take the first (chronologically)
            chain.append(next_run)
            current_successors = find_successors(next_run)
        
        return chain
    
    def close_old_umbrella_issue(self, run_key: str, new_issue_id: int, new_commit_sha: str) -> bool:
        """
        Mark an umbrella issue as closed due to a new commit and link to the new issue.
        
        Args:
            run_key: The run key whose issue should be marked as closed
            new_issue_id: The new issue ID to link to
            new_commit_sha: The new commit SHA that triggered the new issue
            
        Returns:
            True if update was successful, False if run not found
        """
        return self.update(run_key, {
            'status': RunStatus.COMPLETED,
            'wait_reason': f'Superseded by new commit {new_commit_sha[:7]} - see issue #{new_issue_id}'
        })


# Helper functions for backwards compatibility and convenience
def get_default_registry() -> RunRegistry:
    """Get the default registry instance."""
    return RunRegistry()


def lookup_run(run_key: str) -> Optional[RunMetadata]:
    """Convenience function to lookup a run using the default registry."""
    registry = get_default_registry()
    return registry.lookup(run_key)


def update_run(run_key: str, data: Dict[str, Any]) -> bool:
    """Convenience function to update a run using the default registry."""
    registry = get_default_registry()
    return registry.update(run_key, data)
