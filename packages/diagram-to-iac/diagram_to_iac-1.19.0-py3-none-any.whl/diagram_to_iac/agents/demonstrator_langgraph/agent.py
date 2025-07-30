"""
DemonstratorAgent: Intelligent Interactive Dry-Run Agent

This agent specializes in demonstrating errors, analyzing fixes, and guiding users
through interactive problem-solving in an organic, agentic way.

Follows the same organic LangGraph pattern as other agents in the system.
"""

import os
import re
import yaml
import uuid
import logging
import getpass
from datetime import datetime
from typing import Dict, List, Optional, Union, TypedDict, Any

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from diagram_to_iac.core.agent_base import AgentBase
from diagram_to_iac.core.memory import create_memory
from diagram_to_iac.core.config_loader import get_config, get_config_value
from diagram_to_iac.tools.llm_utils.router import LLMRouter, get_llm
from diagram_to_iac.tools.text_utils import (
    generate_organic_issue_title,
    enhance_error_message_for_issue,
    create_issue_metadata_section,
)

# Import the agents we need to delegate to
from diagram_to_iac.agents.git_langgraph import GitAgent, GitAgentInput
from diagram_to_iac.agents.terraform_langgraph import TerraformAgent, TerraformAgentInput


class DemonstratorAgentInput(TypedDict):
    """Input structure for DemonstratorAgent."""
    
    query: str  # The demonstration request
    error_type: str  # Type of error to demonstrate
    error_message: str  # Original error message
    repo_url: str  # Repository URL
    branch_name: Optional[str]  # Branch name
    stack_detected: Optional[Dict[str, int]]  # Detected stack info
    issue_title: str  # Proposed issue title
    issue_body: str  # Proposed issue body
    existing_issue_id: Optional[int]  # Existing issue ID if any
    thread_id: Optional[str]  # Thread ID for conversation continuity


class DemonstratorAgentOutput(TypedDict):
    """Output structure for DemonstratorAgent."""
    
    result: str  # Demonstration result
    action_taken: str  # What action was taken
    user_choice: str  # User's choice during demonstration
    retry_attempted: bool  # Whether a retry was attempted
    retry_successful: Optional[bool]  # Whether retry succeeded
    issue_created: bool  # Whether an issue was created
    error_message: Optional[str]  # Any error during demonstration
    thread_id: str  # Thread ID


class DemonstratorAgentState(TypedDict):
    """State structure for DemonstratorAgent LangGraph."""
    
    input_message: HumanMessage
    query: str
    error_type: str
    error_message: str
    repo_url: str
    branch_name: Optional[str]
    stack_detected: Optional[Dict[str, int]]
    issue_title: str
    issue_body: str
    existing_issue_id: Optional[int]
    thread_id: Optional[str]
    
    # State tracking
    error_analysis: Optional[Dict[str, Any]]
    user_choice: Optional[str]
    user_inputs: Optional[Dict[str, str]]
    retry_attempted: bool
    retry_successful: Optional[bool]
    issue_created: bool
    final_result: str
    operation_type: str
    error_occurred: Optional[str]


