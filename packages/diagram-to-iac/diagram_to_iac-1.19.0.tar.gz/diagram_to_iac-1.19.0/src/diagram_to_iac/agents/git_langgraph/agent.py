"""
Git Agent - Phase 4 Implementation

Hybrid-agent architecture for DevOps automation featuring:
- Light LLM "planner" node that decides the next action via routing tokens
- Small, single-purpose tool agents (Shell, Git, GitHub) that execute real commands
- LangGraph state machine that orchestrates the control flow
- Configuration-driven behavior with robust error handling
- Memory integration for operation tracking

This agent demonstrates the orchestration pattern before scaling to Terraform, Ansible, etc.

Architecture:
1. Planner LLM analyzes user input and emits routing tokens:
   - "ROUTE_TO_CLONE" for git clone operations
   - "ROUTE_TO_ISSUE" for GitHub issue creation
   - "ROUTE_TO_SHELL" for shell command execution
   - "ROUTE_TO_END" when no action needed
2. Router function maps tokens to appropriate tool nodes
3. Tool nodes execute real operations using battle-tested tools
4. State machine handles error paths and success flows
"""

import os
import uuid
import logging
from typing import TypedDict, Annotated, Optional, List, Dict, Any

import yaml
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

# Import our battle-tested tools
from diagram_to_iac.tools.git import (
    GitExecutor,
    git_clone,
    gh_open_issue,
    GitCloneInput,
)
# Shell tools were moved from the shell_langgraph agent package into the common
# tools module. Import from the new location to keep the agent functional.
from diagram_to_iac.tools.shell import ShellExecutor, shell_exec
from diagram_to_iac.tools.llm_utils.router import get_llm, LLMRouter
from diagram_to_iac.core.agent_base import AgentBase
from diagram_to_iac.core.memory import create_memory, LangGraphMemoryAdapter
from diagram_to_iac.services.observability import log_event
from diagram_to_iac.core.config_loader import get_config, get_config_value

from diagram_to_iac.services.observability import log_event

from .pr import GitPrCreator



# --- Pydantic Schemas for Agent I/O ---
class GitAgentInput(BaseModel):
    """Input schema for GitAgent operations."""
    query: str = Field(..., description="The DevOps request (git clone, GitHub issue, shell command)")
    thread_id: str | None = Field(None, description="Optional thread ID for conversation history")
    workspace_path: str | None = Field(None, description="Optional workspace directory for shell commands")
    issue_id: int | None = Field(None, description="Existing issue number to comment on")
    trigger_pr_creation_for_error_type: Optional[str] = Field(None, description="If set, triggers PR creation for this error type (e.g., 'syntax_fmt', 'missing_backend').")
    pr_title: Optional[str] = Field(None, description="Title for the auto-created PR.")
    pr_body: Optional[str] = Field(None, description="Body for the auto-created PR.")
    repo_local_path: Optional[str] = Field(None, description="Local path to the git repository for PR creation.")


class GitAgentOutput(BaseModel):
    """Output schema for GitAgent operations."""
    success: bool = Field(..., description="Indicates if the operation was successful")
    created_pr_id: Optional[int] = Field(None, description="ID of the created pull request, if any")
    pr_url: Optional[str] = Field(None, description="URL of the created pull request, if any")
    created_issue_id: Optional[int] = Field(None, description="ID of the created issue, if any")
    issue_url: Optional[str] = Field(None, description="URL of the created issue, if any")
    summary: Optional[str] = Field(None, description="Summary of the operation result")
    artifacts: Optional[Dict[str, Any]] = Field(None, description="Optional artifacts returned by the operation")

    model_config = {"extra": "ignore"}


# --- Agent State Definition ---
class GitAgentState(TypedDict):
    """State definition for the GitAgent LangGraph."""
    input_message: HumanMessage
    tool_output: Annotated[list[BaseMessage], lambda x, y: x + y]
    final_result: str
    error_message: Optional[str]
    operation_type: Optional[str]
    workspace_path: Optional[str]
    repo_path: Optional[str]
    issue_id: Optional[int]
    trigger_pr_creation_for_error_type: Optional[str]
    pr_title: Optional[str]
    pr_body: Optional[str]
    pr_url: Optional[str]
    repo_local_path: Optional[str]


