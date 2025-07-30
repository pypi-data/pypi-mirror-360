import os
import shlex
import subprocess
import time
import logging
import yaml
from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from diagram_to_iac.core.memory import create_memory
from diagram_to_iac.core.config_loader import get_config, get_config_value


# --- Pydantic Schemas for Tool Inputs ---
class ShellExecInput(BaseModel):
    """Input schema for shell command execution following our established pattern."""
    command: str = Field(..., description="Shell command to execute")
    cwd: Optional[str] = Field(None, description="Working directory for command execution")
    timeout: Optional[int] = Field(None, description="Timeout in seconds (overrides config default)")
    env_vars: Optional[Dict[str, str]] = Field(None, description="Additional environment variables to set")


class ShellExecOutput(BaseModel):
    """Output schema for shell command execution following our established pattern."""
    output: str = Field(..., description="Combined stdout and stderr output")
    exit_code: int = Field(..., description="Process exit code")
    command: str = Field(..., description="Executed command")
    duration: float = Field(..., description="Execution time in seconds")
    cwd: str = Field(..., description="Working directory used")
    truncated: bool = Field(False, description="Whether output was truncated")


class ShellExecutor:
    """
    ShellExecutor provides safe shell command execution following our established pattern.
    
    Features:
    - Configuration-driven security (allowed binaries, workspace restrictions)
    - Comprehensive logging with structured messages
    - Memory integration for operation tracking
    - Robust error handling with graceful fallbacks
    - Timeout protection and output size limits
    """
    
    def __init__(self, config_path: str = None, memory_type: str = "persistent"):
        """
        Initialize ShellExecutor following our established pattern.
        
        Args:
            config_path: Optional path to shell tools configuration file
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
        
        # Load configuration using centralized system with fallback to direct file loading  
        try:
            # Use centralized configuration loading
            base_config = get_config()
            shell_config = base_config.get('tools', {}).get('shell', {})
            
            # Load tool-specific config if provided
            tool_config = {}
            if config_path and os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    tool_config = yaml.safe_load(f) or {}
            
            # Merge configurations (tool config overrides base config)
            merged_config = self._deep_merge(shell_config, tool_config)
            
            if not merged_config:
                self.logger.warning("No shell configuration found in centralized system. Using defaults.")
                self._set_default_config()
            else:
                # Ensure required fields are present with defaults from centralized system
                required_fields = {
                    'default_timeout': get_config_value("network.shell_timeout", 30),
                    'workspace_base': get_config_value("system.workspace_base", '/workspace'),
                    'allow_relative_paths': get_config_value("tools.shell.allow_relative_paths", True),
                    'restrict_to_workspace': get_config_value("tools.shell.restrict_to_workspace", True),
                }
                
                # Add missing required fields
                for field, default_value in required_fields.items():
                    if field not in merged_config:
                        merged_config[field] = default_value
                
                # Ensure the config has the expected nested structure for backward compatibility
                if 'shell_executor' not in merged_config and merged_config:
                    # Wrap flat config in expected nested structure
                    self.config = {'shell_executor': merged_config}
                else:
                    self.config = merged_config
                self.logger.info("Configuration loaded from centralized system")
        except Exception as e:
            self.logger.warning(f"Failed to load from centralized config: {e}. Falling back to direct file loading.")
            # Fallback to direct file loading for backward compatibility
            if config_path is None:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                config_path = os.path.join(base_dir, 'shell_config.yaml')
                self.logger.debug(f"Default config path set to: {config_path}")
            
            try:
                with open(config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                if self.config is None:
                    self.logger.warning(f"Configuration file at {config_path} is empty. Using default values.")
                    self._set_default_config()
                else:
                    self.logger.info(f"Configuration loaded successfully from {config_path}")
            except FileNotFoundError:
                self.logger.warning(f"Configuration file not found at {config_path}. Using default values.")
                self._set_default_config()
            except yaml.YAMLError as e:
                self.logger.error(f"Error parsing YAML configuration from {config_path}: {e}. Using default values.", exc_info=True)
                self._set_default_config()
        
        # Initialize memory system following our pattern
        self.memory = create_memory(memory_type)
        self.logger.info(f"Shell executor memory system initialized: {type(self.memory).__name__}")
        
        # Log configuration summary
        shell_config = self.config.get('shell_executor', {}) or self.config  # Support both formats
        self.logger.info(f"Shell executor initialized with allowed binaries: {shell_config.get('allowed_binaries', [])}")
        self.logger.info(f"Workspace base: {shell_config.get('workspace_base', '/workspace')}")
        self.logger.info(f"Default timeout: {shell_config.get('default_timeout', 30)}s")
    
    def _set_default_config(self):
        """Set default configuration using centralized system."""
        self.logger.info("Setting default configuration for ShellExecutor.")
        self.config = {
            'shell_executor': {
                'allowed_binaries': get_config_value("tools.shell.allowed_binaries", ['git', 'bash', 'sh', 'gh', 'ls']),
                'default_timeout': get_config_value("network.shell_timeout", 30),
                'max_output_size': get_config_value("tools.shell.max_output_size", 8192),
                'workspace_base': get_config_value("system.workspace_base", '/workspace'),
                'allow_relative_paths': get_config_value("tools.shell.allow_relative_paths", True),
                'restrict_to_workspace': get_config_value("tools.shell.restrict_to_workspace", True),
                'enable_detailed_logging': get_config_value("tools.shell.enable_detailed_logging", True),
                'log_command_execution': get_config_value("tools.shell.log_command_execution", True),
                'log_output_truncation': get_config_value("tools.shell.log_output_truncation", True)
            },
            'error_messages': {
                'binary_not_allowed': "Shell executor: Binary '{binary}' is not allowed.",
                'invalid_workspace_path': "Shell executor: Path '{path}' is outside the allowed workspace.",
                'command_timeout': "Shell executor: Command timed out after {timeout} seconds.",
                'execution_failed': "Shell executor: Command failed with exit code {exit_code}.",
                'output_truncated': "Shell executor: Output truncated to {size} bytes."
            },
            'success_messages': {
                'command_executed': "Shell executor: Command completed successfully in {duration:.2f}s.",
                'output_captured': "Shell executor: Captured {size} bytes of output."
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
    
    def _validate_binary(self, command: str) -> None:
        """Validate that the command uses an allowed binary."""
        try:
            # Parse command to get the binary
            cmd_parts = shlex.split(command)
            if not cmd_parts:
                raise ValueError("Empty command provided")
            
            binary = cmd_parts[0]
            # Try both centralized config format and legacy format
            allowed_binaries = (
                self.config.get('allowed_binaries', []) or  # Centralized format
                self.config.get('shell_executor', {}).get('allowed_binaries', [])  # Legacy format
            )
            
            if binary not in allowed_binaries:
                # Try both centralized config format and legacy format for error messages
                error_messages = (
                    self.config.get('error_messages', {}) or
                    self.config.get('shell_executor', {}).get('error_messages', {})
                )
                error_msg = error_messages.get(
                    'binary_not_allowed',
                    "Shell executor: Binary '{binary}' is not in the allowed list."
                ).format(binary=binary)
                self.logger.error(f"Binary validation failed: {error_msg}")
                raise ValueError(error_msg)
            
            self.logger.debug(f"Binary validation passed: '{binary}' is allowed")
            
        except Exception as e:
            self.logger.error(f"Binary validation error: {e}")
            raise
    
    def _validate_workspace_path(self, cwd: Optional[str]) -> str:
        """Validate and resolve the working directory path."""
        shell_config = self.config.get('shell_executor', {}) or self.config  # Support both formats
        workspace_base = shell_config.get('workspace_base', '/workspace')
        
        if cwd is None:
            resolved_cwd = os.getcwd()
            self.logger.debug(f"Using current working directory: {resolved_cwd}")
        else:
            # Resolve absolute path
            resolved_cwd = os.path.abspath(cwd)
            
            # Check if path is within workspace if restriction is enabled
            if shell_config.get('restrict_to_workspace', True):
                workspace_path = os.path.abspath(workspace_base)
                try:
                    # Check if resolved_cwd is within workspace_path
                    os.path.relpath(resolved_cwd, workspace_path)
                    if not resolved_cwd.startswith(workspace_path):
                        raise ValueError()
                except ValueError:
                    error_msg = self.config.get('error_messages', {}).get(
                        'invalid_workspace_path',
                        "Shell executor: Path '{path}' is outside the allowed workspace."
                    ).format(path=resolved_cwd)
                    self.logger.error(f"Workspace validation failed: {error_msg}")
                    raise ValueError(error_msg)
            
            self.logger.debug(f"Workspace validation passed: {resolved_cwd}")
        
        return resolved_cwd
    
    def shell_exec(self, shell_input: ShellExecInput) -> ShellExecOutput:
        """
        Execute shell command with comprehensive safety checks and logging.
        
        Args:
            shell_input: Validated input containing command and execution parameters
            
        Returns:
            ShellExecOutput: Structured output with execution results
            
        Raises:
            ValueError: For validation errors (binary not allowed, invalid path)
            RuntimeError: For execution failures
        """
        start_time = time.time()
        command = shell_input.command
        
        self.logger.info(f"Shell executor invoked with command: '{command}'")
        
        # Store command invocation in memory
        self.memory.add_to_conversation(
            "system", 
            f"Shell command invoked: {command}", 
            {
                "tool": "shell_executor", 
                "command": command, 
                "cwd": shell_input.cwd,
                "timeout": shell_input.timeout
            }
        )
        
        try:
            # Validation following our pattern
            self._validate_binary(command)
            resolved_cwd = self._validate_workspace_path(shell_input.cwd)
            
            # Get timeout from input or config
            shell_config = self.config.get('shell_executor', {}) or self.config  # Support both formats
            timeout = shell_input.timeout or shell_config.get('default_timeout', 30)
            max_output_size = shell_config.get('max_output_size', 8192)
            
            self.logger.debug(f"Executing command in '{resolved_cwd}' with timeout {timeout}s")
            
            # Execute command with timeout protection
            try:
                cmd_list = shlex.split(command)
                env = os.environ.copy()
                env.update({"GIT_TERMINAL_PROMPT": "0"})
                
                # Add any additional environment variables
                if shell_input.env_vars:
                    env.update(shell_input.env_vars)
                    self.logger.debug(f"Added {len(shell_input.env_vars)} additional environment variables")

                result = subprocess.run(
                    cmd_list,
                    cwd=resolved_cwd,
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env
                )
                
                # Combine stdout and stderr
                combined_output = result.stdout + result.stderr
                
                # Truncate output if too large
                truncated = False
                if len(combined_output) > max_output_size:
                    combined_output = combined_output[-max_output_size:]
                    truncated = True
                    truncation_msg = self.config.get('error_messages', {}).get(
                        'output_truncated',
                        "Shell executor: Output truncated to {size} bytes."
                    ).format(size=max_output_size)
                    self.logger.warning(truncation_msg)
                
                duration = time.time() - start_time
                
                # Create output object
                output = ShellExecOutput(
                    output=combined_output,
                    exit_code=result.returncode,
                    command=command,
                    duration=duration,
                    cwd=resolved_cwd,
                    truncated=truncated
                )
                
                # Handle non-zero exit codes
                if result.returncode != 0:
                    error_msg = self.config.get('error_messages', {}).get(
                        'execution_failed',
                        "Shell executor: Command failed with exit code {exit_code}."
                    ).format(exit_code=result.returncode)
                    
                    self.logger.error(f"{error_msg} Output: {combined_output}")
                    
                    # Store error in memory
                    self.memory.add_to_conversation(
                        "system", 
                        f"Shell command failed: {error_msg}", 
                        {
                            "tool": "shell_executor", 
                            "command": command, 
                            "exit_code": result.returncode,
                            "error": True,
                            "output": combined_output
                        }
                    )
                    
                    raise RuntimeError(f"{error_msg}\nOutput: {combined_output}")
                
                # Log successful execution
                success_msg = self.config.get('success_messages', {}).get(
                    'command_executed',
                    "Shell executor: Command completed successfully in {duration:.2f}s."
                ).format(duration=duration)
                
                self.logger.info(success_msg)
                self.logger.debug(f"Command output ({len(combined_output)} bytes): {combined_output}")
                
                # Store successful result in memory
                self.memory.add_to_conversation(
                    "system", 
                    f"Shell command succeeded: {success_msg}", 
                    {
                        "tool": "shell_executor", 
                        "command": command, 
                        "exit_code": result.returncode,
                        "duration": duration,
                        "output_size": len(combined_output),
                        "truncated": truncated
                    }
                )
                
                return output
                
            except subprocess.TimeoutExpired:
                duration = time.time() - start_time
                timeout_msg = self.config.get('error_messages', {}).get(
                    'command_timeout',
                    "Shell executor: Command timed out after {timeout} seconds."
                ).format(timeout=timeout)
                
                self.logger.error(f"{timeout_msg} Command: {command}")
                
                # Store timeout error in memory
                self.memory.add_to_conversation(
                    "system", 
                    f"Shell command timeout: {timeout_msg}", 
                    {
                        "tool": "shell_executor", 
                        "command": command, 
                        "timeout": timeout,
                        "duration": duration,
                        "error": True
                    }
                )
                
                raise RuntimeError(timeout_msg)
                
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Shell executor error after {duration:.2f}s: {e}", exc_info=True)
            
            # Store error in memory
            self.memory.add_to_conversation(
                "system", 
                f"Shell executor error: {str(e)}", 
                {
                    "tool": "shell_executor", 
                    "command": command, 
                    "error": True,
                    "duration": duration
                }
            )
            
            raise


# Global executor instance following our pattern
_shell_executor = None

def get_shell_executor(config_path: str = None, memory_type: str = "persistent") -> ShellExecutor:
    """Get or create the global shell executor instance."""
    global _shell_executor
    if _shell_executor is None:
        _shell_executor = ShellExecutor(config_path=config_path, memory_type=memory_type)
    return _shell_executor


# --- LangChain Tool Integration ---
@tool(args_schema=ShellExecInput)
def shell_exec(command: str, cwd: str = None, timeout: int = None) -> str:
    """
    Execute shell commands safely with comprehensive logging and monitoring.
    
    This tool follows our established pattern with:
    - Configuration-driven security (allowed binaries, workspace restrictions)
    - Comprehensive logging and error handling
    - Memory integration for operation tracking
    - Timeout protection and output size limits
    
    Args:
        command: Shell command to execute
        cwd: Working directory (optional, defaults to current directory)
        timeout: Timeout in seconds (optional, uses config default)
        
    Returns:
        str: Combined stdout and stderr output
        
    Raises:
        ValueError: For validation errors (binary not allowed, invalid path)
        RuntimeError: For execution failures or timeouts
    """
    executor = get_shell_executor()
    
    shell_input = ShellExecInput(
        command=command,
        cwd=cwd,
        timeout=timeout
    )
    
    result = executor.shell_exec(shell_input)
    return result.output


# Convenience function following our pattern
def shell_exec_simple(cmd: str, cwd: str = None, timeout: int = 30) -> str:
    """
    Simple shell execution function matching the original interface.
    
    This maintains backward compatibility while using our comprehensive framework.
    """
    return shell_exec(command=cmd, cwd=cwd, timeout=timeout)
