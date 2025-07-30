"""
Terraform tools implementation following our established comprehensive pattern.

This module provides secure Terraform operations with:
- Configuration-driven behavior via ``shell_exec``
- Comprehensive logging with structured messages
- Memory integration for operation tracking
- Robust error handling with graceful fallbacks
- Integration with our ``ShellExecutor`` for safe command execution
- Pydantic schemas for type safety and validation
"""

import os
import time
import logging
import yaml
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from langchain_core.tools import tool

# Import centralized config loader
try:
    from ...core.config_loader import get_config_section, get_config_value
except ImportError:
    # Fallback for testing or when config loader is not available
    def get_config_section(section: str) -> Dict[str, Any]:
        return {}
    def get_config_value(path: str, default: Any = None) -> Any:
        return default

from diagram_to_iac.core.memory import create_memory
from diagram_to_iac.core.config_loader import get_config, get_config_value
from diagram_to_iac.tools.shell import get_shell_executor, ShellExecInput


# --- Pydantic Schemas for Terraform Operations ---
class TerraformInitInput(BaseModel):
    """Input schema for terraform init operations following our established pattern."""
    repo_path: str = Field(..., description="Path to Terraform repository/directory")
    upgrade: Optional[bool] = Field(False, description="Pass -upgrade flag to terraform init")
    backend_config: Optional[Dict[str, str]] = Field(None, description="Backend configuration parameters")
    
    @field_validator('repo_path')
    @classmethod
    def validate_repo_path(cls, v):
        """Validate that repo_path exists and is a directory."""
        if not v or not isinstance(v, str):
            raise ValueError("Repository path must be a non-empty string")
        
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Repository path does not exist: {v}")
        
        if not path.is_dir():
            raise ValueError(f"Repository path must be a directory: {v}")
        
        return str(path.absolute())


class TerraformInitOutput(BaseModel):
    """Output schema for terraform init operations following our established pattern."""
    status: str = Field(..., description="Operation status: SUCCESS, ERROR, TIMEOUT")
    error_message: Optional[str] = Field(None, description="Error details if operation failed")
    duration: float = Field(..., description="Operation duration in seconds")
    command_executed: Optional[str] = Field(None, description="Terraform command that was executed")
    repo_path: str = Field(..., description="Repository path used for operation")
    output: Optional[str] = Field(None, description="Terraform command output")


class TerraformPlanInput(BaseModel):
    """Input schema for terraform plan operations following our established pattern."""
    repo_path: str = Field(..., description="Path to Terraform repository/directory")
    out_file: Optional[str] = Field(None, description="Output file for plan (default: plan.tfplan)")
    var_file: Optional[str] = Field(None, description="Variables file to use")
    vars: Optional[Dict[str, str]] = Field(None, description="Variables to pass to terraform plan")
    destroy: Optional[bool] = Field(False, description="Create a destroy plan")
    
    @field_validator('repo_path')
    @classmethod
    def validate_repo_path(cls, v):
        """Validate that repo_path exists and is a directory."""
        if not v or not isinstance(v, str):
            raise ValueError("Repository path must be a non-empty string")
        
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Repository path does not exist: {v}")
        
        if not path.is_dir():
            raise ValueError(f"Repository path must be a directory: {v}")
        
        return str(path.absolute())


class TerraformPlanOutput(BaseModel):
    """Output schema for terraform plan operations following our established pattern."""
    status: str = Field(..., description="Operation status: SUCCESS, ERROR, TIMEOUT")
    plan_file: Optional[str] = Field(None, description="Path to generated plan file if successful")
    error_message: Optional[str] = Field(None, description="Error details if operation failed")
    duration: float = Field(..., description="Operation duration in seconds")
    command_executed: Optional[str] = Field(None, description="Terraform command that was executed")
    repo_path: str = Field(..., description="Repository path used for operation")
    output: Optional[str] = Field(None, description="Terraform command output")