class DemonstratorAgent(AgentBase):
    """
    DemonstratorAgent specializes in interactive dry-run demonstrations.
    
    Uses organic LangGraph architecture to:
    1. Analyze errors intelligently
    2. Guide users through fixing problems
    3. Demonstrate potential solutions
    4. Handle retries with user-provided fixes
    5. Create GitHub issues when needed
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        memory_type: str = "persistent",
        git_agent: Optional[GitAgent] = None,
        terraform_agent: Optional[TerraformAgent] = None,
    ) -> None:
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Load configuration using centralized system
        try:
            # Get demonstrator-specific config from agents section  
            agents_config = get_config_value('agents', {})
            demonstrator_config = agents_config.get('demonstrator', {})
            
            if demonstrator_config:
                # Start with default config and merge loaded config
                self._set_default_config()
                
                # Merge demonstrator-specific config
                for key, value in demonstrator_config.items():
                    if isinstance(value, dict) and key in self.config and isinstance(self.config[key], dict):
                        self.config[key].update(value)
                    else:
                        self.config[key] = value
                
                self.logger.info("Demonstrator configuration loaded from centralized system")
            else:
                self.logger.info("No demonstrator configuration found in centralized system. Using defaults.")
                self._set_default_config()
        except Exception as e:
            self.logger.warning(f"Failed to load from centralized config: {e}. Using defaults.")
            self._set_default_config()

        # Initialize enhanced LLM router
        self.llm_router = LLMRouter()
        self.logger.info("Enhanced LLM router initialized")

        # Initialize enhanced memory system
        self.memory = create_memory(memory_type)
        self.logger.info(f"Enhanced memory system initialized: {type(self.memory).__name__}")

        # Initialize checkpointer
        self.checkpointer = MemorySaver()
        self.logger.info("MemorySaver checkpointer initialized")

        # Initialize delegate agents
        self.git_agent = git_agent or GitAgent()
        self.terraform_agent = terraform_agent or TerraformAgent()
        self.logger.info("Delegate agents initialized")

        # Build and compile the LangGraph
        self.runnable = self._build_graph()
        self.logger.info("DemonstratorAgent initialized successfully with organic LangGraph architecture")

    def _set_default_config(self):
        """Set default configuration values using centralized system."""
        self.config = {
            "llm": {
                "model_name": get_config_value("ai.default_model", "gpt-4o-mini"), 
                "temperature": get_config_value("ai.default_temperature", 0.1)
            },
            "routing_keys": {
                "analyze": get_config_value("routing.tokens.analyze", "ROUTE_TO_ANALYZE"),
                "demonstrate": get_config_value("routing.tokens.demonstrate", "ROUTE_TO_DEMONSTRATE"), 
                "collect_inputs": get_config_value("routing.tokens.collect_inputs", "ROUTE_TO_COLLECT_INPUTS"),
                "retry": get_config_value("routing.tokens.retry", "ROUTE_TO_RETRY"),
                "create_issue": get_config_value("routing.tokens.create_issue", "ROUTE_TO_CREATE_ISSUE"),
                "end": get_config_value("routing.tokens.end", "ROUTE_TO_END"),
            },
            "prompts": {
                "planner_prompt": """User request: "{user_input}"

This is a dry-run demonstration request for error: {error_type}
Error message: {error_message}

Analyze this request and determine the appropriate action:
1. If need to analyze the error for user guidance, respond with "{route_analyze}"
2. If need to demonstrate the issue to user, respond with "{route_demonstrate}"
3. If need to collect user inputs for fixing, respond with "{route_collect_inputs}"
4. If need to retry with new information, respond with "{route_retry}"
5. If need to create GitHub issue, respond with "{route_create_issue}"
6. If demonstration is complete, respond with "{route_end}"

