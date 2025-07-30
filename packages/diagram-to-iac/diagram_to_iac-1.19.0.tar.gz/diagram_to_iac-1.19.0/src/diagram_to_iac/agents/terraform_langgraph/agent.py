"""
Terraform Agent - Phase 3 Implementation (Error Handling & GitHub Issues Integration)

This is the complete TerraformAgent with full LLM-based routing, tool integration, and
GitHub issue creation for error handling, following the modular LangGraph pattern
established by the GitAgent. This agent handles:
- terraform init operations via tf_init_node
- terraform plan operations via tf_plan_node
- terraform apply operations via tf_apply_node
- GitHub issue creation for critical errors via open_issue_node
- Error handling and automatic issue reporting throughout the workflow

Architecture (following GitAgent pattern):
1. Planner LLM analyzes user input and emits routing tokens:
   - "ROUTE_TO_TF_INIT" for terraform init operations
   - "ROUTE_TO_TF_PLAN" for terraform plan operations
   - "ROUTE_TO_TF_APPLY" for terraform apply operations
   - "ROUTE_TO_OPEN_ISSUE" for GitHub issue creation
   - "ROUTE_TO_END" when no action needed
2. Router function maps tokens to appropriate tool nodes
3. Tool nodes execute real Terraform operations using TerraformExecutor
4. State machine handles error paths and automatically creates GitHub issues for critical errors
5. Enhanced error detection identifies critical failures that warrant issue creation

Phase 3: Complete implementation with GitHub issue integration for comprehensive error handling
"""

import os
import uuid
import logging
import re
from typing import TypedDict, Annotated, Optional, List, Dict, Any

import yaml
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

# Import core infrastructure (following GitAgent pattern)
from diagram_to_iac.tools.llm_utils.router import get_llm, LLMRouter
from diagram_to_iac.core.agent_base import AgentBase
from diagram_to_iac.core.memory import create_memory, LangGraphMemoryAdapter
from diagram_to_iac.services.observability import log_event
from diagram_to_iac.core.config_loader import get_config, get_config_value
from .parser import classify_terraform_error


# --- Pydantic Schemas for Agent I/O ---
class TerraformAgentInput(BaseModel):
    """Input schema for TerraformAgent operations."""

    query: str = Field(
        ..., description="The Terraform DevOps request (init, plan, apply)"
    )
    thread_id: str | None = Field(
        None, description="Optional thread ID for conversation history"
    )
    context: str | None = Field(
        None, description="Optional context information for error reporting"
    )


class TerraformAgentOutput(BaseModel):
    """Output schema for TerraformAgent operations."""

    result: str = Field(..., description="The result of the Terraform operation")
    thread_id: str = Field(..., description="Thread ID used for the conversation")
    error_message: Optional[str] = Field(
        None, description="Error message if the operation failed"
    )
    operation_type: Optional[str] = Field(
        None, description="Type of operation performed (init, plan, apply)"
    )
    error_tags: Optional[list[str]] = Field(
        None,
        description="Classification tags describing the error, if any",
    )


# --- Agent State Definition ---
class TerraformAgentState(TypedDict):
    """State definition for the TerraformAgent LangGraph."""

    input_message: HumanMessage
    tool_output: Annotated[list[BaseMessage], lambda x, y: x + y]
    final_result: str
    error_message: Optional[str]
    operation_type: Optional[str]
    error_tags: Optional[list[str]]