class TerraformApplyInput(BaseModel):
    """Input schema for terraform apply operations following our established pattern."""
    repo_path: str = Field(..., description="Path to Terraform repository/directory")
    plan_file: Optional[str] = Field(None, description="Plan file to apply (if not provided, applies current state)")
    auto_approve: Optional[bool] = Field(True, description="Pass -auto-approve flag (default: True for automation)")
    var_file: Optional[str] = Field(None, description="Variables file to use")
    vars: Optional[Dict[str, str]] = Field(None, description="Variables to pass to terraform apply")
    
    @field_validator('repo_path')
    @classmethod
    def validate_repo_path(cls, v):
        """Validate that repo_path exists and is a directory."""
        if not v or not isinstance(v, str):
            raise ValueError("Repository path must be a non-empty string")
        
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Repository path does not exist: {v}")
        
        if not path.is_dir():
            raise ValueError(f"Repository path must be a directory: {v}")
        
        return str(path.absolute())


class TerraformApplyOutput(BaseModel):
    """Output schema for terraform apply operations following our established pattern."""
    status: str = Field(..., description="Operation status: SUCCESS, ERROR, TIMEOUT")
    error_message: Optional[str] = Field(None, description="Error details if operation failed")
    duration: float = Field(..., description="Operation duration in seconds")
    command_executed: Optional[str] = Field(None, description="Terraform command that was executed")
    repo_path: str = Field(..., description="Repository path used for operation")
    output: Optional[str] = Field(None, description="Terraform command output")


