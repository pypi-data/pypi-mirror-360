"""
Git tools implementation following our established comprehensive pattern.

This module provides secure git operations with:
- Configuration-driven behavior via YAML
- Comprehensive logging with structured messages  
- Memory integration for operation tracking
- Robust error handling with graceful fallbacks
- Integration with our ShellExecutor for safe command execution
- Pydantic schemas for type safety and validation
"""

import os
import re
import logging
import yaml
from typing import Optional, Dict, Any, List
from pathlib import Path
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator

# Import centralized config loader
try:
    from ...core.config_loader import get_config, get_config_section, get_config_value
except ImportError:
    # Fallback for testing or when config loader is not available
    def get_config() -> Dict[str, Any]:
        return {}
    def get_config_section(section: str) -> Dict[str, Any]:
        return {}
    def get_config_value(path: str, default: Any = None) -> Any:
        return default
from langchain_core.tools import tool

from diagram_to_iac.core.memory import create_memory
from diagram_to_iac.core.config_loader import get_config, get_config_value
from diagram_to_iac.tools.shell import get_shell_executor, ShellExecInput


# --- Pydantic Schemas for Git Operations ---
class GitCloneInput(BaseModel):
    """Input schema for git clone operations following our established pattern."""
    repo_url: str = Field(..., description="Git repository URL to clone")
    depth: Optional[int] = Field(None, description="Clone depth (overrides config default)")
    branch: Optional[str] = Field(None, description="Specific branch to clone")
    target_dir: Optional[str] = Field(None, description="Target directory name (overrides auto-detection)")
    workspace: Optional[str] = Field(None, description="Workspace path (overrides config default)")
    
    @field_validator('repo_url')
    @classmethod
    def validate_repo_url(cls, v):
        """Validate that repo_url is a valid URL."""
        if not v or not isinstance(v, str):
            raise ValueError("Repository URL must be a non-empty string")
        
        # Basic URL validation
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Repository URL must be a valid URL with scheme and host")
        
        return v


class GitCloneOutput(BaseModel):
    """Output schema for git clone operations following our established pattern."""
    status: str = Field(..., description="Operation status: SUCCESS, AUTH_FAILED, ERROR, TIMEOUT, ALREADY_EXISTS")
    repo_path: Optional[str] = Field(None, description="Path to cloned repository if successful")
    repo_name: Optional[str] = Field(None, description="Extracted repository name")
    error_message: Optional[str] = Field(None, description="Error details if operation failed")
    duration: float = Field(..., description="Operation duration in seconds")
    command_executed: Optional[str] = Field(None, description="Git command that was executed")
    workspace_used: str = Field(..., description="Workspace directory used for operation")