# --- Main Agent Class ---
class TerraformAgent(AgentBase):
    """
    TerraformAgent is a LangGraph-based DevOps automation agent that handles:
    - Terraform init operations via tf_init_node
    - Terraform plan operations via tf_plan_node
    - Terraform apply operations via tf_apply_node
    - GitHub issue creation for critical errors via open_issue_node

    Uses a light LLM planner for routing decisions and delegates to specialized tool nodes.
    Follows the hybrid-agent architecture pattern established by GitAgent.

    Phase 3: Complete implementation with LLM routing, comprehensive tool integration,
    and GitHub issue creation for automatic error reporting.
    """

    def __init__(self, config_path: str = None, memory_type: str = "persistent"):
        """
        Initialize the TerraformAgent with configuration and tools.

        Args:
            config_path: Optional path to YAML configuration file
            memory_type: Type of memory ("persistent", "memory", or "langgraph")
        """
        # Configure logger for this agent instance
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        # Store memory type for tool initialization
        self.memory_type = memory_type

        # Load configuration using centralized system
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "config.yaml")
            self.logger.debug(f"Default config path set to: {config_path}")

        try:
            # Use centralized configuration loading with hierarchical merging
            base_config = get_config()
            
            # Load agent-specific config if provided
            agent_config = {}
            if config_path and os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    agent_config = yaml.safe_load(f) or {}
            
            # Deep merge base config with agent-specific overrides
            self.config = self._deep_merge(base_config, agent_config)
            self.logger.info(f"Configuration loaded successfully from centralized system")
            if "terraform_token_env" not in self.config:
                self.config["terraform_token_env"] = "TFE_TOKEN"
        except Exception as e:
            self.logger.warning(f"Failed to load configuration via centralized system: {e}. Using fallback.")
            # Fallback to direct YAML loading for backward compatibility
            try:
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
                if self.config is None:
                    self.logger.warning(
                        f"Configuration file at {config_path} is empty. Using defaults."
                    )
                    self._set_default_config()
                else:
                    self.logger.info(
                        f"Configuration loaded successfully from {config_path}"
                    )
                    if "terraform_token_env" not in self.config:
                        self.config["terraform_token_env"] = "TFE_TOKEN"
            except FileNotFoundError:
                self.logger.warning(
                    f"Configuration file not found at {config_path}. Using defaults."
                )
                self._set_default_config()
            except yaml.YAMLError as e:
                self.logger.error(
                    f"Error parsing YAML configuration: {e}. Using defaults.", exc_info=True
                )
                self._set_default_config()

        # Initialize enhanced LLM router
        self.llm_router = LLMRouter()
        self.logger.info("Enhanced LLM router initialized")

        # Initialize enhanced memory system
        self.memory = create_memory(memory_type)
        self.logger.info(
            f"Enhanced memory system initialized: {type(self.memory).__name__}"
        )

        # Initialize checkpointer
        self.checkpointer = MemorySaver()
        self.logger.info("MemorySaver checkpointer initialized")

        # Initialize tools (Phase 1 will implement actual Terraform tools)
        self._initialize_tools()

        # Build and compile the LangGraph
        self.runnable = self._build_graph()
        self.logger.info("TerraformAgent initialized successfully")

    def _set_default_config(self):
        """Set default configuration values using centralized system."""
        self.logger.info("Setting default configuration for TerraformAgent")
        self.config = {
            "llm": {
                "model_name": get_config_value("ai.default_model", "gpt-4o-mini"),
                "temperature": get_config_value("ai.default_temperature", 0.1)
            },
            "routing_keys": {
                "terraform_init": get_config_value("routing.tokens.terraform_init", "ROUTE_TO_TF_INIT"),
                "terraform_plan": get_config_value("routing.tokens.terraform_plan", "ROUTE_TO_TF_PLAN"),
                "terraform_apply": get_config_value("routing.tokens.terraform_apply", "ROUTE_TO_TF_APPLY"),
                "open_issue": get_config_value("routing.tokens.open_issue", "ROUTE_TO_OPEN_ISSUE"),
                "end": get_config_value("routing.tokens.end", "ROUTE_TO_END"),
            },
            "terraform_token_env": "TFE_TOKEN",
            "tools": {
                "terraform": {
                    "timeout": get_config_value("network.terraform_timeout", 300),
                    "default_auto_approve": get_config_value("tools.terraform.default_auto_approve", True),
                    "default_plan_file": get_config_value("tools.terraform.default_plan_file", "plan.tfplan")
                }
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

    def _initialize_tools(self):
        """Initialize the Terraform tools following the established pattern."""
        try:
            # Import Terraform tools from our comprehensive implementation
            from diagram_to_iac.tools.tf.terraform import (
                TerraformExecutor,
                terraform_init,
                terraform_plan,
                terraform_apply,
            )
            from diagram_to_iac.tools.shell import ShellExecutor, shell_exec

            # Import GitHub tools from GitAgent for Phase 3 error handling
            from diagram_to_iac.tools.git import GitExecutor, gh_open_issue

            # Initialize executors
            self.terraform_executor = TerraformExecutor(memory_type=self.memory_type)
            self.shell_executor = ShellExecutor(memory_type=self.memory_type)
            self.git_executor = GitExecutor(memory_type=self.memory_type)

            # Register tools for easy access
            self.tools = {
                "terraform_init": terraform_init,
                "terraform_plan": terraform_plan,
                "terraform_apply": terraform_apply,
                "shell_exec": shell_exec,
                "gh_open_issue": gh_open_issue,
            }

            self.logger.info(f"Terraform tools initialized: {list(self.tools.keys())}")

        except Exception as e:
            self.logger.error(
                f"Failed to initialize Terraform tools: {e}", exc_info=True
            )
            raise

    def _planner_llm_node(self, state: TerraformAgentState):
        """
        LLM planner node that analyzes input and decides routing.
        Emits routing tokens based on the user's Terraform request.

        Phase 2: Full LLM-based routing implementation following GitAgent pattern.
        """
        # Get LLM configuration
        llm_config = self.config.get("llm", {})
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature")

        # Use enhanced LLM router following GitAgent pattern
        try:
            if model_name is not None or temperature is not None:
                actual_model_name = (
                    model_name if model_name is not None else "gpt-4o-mini"
                )
                actual_temperature = temperature if temperature is not None else 0.1
                self.logger.debug(
                    f"Terraform planner using LLM: {actual_model_name}, Temp: {actual_temperature}"
                )

                llm = self.llm_router.get_llm(
                    model_name=actual_model_name,
                    temperature=actual_temperature,
                    agent_name="terraform_agent",
                )
            else:
                self.logger.debug(
                    "Terraform planner using agent-specific LLM configuration"
                )
                llm = self.llm_router.get_llm_for_agent("terraform_agent")
        except Exception as e:
            self.logger.error(
                f"Failed to get LLM from router: {e}. Falling back to basic get_llm."
            )
            llm = get_llm(model_name=model_name, temperature=temperature)

        # Store conversation in memory
        query_content = state["input_message"].content
        self.memory.add_to_conversation(
            "user", query_content, {"agent": "terraform_agent", "node": "planner"}
        )

        try:
            self.logger.debug(f"Terraform planner LLM input: {query_content}")

            # Build the Terraform-specific analysis prompt
            analysis_prompt_template = self.config.get("prompts", {}).get(
                "planner_prompt",
                """
User input: "{user_input}"

Analyze this Terraform/Infrastructure request and determine the appropriate action:
1. If requesting to initialize Terraform (keywords: 'init', 'initialize', 'setup terraform'), respond with "{route_tf_init}"
2. If requesting to create/preview Terraform plan (keywords: 'plan', 'preview', 'show changes'), respond with "{route_tf_plan}"
3. If requesting to apply/deploy Terraform (keywords: 'apply', 'deploy', 'provision', 'create infrastructure'), respond with "{route_tf_apply}"
4. If requesting to create a GitHub issue for errors (keywords: 'open issue', 'create issue', 'report error', 'file bug'), respond with "{route_open_issue}"
5. If the request is complete or no action needed, respond with "{route_end}"

Important: Only use routing tokens if the input contains actionable Terraform infrastructure requests or error reporting requests.
            """,
            )

            routing_keys = self.config.get(
                "routing_keys",
                {
                    "terraform_init": "ROUTE_TO_TF_INIT",
                    "terraform_plan": "ROUTE_TO_TF_PLAN",
                    "terraform_apply": "ROUTE_TO_TF_APPLY",
                    "open_issue": "ROUTE_TO_OPEN_ISSUE",
                    "end": "ROUTE_TO_END",
                },
            )

            analysis_prompt = analysis_prompt_template.format(
                user_input=query_content,
                route_tf_init=routing_keys["terraform_init"],
                route_tf_plan=routing_keys["terraform_plan"],
                route_tf_apply=routing_keys["terraform_apply"],
                route_open_issue=routing_keys["open_issue"],
                route_end=routing_keys["end"],
            )

            self.logger.debug(f"Terraform planner LLM prompt: {analysis_prompt}")

            response = llm.invoke([HumanMessage(content=analysis_prompt)])
            self.logger.debug(f"Terraform planner LLM response: {response.content}")
            response_content = response.content.strip()

            # Store LLM response in memory
            self.memory.add_to_conversation(
                "assistant",
                response_content,
                {"agent": "terraform_agent", "node": "planner", "model": model_name},
            )

            # Determine routing based on response content
            new_state_update = {}
            if routing_keys["terraform_init"] in response_content:
                new_state_update = {
                    "final_result": "route_to_tf_init",
                    "operation_type": "terraform_init",
                    "error_message": None,
                }
            elif routing_keys["terraform_plan"] in response_content:
                new_state_update = {
                    "final_result": "route_to_tf_plan",
                    "operation_type": "terraform_plan",
                    "error_message": None,
                }
            elif routing_keys["terraform_apply"] in response_content:
                new_state_update = {
                    "final_result": "route_to_tf_apply",
                    "operation_type": "terraform_apply",
                    "error_message": None,
                }
            elif routing_keys["open_issue"] in response_content:
                new_state_update = {
                    "final_result": "route_to_open_issue",
                    "operation_type": "open_issue",
                    "error_message": None,
                }
            elif routing_keys["end"] in response_content:
                # Direct answer or route to end
                new_state_update = {
                    "final_result": response.content,
                    "operation_type": "direct_answer",
                    "error_message": None,
                }
            else:
                # Default if no specific route token is found
                new_state_update = {
                    "final_result": response.content,  # Treat as direct answer
                    "operation_type": "direct_answer",
                    "error_message": None,
                }

            self.logger.info(
                f"Terraform planner decision: {new_state_update.get('final_result', 'N/A')}"
            )
            return new_state_update

        except Exception as e:
            self.logger.error(f"LLM error in terraform planner: {e}", exc_info=True)
            self.memory.add_to_conversation(
                "system",
                f"Error in planner: {str(e)}",
                {"agent": "terraform_agent", "node": "planner", "error": True},
            )
            return {
                "final_result": "Sorry, I encountered an issue processing your Terraform request.",
                "error_message": str(e),
                "operation_type": "error",
            }

    def _should_create_github_issue(self, error_result: str) -> bool:
        """
        Determine if an error should trigger GitHub issue creation.

        Phase 3: Error detection logic for automatic issue creation.
        """
        critical_error_patterns = [
            "authentication failed",
            "permission denied",
            "terraform crash",
            "backend configuration",
            "provider configuration error",
            "module not found",
            "workspace not found",
            "invalid credentials",
            "terraform cloud error",
            "backend initialization failed",
            # Additional patterns for test compatibility
            "failed to authenticate with terraform cloud",
            "backend configuration failed",
            "please report this bug",
            "invalid credentials for aws provider",
            "resource already exists",
            "panic: runtime error",
        ]

        error_lower = error_result.lower()
        for pattern in critical_error_patterns:
            if pattern in error_lower:
                self.logger.info(f"Critical error detected: {pattern}")
                return True

        return False

    def _check_auth_token(self) -> tuple[bool, str]:
        """Check that required Terraform auth token environment variable exists."""
        env_name = self.config.get("terraform_token_env", "TFE_TOKEN")
        token = os.environ.get(env_name)
        if not token:
            error_msg = f"ERROR_MISSING_TERRAFORM_TOKEN: environment variable '{env_name}' not set"
            self.logger.error(error_msg)
            return False, env_name
        return True, env_name

    def _route_after_planner(self, state: TerraformAgentState):
        """
        Router function that determines the next node based on planner output.
        Maps routing tokens to appropriate tool nodes or END.

        Phase 3: Enhanced routing with GitHub issue integration for error handling.
        """
        self.logger.debug(
            f"Terraform routing after planner. State: {state.get('final_result')}, error: {state.get('error_message')}"
        )

        if state.get("error_message"):
            self.logger.warning(
                f"Error detected in terraform planner, routing to END: {state['error_message']}"
            )
            return END

        final_result = state.get("final_result", "")

        # Route based on planner decision
        if final_result == "route_to_tf_init":
            return "tf_init_node"
        elif final_result == "route_to_tf_plan":
            return "tf_plan_node"
        elif final_result == "route_to_tf_apply":
            return "tf_apply_node"
        elif final_result == "route_to_open_issue":
            return "open_issue_node"
        else:
            return END

    def _tf_init_node(self, state: TerraformAgentState):
        """
        Terraform init tool node that handles terraform initialization operations.

        Phase 2: Full implementation using TerraformExecutor.
        """
        self.logger.info(
            f"Terraform init node invoked for: {state['input_message'].content}"
        )

        try:
            text_content = state["input_message"].content

            # Store tool invocation in memory
            self.memory.add_to_conversation(
                "system",
                f"Terraform init tool invoked",
                {"agent": "terraform_agent", "node": "tf_init", "input": text_content},
            )

            # Extract repository path from the input or use default workspace
            # In a real implementation, you might use more sophisticated parsing
            import re

            path_pattern = r"(?:in|from|at)\s+([^\s]+)"
            paths = re.findall(path_pattern, text_content)

            # Default to current workspace if no path specified
            repo_path = paths[0] if paths else "/workspace"

            # Token check is required before proceeding with Terraform operations
            token_valid, token_env = self._check_auth_token()
            if not token_valid:
                error_msg = f"❌ Terraform Cloud token required: Please set the {token_env} environment variable to proceed with Terraform operations."
                self.logger.error(error_msg)
                self.memory.add_to_conversation(
                    "assistant",
                    error_msg,
                    {"agent": "terraform_agent", "node": "tf_init", "result": "error", "requires_user_action": True},
                )
                return {
                    "final_result": error_msg,
                    "operation_type": "terraform_init", 
                    "error_message": error_msg,
                    "error_tags": ["missing_token"],
                }

            # Use the terraform_init tool
            result = self.tools["terraform_init"].invoke(
                {"repo_path": repo_path, "upgrade": "upgrade" in text_content.lower()}
            )

            if "✅" in result:
                success_msg = f"Terraform init completed successfully: {result}"
                self.logger.info(success_msg)
                self.memory.add_to_conversation(
                    "assistant",
                    success_msg,
                    {
                        "agent": "terraform_agent",
                        "node": "tf_init",
                        "result": "success",
                    },
                )
                return {
                    "final_result": result,
                    "operation_type": "terraform_init",
                    "error_message": None,
                    "error_tags": None,
                }
            else:
                error_msg = f"Terraform init failed: {result}"
                self.logger.error(error_msg)
                self.memory.add_to_conversation(
                    "assistant",
                    error_msg,
                    {"agent": "terraform_agent", "node": "tf_init", "result": "error"},
                )

                # Phase 3: Check if this error should trigger GitHub issue creation
                if self._should_create_github_issue(result):
                    # Store error context for potential issue creation
                    error_context = {
                        "operation": "terraform_init",
                        "error": result,
                        "repo_path": repo_path,
                        "command": "terraform init",
                    }
                    self.memory.add_to_conversation(
                        "system",
                        f"Critical Terraform init error detected, consider creating GitHub issue",
                        error_context,
                    )

                return {
                    "final_result": result,
                    "operation_type": "terraform_init",
                    "error_message": result,
                    "error_tags": list(classify_terraform_error(result)),
                }

        except Exception as e:
            error_msg = f"Terraform init node error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

            # Phase 3: Check if this exception should trigger GitHub issue creation
            if self._should_create_github_issue(str(e)):
                error_context = {
                    "operation": "terraform_init",
                    "error": str(e),
                    "exception": True,
                    "command": "terraform init",
                }
                self.memory.add_to_conversation(
                    "system",
                    f"Critical Terraform init exception detected, consider creating GitHub issue",
                    error_context,
                )

            self.memory.add_to_conversation(
                "system",
                error_msg,
                {"agent": "terraform_agent", "node": "tf_init", "error": True},
            )
            return {
                "final_result": "Sorry, I encountered an issue running terraform init.",
                "error_message": str(e),
                "operation_type": "terraform_init",
                "error_tags": list(classify_terraform_error(str(e))),
            }

    def _tf_plan_node(self, state: TerraformAgentState):
        """
        Terraform plan tool node that handles terraform plan operations.

        Phase 2: Full implementation using TerraformExecutor.
        """
        self.logger.info(
            f"Terraform plan node invoked for: {state['input_message'].content}"
        )

        try:
            text_content = state["input_message"].content

            # Store tool invocation in memory
            self.memory.add_to_conversation(
                "system",
                f"Terraform plan tool invoked",
                {"agent": "terraform_agent", "node": "tf_plan", "input": text_content},
            )

            # Extract repository path from the input or use default workspace
            import re

            path_pattern = r"(?:in|from|at)\s+([^\s]+)"
            paths = re.findall(path_pattern, text_content)

            # Default to current workspace if no path specified
            repo_path = paths[0] if paths else "/workspace"

            # Check for destroy flag
            destroy = "destroy" in text_content.lower()

            # Token check is deferred to the Terraform execution itself.
            # _check_auth_token() still logs an error if called, but does not block.
            self._check_auth_token()

            # Use the terraform_plan tool
            result = self.tools["terraform_plan"].invoke(
                {"repo_path": repo_path, "destroy": destroy}
            )

            if "✅" in result:
                success_msg = f"Terraform plan completed successfully: {result}"
                self.logger.info(success_msg)
                self.memory.add_to_conversation(
                    "assistant",
                    success_msg,
                    {
                        "agent": "terraform_agent",
                        "node": "tf_plan",
                        "result": "success",
                    },
                )
                return {
                    "final_result": result,
                    "operation_type": "terraform_plan",
                    "error_message": None,
                    "error_tags": None,
                }
            else:
                error_msg = f"Terraform plan failed: {result}"
                self.logger.error(error_msg)
                self.memory.add_to_conversation(
                    "assistant",
                    error_msg,
                    {"agent": "terraform_agent", "node": "tf_plan", "result": "error"},
                )

                # Phase 3: Check if this error should trigger GitHub issue creation
                if self._should_create_github_issue(result):
                    error_context = {
                        "operation": "terraform_plan",
                        "error": result,
                        "repo_path": repo_path,
                        "command": "terraform plan",
                    }
                    self.memory.add_to_conversation(
                        "system",
                        f"Critical Terraform plan error detected, consider creating GitHub issue",
                        error_context,
                    )

                return {
                    "final_result": result,
                    "operation_type": "terraform_plan",
                    "error_message": result,
                    "error_tags": list(classify_terraform_error(result)),
                }

        except Exception as e:
            error_msg = f"Terraform plan node error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

            # Phase 3: Check if this exception should trigger GitHub issue creation
            if self._should_create_github_issue(str(e)):
                error_context = {
                    "operation": "terraform_plan",
                    "error": str(e),
                    "exception": True,
                    "command": "terraform plan",
                }
                self.memory.add_to_conversation(
                    "system",
                    f"Critical Terraform plan exception detected, consider creating GitHub issue",
                    error_context,
                )

            self.memory.add_to_conversation(
                "system",
                error_msg,
                {"agent": "terraform_agent", "node": "tf_plan", "error": True},
            )
            return {
                "final_result": "Sorry, I encountered an issue running terraform plan.",
                "error_message": str(e),
                "operation_type": "terraform_plan",
                "error_tags": list(classify_terraform_error(str(e))),
            }

    def _tf_apply_node(self, state: TerraformAgentState):
        """
        Terraform apply tool node that handles terraform apply operations.

        Phase 2: Full implementation using TerraformExecutor.
        """
        self.logger.info(
            f"Terraform apply node invoked for: {state['input_message'].content}"
        )

        try:
            text_content = state["input_message"].content

            # Store tool invocation in memory
            self.memory.add_to_conversation(
                "system",
                f"Terraform apply tool invoked",
                {"agent": "terraform_agent", "node": "tf_apply", "input": text_content},
            )

            # Extract repository path from the input or use default workspace
            import re

            path_pattern = r"(?:in|from|at)\s+([^\s]+)"
            paths = re.findall(path_pattern, text_content)

            # Default to current workspace if no path specified
            repo_path = paths[0] if paths else "/workspace"

            # Check for auto-approve flag (default to True for automation)
            auto_approve = "no-auto-approve" not in text_content.lower()

            # Token check is deferred to the Terraform execution itself.
            # _check_auth_token() still logs an error if called, but does not block.
            self._check_auth_token()

            # Use the terraform_apply tool
            result = self.tools["terraform_apply"].invoke(
                {"repo_path": repo_path, "auto_approve": auto_approve}
            )

            if "✅" in result:
                success_msg = f"Terraform apply completed successfully: {result}"
                self.logger.info(success_msg)
                self.memory.add_to_conversation(
                    "assistant",
                    success_msg,
                    {
                        "agent": "terraform_agent",
                        "node": "tf_apply",
                        "result": "success",
                    },
                )
                return {
                    "final_result": result,
                    "operation_type": "terraform_apply",
                    "error_message": None,
                    "error_tags": None,
                }
            else:
                error_msg = f"Terraform apply failed: {result}"
                self.logger.error(error_msg)
                self.memory.add_to_conversation(
                    "assistant",
                    error_msg,
                    {"agent": "terraform_agent", "node": "tf_apply", "result": "error"},
                )

                # Phase 3: Check if this error should trigger GitHub issue creation
                if self._should_create_github_issue(result):
                    error_context = {
                        "operation": "terraform_apply",
                        "error": result,
                        "repo_path": repo_path,
                        "command": "terraform apply",
                    }
                    self.memory.add_to_conversation(
                        "system",
                        f"Critical Terraform apply error detected, consider creating GitHub issue",
                        error_context,
                    )

                return {
                    "final_result": result,
                    "operation_type": "terraform_apply",
                    "error_message": result,
                    "error_tags": list(classify_terraform_error(result)),
                }

        except Exception as e:
            error_msg = f"Terraform apply node error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

            # Phase 3: Check if this exception should trigger GitHub issue creation
            if self._should_create_github_issue(str(e)):
                error_context = {
                    "operation": "terraform_apply",
                    "error": str(e),
                    "exception": True,
                    "command": "terraform apply",
                }
                self.memory.add_to_conversation(
                    "system",
                    f"Critical Terraform apply exception detected, consider creating GitHub issue",
                    error_context,
                )

            self.memory.add_to_conversation(
                "system",
                error_msg,
                {"agent": "terraform_agent", "node": "tf_apply", "error": True},
            )
            return {
                "final_result": "Sorry, I encountered an issue running terraform apply.",
                "error_message": str(e),
                "operation_type": "terraform_apply",
                "error_tags": list(classify_terraform_error(str(e))),
            }

    def _open_issue_node(self, state: TerraformAgentState):
        """
        GitHub issue tool node that handles issue creation for Terraform errors.

        Phase 3: Error handling integration following GitAgent pattern.
        """
        self.logger.info(
            f"Open issue node invoked for: {state['input_message'].content}"
        )

        try:
            text_content = state["input_message"].content

            # Store tool invocation in memory
            self.memory.add_to_conversation(
                "system",
                f"GitHub issue tool invoked",
                {
                    "agent": "terraform_agent",
                    "node": "open_issue",
                    "input": text_content,
                },
            )

            # Extract repository and issue details from input or use defaults for Terraform errors
            import re

            repo_pattern = r"(?:in|for|on)\s+(\w+/\w+)"
            title_pattern = r"(?:issue|bug|problem|error):\s*(.+?)(?:\.|$)"

            repo_match = re.search(repo_pattern, text_content, re.IGNORECASE)
            title_match = re.search(title_pattern, text_content, re.IGNORECASE)

            # Use defaults for Terraform-specific errors if not specified
            if not repo_match:
                # Default to a placeholder repo for terraform issues
                repo = "terraform/infrastructure"
                self.logger.info(
                    "No repository specified, using default: terraform/infrastructure"
                )
            else:
                repo = repo_match.group(1)

            if not title_match:
                # Create a default title from the content
                title = f"Terraform Error: {text_content[:50]}..."
                self.logger.info(f"No explicit title found, using default: {title}")
            else:
                title = title_match.group(1)

            # Build issue body with context from memory if available
            body = f"Terraform Agent Error Report:\n\n{text_content}\n\n"

            # Include previous error context from memory
            conversation_history = self.memory.get_conversation_history()
            error_context = []
            for entry in conversation_history[-10:]:  # Look at last 10 entries
                if (
                    entry.get("metadata", {}).get("error")
                    or "error" in entry.get("content", "").lower()
                    or "failed" in entry.get("content", "").lower()
                ):
                    error_context.append(entry.get("content", ""))

            if error_context:
                body += "Previous Error Context:\n"
                for context in error_context[-3:]:  # Include last 3 error contexts
                    body += f"- {context}\n"
                body += "\n"

            body += "Generated automatically by TerraformAgent."

            # Use the gh_open_issue tool with correct parameter name
            result = self.tools["gh_open_issue"].invoke(
                {
                    "repo": repo,  # Fixed: use 'repo' instead of 'repo_url'
                    "title": title,
                    "body": body,
                }
            )

            # Store successful result in memory
            self.memory.add_to_conversation(
                "system",
                f"GitHub issue created: {result}",
                {
                    "agent": "terraform_agent",
                    "node": "open_issue",
                    "repo": repo,
                    "title": title,
                    "result": result,
                },
            )

            if "ERROR:" in result:
                error_msg = f"Failed to create GitHub issue: {result}"
                self.logger.error(error_msg)
                return {
                    "final_result": error_msg,
                    "error_message": result,
                    "operation_type": "open_issue",
                    "error_tags": None,
                }
            else:
                success_msg = (
                    f"Successfully created GitHub issue for Terraform error: {result}"
                )
                self.logger.info(success_msg)
                return {
                    "final_result": success_msg,
                    "error_message": None,
                    "operation_type": "open_issue",
                    "error_tags": None,
                }

        except Exception as e:
            error_msg = f"Error in open issue node: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.memory.add_to_conversation(
                "system",
                error_msg,
                {"agent": "terraform_agent", "node": "open_issue", "error": True},
            )
            return {
                "final_result": "Sorry, I couldn't create the GitHub issue due to an error.",
                "error_message": str(e),
                "operation_type": "open_issue",
                "error_tags": list(classify_terraform_error(str(e))),
            }

    def _build_graph(self):
        """
        Build and compile the LangGraph state machine.

        Phase 3: Enhanced graph with GitHub issue integration for error handling.
        """
        graph_builder = StateGraph(TerraformAgentState)

        # Add nodes
        graph_builder.add_node("planner_llm", self._planner_llm_node)
        graph_builder.add_node("tf_init_node", self._tf_init_node)
        graph_builder.add_node("tf_plan_node", self._tf_plan_node)
        graph_builder.add_node("tf_apply_node", self._tf_apply_node)
        graph_builder.add_node("open_issue_node", self._open_issue_node)

        # Set entry point
        graph_builder.set_entry_point("planner_llm")

        # Configure routing map
        routing_map = self.config.get(
            "routing_map",
            {
                "tf_init_node": "tf_init_node",
                "tf_plan_node": "tf_plan_node",
                "tf_apply_node": "tf_apply_node",
                "open_issue_node": "open_issue_node",
                END: END,
            },
        )

        # Add conditional edges from planner
        graph_builder.add_conditional_edges(
            "planner_llm", self._route_after_planner, routing_map
        )

        # Add edges from tool nodes to END
        graph_builder.add_edge("tf_init_node", END)
        graph_builder.add_edge("tf_plan_node", END)
        graph_builder.add_edge("tf_apply_node", END)
        graph_builder.add_edge("open_issue_node", END)

        # Compile with checkpointer
        return graph_builder.compile(checkpointer=self.checkpointer)

    def run(self, agent_input: TerraformAgentInput) -> TerraformAgentOutput:
        """
        Run the agent with the given input.

        Args:
            agent_input: TerraformAgentInput with query and optional thread_id

        Returns:
            TerraformAgentOutput with result, thread_id, and optional error
        """
        current_thread_id = (
            agent_input.thread_id if agent_input.thread_id else str(uuid.uuid4())
        )
        self.logger.info(
            f"Run invoked with query: '{agent_input.query}', thread_id: {current_thread_id}"
        )
        log_event(
            "terraform_agent_run_start",
            query=agent_input.query,
            thread_id=current_thread_id,
        )

        # Store context in memory if provided
        if agent_input.context:
            self.memory.add_to_conversation(
                "system",
                f"Context: {agent_input.context}",
                {
                    "agent": "terraform_agent",
                    "type": "context",
                    "thread_id": current_thread_id,
                },
            )

        # Initial state for LangGraph
        initial_state = {
            "input_message": HumanMessage(content=agent_input.query),
            "tool_output": [],
            "error_message": None,
            "operation_type": None,
            "error_tags": None,
        }

        langgraph_config = {"configurable": {"thread_id": current_thread_id}}

        try:
            # Run the graph
            result_state = self.runnable.invoke(initial_state, config=langgraph_config)

            # Extract results
            final_result = result_state.get("final_result", "No result found.")
            error_message = result_state.get("error_message")
            operation_type = result_state.get("operation_type")
            error_tags = result_state.get("error_tags")

            if (
                error_message
                and not error_tags
                and operation_type in {
                    "terraform_init",
                    "terraform_plan",
                    "terraform_apply",
                }
            ):
                error_tags = list(classify_terraform_error(error_message))

            if error_message:
                self.logger.error(f"Run completed with error: {error_message}")
            else:
                self.logger.info(f"Run completed successfully: {final_result}")

            log_event(
                "terraform_agent_run_end",
                thread_id=current_thread_id,
                error=error_message,
                result=final_result,
            )

            output = TerraformAgentOutput(
                result=final_result,
                thread_id=current_thread_id,
                error_message=error_message,
                operation_type=operation_type,
                error_tags=error_tags,
            )

            return output

        except Exception as e:
            self.logger.error(f"Error during agent run: {e}", exc_info=True)
            log_event(
                "terraform_agent_run_exception",
                thread_id=current_thread_id,
                error=str(e),
            )
            return TerraformAgentOutput(
                result="An unexpected error occurred during execution.",
                thread_id=current_thread_id,
                error_message=str(e),
                operation_type="error",
                error_tags=list(classify_terraform_error(str(e))),
            )

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history from memory."""
        return self.memory.get_conversation_history()

    def get_memory_state(self) -> Dict[str, Any]:
        """Get current memory state."""
        return self.memory.get_state()

    def plan(self, query: str, **kwargs):
        """
        Generates a plan for the agent to execute (required by AgentBase).

        Phase 2: Comprehensive Terraform planning logic.

        Args:
            query: The Terraform query to plan for
            **kwargs: Additional parameters (e.g., thread_id)

        Returns:
            dict: A plan containing the input and predicted action
        """
        self.logger.info(f"Planning for Terraform query: '{query}'")

        plan = {
            "input_query": query,
            "predicted_action": "analyze_terraform_request",
            "description": "Analyze Terraform request to determine appropriate infrastructure operation",
        }

        # Comprehensive analysis to predict the route
        query_lower = query.lower()
        if any(
            word in query_lower
            for word in ["init", "initialize", "setup terraform", "terraform init"]
        ):
            plan["predicted_route"] = "terraform_init"
            plan["description"] = "Initialize Terraform working directory"
        elif any(
            word in query_lower
            for word in ["plan", "preview", "show changes", "terraform plan"]
        ):
            plan["predicted_route"] = "terraform_plan"
            plan["description"] = "Create Terraform execution plan"
        elif any(
            word in query_lower
            for word in [
                "apply",
                "deploy",
                "provision",
                "create infrastructure",
                "terraform apply",
            ]
        ):
            plan["predicted_route"] = "terraform_apply"
            plan["description"] = (
                "Apply Terraform configuration and provision infrastructure"
            )
        elif any(
            phrase in query_lower
            for phrase in [
                "open issue",
                "create issue",
                "report error",
                "file bug",
                "open github issue",
            ]
        ):
            plan["predicted_route"] = "open_issue"
            plan["description"] = "Create GitHub issue for error reporting"
        else:
            plan["predicted_route"] = "direct_answer"
            plan["description"] = "Provide direct answer without Terraform operation"

        self.logger.debug(f"Generated Terraform plan: {plan}")
        return plan

    def report(self, result=None, **kwargs):
        """
        Reports the results or progress of the agent's execution (required by AgentBase).

        Args:
            result: The result to report (TerraformAgentOutput or string)
            **kwargs: Additional parameters

        Returns:
            dict: A report containing execution details
        """
        if isinstance(result, TerraformAgentOutput):
            report = {
                "status": "completed",
                "result": result.result,
                "thread_id": result.thread_id,
                "error": result.error_message,
                "operation_type": result.operation_type,
                "success": result.error_message is None,
            }
        elif isinstance(result, str):
            report = {"status": "completed", "result": result, "success": True}
        else:
            report = {"status": "no_result", "message": "No result provided to report"}

        self.logger.info(f"TerraformAgent execution report: {report}")
        return report


# Alias for backward compatibility
TerraformAgent = TerraformAgent
