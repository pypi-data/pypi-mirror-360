"""
Git Tools Package

This package contains git-related tools and utilities:
- git: Core git operations (clone, GitHub CLI)
- git_config.yaml: Configuration for git operations

Moved from agents/git_langgraph/tools for better organization.
"""

from .git import (
    GitExecutor,
    git_clone,
    gh_open_issue,
    get_git_executor,
    GitCloneInput,
    GitCloneOutput,
    GhOpenIssueInput,
    GhOpenIssueOutput,
)

# Ensure the tool functions reference the exported get_git_executor so that
# tests can patch `diagram_to_iac.tools.git.get_git_executor` and have the
# patch affect the functions imported from this package. Without this,
# git_clone and gh_open_issue would retain references to the original function
# defined in ``git.py`` making patching ineffective.
import importlib

def _patched_get_git_executor():
    """Resolve get_git_executor dynamically so tests can patch it easily."""
    return importlib.import_module(__name__).get_git_executor()

git_clone.func.__globals__["get_git_executor"] = _patched_get_git_executor
gh_open_issue.func.__globals__["get_git_executor"] = _patched_get_git_executor

# Compatibility alias for backward compatibility
GitTool = GitExecutor

__all__ = [
    "GitExecutor", 
    "GitTool",  # Compatibility alias
    "git_clone", 
    "gh_open_issue",
    "get_git_executor",
    "GitCloneInput",
    "GitCloneOutput",
    "GhOpenIssueInput", 
    "GhOpenIssueOutput"
]