class TerraformExecutor:
    """
    TerraformExecutor provides secure Terraform operations following our established pattern.
    
    Features:
    - Configuration-driven behavior via shell_exec
    - Comprehensive logging with structured messages
    - Memory integration for operation tracking
    - Robust error handling with graceful fallbacks
    - Integration with ShellExecutor for secure command execution
    - Terraform-specific error detection and handling
    """
    
    def __init__(self, config_path: str = None, memory_type: str = "persistent"):
        """
        Initialize TerraformExecutor following our established pattern.
        
        Args:
            config_path: Optional path to terraform tools configuration file
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
        
        # Load configuration using centralized system
        try:
            # Get terraform-specific config from tools section
            tools_config = get_config_section('tools')
            terraform_config = tools_config.get('terraform', {})
            shell_config = tools_config.get('shell', {})
            
            if terraform_config or shell_config:
                # Start with default config and merge loaded config
                self._set_default_config()
                
                # Merge terraform-specific config
                if terraform_config:
                    # Update terraform-specific settings
                    for key, value in terraform_config.items():
                        if key != 'allowed_binaries':  # Handle allowed_binaries separately
                            self.config[key] = value
                
                # Merge shell executor config from shell tools section
                if shell_config:
                    shell_executor_config = self.config.get('shell_executor', {})
                    # Update allowed binaries from shell config
                    if 'allowed_binaries' in shell_config:
                        shell_executor_config['allowed_binaries'] = shell_config['allowed_binaries']
                    # Update other shell settings
                    for key, value in shell_config.items():
                        if key in ['max_output_size', 'allow_relative_paths', 'restrict_to_workspace']:
                            shell_executor_config[key] = value
                    self.config['shell_executor'] = shell_executor_config
                
                self.logger.info("Terraform configuration loaded from centralized system")
            else:
                self.logger.warning("No terraform or shell configuration found in centralized system. Using defaults.")
                self._set_default_config()
        except Exception as e:
            self.logger.warning(f"Failed to load from centralized config: {e}. Using defaults.")
            self._set_default_config()
        
        # Initialize memory system following our pattern
        self.memory = create_memory(memory_type)
        self.logger.info(f"Terraform executor memory system initialized: {type(self.memory).__name__}")
        
        # Initialize shell executor dependency
        self.shell_executor = get_shell_executor()
        self.logger.info("Terraform executor initialized with shell executor dependency")
        
        # Log configuration summary
        shell_config = self.config.get('shell_executor', {})
        self.logger.info(f"Terraform executor initialized with workspace: {shell_config.get('workspace_base', '/workspace')}")
        self.logger.info(f"Default timeout: {shell_config.get('default_timeout', 30)}s")
        self.logger.info(f"Allowed binaries: {shell_config.get('allowed_binaries', [])}")
    
    def _set_default_config(self):
        """Set default configuration using centralized system."""
        self.logger.info("Setting default configuration for TerraformExecutor.")
        self.config = {
            'shell_executor': {
                'allowed_binaries': get_config_value("tools.terraform.allowed_binaries", ['terraform', 'git', 'bash', 'sh']),
                'default_timeout': get_config_value("network.terraform_timeout", 300),  # 5 minutes for Terraform operations
                'workspace_base': get_config_value("system.workspace_base", '/workspace'),
                'restrict_to_workspace': get_config_value("tools.terraform.restrict_to_workspace", True),
                'enable_detailed_logging': get_config_value("tools.terraform.enable_detailed_logging", True)
            },
            'terraform_executor': {
                'default_plan_file': get_config_value("tools.terraform.default_plan_file", 'plan.tfplan'),
                'default_auto_approve': get_config_value("tools.terraform.default_auto_approve", True),
                'enable_detailed_logging': get_config_value("tools.terraform.enable_detailed_logging", True),
                'store_operations_in_memory': get_config_value("tools.terraform.store_operations_in_memory", True)
            },
            'error_messages': {
                'terraform_not_found': "Terraform binary not found or not allowed",
                'invalid_repo_path': "Terraform executor: Invalid repository path '{repo_path}'",
                'init_failed': "Terraform init failed",
                'plan_failed': "Terraform plan failed", 
                'apply_failed': "Terraform apply failed",
                'execution_timeout': "Terraform operation timed out after {timeout} seconds"
            },
            'success_messages': {
                'init_started': "Starting terraform init in '{repo_path}'",
                'init_completed': "Successfully completed terraform init in '{repo_path}' in {duration:.2f}s",
                'plan_started': "Starting terraform plan in '{repo_path}'",
                'plan_completed': "Successfully completed terraform plan in '{repo_path}' in {duration:.2f}s",
                'apply_started': "Starting terraform apply in '{repo_path}'",
                'apply_completed': "Successfully completed terraform apply in '{repo_path}' in {duration:.2f}s"
            },
            'status_codes': {
                'success': 'SUCCESS',
                'error': 'ERROR',
                'timeout': 'TIMEOUT'
            }
        }
    
    def _build_terraform_init_command(self, tf_input: TerraformInitInput) -> str:
        """Build terraform init command following our pattern."""
        # Start with basic init command
        cmd_parts = ['terraform', 'init']
        
        # Add upgrade flag if specified
        if tf_input.upgrade:
            cmd_parts.append('-upgrade')
        
        # Add backend config if provided
        if tf_input.backend_config:
            for key, value in tf_input.backend_config.items():
                cmd_parts.extend(['-backend-config', f'{key}={value}'])
        
        # Join command parts
        command = ' '.join(cmd_parts)
        
        self.logger.debug(f"Built terraform init command: {command}")
        return command
    
    def _build_terraform_plan_command(self, tf_input: TerraformPlanInput) -> str:
        """Build terraform plan command following our pattern."""
        terraform_config = self.config.get('terraform_executor', {})
        
        # Start with basic plan command
        cmd_parts = ['terraform', 'plan']
        
        # Determine the out_file to use (default if not provided)
        out_file = tf_input.out_file or terraform_config.get('default_plan_file', 'plan.tfplan')
        
        # Only add output file if not using remote backend
        # Remote backends (like Terraform Cloud) don't support saving plans locally
        if not self._is_remote_backend(tf_input.repo_path):
            cmd_parts.extend(['-out', out_file])
        else:
            self.logger.warning("Remote backend detected - skipping -out flag")
        
        # Add destroy flag if specified
        if tf_input.destroy:
            cmd_parts.append('-destroy')
        
        # Add var file if specified
        if tf_input.var_file:
            cmd_parts.extend(['-var-file', tf_input.var_file])
        
        # Add variables if provided
        if tf_input.vars:
            for key, value in tf_input.vars.items():
                cmd_parts.extend(['-var', f'{key}={value}'])
        
        # Join command parts
        command = ' '.join(cmd_parts)
        
        self.logger.debug(f"Built terraform plan command: {command}")
        return command

    def _is_remote_backend(self, repo_path: str) -> bool:
        """Check if the repository uses a remote backend configuration."""
        try:
            # Check for common remote backend indicators in Terraform files
            for tf_file in Path(repo_path).glob("*.tf"):
                with open(tf_file, 'r') as f:
                    content = f.read()
                    # Look for remote backend configurations
                    if any(backend in content.lower() for backend in ['backend "remote"', 'backend "cloud"', 'terraform cloud']):
                        return True
            return False
        except Exception as e:
            self.logger.debug(f"Could not check backend type: {e}")
            return False  # Default to local backend if unsure

    def _setup_terraform_credentials(self) -> Dict[str, str]:
        """Setup Terraform credentials for CLI authentication."""
        env_vars = {}
        
        # Check for TFE_TOKEN and convert to proper Terraform CLI format
        tfe_token = os.environ.get('TFE_TOKEN')
        if tfe_token:
            # Terraform CLI expects TF_TOKEN_app_terraform_io for app.terraform.io
            env_vars['TF_TOKEN_app_terraform_io'] = tfe_token
            self.logger.debug("Terraform Cloud credentials configured via TF_TOKEN_app_terraform_io")
        else:
            self.logger.warning("TFE_TOKEN not found - Terraform Cloud operations may fail")
        
        return env_vars
    
    def _build_terraform_apply_command(self, tf_input: TerraformApplyInput) -> str:
        """Build terraform apply command following our pattern."""
        terraform_config = self.config.get('terraform_executor', {})
        
        # Start with basic apply command
        cmd_parts = ['terraform', 'apply']
        
        # Add auto-approve flag (default to True for automation)
        auto_approve = tf_input.auto_approve
        if auto_approve is None:
            auto_approve = terraform_config.get('default_auto_approve', True)
        
        if auto_approve:
            cmd_parts.append('-auto-approve')
        
        # Add plan file if specified, otherwise use var file and vars
        if tf_input.plan_file:
            cmd_parts.append(tf_input.plan_file)
        else:
            # Add var file if specified
            if tf_input.var_file:
                cmd_parts.extend(['-var-file', tf_input.var_file])
            
            # Add variables if provided
            if tf_input.vars:
                for key, value in tf_input.vars.items():
                    cmd_parts.extend(['-var', f'{key}={value}'])
        
        # Join command parts
        command = ' '.join(cmd_parts)
        
        self.logger.debug(f"Built terraform apply command: {command}")
        return command
    
    def terraform_init(self, tf_input: TerraformInitInput) -> TerraformInitOutput:
        """
        Execute terraform init operation following our established pattern.
        
        Args:
            tf_input: Terraform init input parameters
            
        Returns:
            TerraformInitOutput: Result of the init operation
        """
        start_time = time.time()
        terraform_config = self.config.get('terraform_executor', {})
        
        try:
            # Log operation start
            start_msg = self.config.get('success_messages', {}).get(
                'init_started',
                "Starting terraform init in '{repo_path}'"
            ).format(repo_path=tf_input.repo_path)
            
            self.logger.info(start_msg)
            
            # Store operation start in memory
            if terraform_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation(
                    "system", 
                    start_msg, 
                    {
                        "tool": "terraform_executor", 
                        "operation": "init",
                        "repo_path": tf_input.repo_path
                    }
                )
            
            # Build terraform command
            command = self._build_terraform_init_command(tf_input)
            
            # Setup Terraform credentials
            additional_env = self._setup_terraform_credentials()
            
            # Execute command using shell executor
            shell_input = ShellExecInput(
                command=command,
                cwd=tf_input.repo_path,
                timeout=self.config.get('shell_executor', {}).get('default_timeout', 300),
                env_vars=additional_env
            )
            
            shell_result = self.shell_executor.shell_exec(shell_input)
            duration = time.time() - start_time
            
            # Log successful execution
            success_msg = self.config.get('success_messages', {}).get(
                'init_completed',
                "Successfully completed terraform init in '{repo_path}' in {duration:.2f}s"
            ).format(repo_path=tf_input.repo_path, duration=duration)
            
            self.logger.info(success_msg)
            
            # Store success in memory
            if terraform_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation(
                    "system", 
                    success_msg, 
                    {
                        "tool": "terraform_executor", 
                        "operation": "init",
                        "repo_path": tf_input.repo_path,
                        "duration": duration,
                        "command": command
                    }
                )
            
            return TerraformInitOutput(
                status=self.config.get('status_codes', {}).get('success', 'SUCCESS'),
                duration=duration,
                command_executed=command,
                repo_path=tf_input.repo_path,
                output=shell_result.output
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = self.config.get('error_messages', {}).get(
                'init_failed',
                "Terraform init failed"
            )
            
            self.logger.error(f"{error_msg}: {str(e)}")
            
            # Store error in memory
            if terraform_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation(
                    "system", 
                    f"Terraform init failed: {str(e)}", 
                    {
                        "tool": "terraform_executor", 
                        "operation": "init",
                        "repo_path": tf_input.repo_path,
                        "error": True,
                        "duration": duration
                    }
                )
            
            return TerraformInitOutput(
                status=self.config.get('status_codes', {}).get('error', 'ERROR'),
                error_message=f"{error_msg}: {str(e)}",
                duration=duration,
                command_executed=self._build_terraform_init_command(tf_input),
                repo_path=tf_input.repo_path
            )
    
    def terraform_plan(self, tf_input: TerraformPlanInput) -> TerraformPlanOutput:
        """
        Execute terraform plan operation following our established pattern.
        
        Args:
            tf_input: Terraform plan input parameters
            
        Returns:
            TerraformPlanOutput: Result of the plan operation
        """
        start_time = time.time()
        terraform_config = self.config.get('terraform_executor', {})
        
        try:
            # Log operation start
            start_msg = self.config.get('success_messages', {}).get(
                'plan_started',
                "Starting terraform plan in '{repo_path}'"
            ).format(repo_path=tf_input.repo_path)
            
            self.logger.info(start_msg)
            
            # Store operation start in memory
            if terraform_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation(
                    "system", 
                    start_msg, 
                    {
                        "tool": "terraform_executor", 
                        "operation": "plan",
                        "repo_path": tf_input.repo_path
                    }
                )
            
            # Build terraform command
            command = self._build_terraform_plan_command(tf_input)
            
            # Setup Terraform credentials
            additional_env = self._setup_terraform_credentials()
            
            # Execute command using shell executor
            shell_input = ShellExecInput(
                command=command,
                cwd=tf_input.repo_path,
                timeout=self.config.get('shell_executor', {}).get('default_timeout', 300),
                env_vars=additional_env
            )
            
            shell_result = self.shell_executor.shell_exec(shell_input)
            duration = time.time() - start_time
            
            # Determine plan file path
            out_file = tf_input.out_file or terraform_config.get('default_plan_file', 'plan.tfplan')
            plan_file_path = os.path.join(tf_input.repo_path, out_file)
            
            # Log successful execution
            success_msg = self.config.get('success_messages', {}).get(
                'plan_completed',
                "Successfully completed terraform plan in '{repo_path}' in {duration:.2f}s"
            ).format(repo_path=tf_input.repo_path, duration=duration)
            
            self.logger.info(success_msg)
            
            # Store success in memory
            if terraform_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation(
                    "system", 
                    success_msg, 
                    {
                        "tool": "terraform_executor", 
                        "operation": "plan",
                        "repo_path": tf_input.repo_path,
                        "duration": duration,
                        "command": command,
                        "plan_file": plan_file_path
                    }
                )
            
            return TerraformPlanOutput(
                status=self.config.get('status_codes', {}).get('success', 'SUCCESS'),
                plan_file=plan_file_path,
                duration=duration,
                command_executed=command,
                repo_path=tf_input.repo_path,
                output=shell_result.output
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = self.config.get('error_messages', {}).get(
                'plan_failed',
                "Terraform plan failed"
            )
            
            self.logger.error(f"{error_msg}: {str(e)}")
            
            # Store error in memory
            if terraform_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation(
                    "system", 
                    f"Terraform plan failed: {str(e)}", 
                    {
                        "tool": "terraform_executor", 
                        "operation": "plan",
                        "repo_path": tf_input.repo_path,
                        "error": True,
                        "duration": duration
                    }
                )
            
            return TerraformPlanOutput(
                status=self.config.get('status_codes', {}).get('error', 'ERROR'),
                error_message=f"{error_msg}: {str(e)}",
                duration=duration,
                command_executed=self._build_terraform_plan_command(tf_input),
                repo_path=tf_input.repo_path
            )
    
    def terraform_apply(self, tf_input: TerraformApplyInput) -> TerraformApplyOutput:
        """
        Execute terraform apply operation following our established pattern.
        
        Args:
            tf_input: Terraform apply input parameters
            
        Returns:
            TerraformApplyOutput: Result of the apply operation
        """
        start_time = time.time()
        terraform_config = self.config.get('terraform_executor', {})
        
        try:
            # Log operation start
            start_msg = self.config.get('success_messages', {}).get(
                'apply_started',
                "Starting terraform apply in '{repo_path}'"
            ).format(repo_path=tf_input.repo_path)
            
            self.logger.info(start_msg)
            
            # Store operation start in memory
            if terraform_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation(
                    "system", 
                    start_msg, 
                    {
                        "tool": "terraform_executor", 
                        "operation": "apply",
                        "repo_path": tf_input.repo_path
                    }
                )
            
            # Build terraform command
            command = self._build_terraform_apply_command(tf_input)
            
            # Setup Terraform credentials
            additional_env = self._setup_terraform_credentials()
            
            # Execute command using shell executor
            shell_input = ShellExecInput(
                command=command,
                cwd=tf_input.repo_path,
                timeout=self.config.get('shell_executor', {}).get('default_timeout', 300),
                env_vars=additional_env
            )
            
            shell_result = self.shell_executor.shell_exec(shell_input)
            duration = time.time() - start_time
            
            # Log successful execution
            success_msg = self.config.get('success_messages', {}).get(
                'apply_completed',
                "Successfully completed terraform apply in '{repo_path}' in {duration:.2f}s"
            ).format(repo_path=tf_input.repo_path, duration=duration)
            
            self.logger.info(success_msg)
            
            # Store success in memory
            if terraform_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation(
                    "system", 
                    success_msg, 
                    {
                        "tool": "terraform_executor", 
                        "operation": "apply",
                        "repo_path": tf_input.repo_path,
                        "duration": duration,
                        "command": command
                    }
                )
            
            return TerraformApplyOutput(
                status=self.config.get('status_codes', {}).get('success', 'SUCCESS'),
                duration=duration,
                command_executed=command,
                repo_path=tf_input.repo_path,
                output=shell_result.output
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = self.config.get('error_messages', {}).get(
                'apply_failed',
                "Terraform apply failed"
            )
            
            self.logger.error(f"{error_msg}: {str(e)}")
            
            # Store error in memory
            if terraform_config.get('store_operations_in_memory', True):
                self.memory.add_to_conversation(
                    "system", 
                    f"Terraform apply failed: {str(e)}", 
                    {
                        "tool": "terraform_executor", 
                        "operation": "apply",
                        "repo_path": tf_input.repo_path,
                        "error": True,
                        "duration": duration
                    }
                )
            
            return TerraformApplyOutput(
                status=self.config.get('status_codes', {}).get('error', 'ERROR'),
                error_message=f"{error_msg}: {str(e)}",
                duration=duration,
                command_executed=self._build_terraform_apply_command(tf_input),
                repo_path=tf_input.repo_path
            )


# Global executor instance following our pattern
_terraform_executor = None

def get_terraform_executor(config_path: str = None, memory_type: str = "persistent") -> TerraformExecutor:
    """Get or create the global terraform executor instance."""
    global _terraform_executor
    if _terraform_executor is None:
        _terraform_executor = TerraformExecutor(config_path=config_path, memory_type=memory_type)
    return _terraform_executor


# --- LangChain Tool Integration ---
@tool(args_schema=TerraformInitInput)
def terraform_init(repo_path: str, upgrade: bool = False, backend_config: Dict[str, str] = None) -> str:
    """
    Initialize a Terraform repository following our established pattern.
    
    Args:
        repo_path: Path to Terraform repository/directory
        upgrade: Pass -upgrade flag to terraform init
        backend_config: Backend configuration parameters
        
    Returns:
        String description of the operation result
    """
    try:
        executor = get_terraform_executor()
        tf_input = TerraformInitInput(
            repo_path=repo_path,
            upgrade=upgrade,
            backend_config=backend_config
        )
        result = executor.terraform_init(tf_input)
        
        if result.status == "SUCCESS":
            return f"✅ Terraform init completed successfully in {result.duration:.2f}s"
        else:
            return f"❌ Terraform init failed: {result.error_message}"
            
    except Exception as e:
        return f"❌ Terraform init error: {str(e)}"


@tool(args_schema=TerraformPlanInput)
def terraform_plan(repo_path: str, out_file: str = None, var_file: str = None, 
                   vars: Dict[str, str] = None, destroy: bool = False) -> str:
    """
    Create a Terraform execution plan following our established pattern.
    
    Args:
        repo_path: Path to Terraform repository/directory
        out_file: Output file for plan (default: plan.tfplan)
        var_file: Variables file to use
        vars: Variables to pass to terraform plan
        destroy: Create a destroy plan
        
    Returns:
        String description of the operation result
    """
    try:
        executor = get_terraform_executor()
        tf_input = TerraformPlanInput(
            repo_path=repo_path,
            out_file=out_file,
            var_file=var_file,
            vars=vars,
            destroy=destroy
        )
        result = executor.terraform_plan(tf_input)
        
        if result.status == "SUCCESS":
            return f"✅ Terraform plan completed successfully in {result.duration:.2f}s. Plan saved to: {result.plan_file}"
        else:
            return f"❌ Terraform plan failed: {result.error_message}"
            
    except Exception as e:
        return f"❌ Terraform plan error: {str(e)}"


@tool(args_schema=TerraformApplyInput)
def terraform_apply(repo_path: str, plan_file: str = None, auto_approve: bool = True,
                    var_file: str = None, vars: Dict[str, str] = None) -> str:
    """
    Apply a Terraform execution plan following our established pattern.
    
    Args:
        repo_path: Path to Terraform repository/directory
        plan_file: Plan file to apply (if not provided, applies current state)
        auto_approve: Pass -auto-approve flag (default: True for automation)
        var_file: Variables file to use
        vars: Variables to pass to terraform apply
        
    Returns:
        String description of the operation result
    """
    try:
        executor = get_terraform_executor()
        tf_input = TerraformApplyInput(
            repo_path=repo_path,
            plan_file=plan_file,
            auto_approve=auto_approve,
            var_file=var_file,
            vars=vars
        )
        result = executor.terraform_apply(tf_input)
        
        if result.status == "SUCCESS":
            return f"✅ Terraform apply completed successfully in {result.duration:.2f}s"
        else:
            return f"❌ Terraform apply failed: {result.error_message}"
            
    except Exception as e:
        return f"❌ Terraform apply error: {str(e)}"


# Convenience functions following our pattern
def terraform_init_simple(repo_path: str, upgrade: bool = False) -> TerraformInitOutput:
    """
    Simple terraform init function matching the original interface.
    
    This maintains backward compatibility while using our comprehensive framework.
    """
    executor = get_terraform_executor()
    tf_input = TerraformInitInput(repo_path=repo_path, upgrade=upgrade)
    return executor.terraform_init(tf_input)


def terraform_plan_simple(repo_path: str, out_file: str = None) -> TerraformPlanOutput:
    """
    Simple terraform plan function matching the original interface.
    
    This maintains backward compatibility while using our comprehensive framework.
    """
    executor = get_terraform_executor()
    tf_input = TerraformPlanInput(repo_path=repo_path, out_file=out_file)
    return executor.terraform_plan(tf_input)


def terraform_apply_simple(repo_path: str, plan_file: str = None, auto_approve: bool = True) -> TerraformApplyOutput:
    """
    Simple terraform apply function matching the original interface.
    
    This maintains backward compatibility while using our comprehensive framework.
    """
    executor = get_terraform_executor()
    tf_input = TerraformApplyInput(repo_path=repo_path, plan_file=plan_file, auto_approve=auto_approve)
    return executor.terraform_apply(tf_input)