class GhOpenIssueInput(BaseModel):
    """Input schema for GitHub CLI issue creation following our established pattern."""
    repo_url: str = Field(..., description="GitHub repository URL (https://github.com/owner/repo)")
    title: str = Field(..., description="Issue title")
    body: str = Field(..., description="Issue body/description")
    labels: Optional[List[str]] = Field(None, description="Issue labels to apply")
    assignees: Optional[List[str]] = Field(None, description="Users to assign to the issue")
    milestone: Optional[str] = Field(None, description="Milestone to associate with the issue")
    issue_id: Optional[int] = Field(None, description="Existing issue number to comment on")
    
    @field_validator('repo_url')
    @classmethod
    def validate_github_repo_url(cls, v):
        """Validate that repo_url is a valid GitHub repository URL."""
        if not v or not isinstance(v, str):
            raise ValueError("Repository URL must be a non-empty string")
        
        # Validate GitHub URL format
        if not v.startswith(('https://github.com/', 'git@github.com:')):
            raise ValueError("Repository URL must be a valid GitHub repository URL")
        
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate issue title."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("Issue title must be a non-empty string")
        return v.strip()
    
    @field_validator('body')
    @classmethod  
    def validate_body(cls, v):
        """Validate issue body."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("Issue body must be a non-empty string")
        return v.strip()


class GhOpenIssueOutput(BaseModel):
    """Output schema for GitHub CLI issue creation following our established pattern."""
    status: str = Field(..., description="Operation status: GH_SUCCESS, GH_AUTH_FAILED, GH_REPO_NOT_FOUND, GH_PERMISSION_DENIED, GH_ERROR")
    issue_url: Optional[str] = Field(None, description="URL of created issue if successful")
    issue_number: Optional[int] = Field(None, description="Issue number if creation was successful")
    repo_owner: Optional[str] = Field(None, description="Repository owner extracted from URL")
    repo_name: Optional[str] = Field(None, description="Repository name extracted from URL")
    error_message: Optional[str] = Field(None, description="Error details if operation failed")
    duration: float = Field(..., description="Operation duration in seconds")
    command_executed: Optional[str] = Field(None, description="GitHub CLI command that was executed")


class GitExecutor:
    """
    GitExecutor provides secure git operations following our established pattern.
    
    Features:
    - Configuration-driven behavior (clone settings, auth patterns, workspace)
    - Comprehensive logging with structured messages
    - Memory integration for operation tracking
    - Robust error handling with graceful fallbacks
    - Integration with ShellExecutor for secure command execution
    - Authentication failure detection and handling
    """
    
    def __init__(self, config_path: str = None, memory_type: str = "persistent"):
        """
        Initialize GitExecutor following our established pattern.
        
        Args:
            config_path: Optional path to git tools configuration file
            memory_type: Type of memory to use ("persistent", "memory", or "langgraph")
        """
        # Configure logger following our pattern
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Load configuration following our pattern
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, 'git_config.yaml')
            self.logger.debug(f"Default config path set to: {config_path}")
        
        # Load configuration using centralized system with fallback to direct file loading
        try:
            # Try to load git configuration from centralized config
            git_config = get_config_section('tools').get('git', {})
            if git_config:
                # Use the git config from centralized system
                self.config = {'git_executor': git_config}
                self.logger.info("Configuration loaded from centralized system")
            else:
                # No git config found, use defaults
                self.logger.warning("No git configuration found in centralized system. Using defaults.")
                self._set_default_config()
        except Exception as e:
            self.logger.warning(f"Failed to load from centralized config: {e}. Falling back to direct file loading.")
            # Fallback to direct file loading for backward compatibility
            if config_path is None:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                config_path = os.path.join(base_dir, 'git_config.yaml')
                self.logger.debug(f"Default config path set to: {config_path}")
            
            try:
                with open(config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                if self.config is None:
                    self.logger.warning(f"Configuration file at {config_path} is empty. Using default values.")
                    self._set_default_config()
                else:
                    self.logger.info(f"Git configuration loaded successfully from {config_path}")
            except FileNotFoundError:
                self.logger.warning(f"Configuration file not found at {config_path}. Using default values.")
                self._set_default_config()
            except yaml.YAMLError as e:
                self.logger.error(f"Error parsing YAML configuration from {config_path}: {e}. Using default values.", exc_info=True)
                self._set_default_config()
        
        # Initialize memory system following our pattern
        self.memory = create_memory(memory_type)
        self.logger.info(f"Git executor memory system initialized: {type(self.memory).__name__}")
        
        # Initialize shell executor dependency
        self.shell_executor = get_shell_executor()
        self.logger.info("Git executor initialized with shell executor dependency")
        
        # Log configuration summary
        git_config = self.config.get('git_executor', {})
        self.logger.info(f"Git executor initialized with workspace: {git_config.get('default_workspace', '/workspace')}")
        self.logger.info(f"Default clone depth: {git_config.get('default_clone_depth', 1)}")
        self.logger.info(f"Auth failure patterns: {len(git_config.get('auth_failure_patterns', []))}")
    
    def _set_default_config(self):
        """Set default configuration using centralized system."""
        self.logger.info("Setting default configuration for GitExecutor.")
        self.config = {
            'git_executor': {
                'default_workspace': get_config_value("system.workspace_base", '/workspace'),
                'default_clone_depth': get_config_value("tools.git.default_clone_depth", 1),
                'default_timeout': get_config_value("network.github_timeout", 300),
                'auth_failure_patterns': [
                    'Authentication failed',
                    'Permission denied',
                    'Could not read from remote repository',
                    'fatal: unable to access',
                    '403 Forbidden',
                    '401 Unauthorized',
                    'Please make sure you have the correct access rights'
                ],
                'repo_path_template': '{workspace}/{repo_name}',
                'sanitize_repo_names': get_config_value("tools.git.sanitize_repo_names", True),
                'enable_detailed_logging': get_config_value("tools.git.enable_detailed_logging", True),
                'store_operations_in_memory': get_config_value("tools.git.store_operations_in_memory", True)
            },
            'error_messages': {
                'invalid_repo_url': "Git executor: Invalid repository URL '{repo_url}'",
                'workspace_not_accessible': "Git executor: Workspace directory '{workspace}' is not accessible",
                'clone_failed': "Git executor: Failed to clone repository '{repo_url}'",
                'auth_failed': "Git executor: Authentication failed for repository '{repo_url}'",
                'timeout_exceeded': "Git executor: Git operation timed out after {timeout} seconds",
                'shell_executor_error': "Git executor: Shell executor error: {error}",
                'repo_already_exists': "Git executor: Repository '{repo_name}' already exists in workspace"
            },
            'success_messages': {
                'clone_started': "Git executor: Starting clone of '{repo_url}'",
                'clone_completed': "Git executor: Successfully cloned '{repo_url}' to '{repo_path}' in {duration:.2f}s",
                'repo_path_resolved': "Git executor: Repository path resolved to '{repo_path}'"
            },
            'status_codes': {
                'success': 'SUCCESS',
                'auth_failed': 'AUTH_FAILED',
                'error': 'ERROR',
                'timeout': 'TIMEOUT',
                'already_exists': 'ALREADY_EXISTS'
            }
        }
    
    def _deep_merge(self, base: dict, overlay: dict) -> dict:
        """
        Deep merge two dictionaries, with overlay taking precedence.
        
        Args:
            base: Base dictionary
            overlay: Dictionary to overlay on base
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL following our pattern."""
        try:
            # Parse URL and extract path
            parsed = urlparse(repo_url)
            path = parsed.path.strip('/')
            
            # Extract repo name (last part, remove .git suffix)
            repo_name = path.split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            
            # Sanitize repo name if configured
            if self.config.get('git_executor', {}).get('sanitize_repo_names', True):
                # Replace invalid characters with underscores
                repo_name = re.sub(r'[^a-zA-Z0-9._-]', '_', repo_name)
            
            self.logger.debug(f"Extracted repo name '{repo_name}' from URL '{repo_url}'")
            return repo_name
            
        except Exception as e:
            self.logger.error(f"Error extracting repo name from '{repo_url}': {e}")
            # Fallback to generic name
            return "repository"
    
    def _build_git_command(self, git_input: GitCloneInput, workspace: str, repo_name: str) -> str:
        """Build git clone command following our pattern with organic authentication."""
        git_config = self.config.get('git_executor', {})
        
        # Start with basic clone command
        cmd_parts = ['git', 'clone']
        
        # Add depth if specified
        depth = git_input.depth or git_config.get('default_clone_depth', 1)
        if depth and depth > 0:
            cmd_parts.extend(['--depth', str(depth)])
        
        # Add branch if specified
        if git_input.branch:
            cmd_parts.extend(['-b', git_input.branch])
        
        # Organically handle repository URL with authentication
        repo_url = self._prepare_authenticated_url(git_input.repo_url)
        cmd_parts.append(repo_url)
        
        # Add target directory
        target_dir = git_input.target_dir or repo_name
        cmd_parts.append(target_dir)
        
        # Join command parts
        command = ' '.join(cmd_parts)
        
        self.logger.debug(f"Built git command: {command}")
        return command
    
    def _prepare_authenticated_url(self, repo_url: str) -> str:
        """
        Organically prepare repository URL with authentication if available.
        
        This method naturally checks for GitHub token and incorporates it
        into the URL when available, making authentication seamless.
        """
        try:
            # Check if GitHub token is available in environment
            github_token = os.environ.get('GITHUB_TOKEN')
            
            if github_token and github_token.strip():
                # Parse the URL to determine if it's a GitHub repository
                parsed = urlparse(repo_url)
                
                # Only apply token authentication for GitHub URLs
                if 'github.com' in parsed.netloc.lower():
                    # Convert to authenticated HTTPS URL format
                    if parsed.scheme == 'https' and '@' not in parsed.netloc:
                        # Reconstruct URL with token authentication
                        authenticated_url = f"https://{github_token}@{parsed.netloc}{parsed.path}"
                        self.logger.debug(f"Using GitHub token authentication for repository access")
                        return authenticated_url
                    else:
                        self.logger.debug(f"Repository URL already contains authentication or is not HTTPS")
                else:
                    self.logger.debug(f"Repository is not on GitHub, using original URL")
            else:
                self.logger.debug(f"No GitHub token found in environment, using original URL")
            
            return repo_url
            
        except Exception as e:
            self.logger.warning(f"Error preparing authenticated URL: {e}, using original URL")
            return repo_url
    
    def _detect_auth_failure(self, error_output: str) -> bool:
        """
        Organically detect authentication failures in command output.
        
        This method checks for various authentication failure patterns
        and provides helpful context about authentication options.
        """
        # Get configured authentication failure patterns
        auth_patterns = self.config.get('git_executor', {}).get('auth_failure_patterns', [])
        
        # Common authentication failure indicators
        common_auth_patterns = [
            'could not read username',
            'could not read password', 
            'terminal prompts disabled',
            'authentication failed',
            'permission denied (publickey)',
            'remote: invalid username or password',
            'fatal: authentication failed',
            'remote: repository not found',  # Often indicates auth issue for private repos
            'remote: permission denied',
            'access denied',
            'invalid credentials'
        ]
        
        # Combine configured patterns with common patterns
        all_patterns = auth_patterns + common_auth_patterns
        
        for pattern in all_patterns:
            if pattern.lower() in error_output.lower():
                self.logger.debug(f"Authentication failure detected with pattern: '{pattern}'")
                
                # Organically check if GitHub token is available and provide helpful context
                github_token = os.environ.get('GITHUB_TOKEN')
                if github_token and github_token.strip():
                    self.logger.info("GitHub token is available but authentication still failed. Token may be invalid or expired.")
                else:
                    self.logger.info("No GitHub token found in environment. For private repositories, set GITHUB_TOKEN environment variable.")
                
                return True
        
        return False
    
    def _validate_workspace(self, workspace: str) -> None:
        """Validate workspace directory accessibility."""
        try:
            workspace_path = Path(workspace)
            
            # Create workspace if it doesn't exist
            if not workspace_path.exists():
                self.logger.info(f"Creating workspace directory: {workspace}")
                workspace_path.mkdir(parents=True, exist_ok=True)
            
            # Check if workspace is accessible
            if not workspace_path.is_dir():
                error_msg = self.config.get('error_messages', {}).get(
                    'workspace_not_accessible',
                    "Git executor: Workspace directory '{workspace}' is not accessible"
                ).format(workspace=workspace)
                raise ValueError(error_msg)
            
            self.logger.debug(f"Workspace validation passed: {workspace}")
            
        except Exception as e:
            self.logger.error(f"Workspace validation failed: {e}")
            raise
    
    def _cleanup_existing_repository(self, repo_path: str, repo_name: str, workspace: str) -> bool:
        """
        Safely clean up existing repository directory before cloning.
        
        Args:
            repo_path: Full path to the repository directory
            repo_name: Name of the repository
            workspace: Workspace base path
            
        Returns:
            bool: True if cleanup successful, False otherwise
        """
        git_config = self.config.get('git_executor', {})
        error_messages = self.config.get('error_messages', {})
        success_messages = self.config.get('success_messages', {})
        
        try:
            repo_path_obj = Path(repo_path)
            workspace_path_obj = Path(workspace).resolve()
            
            # Safety check: ensure repo path is within workspace
            if git_config.get('cleanup_safety_check', True):
                try:
                    repo_path_obj.resolve().relative_to(workspace_path_obj)
                except ValueError:
                    error_msg = error_messages.get('cleanup_safety_violation', '').format(repo_path=repo_path)
                    self.logger.error(error_msg)
                    return False
            
            if repo_path_obj.exists():
                cleanup_msg = error_messages.get('repo_cleanup_started', '').format(
                    repo_name=repo_name, repo_path=repo_path
                )
                self.logger.info(cleanup_msg)
                
                # Store cleanup start in memory
                if git_config.get('store_operations_in_memory', True):
                    self.memory.add_to_conversation("system", cleanup_msg, {
                        "tool": "git_executor",
                        "operation": "cleanup",
                        "repo_name": repo_name,
                        "repo_path": repo_path
                    })
                
                # Remove the directory and all its contents
                import shutil
                shutil.rmtree(repo_path_obj)
                
                success_msg = error_messages.get('repo_cleanup_completed', '').format(repo_name=repo_name)
                self.logger.info(success_msg)
                
                # Store cleanup success in memory
                if git_config.get('store_operations_in_memory', True):
                    self.memory.add_to_conversation("system", success_msg, {
                        "tool": "git_executor",
                        "operation": "cleanup",
                        "status": "success",
                        "repo_name": repo_name
                    })
                
                return True
            
            return True  # Nothing to clean up
            
        except Exception as e:
            error_msg = error_messages.get('repo_cleanup_failed', '').format(
                repo_name=repo_name, error=str(e)
            )
            self.logger.error(error_msg)
            
            # Store cleanup failure in memory
            if git_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation("system", error_msg, {
                    "tool": "git_executor",
                    "operation": "cleanup",
                    "status": "error",
                    "repo_name": repo_name,
                    "error": str(e)
                })
            
            return False
    
    def git_clone(self, git_input: GitCloneInput) -> GitCloneOutput:
        """
        Clone git repository following our established pattern.
        
        Args:
            git_input: GitCloneInput with repository details
            
        Returns:
            GitCloneOutput with operation results
        """
        import time
        start_time = time.time()
        
        # Get configuration values
        git_config = self.config.get('git_executor', {})
        status_codes = self.config.get('status_codes', {})
        error_messages = self.config.get('error_messages', {})
        success_messages = self.config.get('success_messages', {})
        
        # Resolve workspace and repo name
        workspace = git_input.workspace or git_config.get('default_workspace', '/workspace')
        repo_name = self._extract_repo_name(git_input.repo_url)
        
        # Use target_dir if provided, otherwise use repo_name
        target_dir = git_input.target_dir or repo_name
        repo_path = git_config.get('repo_path_template', '{workspace}/{repo_name}').format(
            workspace=workspace, repo_name=target_dir
        )
        
        # Store operation start in memory
        if git_config.get('store_operations_in_memory', True):
            start_msg = success_messages.get('clone_started', '').format(repo_url=git_input.repo_url)
            self.memory.add_to_conversation("system", start_msg, {
                "tool": "git_executor",
                "operation": "clone",
                "repo_url": git_input.repo_url,
                "repo_name": repo_name,
                "workspace": workspace
            })
        
        try:
            # Validate workspace
            self._validate_workspace(workspace)
            
            # Validate repository path safety before any operations
            if git_config.get('cleanup_safety_check', True):
                try:
                    repo_path_obj = Path(repo_path)
                    workspace_path_obj = Path(workspace).resolve()
                    repo_path_obj.resolve().relative_to(workspace_path_obj)
                except ValueError:
                    # Safety violation - target path is outside workspace
                    duration = time.time() - start_time
                    error_msg = error_messages.get('cleanup_safety_violation', '').format(repo_path=repo_path)
                    self.logger.error(error_msg)
                    
                    return GitCloneOutput(
                        status=status_codes.get('error', 'ERROR'),
                        repo_path=repo_path,
                        repo_name=repo_name,
                        error_message=error_msg,
                        duration=duration,
                        workspace_used=workspace
                    )
            
            # Handle existing repository with optional auto-cleanup
            if Path(repo_path).exists():
                if git_config.get('auto_cleanup_existing_repos', True):
                    # Attempt to clean up existing repository
                    cleanup_success = self._cleanup_existing_repository(repo_path, repo_name, workspace)
                    
                    if not cleanup_success:
                        duration = time.time() - start_time
                        
                        # Check if this was a safety violation by looking at the repo path
                        try:
                            repo_path_obj = Path(repo_path)
                            workspace_path_obj = Path(workspace).resolve()
                            repo_path_obj.resolve().relative_to(workspace_path_obj)
                            # If we get here, it's not a safety violation - it's another cleanup error
                            error_msg = error_messages.get('repo_cleanup_failed', '').format(
                                repo_name=repo_name, error="Cleanup operation failed"
                            )
                        except ValueError:
                            # This is a safety violation
                            error_msg = error_messages.get('cleanup_safety_violation', '').format(repo_path=repo_path)
                        
                        self.logger.error(error_msg)
                        
                        return GitCloneOutput(
                            status=status_codes.get('error', 'ERROR'),
                            repo_path=repo_path,
                            repo_name=repo_name,
                            error_message=error_msg,
                            duration=duration,
                            workspace_used=workspace
                        )
                else:
                    # Return already exists error if auto-cleanup is disabled
                    duration = time.time() - start_time
                    error_msg = error_messages.get('repo_already_exists', '').format(repo_name=repo_name)
                    self.logger.warning(error_msg)
                    
                    # Store in memory
                    if git_config.get('store_operations_in_memory', True):
                        self.memory.add_to_conversation("system", error_msg, {
                            "tool": "git_executor",
                            "operation": "clone",
                            "status": "already_exists",
                            "error": True
                        })
                    
                    return GitCloneOutput(
                        status=status_codes.get('already_exists', 'ALREADY_EXISTS'),
                        repo_path=repo_path,
                        repo_name=repo_name,
                        error_message=error_msg,
                        duration=duration,
                        workspace_used=workspace
                    )
            
            # Build and execute git command
            git_command = self._build_git_command(git_input, workspace, repo_name)
            timeout = git_config.get('default_timeout', 300)
            
            self.logger.info(f"Executing git clone: {git_command}")
            
            # Execute command via shell executor
            shell_input = ShellExecInput(
                command=git_command,
                cwd=workspace,
                timeout=timeout
            )
            
            shell_result = self.shell_executor.shell_exec(shell_input)
            duration = time.time() - start_time
            
            # Success case
            success_msg = success_messages.get('clone_completed', '').format(
                repo_url=git_input.repo_url,
                repo_path=repo_path,
                duration=duration
            )
            self.logger.info(success_msg)
            
            # Store success in memory
            if git_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation("system", success_msg, {
                    "tool": "git_executor",
                    "operation": "clone",
                    "status": "success",
                    "repo_path": repo_path,
                    "duration": duration,
                    "command": git_command
                })
            
            return GitCloneOutput(
                status=status_codes.get('success', 'SUCCESS'),
                repo_path=repo_path,
                repo_name=repo_name,
                duration=duration,
                command_executed=git_command,
                workspace_used=workspace
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_str = str(e)
            
            # Detect authentication failures
            if self._detect_auth_failure(error_str):
                error_msg = error_messages.get('auth_failed', '').format(repo_url=git_input.repo_url)
                status = status_codes.get('auth_failed', 'AUTH_FAILED')
                self.logger.warning(f"Authentication failure detected: {error_msg}")
            elif "timed out" in error_str.lower():
                error_msg = error_messages.get('timeout_exceeded', '').format(timeout=timeout)
                status = status_codes.get('timeout', 'TIMEOUT')
                self.logger.error(f"Timeout error: {error_msg}")
            else:
                error_msg = error_messages.get('clone_failed', '').format(repo_url=git_input.repo_url)
                status = status_codes.get('error', 'ERROR')
                self.logger.error(f"Clone failed: {error_msg}. Details: {error_str}")
            
            # Store error in memory
            if git_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation("system", f"{error_msg}. Error: {error_str}", {
                    "tool": "git_executor",
                    "operation": "clone",
                    "status": status.lower(),
                    "error": True,
                    "error_details": error_str
                })
            
            return GitCloneOutput(
                status=status,
                repo_name=repo_name,
                error_message=f"{error_msg}. Details: {error_str}",
                duration=duration,
                command_executed=git_command if 'git_command' in locals() else None,
                workspace_used=workspace
            )
    
    def gh_open_issue(self, gh_input: GhOpenIssueInput) -> GhOpenIssueOutput:
        """
        Create GitHub issue using GitHub CLI following our established pattern.
        
        Args:
            gh_input: GhOpenIssueInput with issue details
            
        Returns:
            GhOpenIssueOutput with operation results
        """
        import time
        start_time = time.time()
        
        # Get configuration values
        git_config = self.config.get('git_executor', {})
        gh_config = git_config.get('github_cli', {})
        status_codes = self.config.get('status_codes', {})
        error_messages = self.config.get('error_messages', {})
        success_messages = self.config.get('success_messages', {})
        
        # Extract owner/repo from URL
        owner, repo_name = self._extract_owner_repo(gh_input.repo_url)
        
        # Store operation start in memory
        if git_config.get('store_operations_in_memory', True):
            if gh_input.issue_id is None:
                start_msg = success_messages.get('issue_creation_started',
                                               f"Starting GitHub issue creation for {owner}/{repo_name}")
            else:
                start_msg = success_messages.get('issue_comment_started',
                                               f"Adding comment to issue {gh_input.issue_id} for {owner}/{repo_name}")
            self.memory.add_to_conversation("system", start_msg, {
                "tool": "git_executor",
                "operation": "gh_open_issue",
                "repo_url": gh_input.repo_url,
                "title": gh_input.title,
                "issue_id": gh_input.issue_id,
            })
        
        try:
            # Build GitHub CLI command
            timeout = gh_config.get('default_timeout', 30)
            if gh_input.issue_id is None:
                gh_command = f"gh issue create -R {owner}/{repo_name} -t \"{gh_input.title}\" -b \"{gh_input.body}\""
            else:
                gh_command = f"gh issue comment {gh_input.issue_id} -R {owner}/{repo_name} -b \"{gh_input.body}\""
            
            # Add optional parameters when creating new issue
            if gh_input.issue_id is None:
                if gh_input.labels:
                    labels_str = ",".join(gh_input.labels)
                    gh_command += f" --label \"{labels_str}\""

                # Handle assignees - auto-assign to repository owner or Copilot if none provided
                assignees_to_use = gh_input.assignees or []
                if not assignees_to_use:
                    # Get configured Copilot assignee, fallback to "Copilot"
                    copilot_assignee = get_config_value("github.copilot_assignee", "Copilot")
                    
                    # Try to assign to configured Copilot user first, fallback to repository owner
                    try:
                        # Check if the configured Copilot user exists
                        check_copilot_cmd = f"gh api /users/{copilot_assignee}"
                        check_shell_input = ShellExecInput(command=check_copilot_cmd, timeout=10)
                        check_result = self.shell_executor.shell_exec(check_shell_input)
                        
                        if check_result.exit_code == 0:
                            assignees_to_use = [copilot_assignee]
                            self.logger.info(f"Auto-assigning issue to @{copilot_assignee}")
                        else:
                            # Fallback to repository owner
                            assignees_to_use = [owner]
                            self.logger.info(f"Auto-assigning issue to repository owner: @{owner}")
                    except Exception as e:
                        # Fallback to repository owner if check fails
                        assignees_to_use = [owner]
                        self.logger.info(f"Failed to check @{copilot_assignee}, assigning to repository owner: @{owner}. Error: {e}")
                
                if assignees_to_use:
                    assignees_str = ",".join(assignees_to_use)
                    gh_command += f" --assignee \"{assignees_str}\""

                if gh_input.milestone:
                    gh_command += f" --milestone \"{gh_input.milestone}\""
            
            self.logger.info(f"Executing GitHub CLI command: {gh_command}")
            
            # Execute command using our shell executor
            shell_input = ShellExecInput(command=gh_command, timeout=timeout)
            shell_result = self.shell_executor.shell_exec(shell_input)
            
            duration = time.time() - start_time
            
            # Parse issue URL and number from output
            issue_url = shell_result.output.strip()
            issue_number = gh_input.issue_id

            # Extract issue number when creating
            if gh_input.issue_id is None:
                import re
                match = re.search(r'/issues/(\d+)', issue_url)
                if match:
                    issue_number = int(match.group(1))
            
            # Log success
            if gh_input.issue_id is None:
                success_msg = success_messages.get('issue_created',
                                                 f"Successfully created GitHub issue #{issue_number} for {owner}/{repo_name} in {duration:.2f}s")
            else:
                success_msg = success_messages.get('comment_added',
                                                 f"Added comment to issue #{issue_number} for {owner}/{repo_name} in {duration:.2f}s")
            self.logger.info(success_msg)
            
            # Store success in memory
            if git_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation("system", success_msg, {
                    "tool": "git_executor",
                    "operation": "gh_open_issue",
                    "status": "success",
                    "issue_url": issue_url,
                    "issue_number": issue_number,
                    "duration": duration
                })
            
            return GhOpenIssueOutput(
                status=status_codes.get('gh_success', 'GH_SUCCESS'),
                issue_url=issue_url,
                issue_number=issue_number,
                repo_owner=owner,
                repo_name=repo_name,
                duration=duration,
                command_executed=gh_command
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_str = str(e)
            
            # Detect specific GitHub CLI errors
            if any(pattern in error_str.lower() for pattern in gh_config.get('auth_failure_patterns', [])):
                status = status_codes.get('gh_auth_failed', 'GH_AUTH_FAILED')
                error_msg = error_messages.get('gh_auth_failed', '').format(repo_url=gh_input.repo_url)
            elif "not found" in error_str.lower() or "repository" in error_str.lower():
                status = status_codes.get('gh_repo_not_found', 'GH_REPO_NOT_FOUND')
                error_msg = error_messages.get('gh_repo_not_found', '').format(repo_url=gh_input.repo_url)
            elif "permission" in error_str.lower() or "forbidden" in error_str.lower():
                status = status_codes.get('gh_permission_denied', 'GH_PERMISSION_DENIED')
                error_msg = error_messages.get('gh_permission_denied', '').format(repo_url=gh_input.repo_url)
            else:
                status = status_codes.get('gh_error', 'GH_ERROR')
                error_msg = error_messages.get('gh_error', '').format(repo_url=gh_input.repo_url)
            
            self.logger.error(f"GitHub issue creation failed: {error_msg}. Details: {error_str}")
            
            # Store error in memory
            if git_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation("system", f"GitHub issue creation failed: {error_msg}", {
                    "tool": "git_executor",
                    "operation": "gh_open_issue",
                    "status": "error",
                    "error": error_str,
                    "duration": duration
                })
            
            return GhOpenIssueOutput(
                status=status,
                repo_owner=owner,
                repo_name=repo_name,
                error_message=f"{error_msg}. Details: {error_str}",
                duration=duration,
                command_executed=gh_command if 'gh_command' in locals() else None
            )

    def _extract_owner_repo(self, repo_url: str) -> tuple:
        """Extract owner and repository name from GitHub URL."""
        # Handle both HTTPS and SSH URLs
        if repo_url.startswith('https://github.com/'):
            # https://github.com/owner/repo or https://github.com/owner/repo.git
            path = repo_url.replace('https://github.com/', '').rstrip('.git')
        elif repo_url.startswith('git@github.com:'):
            # git@github.com:owner/repo.git
            path = repo_url.replace('git@github.com:', '').rstrip('.git')
        else:
            raise ValueError(f"Unsupported GitHub URL format: {repo_url}")
        
        parts = path.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid GitHub repository path: {path}")
        
        return parts[0], parts[1]


# --- Global Git Executor Instance ---
_git_executor = None

def get_git_executor() -> GitExecutor:
    """Get or create the global GitExecutor instance following our pattern."""
    global _git_executor
    if _git_executor is None:
        _git_executor = GitExecutor()
    return _git_executor


# --- LangChain Tool Integration ---
@tool(args_schema=GitCloneInput)
def git_clone(repo_url: str, depth: int = None, branch: str = None, target_dir: str = None, workspace: str = None) -> str:
    """
    Clone a git repository using our comprehensive git executor.
    
    This tool provides secure git cloning with:
    - Authentication failure detection
    - Timeout protection  
    - Workspace management
    - Comprehensive logging and memory tracking
    
    Args:
        repo_url: Git repository URL to clone
        depth: Clone depth (optional, uses config default)
        branch: Specific branch to clone (optional)
        target_dir: Target directory name (optional, auto-detected from URL)
        workspace: Workspace path (optional, uses config default)
        
    Returns:
        String representation of clone results (repo path or error status)
    """
    try:
        git_input = GitCloneInput(
            repo_url=repo_url,
            depth=depth,
            branch=branch, 
            target_dir=target_dir,
            workspace=workspace
        )
        
        executor = get_git_executor()
        result = executor.git_clone(git_input)
        
        # Return simple string for LangChain tool compatibility
        if result.status == "SUCCESS":
            return result.repo_path
        elif result.status == "AUTH_FAILED":
            return "AUTH_FAILED"
        else:
            return f"ERROR: {result.error_message}"
            
    except Exception as e:
        return f"ERROR: Git clone tool error: {str(e)}"

# --- GitHub CLI Tool Integration ---
@tool(args_schema=GhOpenIssueInput)
def gh_open_issue(repo_url: str, title: str, body: str, labels: List[str] = None, assignees: List[str] = None, milestone: str = None, issue_id: int = None) -> str:
    """
    Create a GitHub issue using GitHub CLI.
    
    This tool provides secure GitHub issue creation with:
    - Authentication validation
    - Repository access verification
    - Comprehensive logging and memory tracking
    
    Args:
        repo_url: GitHub repository URL (https://github.com/owner/repo)
        title: Issue title
        body: Issue body/description
        labels: Optional list of labels to apply
        assignees: Optional list of users to assign
        milestone: Optional milestone to associate
        
    Returns:
        String representation of results (issue URL or error status)
    """
    try:
        gh_input = GhOpenIssueInput(
            repo_url=repo_url,
            title=title,
            body=body,
            labels=labels,
            assignees=assignees,
            milestone=milestone,
            issue_id=issue_id,
        )
        
        executor = get_git_executor()
        result = executor.gh_open_issue(gh_input)
        
        # Return simple string for LangChain tool compatibility
        if result.status == "GH_SUCCESS":
            return result.issue_url
        elif result.status == "GH_AUTH_FAILED":
            return "AUTH_FAILED"
        else:
            return f"ERROR: {result.error_message}"
            
    except Exception as e:
        return f"ERROR: GitHub issue tool error: {str(e)}"


# Compatibility alias for backward compatibility
GitTool = GitExecutor