# --- Main Agent Class ---
class GitAgent(AgentBase):
    """
    GitAgent is a LangGraph-based DevOps automation agent that can:
    - Clone Git repositories via git_clone tool
    - Create GitHub issues via gh_open_issue tool  
    - Execute shell commands via shell_exec tool
    
    Uses a light LLM planner for routing decisions and delegates to specialized tool nodes.
    Demonstrates hybrid-agent architecture with configuration-driven behavior.
    """
    
    def __init__(self, config_path: str = None, memory_type: str = "persistent"):
        """
        Initialize the GitAgent with configuration and tools.
        
        Args:
            config_path: Optional path to YAML configuration file
            memory_type: Type of memory ("persistent", "memory", or "langgraph")
        """
        # Configure logger for this agent instance
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Store memory type for tool initialization
        self.memory_type = memory_type
        
        # Load configuration using centralized system
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, 'config.yaml')
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
        except Exception as e:
            self.logger.warning(f"Failed to load configuration via centralized system: {e}. Using fallback.")
            # Fallback to direct YAML loading for backward compatibility
            try:
                with open(config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                if self.config is None:
                    self.logger.warning(f"Configuration file at {config_path} is empty. Using defaults.")
                    self._set_default_config()
                else:
                    self.logger.info(f"Configuration loaded successfully from {config_path}")
            except FileNotFoundError:
                self.logger.warning(f"Configuration file not found at {config_path}. Using defaults.")
                self._set_default_config()
            except yaml.YAMLError as e:
                self.logger.error(f"Error parsing YAML configuration: {e}. Using defaults.", exc_info=True)
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
        
        # Initialize tools (using our battle-tested implementations)
        self._initialize_tools()
        
        # Build and compile the LangGraph
        self.runnable = self._build_graph()
        self.logger.info("GitAgent initialized successfully")
    
    def _set_default_config(self):
        """Set default configuration values using centralized system."""
        self.logger.info("Setting default configuration for GitAgent")
        self.config = {
            'llm': {
                'model_name': get_config_value("ai.default_model", "gpt-4o-mini"),
                'temperature': get_config_value("ai.git_agent_temperature", 0.1)
            },
            'routing_keys': {
                'git_clone': get_config_value("routing.tokens.git_clone", "ROUTE_TO_GIT_CLONE"),
                'github_cli': get_config_value("routing.tokens.github_cli", "ROUTE_TO_GITHUB_CLI"),
                'shell_exec': get_config_value("routing.tokens.shell_exec", "ROUTE_TO_SHELL_EXEC"),
                'create_pr': get_config_value("routing.tokens.create_pr", "ROUTE_TO_CREATE_PR"),
                'end': get_config_value("routing.tokens.end", "ROUTE_TO_END")
            },
            'git_pr_creator': {
                'copilot_assignee': get_config_value("github.copilot_assignee", "CopilotUser"),
                'default_assignees': get_config_value("github.default_assignees", ["team-infra"]),
                'remote_name': get_config_value("tools.git.remote_name", "origin")
            },
            'tools': {
                'git_clone': {
                    'enabled': True,
                    'timeout': get_config_value("network.github_timeout", 300)
                },
                'gh_open_issue': {
                    'enabled': True,
                    'timeout': get_config_value("network.github_timeout", 15)
                },
                'shell_exec': {
                    'enabled': True,
                    'timeout': get_config_value("network.shell_timeout", 30)
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
        """Initialize the DevOps tools."""
        try:
            # Initialize GitExecutor (handles both git clone and GitHub CLI)
            self.git_executor = GitExecutor(memory_type=self.memory_type)
            
            # Initialize ShellExecutor
            self.shell_executor = ShellExecutor(memory_type=self.memory_type)
            
            # GitPrCreator is initialized on-demand in _create_pr_node
            # self.git_pr_creator can be removed if not used elsewhere, or kept as None
            self.git_pr_creator = None

            # Register tools for easy access
            self.tools = {
                "git_clone": git_clone,
                "gh_open_issue": gh_open_issue,
                "shell_exec": shell_exec
            }
            
            self.logger.info(f"Tools initialized: {list(self.tools.keys())}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize tools: {e}", exc_info=True)
            raise
    
    def _planner_llm_node(self, state: GitAgentState):
        """
        LLM planner node that analyzes input and decides routing.
        Emits routing tokens based on the user's DevOps request.
        """
        # Check for direct PR creation trigger
        if state.get('trigger_pr_creation_for_error_type') and state.get('repo_local_path'):
            self.logger.info(f"PR creation triggered directly for error type: {state.get('trigger_pr_creation_for_error_type')}")
            return {
                "final_result": self.config['routing_keys']['create_pr'],
                "operation_type": "create_pr",
                "error_message": None
            }

        # Get LLM configuration
        llm_config = self.config.get('llm', {})
        model_name = llm_config.get('model_name')
        temperature = llm_config.get('temperature')
        
        # Use enhanced LLM router
        try:
            if model_name is not None or temperature is not None:
                actual_model_name = model_name if model_name is not None else 'gpt-4o-mini'
                actual_temperature = temperature if temperature is not None else 0.1
                self.logger.debug(f"Planner using LLM: {actual_model_name}, Temp: {actual_temperature}")
                
                llm = self.llm_router.get_llm(
                    model_name=actual_model_name,
                    temperature=actual_temperature,
                    agent_name="git_agent"
                )
            else:
                self.logger.debug("Planner using agent-specific LLM configuration")
                llm = self.llm_router.get_llm_for_agent("git_agent")
        except Exception as e:
            self.logger.error(f"Failed to get LLM from router: {e}. Falling back to basic get_llm.")
            llm = get_llm(model_name=model_name, temperature=temperature)
        
        # Store conversation in memory
        query_content = state['input_message'].content
        self.memory.add_to_conversation("user", query_content, {
            "agent": "git_agent", 
            "node": "planner"
        })
        
        try:
            self.logger.debug(f"Planner LLM input: {query_content}")
            
            # Build the analysis prompt
            analysis_prompt_template = self.config.get('prompts', {}).get('planner_prompt', """
User input: "{user_input}"
Analyze this DevOps request and determine the appropriate action:
1. If requesting to clone a Git repository (keywords: 'clone', 'download repo', 'git clone'), respond with "{route_git_clone}"
2. If requesting to open a GitHub issue (keywords: 'open issue', 'create issue', 'report bug'), respond with "{route_github_cli}"
3. If requesting a shell command (keywords: 'run command', 'execute', 'shell'), respond with "{route_shell_exec}"
4. If the request is complete or no action needed, respond with "{route_end}"

Important: Only use routing tokens if the input contains actionable DevOps requests.
            """)
            
            routing_keys = self.config.get('routing_keys', {
                "git_clone": "ROUTE_TO_GIT_CLONE",
                "github_cli": "ROUTE_TO_GITHUB_CLI",
                "shell_exec": "ROUTE_TO_SHELL_EXEC", 
                "end": "ROUTE_TO_END"
            })
            
            analysis_prompt = analysis_prompt_template.format(
                user_input=query_content,
                route_git_clone=routing_keys['git_clone'],
                route_github_cli=routing_keys['github_cli'],
                route_shell_exec=routing_keys['shell_exec'],
                route_end=routing_keys['end']
            )
            
            self.logger.debug(f"Planner LLM prompt: {analysis_prompt}")
            
            response = llm.invoke([HumanMessage(content=analysis_prompt)])
            self.logger.debug(f"Planner LLM response: {response.content}")
            response_content = response.content.strip()
            
            # Store LLM response in memory
            self.memory.add_to_conversation("assistant", response_content, {
                "agent": "git_agent", 
                "node": "planner", 
                "model": model_name
            })
            
            # Determine routing based on response content
            new_state_update = {}
            if routing_keys['git_clone'] in response_content:
                new_state_update = {
                    "final_result": "route_to_clone",
                    "operation_type": "clone",
                    "error_message": None
                }
            elif routing_keys['github_cli'] in response_content:
                new_state_update = {
                    "final_result": "route_to_issue", 
                    "operation_type": "issue",
                    "error_message": None
                }
            elif routing_keys['shell_exec'] in response_content:
                new_state_update = {
                    "final_result": "route_to_shell",
                    "operation_type": "shell", 
                    "error_message": None
                }
            elif routing_keys['end'] in response_content: # Explicitly check for 'end'
                # Direct answer or route to end
                new_state_update = {
                    "final_result": response.content,
                    "operation_type": "direct_answer",
                    "error_message": None
                }
            
            else: # Default if no specific route token is found
                new_state_update = {
                    "final_result": response.content, # Treat as direct answer
                    "operation_type": "direct_answer",
                    "error_message": None
                }

            self.logger.info(f"Planner decision: {new_state_update.get('final_result', 'N/A')}")
            return new_state_update
            
        except Exception as e:
            self.logger.error(f"LLM error in planner: {e}", exc_info=True)
            self.memory.add_to_conversation("system", f"Error in planner: {str(e)}", {
                "agent": "git_agent", 
                "node": "planner", 
                "error": True
            })
            return {
                "final_result": "Sorry, I encountered an issue processing your request.",
                "error_message": str(e),
                "operation_type": "error"
            }
    
    def _clone_repo_node(self, state: GitAgentState):
        """
        Git clone tool node that handles repository cloning operations.
        """
        self.logger.info(f"Clone repo node invoked for: {state['input_message'].content}")
        
        try:
            text_content = state['input_message'].content
            
            # Store tool invocation in memory
            self.memory.add_to_conversation("system", f"Git clone tool invoked", {
                "agent": "git_agent", 
                "node": "clone_repo", 
                "input": text_content
            })
            
            # For now, extract a simple repo URL from the input
            # In a real implementation, you might use more sophisticated parsing
            import re
            url_pattern = r'https?://github\.com/[\w\-\.]+/[\w\-\.]+'
            urls = re.findall(url_pattern, text_content)
            
            if not urls:
                words = text_content.split()
                repo_url = words[-1]
            else:
                repo_url = urls[0]

            # Use the git executor directly to allow invalid URLs
            git_input = GitCloneInput.model_construct(
                repo_url=repo_url,
                workspace=state.get("workspace_path") or None,
            )
            result_obj = self.git_executor.git_clone(git_input)
            
            # Organically handle different result statuses
            if result_obj.status == "SUCCESS":
                result = result_obj.repo_path
                state["repo_path"] = result_obj.repo_path
                success_msg = f"Successfully cloned repository: {result}"
                
                self.memory.add_to_conversation("system", f"Repository cloned: {result}", {
                    "agent": "git_agent", 
                    "node": "clone_repo", 
                    "repo_url": repo_url,
                    "result": "SUCCESS"
                })
                
                return {
                    "final_result": success_msg,
                    "error_message": None,
                    "operation_type": "clone",
                    "repo_path": result_obj.repo_path
                }
                
            elif result_obj.status == "AUTH_FAILED":
                # Organically handle authentication failures with helpful context
                github_token = os.environ.get('GITHUB_TOKEN')
                if github_token and github_token.strip():
                    auth_msg = f"Git executor: Authentication failed for repository '{repo_url}'. GitHub token is present but may be invalid or expired. Please check token permissions."
                else:
                    auth_msg = f"Git executor: Authentication failed for repository '{repo_url}'. For private repositories, please set the GITHUB_TOKEN environment variable with a valid personal access token."
                
                self.memory.add_to_conversation("system", f"Repository cloned: {auth_msg}", {
                    "agent": "git_agent", 
                    "node": "clone_repo", 
                    "repo_url": repo_url,
                    "result": "AUTH_FAILED"
                })
                
                return {
                    "final_result": f"Clone failed: {auth_msg}",
                    "error_message": result_obj.error_message or "Authentication failed",
                    "operation_type": "clone",
                    "repo_path": None
                }
                
            else:
                # Handle other errors (timeout, invalid URL, etc.)
                error_msg = result_obj.error_message or f"Git executor: Failed to clone repository '{repo_url}'"
                
                self.memory.add_to_conversation("system", f"Repository cloned: {error_msg}", {
                    "agent": "git_agent", 
                    "node": "clone_repo", 
                    "repo_url": repo_url,
                    "result": result_obj.status
                })
                
                return {
                    "final_result": f"Clone failed: {error_msg}",
                    "error_message": result_obj.error_message or error_msg,
                    "operation_type": "clone",
                    "repo_path": None
                }
            
        except Exception as e:
            self.logger.error(f"Error in clone repo node: {e}", exc_info=True)
            self.memory.add_to_conversation("system", f"Clone error: {str(e)}", {
                "agent": "git_agent", 
                "node": "clone_repo", 
                "error": True
            })
            return {
                "final_result": "Sorry, I couldn't clone the repository due to an error.",
                "error_message": str(e),
                "operation_type": "clone",
                "repo_path": None
            }
    
    def _open_issue_node(self, state: GitAgentState):
        """
        GitHub issue tool node that handles issue creation operations.
        """
        self.logger.info(f"Open issue node invoked for: {state['input_message'].content}")
        
        try:
            text_content = state['input_message'].content
            
            # Store tool invocation in memory
            self.memory.add_to_conversation("system", f"GitHub issue tool invoked", {
                "agent": "git_agent", 
                "node": "open_issue", 
                "input": text_content
            })
            
            # Enhanced parsing for both test format and supervisor format
            import re
            
            # Pattern 1: Enhanced supervisor format - "open issue TITLE for repository URL: BODY"
            supervisor_pattern = r'^open issue\s+(.+?)\s+for repository\s+(https://github\.com/[\w\-\.]+/[\w\-\.]+):\s*(.+)$'
            supervisor_match = re.search(supervisor_pattern, text_content, re.IGNORECASE | re.DOTALL)
            
            if supervisor_match:
                title = supervisor_match.group(1).strip()
                repo_url = supervisor_match.group(2).strip()
                body = supervisor_match.group(3).strip()
                repo = repo_url.replace('https://github.com/', '')
                
                # Clean ANSI codes from title and body for better presentation
                from diagram_to_iac.tools.text_utils import clean_ansi_codes, enhance_error_message_for_issue
                title = clean_ansi_codes(title)
                body = enhance_error_message_for_issue(body)
                
                self.logger.info(f"Parsed enhanced supervisor format - Title: {title}, Repo: {repo}")
                
            else:
                # Pattern 2: Legacy supervisor format - "open issue TITLE: BODY"
                legacy_supervisor_pattern = r'^open issue\s+([^:]+):\s*(.+)$'
                legacy_supervisor_match = re.search(legacy_supervisor_pattern, text_content, re.IGNORECASE | re.DOTALL)
                
                if legacy_supervisor_match:
                    title = legacy_supervisor_match.group(1).strip()
                    body = legacy_supervisor_match.group(2).strip()
                    
                    # Clean ANSI codes from title and body for better presentation
                    from diagram_to_iac.tools.text_utils import clean_ansi_codes, enhance_error_message_for_issue
                    title = clean_ansi_codes(title)
                    body = enhance_error_message_for_issue(body)
                    
                    # Extract repository from the body if present
                    repo_in_body = re.search(r'\*?\*?Repository:\*?\*?\s*(https://github\.com/[\w\-\.]+/[\w\-\.]+)', body)
                    if repo_in_body:
                        repo_url = repo_in_body.group(1)
                        repo = repo_url.replace('https://github.com/', '')
                    else:
                        # No fallback - require explicit repository specification
                        error_msg = "Could not extract repository from issue request. Repository must be specified in body as 'Repository: https://github.com/owner/repo'"
                        self.logger.warning(error_msg)
                        self.memory.add_to_conversation("system", error_msg, {
                            "agent": "git_agent", 
                            "node": "open_issue", 
                            "error": True
                        })
                        return {
                            "final_result": error_msg,
                            "error_message": "Missing repository specification",
                            "operation_type": "issue"
                        }
                    
                    self.logger.info(f"Parsed legacy supervisor format - Title: {title}, Repo: {repo}")
                
                else:
                    # Pattern 3: Test format - "titled 'X' with body 'Y' in repository user/repo"
                    repo_pattern = r'(?:in|for|on|repository)\s+(?:repository\s+)?(\w+/\w+)'
                    title_pattern = r"titled\s*['\"]([^'\"]+)['\"]"
                    body_pattern = r'(?:with\s+body|body|content|description)\s*[\'"]?([^\'"\n]+)[\'"]?'
                    
                    repo_match = re.search(repo_pattern, text_content, re.IGNORECASE)
                    title_match = re.search(title_pattern, text_content, re.IGNORECASE)
                    body_match = re.search(body_pattern, text_content, re.IGNORECASE)
                    
                    if not repo_match or not title_match:
                        error_msg = "Could not extract repository name and issue title from the request."
                        self.logger.warning(error_msg)
                        self.memory.add_to_conversation("system", error_msg, {
                            "agent": "git_agent", 
                            "node": "open_issue", 
                            "error": True
                        })
                        return {
                            "final_result": error_msg,
                            "error_message": "Missing repository or issue details",
                            "operation_type": "issue"
                        }
                    
                    repo = repo_match.group(1)
                    title = title_match.group(1).strip()
                    body = body_match.group(1).strip() if body_match else f"Issue created via GitAgent: {text_content}"
                    repo_url = f"https://github.com/{repo}"
                    
                    # Clean ANSI codes from title and body for better presentation
                    from diagram_to_iac.tools.text_utils import clean_ansi_codes, enhance_error_message_for_issue
                    title = clean_ansi_codes(title)
                    body = enhance_error_message_for_issue(body)
                    
                    self.logger.info(f"Parsed test format - Title: {title}, Repo: {repo}")
            
            # Convert repo to full URL format expected by the tool
            gh_params = {
                "repo_url": repo_url,
                "title": title,
                "body": body,
            }
            if state.get("issue_id") is not None:
                gh_params["issue_id"] = state["issue_id"]

            result = self.tools['gh_open_issue'].invoke(gh_params)
            
            # Store successful result in memory
            self.memory.add_to_conversation("system", f"Issue created: {result}", {
                "agent": "git_agent", 
                "node": "open_issue", 
                "repo": repo,
                "title": title,
                "result": result
            })
            
            action = "added comment to" if state.get("issue_id") is not None else "created"
            return {
                "final_result": f"Successfully {action} GitHub issue: {result}",
                "error_message": None,
                "operation_type": "issue"
            }
            
        except Exception as e:
            self.logger.error(f"Error in open issue node: {e}", exc_info=True)
            self.memory.add_to_conversation("system", f"Issue creation error: {str(e)}", {
                "agent": "git_agent", 
                "node": "open_issue", 
                "error": True
            })
            return {
                "final_result": "Sorry, I couldn't create the GitHub issue due to an error.",
                "error_message": str(e),
                "operation_type": "issue"
            }
    
    def _shell_exec_node(self, state: GitAgentState):
        """
        Shell execution tool node that handles command execution operations.
        """
        self.logger.info(f"Shell exec node invoked for: {state['input_message'].content}")
        
        try:
            text_content = state['input_message'].content
            
            # Store tool invocation in memory
            self.memory.add_to_conversation("system", f"Shell exec tool invoked", {
                "agent": "git_agent", 
                "node": "shell_exec", 
                "input": text_content
            })
            
            # Extract command from input (simplified parsing)
            import re
            
            # More flexible patterns to match test inputs
            command_patterns = [
                r'(?:run|execute|command):\s*[\'"]?(.+?)[\'"]?(?:\.|$)',  # "execute: command"
                r'(?:run|execute)\s+[\'"]([^\'\"]+)[\'"]',               # "execute 'command'"
                r'(?:run|execute)\s+([^\'\"\n\.]+)',                     # "execute command"
            ]
            
            command = None
            for pattern in command_patterns:
                command_match = re.search(pattern, text_content, re.IGNORECASE)
                if command_match:
                    command = command_match.group(1).strip()
                    break
            
            if not command:
                # Try to extract anything that looks like a command
                words = text_content.split()
                command_candidates = []
                for word in words:
                    if word in ['git', 'ls', 'pwd', 'echo', 'cat', 'grep', 'find', 'mkdir', 'rm']:
                        # Find the rest of the command
                        idx = words.index(word)
                        # Look for quoted command or take words until common sentence endings
                        remaining = words[idx:]
                        command_end = len(remaining)
                        for i, w in enumerate(remaining):
                            if w.lower() in ['in', 'to', 'for', 'directory', 'files', 'folder']:
                                command_end = i
                                break
                        command_candidates.append(' '.join(remaining[:command_end]))
                        break
                
                if not command_candidates:
                    error_msg = "Could not extract a shell command from the request."
                    self.logger.warning(error_msg)
                    self.memory.add_to_conversation("system", error_msg, {
                        "agent": "git_agent", 
                        "node": "shell_exec", 
                        "error": True
                    })
                    return {
                        "final_result": error_msg,
                        "error_message": "No command found",
                        "operation_type": "shell"
                    }
                command = command_candidates[0]
            
            # Use the shell_exec tool
            tool_input = {"command": command}
            if state.get("workspace_path"):
                tool_input["cwd"] = state["workspace_path"]
            result = self.tools['shell_exec'].invoke(tool_input)
            
            # Store successful result in memory
            self.memory.add_to_conversation("system", f"Command executed: {result}", {
                "agent": "git_agent", 
                "node": "shell_exec", 
                "command": command,
                "result": result
            })
            
            return {
                "final_result": f"Command executed successfully: {result}",
                "error_message": None,
                "operation_type": "shell"
            }
            
        except Exception as e:
            self.logger.error(f"Error in shell exec node: {e}", exc_info=True)
            self.memory.add_to_conversation("system", f"Shell exec error: {str(e)}", {
                "agent": "git_agent", 
                "node": "shell_exec", 
                "error": True
            })
            return {
                "final_result": "Sorry, I couldn't execute the command due to an error.",
                "error_message": str(e),
                "operation_type": "shell"
            }

    def _create_pr_node(self, state: GitAgentState):
        self.logger.info(f"Create PR node invoked for error type: {state.get('trigger_pr_creation_for_error_type')}")
        error_type = state.get('trigger_pr_creation_for_error_type')
        title = state.get('pr_title') or f"Auto-fix for {error_type}"
        body = state.get('pr_body') or f"Automated PR to address {error_type}."
        repo_local_path = state.get('repo_local_path')

        if not error_type or not repo_local_path:
            error_msg = "Missing error_type or repo_local_path for PR creation."
            self.logger.error(error_msg)
            return {
                "final_result": f"PR creation failed: {error_msg}",
                "error_message": error_msg,
                "operation_type": "create_pr",
                "pr_url": None,
                "repo_path": repo_local_path # Keep repo_path consistent
            }

        # Initialize GitPrCreator with the specific repo_local_path for this operation
        git_pr_config = self.config.get('git_pr_creator', {})
        copilot_assignee = git_pr_config.get('copilot_assignee')
        default_assignees = git_pr_config.get('default_assignees', [])
        remote_name = git_pr_config.get('remote_name', 'origin')

        pr_creator = GitPrCreator(
            repo_path=repo_local_path,
            remote_name=remote_name,
            copilot_assignee=copilot_assignee,
            default_assignees=default_assignees
        )

        pr_result = pr_creator.create_draft_pr(
            error_type=error_type,
            title=title,
            body=body
        )

        if pr_result and pr_result.get("status") == "success" and pr_result.get("pr_url"):
            self.memory.add_to_conversation("system", f"Draft PR created: {pr_result['pr_url']}", {
                "agent": "git_agent", "node": "create_pr", "result": "SUCCESS", "pr_details": pr_result
            })
            return {
                "final_result": f"Successfully created draft PR: {pr_result['pr_url']}",
                "error_message": None,
                "operation_type": "create_pr",
                "pr_url": pr_result["pr_url"],
                "repo_path": repo_local_path
            }
        else:
            error_msg = "Failed to create draft PR."
            if pr_result and pr_result.get("message"):
                 error_msg = pr_result.get("message")
            self.logger.error(f"PR creation failed: {error_msg}")
            self.memory.add_to_conversation("system", f"PR creation failed: {error_msg}", {
                "agent": "git_agent", "node": "create_pr", "result": "FAILURE", "error_details": pr_result
            })
            return {
                "final_result": f"PR creation failed: {error_msg}",
                "error_message": error_msg,
                "operation_type": "create_pr",
                "pr_url": None,
                "repo_path": repo_local_path
            }
    
    def _route_after_planner(self, state: GitAgentState):
        """
        Router function that determines the next node based on planner output.
        Maps routing tokens to appropriate tool nodes or END.
        """
        self.logger.debug(f"Routing after planner. State: {state.get('final_result')}, error: {state.get('error_message')}")
        
        if state.get("error_message"):
            self.logger.warning(f"Error detected in planner, routing to END: {state['error_message']}")
            return END
        
        final_result = state.get("final_result", "").strip()
        
        # Enhanced routing logic with multiple token support
        if final_result in ["route_to_clone", "ROUTE_TO_GIT_CLONE"]:
            return "clone_repo"
        elif final_result in ["route_to_issue", "ROUTE_TO_GITHUB_ISSUE"]:
            return "open_issue"
        elif final_result in ["route_to_shell", "ROUTE_TO_SHELL"]:
            return "shell_exec"
        elif final_result in ["route_to_create_pr", "ROUTE_TO_CREATE_PR"]:
            return "create_pr_node"
        elif final_result in ["route_to_end", "ROUTE_TO_END"]:
            return END
        else:
            self.logger.warning(f"Unknown routing token: {final_result}, routing to END")
            return END
    
    def _build_graph(self):
        """
        Build and compile the LangGraph state machine.
        Creates nodes for planner and each tool, sets up routing.
        """
        graph_builder = StateGraph(GitAgentState)
        
        # Add nodes
        graph_builder.add_node("planner_llm", self._planner_llm_node)
        graph_builder.add_node("clone_repo", self._clone_repo_node)
        graph_builder.add_node("open_issue", self._open_issue_node)
        graph_builder.add_node("shell_exec", self._shell_exec_node)
        graph_builder.add_node("create_pr_node", self._create_pr_node)
        
        # Set entry point
        graph_builder.set_entry_point("planner_llm")
        
        # Configure routing map
        routing_map = self.config.get('routing_map', {
            "clone_repo": "clone_repo",
            "open_issue": "open_issue",
            "shell_exec": "shell_exec",
            "create_pr_node": "create_pr_node", # Added for PR creation
            END: END
        })
        
        # Add conditional edges from planner
        graph_builder.add_conditional_edges(
            "planner_llm",
            self._route_after_planner,
            routing_map
        )
        
        # Add edges from tool nodes to END
        graph_builder.add_edge("clone_repo", END)
        graph_builder.add_edge("open_issue", END)
        graph_builder.add_edge("shell_exec", END)
        graph_builder.add_edge("create_pr_node", END) # New edge for PR node
        
        # Compile with checkpointer
        return graph_builder.compile(checkpointer=self.checkpointer)
    
    def run(self, agent_input: GitAgentInput) -> GitAgentOutput:
        """
        Run the agent with the given input.
        
        Args:
            agent_input: GitAgentInput with query and optional thread_id
            
        Returns:
            GitAgentOutput with result, thread_id, and optional error
        """
        current_thread_id = agent_input.thread_id if agent_input.thread_id else str(uuid.uuid4())
        self.logger.info(
            f"Run invoked with query: '{agent_input.query}', thread_id: {current_thread_id}"
        )
        log_event(
            "git_agent_run_start",
            query=agent_input.query,
            thread_id=current_thread_id,
        )
        
        # Initial state for LangGraph
        initial_state = {
            "input_message": HumanMessage(content=agent_input.query),
            "tool_output": [],
            "error_message": None,
            "operation_type": None,
            "workspace_path": agent_input.workspace_path,
            "repo_path": None, # This is for clone output, repo_local_path is for PR input
            "issue_id": agent_input.issue_id,
            "trigger_pr_creation_for_error_type": agent_input.trigger_pr_creation_for_error_type,
            "pr_title": agent_input.pr_title,
            "pr_body": agent_input.pr_body,
            "repo_local_path": agent_input.repo_local_path,
            "pr_url": None,
        }
        
        langgraph_config = {"configurable": {"thread_id": current_thread_id}}
        
        try:
            # Run the graph
            result_state = self.runnable.invoke(initial_state, config=langgraph_config)

            # Extract results
            final_result = result_state.get("final_result", "No result found.")
            error_message = result_state.get("error_message")
            operation_type = result_state.get("operation_type")
            repo_path = result_state.get("repo_path") # Output from clone
            pr_url = result_state.get("pr_url") # Output from PR creation
            
            if error_message:
                self.logger.error(f"Run completed with error: {error_message}")
            else:
                self.logger.info(f"Run completed successfully: {final_result}")

            log_event(
                "git_agent_run_end",
                thread_id=current_thread_id,
                error=error_message,
                result=final_result,
            )
            
            # Determine success based on whether there was an error
            success = error_message is None or error_message == ""
            
            # Extract PR/Issue IDs from URLs if available
            created_pr_id = None
            created_issue_id = None
            if pr_url:
                # Extract PR ID from GitHub URL pattern
                import re
                pr_match = re.search(r'/pull/(\d+)', pr_url)
                if pr_match:
                    created_pr_id = int(pr_match.group(1))
                else:
                    # Check if it's an issue URL
                    issue_match = re.search(r'/issues/(\d+)', pr_url)
                    if issue_match:
                        created_issue_id = int(issue_match.group(1))
            
            output = GitAgentOutput(
                success=success,
                created_pr_id=created_pr_id,
                pr_url=pr_url if created_pr_id else None,
                created_issue_id=created_issue_id,
                issue_url=pr_url if created_issue_id else None,
                summary=final_result,
                artifacts={
                    "thread_id": current_thread_id,
                    "repo_path": repo_path,
                    "operation_type": operation_type,
                    "error_message": error_message
                }
            )
            return output
            
        except Exception as e:
            self.logger.error(f"Error during agent run: {e}", exc_info=True)
            log_event(
                "git_agent_run_exception",
                thread_id=current_thread_id,
                error=str(e),
            )
            return GitAgentOutput(
                success=False,
                created_pr_id=None,
                pr_url=None,
                created_issue_id=None,
                issue_url=None,
                summary="An unexpected error occurred during execution.",
                artifacts={
                    "thread_id": current_thread_id,
                    "repo_path": None,  # Or more specifically result_state.get("repo_path") if available
                    "operation_type": "error",
                    "error_message": str(e)
                }
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
        For GitAgent, the plan analyzes the DevOps request to predict routing.
        
        Args:
            query: The DevOps query to plan for
            **kwargs: Additional parameters (e.g., thread_id)
            
        Returns:
            dict: A plan containing the input and predicted action
        """
        self.logger.info(f"Planning for DevOps query: '{query}'")
        
        plan = {
            "input_query": query,
            "predicted_action": "analyze_and_route",
            "description": "Analyze DevOps request to determine appropriate tool routing"
        }
        
        # Simple analysis to predict the route
        query_lower = query.lower()
        if any(word in query_lower for word in ['clone', 'download repo', 'git clone']):
            plan["predicted_route"] = "git_clone"
        elif any(word in query_lower for word in ['open issue', 'create issue', 'report bug', 'issue']) or \
             ('open' in query_lower and 'issue' in query_lower):
            plan["predicted_route"] = "github_issue"
        elif any(word in query_lower for word in ['run command', 'execute', 'shell']):
            plan["predicted_route"] = "shell_command"
        else:
            plan["predicted_route"] = "direct_response"
            
        self.logger.debug(f"Generated plan: {plan}")
        return plan

    def report(self, result=None, **kwargs):
        """
        Reports the results or progress of the agent's execution (required by AgentBase).
        
        Args:
            result: The result to report (GitAgentOutput or string)
            **kwargs: Additional parameters
            
        Returns:
            dict: A report containing execution details
        """
        if isinstance(result, GitAgentOutput):
            report = {
                "status": "completed",
                "result": result.summary,
                "thread_id": result.artifacts.get("thread_id") if result.artifacts else None,
                "error": result.artifacts.get("error_message") if result.artifacts else None,
                "operation_type": result.artifacts.get("operation_type") if result.artifacts else None,
                "success": result.success,
                "pr_url": result.pr_url,
                "issue_url": result.issue_url,
                "created_pr_id": result.created_pr_id,
                "created_issue_id": result.created_issue_id
            }
        elif isinstance(result, str):
            report = {
                "status": "completed", 
                "result": result,
                "success": True
            }
        else:
            report = {
                "status": "no_result",
                "message": "No result provided to report"
            }
            
        self.logger.info(f"GitAgent execution report: {report}")
        return report


# Alias for backward compatibility
GitAgent = GitAgent