Important: Focus on being helpful and educational in demonstrating the error and potential fixes."""
            },
        }
        self.logger.info("Default configuration set")

    # --- AgentBase interface ---
    
    def plan(self, query: str, **kwargs):
        """Generate a plan for the demonstration (required by AgentBase)."""
        return {
            "input_query": query,
            "predicted_action": "interactive_demonstration",
            "description": "Demonstrate error and guide user through fixing it",
        }

    def report(self, *args, **kwargs):
        """Get current memory state (required by AgentBase)."""
        return self.get_memory_state()

    def run(self, demo_input: DemonstratorAgentInput) -> DemonstratorAgentOutput:
        """
        Run the DemonstratorAgent with organic LangGraph execution.
        """
        self.logger.info(f"DemonstratorAgent run invoked for error type: '{demo_input['error_type']}'")

        if not self.runnable:
            error_msg = "DemonstratorAgent runnable not initialized"
            self.logger.error(error_msg)
            return DemonstratorAgentOutput(
                result=f"Error: {error_msg}",
                action_taken="error",
                user_choice="none",
                retry_attempted=False,
                retry_successful=None,
                issue_created=False,
                error_message=error_msg,
                thread_id=demo_input.get("thread_id", str(uuid.uuid4())),
            )

        try:
            # Create initial state
            initial_state: DemonstratorAgentState = {
                "input_message": HumanMessage(content=demo_input["query"]),
                "query": demo_input["query"],
                "error_type": demo_input["error_type"],
                "error_message": demo_input["error_message"],
                "repo_url": demo_input["repo_url"],
                "branch_name": demo_input.get("branch_name"),
                "stack_detected": demo_input.get("stack_detected"),
                "issue_title": demo_input["issue_title"],
                "issue_body": demo_input["issue_body"],
                "existing_issue_id": demo_input.get("existing_issue_id"),
                "thread_id": demo_input.get("thread_id", str(uuid.uuid4())),
                "error_analysis": None,
                "user_choice": None,
                "user_inputs": None,
                "retry_attempted": False,
                "retry_successful": None,
                "issue_created": False,
                "final_result": "",
                "operation_type": "",
                "error_occurred": None,
            }

            # Execute the organic LangGraph workflow
            config = {"configurable": {"thread_id": initial_state["thread_id"]}}
            final_state = self.runnable.invoke(initial_state, config=config)

            # Convert final state to output
            return DemonstratorAgentOutput(
                result=final_state.get("final_result", "Demonstration completed"),
                action_taken=final_state.get("operation_type", "unknown"),
                user_choice=final_state.get("user_choice", "none"),
                retry_attempted=final_state.get("retry_attempted", False),
                retry_successful=final_state.get("retry_successful"),
                issue_created=final_state.get("issue_created", False),
                error_message=final_state.get("error_occurred"),
                thread_id=final_state["thread_id"],
            )

        except Exception as e:
            self.logger.error(f"Error in DemonstratorAgent run: {e}", exc_info=True)
            return DemonstratorAgentOutput(
                result=f"Demonstration failed: {str(e)}",
                action_taken="error",
                user_choice="none",
                retry_attempted=False,
                retry_successful=None,
                issue_created=False,
                error_message=str(e),
                thread_id=demo_input.get("thread_id", str(uuid.uuid4())),
            )

    # --- Organic LangGraph Architecture ---

    def _build_graph(self) -> StateGraph:
        """Build the organic LangGraph for DemonstratorAgent."""
        graph = StateGraph(DemonstratorAgentState)

        # Add nodes
        graph.add_node("planner_node", self._planner_node)
        graph.add_node("analyze_error_node", self._analyze_error_node)
        graph.add_node("demonstrate_issue_node", self._demonstrate_issue_node)
        graph.add_node("collect_inputs_node", self._collect_inputs_node)
        graph.add_node("retry_operation_node", self._retry_operation_node)
        graph.add_node("create_issue_node", self._create_issue_node)

        # Set entry point
        graph.set_entry_point("planner_node")

        # Add routing
        graph.add_conditional_edges("planner_node", self._route_after_planner)
        graph.add_conditional_edges("analyze_error_node", self._route_after_analysis)
        graph.add_conditional_edges("demonstrate_issue_node", self._route_after_demonstration)
        graph.add_conditional_edges("collect_inputs_node", self._route_after_collection)
        graph.add_conditional_edges("retry_operation_node", self._route_after_retry)
        graph.add_edge("create_issue_node", END)

        return graph.compile(checkpointer=self.checkpointer)

    def _planner_node(self, state: DemonstratorAgentState) -> DemonstratorAgentState:
        """LLM planner node for demonstration workflow."""
        self.logger.info("DemonstratorAgent planner analyzing demonstration request")

        # Get LLM
        llm_config = self.config.get("llm", {})
        try:
            llm = self.llm_router.get_llm(
                model_name=llm_config.get("model_name", "gpt-4o-mini"),
                temperature=llm_config.get("temperature", 0.1),
                agent_name="demonstrator_agent",
            )
        except Exception as e:
            self.logger.error(f"Failed to get LLM: {e}")
            llm = get_llm()

        # Store conversation in memory
        self.memory.add_to_conversation(
            "user", state["query"], {"agent": "demonstrator_agent", "node": "planner"}
        )

        try:
            # Build analysis prompt
            routing_keys = self.config.get("routing_keys", {})
            prompt_template = self.config.get("prompts", {}).get("planner_prompt", "")
            
            analysis_prompt = prompt_template.format(
                user_input=state["query"],
                error_type=state["error_type"],
                error_message=state["error_message"],
                route_analyze=routing_keys.get("analyze", "ROUTE_TO_ANALYZE"),
                route_demonstrate=routing_keys.get("demonstrate", "ROUTE_TO_DEMONSTRATE"),
                route_collect_inputs=routing_keys.get("collect_inputs", "ROUTE_TO_COLLECT_INPUTS"),
                route_retry=routing_keys.get("retry", "ROUTE_TO_RETRY"),
                route_create_issue=routing_keys.get("create_issue", "ROUTE_TO_CREATE_ISSUE"),
                route_end=routing_keys.get("end", "ROUTE_TO_END"),
            )

            response = llm.invoke([HumanMessage(content=analysis_prompt)])
            response_content = response.content.strip()

            # Store LLM response
            self.memory.add_to_conversation(
                "assistant", response_content, 
                {"agent": "demonstrator_agent", "node": "planner"}
            )

            # Determine routing
            if routing_keys.get("analyze", "ROUTE_TO_ANALYZE") in response_content:
                next_action = "analyze_error"
            elif routing_keys.get("demonstrate", "ROUTE_TO_DEMONSTRATE") in response_content:
                next_action = "demonstrate_issue"
            elif routing_keys.get("collect_inputs", "ROUTE_TO_COLLECT_INPUTS") in response_content:
                next_action = "collect_inputs"
            elif routing_keys.get("retry", "ROUTE_TO_RETRY") in response_content:
                next_action = "retry_operation"
            elif routing_keys.get("create_issue", "ROUTE_TO_CREATE_ISSUE") in response_content:
                next_action = "create_issue"
            else:
                next_action = "analyze_error"  # Default: start with analysis

            self.logger.info(f"DemonstratorAgent planner decision: {next_action}")

            return {
                **state,
                "final_result": next_action,
                "operation_type": "planning",
            }

        except Exception as e:
            self.logger.error(f"Error in demonstrator planner: {e}")
            return {
                **state,
                "final_result": "create_issue",
                "operation_type": "planner_error",
                "error_occurred": str(e),
            }

    def _analyze_error_node(self, state: DemonstratorAgentState) -> DemonstratorAgentState:
        """Analyze the error and provide intelligent guidance."""
        self.logger.info(f"Analyzing error type: {state['error_type']}")

        try:
            # Analyze the error for fixability and guidance
            error_analysis = self._get_error_analysis(state["error_type"], state["error_message"])
            
            self.logger.info(f"Error analysis complete: fixable={error_analysis['fixable']}")

            return {
                **state,
                "error_analysis": error_analysis,
                "final_result": "demonstrate_issue",
                "operation_type": "analysis_complete",
            }

        except Exception as e:
            self.logger.error(f"Error in analysis node: {e}")
            return {
                **state,
                "final_result": "create_issue",
                "operation_type": "analysis_error",
                "error_occurred": str(e),
            }

    def _demonstrate_issue_node(self, state: DemonstratorAgentState) -> DemonstratorAgentState:
        """Demonstrate the issue to the user interactively."""
        self.logger.info("Demonstrating issue to user")

        try:
            error_analysis = state.get("error_analysis") or self._get_error_analysis(
                state["error_type"], state["error_message"]
            )

            # Display the demonstration
            print("\n" + "="*80)
            print("🔍 INTELLIGENT DRY RUN: R2D Workflow Error Analysis")
            print("="*80)
            
            print(f"\n📍 **Repository:** {state['repo_url']}")
            print(f"🏷️  **Error Type:** {state['error_type']}")
            if state.get("existing_issue_id"):
                print(f"🔗 **Existing Issue:** Found issue #{state['existing_issue_id']} (would update)")
            else:
                print(f"🆕 **New Issue:** Would create new issue")
            
            print(f"\n🧠 **Error Analysis:**")
            print(f"   {error_analysis['description']}")
            
            if error_analysis['fixable']:
                print(f"\n✅ **Good News:** This error can potentially be fixed!")
                print(f"   {error_analysis['fix_guidance']}")
                
                if error_analysis['required_inputs']:
                    print(f"\n📝 **Required Information:**")
                    for req in error_analysis['required_inputs']:
                        print(f"   • {req}")
            else:
                print(f"\n❌ **This error requires manual intervention:**")
                print(f"   {error_analysis['manual_steps']}")
            
            print(f"\n📝 **Proposed Issue Title:**")
            print(f"   {state['issue_title']}")
            
            print("\n" + "="*80)
            print("🤔 What would you like to do?")
            print("="*80)
            
            if error_analysis['fixable']:
                print("1. 🔧 Fix - Provide missing information and retry")
                print("2. 🚀 Create Issue - Log this error as a GitHub issue")
                print("3. 📋 Details - Show full error details and proposed issue")
                print("4. ❌ Abort - Skip and end workflow")
                max_choice = 4
            else:
                print("1. 🚀 Create Issue - Log this error as a GitHub issue")
                print("2. 📋 Details - Show full error details and proposed issue")
                print("3. ❌ Abort - Skip and end workflow")
                max_choice = 3

            # Get user choice
            choice = self._get_user_choice(max_choice, error_analysis['fixable'])
            
            return {
                **state,
                "error_analysis": error_analysis,
                "user_choice": choice,
                "final_result": self._map_choice_to_action(choice, error_analysis['fixable']),
                "operation_type": "demonstration_complete",
            }

        except Exception as e:
            self.logger.error(f"Error in demonstration node: {e}")
            return {
                **state,
                "final_result": "create_issue",
                "operation_type": "demonstration_error",
                "error_occurred": str(e),
            }

    def _collect_inputs_node(self, state: DemonstratorAgentState) -> DemonstratorAgentState:
        """Collect required inputs from user for fixing the error."""
        self.logger.info("Collecting user inputs for error fix")

        try:
            error_analysis = state["error_analysis"]
            
            print(f"\n🛠️  **Error Fix Mode: {state['error_type']}**")
            print(f"📋 {error_analysis['fix_guidance']}")
            
            # Collect required inputs from user
            user_inputs = {}
            for requirement in error_analysis['required_inputs']:
                key = requirement.split(':')[0].strip()
                description = requirement.split(':', 1)[1].strip() if ':' in requirement else requirement
                
                print(f"\n📝 **{key}:**")
                print(f"   {description}")
                
                # Handle sensitive inputs differently
                if any(sensitive in key.lower() for sensitive in ['token', 'key', 'password']):
                    value = getpass.getpass(f"Enter {key} (will be hidden): ").strip()
                    if value:
                        user_inputs[key] = "***PROVIDED***"  # Don't store actual value
                        os.environ[key] = value  # Set in environment
                    else:
                        user_inputs[key] = "***NOT_PROVIDED***"
                else:
                    value = input(f"Enter {key}: ").strip()
                    user_inputs[key] = value or "***NOT_PROVIDED***"
            
            # Ask if user wants to retry
            print(f"\n🔄 **Ready to Retry**")
            print(f"📊 Collected information:")
            for key, value in user_inputs.items():
                print(f"   • {key}: {value}")
            
            retry_choice = input(f"\nWould you like to retry the operation with this information? (y/N): ").strip().lower()
            
            if retry_choice in ['y', 'yes']:
                next_action = "retry_operation"
            else:
                next_action = "create_issue"

            return {
                **state,
                "user_inputs": user_inputs,
                "final_result": next_action,
                "operation_type": "inputs_collected",
            }

        except Exception as e:
            self.logger.error(f"Error in collect inputs node: {e}")
            return {
                **state,
                "final_result": "create_issue",
                "operation_type": "collect_inputs_error",
                "error_occurred": str(e),
            }

    def _retry_operation_node(self, state: DemonstratorAgentState) -> DemonstratorAgentState:
        """Retry the failed operation with user-provided fixes."""
        self.logger.info("Retrying operation with user-provided fixes")

        try:
            print(f"\n🚀 Retrying the operation...")
            
            # Determine what to retry based on error type
            if state["error_type"] in ["auth_failed", "terraform_init"]:
                result = self._retry_terraform_operation(state)
            elif state["error_type"] == "api_key_error":
                result = self._retry_api_operation(state)
            else:
                result = {"success": False, "message": "Retry not supported for this error type"}

            return {
                **state,
                "retry_attempted": True,
                "retry_successful": result["success"],
                "final_result": "end" if result["success"] else "create_issue",
                "operation_type": "retry_complete",
            }

        except Exception as e:
            self.logger.error(f"Error in retry node: {e}")
            return {
                **state,
                "retry_attempted": True,
                "retry_successful": False,
                "final_result": "create_issue",
                "operation_type": "retry_error",
                "error_occurred": str(e),
            }

    def _create_issue_node(self, state: DemonstratorAgentState) -> DemonstratorAgentState:
        """Create GitHub issue using GitAgent."""
        self.logger.info("Creating GitHub issue")

        try:
            print("\n🚀 Creating GitHub issue...")
            
            issue_result = self.git_agent.run(
                GitAgentInput(
                    query=f"open issue {state['issue_title']} for repository {state['repo_url']}: {state['issue_body']}",
                    issue_id=state.get("existing_issue_id"),
                    thread_id=state["thread_id"],
                )
            )

            if issue_result.error_message:
                self.logger.error(f"Issue creation failed: {issue_result.error_message}")
                success = False
                result_msg = f"Issue creation failed: {issue_result.error_message}"
            else:
                success = True
                result_msg = f"GitHub issue created: {issue_result.result}"
                print(f"\n✅ Success! {result_msg}")

            return {
                **state,
                "issue_created": success,
                "final_result": result_msg,
                "operation_type": "issue_creation_complete",
            }

        except Exception as e:
            self.logger.error(f"Error in create issue node: {e}")
            return {
                **state,
                "issue_created": False,
                "final_result": f"Issue creation failed: {str(e)}",
                "operation_type": "issue_creation_error",
                "error_occurred": str(e),
            }

    # --- Routing Methods ---

    def _route_after_planner(self, state: DemonstratorAgentState) -> str:
        """Route after planner decision."""
        final_result = state.get("final_result", "")
        
        if final_result == "analyze_error":
            return "analyze_error_node"
        elif final_result == "demonstrate_issue":
            return "demonstrate_issue_node"
        elif final_result == "collect_inputs":
            return "collect_inputs_node"
        elif final_result == "retry_operation":
            return "retry_operation_node"
        elif final_result == "create_issue":
            return "create_issue_node"
        else:
            return END

    def _route_after_analysis(self, state: DemonstratorAgentState) -> str:
        """Route after error analysis."""
        return "demonstrate_issue_node"  # Always demonstrate after analysis

    def _route_after_demonstration(self, state: DemonstratorAgentState) -> str:
        """Route after demonstration based on user choice."""
        final_result = state.get("final_result", "")
        
        if final_result == "collect_inputs":
            return "collect_inputs_node"
        elif final_result == "create_issue":
            return "create_issue_node"
        elif final_result == "show_details":
            return "demonstrate_issue_node"  # Show details and return to demo
        elif final_result == "abort":
            return END
        else:
            return END

    def _route_after_collection(self, state: DemonstratorAgentState) -> str:
        """Route after input collection."""
        final_result = state.get("final_result", "")
        
        if final_result == "retry_operation":
            return "retry_operation_node"
        else:
            return "create_issue_node"

    def _route_after_retry(self, state: DemonstratorAgentState) -> str:
        """Route after retry attempt."""
        if state.get("retry_successful", False):
            return END
        else:
            return "create_issue_node"

    # --- Helper Methods ---

    def _get_error_analysis(self, error_type: str, error_message: str) -> Dict[str, Any]:
        """Analyze the error and provide guidance."""
        analysis = {
            "description": "Unknown error occurred",
            "fixable": False,
            "fix_guidance": "",
            "required_inputs": [],
            "manual_steps": "Please check the logs and create a GitHub issue",
        }
        
        if error_type == "auth_failed" or "missing_terraform_token" in error_message.lower():
            analysis.update({
                "description": "Terraform Cloud authentication is missing. The TFE_TOKEN environment variable is not set.",
                "fixable": True,
                "fix_guidance": "Terraform requires a valid token to authenticate with Terraform Cloud. You can get this token from your Terraform Cloud account.",
                "required_inputs": [
                    "TFE_TOKEN: Your Terraform Cloud API token",
                    "TF_WORKSPACE: Terraform Cloud workspace name (optional)"
                ],
            })
        elif error_type == "api_key_error" or "401" in error_message:
            analysis.update({
                "description": "API authentication failed. The API key might be missing or invalid.",
                "fixable": True,
                "fix_guidance": "The system needs valid API credentials to function properly.",
                "required_inputs": [
                    "OPENAI_API_KEY: Your OpenAI API key (if using OpenAI)",
                    "ANTHROPIC_API_KEY: Your Anthropic API key (if using Claude)",
                    "GITHUB_TOKEN: Your GitHub Personal Access Token"
                ],
            })
        elif error_type == "terraform_init":
            if "backend" in error_message.lower():
                analysis.update({
                    "description": "Terraform backend configuration issue. The backend might not be properly configured.",
                    "fixable": True,
                    "fix_guidance": "Terraform backend needs proper configuration or credentials.",
                    "required_inputs": [
                        "Backend configuration details",
                        "Access credentials for the backend"
                    ],
                })
            else:
                analysis.update({
                    "description": "Terraform initialization failed for unknown reasons.",
                    "fixable": False,
                    "manual_steps": "Check Terraform configuration files, ensure providers are properly specified, and verify network connectivity."
                })
        elif error_type == "network_error":
            analysis.update({
                "description": "Network connectivity issue. Cannot reach external services.",
                "fixable": True,
                "fix_guidance": "Check your internet connection and try again. You may also need to configure proxy settings.",
                "required_inputs": [
                    "Network connectivity confirmation",
                    "Proxy settings (if behind a corporate firewall)"
                ],
            })
        elif error_type == "permission_error":
            analysis.update({
                "description": "Permission denied. The system lacks necessary permissions.",
                "fixable": False,
                "manual_steps": "Check file permissions, directory access rights, and ensure the process has necessary privileges."
            })
            
        return analysis

    def _get_user_choice(self, max_choice: int, fixable: bool) -> str:
        """Get user choice with error handling."""
        while True:
            try:
                if fixable:
                    choice = input(f"\nEnter your choice (1-{max_choice}): ").strip()
                else:
                    choice = input(f"\nEnter your choice (1-{max_choice}): ").strip()
                
                if choice in [str(i) for i in range(1, max_choice + 1)]:
                    return choice
                else:
                    print(f"❓ Invalid choice '{choice}'. Please enter a valid option.")
                    continue
                    
            except (KeyboardInterrupt, EOFError):
                print(f"\n\n⚠️  User interrupted! Aborting workflow.")
                return "abort"

    def _map_choice_to_action(self, choice: str, fixable: bool) -> str:
        """Map user choice to next action."""
        if choice == "abort":
            return "abort"
            
        if fixable:
            if choice == "1":
                return "collect_inputs"
            elif choice == "2":
                return "create_issue"
            elif choice == "3":
                return "show_details"
            elif choice == "4":
                return "abort"
        else:
            if choice == "1":
                return "create_issue"
            elif choice == "2":
                return "show_details"
            elif choice == "3":
                return "abort"
                
        return "create_issue"  # Default

    def _retry_terraform_operation(self, state: DemonstratorAgentState) -> Dict[str, Any]:
        """Retry Terraform operation with new credentials."""
        try:
            # Extract repo name from URL
            repo_name = state["repo_url"].split('/')[-1].replace('.git', '')
            repo_path = f"/workspace/{repo_name}"
            
            # Try terraform init again
            tf_result = self.terraform_agent.run(
                TerraformAgentInput(
                    query=f"terraform init in {repo_path}",
                    thread_id=state["thread_id"],
                )
            )
            
            if tf_result.error_message:
                print(f"❌ Retry failed: {tf_result.error_message}")
                return {"success": False, "message": tf_result.error_message}
            else:
                print(f"✅ Retry successful! Terraform init completed.")
                return {"success": True, "message": "Terraform init completed successfully"}
                
        except Exception as e:
            print(f"❌ Retry failed with exception: {e}")
            return {"success": False, "message": str(e)}

    def _retry_api_operation(self, state: DemonstratorAgentState) -> Dict[str, Any]:
        """Retry API operation with new credentials."""
        try:
            # Test API connection
            llm = self.llm_router.get_llm(
                model_name="gpt-4o-mini",
                temperature=0.1,
                agent_name="demonstrator_agent",
            )
            
            test_response = llm.invoke([HumanMessage(content="Test API connection")])
            
            if test_response and test_response.content:
                print(f"✅ Retry successful! API connection restored.")
                return {"success": True, "message": "API connection successful"}
            else:
                print(f"❌ Retry failed: No response from API")
                return {"success": False, "message": "No response from API"}
                
        except Exception as e:
            print(f"❌ Retry failed with exception: {e}")
            return {"success": False, "message": str(e)}
