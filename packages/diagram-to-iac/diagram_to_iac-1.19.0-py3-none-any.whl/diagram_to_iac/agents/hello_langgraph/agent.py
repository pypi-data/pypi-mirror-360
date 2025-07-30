import os
import re
import os
from typing import TypedDict, Annotated, Optional, List, Dict, Any
import yaml
import uuid
import logging

from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

# Import tools and enhanced utilities
from diagram_to_iac.tools.hello.cal_utils import add_two, multiply_two
from diagram_to_iac.tools.llm_utils.router import get_llm, LLMRouter
from diagram_to_iac.core.agent_base import AgentBase
from diagram_to_iac.tools.hello.text_utils import extract_numbers_from_text, extract_numbers_from_text_with_duplicates
from diagram_to_iac.core.memory import (
    create_memory,
    LangGraphMemoryAdapter,
    agent_state_enabled,
    load_agent_state,
    save_agent_state,
    current_git_sha,
)
from diagram_to_iac.core.config_loader import get_config, get_config_value


# --- Pydantic Schemas for Agent I/O ---
class HelloAgentInput(BaseModel):
    query: str = Field(..., description="The input query or question for the HelloAgent")
    thread_id: str | None = Field(None, description="Optional thread ID for conversation history.")

class HelloAgentOutput(BaseModel):
    answer: str = Field(..., description="The final answer or result from the HelloAgent")
    thread_id: str = Field(..., description="The thread ID used for the conversation.")
    error_message: Optional[str] = Field(None, description="Optional error message if the agent run failed.")


# --- Helper Functions ---
# extract_numbers_from_text is now imported from text_utils


# --- Agent State Definition ---
class HelloAgentState(TypedDict):
    input_message: HumanMessage
    tool_output: Annotated[list[BaseMessage], lambda x, y: x + y]
    final_answer: str
    error_message: Optional[str] # New field for error messages


# --- Main Agent Class ---
class HelloAgent(AgentBase):
    """
    HelloAgent is an example LangGraph-based agent that can perform simple arithmetic
    operations (addition, multiplication) or provide direct answers using an LLM.
    It demonstrates configuration loading, Pydantic I/O schemas, error handling,
    logging, and persistent conversation state via SQLite.
    """
    def __init__(self, config_path: str = None, memory_type: str = "persistent"):
        """
        Initializes the HelloAgent.

        Args:
            config_path: Optional path to a YAML configuration file. If None,
                         loads from a default path.
            memory_type: Type of memory to use ("persistent", "memory", or "langgraph")
        
        Initializes configuration, logger, enhanced LLM router, memory system,
        checkpointer, and compiles the LangGraph runnable.
        """
        # Configure logger for this agent instance
        # Using __name__ for the logger is a common practice to get module-based loggers
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # BasicConfig should ideally be called once at application entry point.
        # Guard to avoid reconfiguring if already set (e.g., by another agent or app init)
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(
                level=logging.INFO, # Default level, can be overridden by env var or config later
                format='%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        # Load configuration using centralized system
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, 'config.yaml')
            self.logger.debug(f"Default config path set to: {config_path}")

        # Handle configuration loading with proper fallback and logging for tests
        if config_path:
            # First try to load agent-specific config directly for test compatibility
            if not os.path.exists(config_path):
                self.logger.warning(f"Configuration file not found at {config_path}. Using default values.")
                self._set_default_config()
            else:
                try:
                    with open(config_path, 'r') as f:
                        content = f.read().strip()
                        if not content:
                            self.logger.warning(f"Configuration file at {config_path} is empty. Using default values.")
                            self._set_default_config()
                        else:
                            f.seek(0)  # Reset file pointer
                            agent_config = yaml.safe_load(f)
                            if agent_config is None:
                                self.logger.warning(f"Configuration file at {config_path} is empty. Using default values.")
                                self._set_default_config()
                            else:
                                # Use centralized config as base and merge with agent-specific overrides
                                try:
                                    base_config = get_config()
                                    self.config = self._deep_merge(base_config, agent_config)
                                    self.logger.info(f"Configuration loaded successfully from {config_path}")
                                except Exception as e:
                                    # Fallback to agent-specific config only
                                    self.config = agent_config
                                    self.logger.info(f"Configuration loaded successfully from {config_path}")
                except yaml.YAMLError as e:
                    self.logger.error(f"Error parsing YAML configuration from {config_path}: {e}. Using default values.", exc_info=True)
                    self._set_default_config()
                except Exception as e:
                    self.logger.error(f"Unexpected error loading configuration from {config_path}: {e}. Using default values.", exc_info=True)
                    self._set_default_config()
        else:
            # No config path provided, use centralized config only
            try:
                self.config = get_config()
                self.logger.info(f"Configuration loaded successfully from centralized system")
            except Exception as e:
                self.logger.warning(f"Failed to load configuration via centralized system: {e}. Using default values.")
                self._set_default_config()

        # Ensure a dummy API key is set so tests can initialize the router without real credentials
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = "test-key"

        # Initialize enhanced LLM router
        self.llm_router = LLMRouter()
        self.logger.info("Enhanced LLM router initialized with multi-provider support")

        # Initialize enhanced memory system
        self.memory = create_memory(memory_type)
        self.logger.info(f"Enhanced memory system initialized: {type(self.memory).__name__}")

        self.logger.info(f"Initialized with LLM model: {self.config.get('llm', {}).get('model_name', 'N/A')}, Temperature: {self.config.get('llm', {}).get('temperature', 'N/A')}")

        # Initialize checkpointer - Reverting to MemorySaver
        self.logger.info("Using MemorySaver for checkpointer.")
        self.checkpointer = MemorySaver()

        # Register tools
        self.tools = {"add_two": add_two, "multiply_two": multiply_two}
        self.logger.info(f"Tools registered: {list(self.tools.keys())}")

        self.runnable = self._build_graph()

        # Load persistent agent state and determine if we should resume
        self.persistent_state_enabled = agent_state_enabled()
        self.agent_state = load_agent_state() if self.persistent_state_enabled else {}
        self.current_sha = current_git_sha() if self.persistent_state_enabled else None
        self._resume = (
            self.persistent_state_enabled
            and self.agent_state.get("commit_sha") == self.current_sha
            and "last_successful_node" in self.agent_state
        )

    def _set_default_config(self):
        self.logger.info("Setting default configuration for HelloAgent.")
        # Use hardcoded defaults when agent-specific config fails
        # This ensures test compatibility with expected DEFAULT_TEMP and DEFAULT_MODEL
        self.config = {
            'llm': {
                'model_name': "gpt-4o-mini",
                'temperature': 0.0
            },
            'routing_keys': {
                'addition': "ROUTE_TO_ADDITION",
                'multiplication': "ROUTE_TO_MULTIPLICATION"
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

    def _planner_llm_node(self, state: HelloAgentState):
        """LLM decides if tool is needed, and which specific tool to route to."""
        # Config values for the LLM
        llm_config = self.config.get('llm', {})
        # Don't provide defaults here - check if they're explicitly set in config
        model_name = llm_config.get('model_name')
        temperature = llm_config.get('temperature')
        
        # Use enhanced LLM router for agent-specific model selection
        try:
            if model_name is not None or temperature is not None:
                actual_model_name = model_name if model_name is not None else "gpt-4o-mini"
                actual_temperature = temperature if temperature is not None else 0.0
                self.logger.debug(
                    f"Planner using LLM: {actual_model_name}, Temp: {actual_temperature}"
                )
                llm = self.llm_router.get_llm(
                    model_name=actual_model_name,
                    temperature=actual_temperature,
                    agent_name="hello_agent",
                )
            else:
                self.logger.debug("Planner using agent-specific LLM configuration")
                llm = self.llm_router.get_llm_for_agent("hello_agent")
        except Exception as e:
            self.logger.error(
                f"Failed to get LLM from router: {e}. Falling back to local creation."
            )
            fallback_model = model_name or self.config.get("llm", {}).get("model_name", "gpt-4o-mini")
            fallback_temp = temperature if temperature is not None else self.config.get("llm", {}).get("temperature", 0.0)
            llm = self.llm_router._create_llm_instance(
                {
                    "model": fallback_model,
                    "temperature": fallback_temp,
                    "provider": self.llm_router._detect_provider(fallback_model),
                }
            )

        # Store conversation in memory
        query_content = state['input_message'].content
        self.memory.add_to_conversation("user", query_content, {"agent": "hello_agent", "node": "planner"})

        try:
            self.logger.debug(f"Planner LLM input message content: {query_content}")
            analysis_prompt_template = self.config.get('prompts', {}).get('planner_prompt', """User input: "{user_input}"

Analyze this input and determine the appropriate action:
1. If it's asking for addition (words like 'add', 'plus', 'sum', '+' symbol), respond with "{route_add}"
2. If it's asking for multiplication (words like 'multiply', 'times', '*' symbol), respond with "{route_multiply}"
3. If it's a general question not requiring math tools, provide a direct answer

Important: Only use routing responses if the input contains numbers that can be operated on.""")

            routing_keys = self.config.get('routing_keys', {
                "addition": "ROUTE_TO_ADDITION",
                "multiplication": "ROUTE_TO_MULTIPLICATION"
            })

            analysis_prompt = analysis_prompt_template.format(
                user_input=query_content,
                route_add=routing_keys['addition'],
                route_multiply=routing_keys['multiplication']
            )
            self.logger.debug(f"Planner LLM prompt: {analysis_prompt}")

            response = llm.invoke([HumanMessage(content=analysis_prompt)])
            self.logger.debug(f"Planner LLM raw response content: {response.content}")
            response_content = response.content.strip()

            # Store LLM response in memory
            self.memory.add_to_conversation("assistant", response_content, {"agent": "hello_agent", "node": "planner", "model": model_name})

            new_state_update = {}
            if routing_keys['addition'] in response_content:
                new_state_update = {"final_answer": "route_to_addition", "error_message": None}
            elif routing_keys['multiplication'] in response_content:
                new_state_update = {"final_answer": "route_to_multiplication", "error_message": None}
            else:
                new_state_update = {"final_answer": response.content, "error_message": None}

            self.logger.info(f"Planner LLM decision: {new_state_update.get('final_answer', 'N/A')}")
            return new_state_update
        except Exception as e:
            self.logger.error(f"LLM error in _planner_llm_node: {e}", exc_info=True)
            # Store error in memory
            self.memory.add_to_conversation("system", f"Error in planner: {str(e)}", {"agent": "hello_agent", "node": "planner", "error": True})
            return {
                "final_answer": "Sorry, I encountered an issue processing your request with the language model.",
                "error_message": str(e),
                "tool_output": state.get("tool_output", [])
            }

    def _addition_tool_node(self, state: HelloAgentState):
        """
        Handles addition operations. Extracts numbers from input, invokes the add_two tool,
        and updates the state with the result or an error message.
        Input from state: state['input_message'].content
        Output to state: Updates 'final_answer', 'tool_output', and 'error_message'.
        """
        self.logger.info(f"Addition tool node invoked for input: {state['input_message'].content}")
        try:
            text_content = state['input_message'].content
            found_numbers = extract_numbers_from_text_with_duplicates(text_content)
            self.logger.debug(f"Numbers found for addition: {found_numbers}")

            # Store tool invocation in memory
            self.memory.add_to_conversation("system", f"Addition tool invoked with numbers: {found_numbers}", 
                                          {"agent": "hello_agent", "node": "addition_tool", "numbers": found_numbers})

            new_state_update = {}
            if len(found_numbers) < 2:
                self.logger.warning(f"Not enough numbers found in '{text_content}' for addition.")
                error_msg = self.config.get('error_messages', {}).get(
                    'numbers_not_found_addition',
                    "Addition tool: Could not find two numbers in the input for addition."
                )
                # Store error in memory
                self.memory.add_to_conversation("system", error_msg, 
                                              {"agent": "hello_agent", "node": "addition_tool", "error": True})
                return {"final_answer": error_msg}

            # If we have enough numbers, proceed to try tool invocation
            num1, num2 = found_numbers[0], found_numbers[1]
            # result = add_two.invoke({"x": num1, "y": num2}) # Old direct call
            result = self.tools['add_two'].invoke({"x": num1, "y": num2})
            self.logger.debug(f"Addition tool raw result: {result}")
            
            # Store successful result in memory
            self.memory.add_to_conversation("system", f"Addition result: {num1} + {num2} = {result}", 
                                          {"agent": "hello_agent", "node": "addition_tool", "operation": "addition", "result": result})
            
            new_state_update = {
                "final_answer": str(result),
                "tool_output": [HumanMessage(content=f"Addition tool result: {num1} + {num2} = {result}")],
                "error_message": None
            }

            self.logger.info(f"Addition tool node result: {new_state_update.get('final_answer', 'N/A')}")
            return new_state_update
        except Exception as e:
            self.logger.error(f"Addition tool error: {e}", exc_info=True)
            # Store error in memory
            self.memory.add_to_conversation("system", f"Addition tool error: {str(e)}", 
                                          {"agent": "hello_agent", "node": "addition_tool", "error": True})
            return {
                "final_answer": "Sorry, I couldn't perform the addition due to an error.",
                "error_message": str(e),
                "tool_output": state.get("tool_output", [])
            }

    def _multiplication_tool_node(self, state: HelloAgentState):
        """
        Handles multiplication operations. Extracts numbers from input, invokes the multiply_two tool,
        and updates the state with the result or an error message.
        Input from state: state['input_message'].content
        Output to state: Updates 'final_answer', 'tool_output', and 'error_message'.
        """
        self.logger.info(f"Multiplication tool node invoked for input: {state['input_message'].content}")
        try:
            text_content = state['input_message'].content
            found_numbers = extract_numbers_from_text_with_duplicates(text_content)
            self.logger.debug(f"Numbers found for multiplication: {found_numbers}")

            # Store tool invocation in memory
            self.memory.add_to_conversation("system", f"Multiplication tool invoked with numbers: {found_numbers}", 
                                          {"agent": "hello_agent", "node": "multiplication_tool", "numbers": found_numbers})

            new_state_update = {}
            if len(found_numbers) < 2:
                self.logger.warning(f"Not enough numbers found in '{text_content}' for multiplication.")
                error_msg = self.config.get('error_messages', {}).get(
                    'numbers_not_found_multiplication',
                    "Multiplication tool: Could not find two numbers in the input for multiplication."
                )
                # Store error in memory
                self.memory.add_to_conversation("system", error_msg, 
                                              {"agent": "hello_agent", "node": "multiplication_tool", "error": True})
                return {"final_answer": error_msg}

            num1, num2 = found_numbers[0], found_numbers[1]
            # result = multiply_two.invoke({"x": num1, "y": num2}) # Old direct call
            result = self.tools['multiply_two'].invoke({"x": num1, "y": num2})
            self.logger.debug(f"Multiplication tool raw result: {result}")
            
            # Store successful result in memory
            self.memory.add_to_conversation("system", f"Multiplication result: {num1} * {num2} = {result}", 
                                          {"agent": "hello_agent", "node": "multiplication_tool", "operation": "multiplication", "result": result})
            
            new_state_update = {
                "final_answer": str(result),
                "tool_output": [HumanMessage(content=f"Multiplication tool result: {num1} * {num2} = {result}")],
                "error_message": None
            }

            self.logger.info(f"Multiplication tool node result: {new_state_update.get('final_answer', 'N/A')}")
            return new_state_update
        except Exception as e:
            self.logger.error(f"Multiplication tool error: {e}", exc_info=True)
            # Store error in memory
            self.memory.add_to_conversation("system", f"Multiplication tool error: {str(e)}", 
                                          {"agent": "hello_agent", "node": "multiplication_tool", "error": True})
            return {
                "final_answer": "Sorry, I couldn't perform the multiplication due to an error.",
                "error_message": str(e),
                "tool_output": state.get("tool_output", [])
            }

    def _route_after_planner(self, state: HelloAgentState):
        """
        Routes to the appropriate tool node or ends the graph based on the 'final_answer'
        field in the state, which is set by the planner. Also routes to END if an error
        is present in the state.
        Input from state: state['final_answer'], state['error_message']
        Output: Name of the next node (str) or END.
        """
        self.logger.debug(f"Routing after planner. Current state final_answer: '{state.get('final_answer')}', error_message: '{state.get('error_message')}'")
        if state.get("error_message"): # Check if an error occurred in the planner node
            self.logger.warning(f"Error detected in planner state, routing to END. Error: {state['error_message']}")
            return END

        final_answer = state.get("final_answer", "")
        
        # Use the same routing keys as the planner for consistency
        if final_answer == "route_to_addition":
            return "addition_tool"
        elif final_answer == "route_to_multiplication":
            return "multiplication_tool"
        return END

    def _build_graph(self):
        graph_builder = StateGraph(HelloAgentState)
        graph_builder.add_node("planner_llm", self._planner_llm_node)
        graph_builder.add_node("addition_tool", self._addition_tool_node)
        graph_builder.add_node("multiplication_tool", self._multiplication_tool_node)

        graph_builder.set_entry_point("planner_llm")

        routing_map = self.config.get('routing_map', {
            "addition_tool": "addition_tool",
            "multiplication_tool": "multiplication_tool",
            END: END
        })
        graph_builder.add_conditional_edges(
            "planner_llm",
            self._route_after_planner,
            routing_map
        )
        graph_builder.add_edge("addition_tool", END)
        graph_builder.add_edge("multiplication_tool", END)

        # Use the instance checkpointer
        return graph_builder.compile(checkpointer=self.checkpointer)

    def run(self, agent_input: HelloAgentInput) -> HelloAgentOutput:
        """Runs the agent with the given input."""
        current_thread_id = agent_input.thread_id if agent_input.thread_id is not None else str(uuid.uuid4())
        self.logger.info(f"Run invoked with query: '{agent_input.query}', thread_id: {current_thread_id}")
        if self._resume and self.agent_state.get("final_answer"):
            self.logger.info("Using saved agent state to skip execution")
            return HelloAgentOutput(answer=self.agent_state.get("final_answer", ""), thread_id=current_thread_id, error_message=self.agent_state.get("error_message"))



        initial_state = {
            "input_message": HumanMessage(content=agent_input.query),
            "tool_output": [],
            "error_message": None
        }

        langgraph_config = {"configurable": {"thread_id": current_thread_id}}

        result_state = self.runnable.invoke(initial_state, config=langgraph_config)

        output: HelloAgentOutput
        final_answer_str = result_state.get("final_answer", "No answer found.")
        error_msg_str = result_state.get("error_message")

        if error_msg_str:
            if final_answer_str and final_answer_str.startswith("Sorry, I encountered an issue"):
                self.logger.error(f"Run completed with error. Final answer: '{final_answer_str}', Error detail: {error_msg_str}, Thread ID: {current_thread_id}")
                # final_answer_str remains the "Sorry..." message
            else:
                routing_keys_values = [
                    self.config.get('routing_keys', {}).get('addition', 'ROUTE_TO_ADDITION'),
                    self.config.get('routing_keys', {}).get('multiplication', 'ROUTE_TO_MULTIPLICATION')
                ]
                if final_answer_str in routing_keys_values and error_msg_str: # If final_answer is a route key but there's an error
                     self.logger.error(f"Run completed with error. Error detail: {error_msg_str}, (Final answer was a routing key: {final_answer_str}), Thread ID: {current_thread_id}")
                     final_answer_str = f"An error occurred: {error_msg_str}" # Prioritize the error message string
                elif error_msg_str: # If there's an error message and final_answer is not a routing key
                     self.logger.info(f"Run completed with specific message/error. Final answer: '{final_answer_str}', Error detail: {error_msg_str}, Thread ID: {current_thread_id}")
                     # final_answer_str might already be the specific error (e.g., "Not enough numbers...")
                     # or it could be a direct LLM response if planner failed to route but didn't set "Sorry..."
                     # If final_answer is not a "Sorry..." message, and error_message is present, it might be better to use error_message.
                     # This logic depends on how nodes set final_answer vs error_message.
                     # For now, if error_message is present and final_answer isn't a "Sorry..." message, we assume final_answer might be a more specific error or relevant info.
                # If error_msg_str is set, it implies something went wrong.
                # The final_answer_str should reflect this.
                # If final_answer is already a "Sorry..." message, it's fine.
                # If final_answer is something else (e.g. a routing key, or previous valid data) but error_message is now set,
                # we should probably use the error_message or the "Sorry..." message.
                # Let's simplify: if error_msg_str is present, the answer should reflect an error.
                if not (final_answer_str and final_answer_str.startswith("Sorry, I encountered an issue")):
                    # If final_answer isn't already a generic "Sorry..." message, but an error occurred,
                    # use the more specific error_message if it's not just a technical detail.
                    # This part of logic might need more refinement based on how error_message vs final_answer is set in nodes.
                    # For the current error handling, nodes set final_answer to "Sorry..." AND error_message to details.
                    # Or for validation like "not enough numbers", final_answer is the specific warning, and error_message is technical.
                    # The current code already prioritizes the "Sorry..." message if it exists.
                    # If not, and error_message exists, it means final_answer is something else (e.g. "Not enough numbers...").
                    # This is fine.
                    pass # Current logic for final_answer_str should be okay based on node error setting.


        else:
            self.logger.info(
                f"Run completed successfully. Output answer: '{final_answer_str}', Thread ID: {current_thread_id}"
            )

        history = list(self.runnable.get_state_history(langgraph_config))
        last_node = None
        if len(history) >= 2:
            chron = list(reversed(history))
            before_end = chron[-2]
            if before_end.next:
                last_node = before_end.next[0]

        self.agent_state = {
            "commit_sha": self.current_sha,
            "last_successful_node": last_node,
            "guard_results": {"startup": True},
            "final_answer": final_answer_str,
            "error_message": error_msg_str,
            "thread_id": current_thread_id,
        }
        if self.persistent_state_enabled:
            save_agent_state(self.agent_state)

        return HelloAgentOutput(
            answer=final_answer_str,
            thread_id=current_thread_id,
            error_message=error_msg_str,
        )

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history from memory.
        
        Returns:
            List[Dict]: List of conversation messages with metadata
        """
        return self.memory.get_conversation_history()
    
    def get_memory_state(self) -> Dict[str, Any]:
        """
        Get the current memory state.
        
        Returns:
            Dict: Current state stored in memory
        """
        return self.memory.get_state()
    
    def clear_memory(self) -> None:
        """Clear all memory including conversation history."""
        self.memory.clear_state()
        self.logger.info("Memory cleared including conversation history")

    def plan(self, input_text: str, **kwargs):
        """
        Generates a plan for the agent to execute (required by AgentBase).
        For HelloAgent, the plan is simply to analyze the input and determine the appropriate action.
        
        Args:
            input_text: The input query to plan for
            **kwargs: Additional parameters (e.g., thread_id)
            
        Returns:
            dict: A plan containing the input and any additional context
        """
        self.logger.info(f"Planning for input: '{input_text}'")
        
        plan = {
            "input_text": input_text,
            "predicted_action": "analyze_and_route",
            "description": "Analyze input to determine if math operations are needed or if direct LLM response is sufficient"
        }
        
        # Simple analysis to predict the route
        if any(word in input_text.lower() for word in ['add', 'plus', 'sum', '+']):
            plan["predicted_route"] = "addition_tool"
        elif any(word in input_text.lower() for word in ['multiply', 'times', '*']):
            plan["predicted_route"] = "multiplication_tool"
        else:
            plan["predicted_route"] = "llm_response"
            
        return plan

    def report(self, result=None, **kwargs):
        """
        Reports the results or progress of the agent's execution (required by AgentBase).
        
        Args:
            result: The result to report (HelloAgentOutput or string)
            **kwargs: Additional parameters
            
        Returns:
            dict: A report containing execution details
        """
        if isinstance(result, HelloAgentOutput):
            report = {
                "status": "completed",
                "answer": result.answer,
                "thread_id": result.thread_id,
                "error_message": result.error_message,
                "success": result.error_message is None
            }
        elif isinstance(result, str):
            report = {
                "status": "completed", 
                "answer": result,
                "success": True
            }
        else:
            report = {
                "status": "no_result",
                "message": "No result provided to report"
            }
            
        self.logger.info(f"Agent execution report: {report}")
        return report


# --- Main execution for demonstration ---
if __name__ == "__main__":
    # Example: Instantiate the agent (will load config from default path)
    agent = HelloAgent() # Uses MemorySaver by default now

    print("Hello LangGraph Agent (Configurable, Pydantic I/O, MemorySaver)!")
    print("=" * 50)
    
    # Create agent instance
    agent = HelloAgent()
    
    test_queries = [
        "What is 4 + 5?",
        "What is 4 * 5?",
        "Please add 7 and 3 together",
        "Multiply 6 times 8",
        "What is 2 divided by 2?",
        "Can you add 10 and 20 for me and also tell me a joke?"
    ]

    for query_text in test_queries:
        agent_input_obj = HelloAgentInput(query=query_text)
        output_obj = agent.run(agent_input_obj)
        print(f"Input Query: '{query_text}'\nAgent Answer: '{output_obj.answer}'")
        print("-" * 50)

    # Example with thread_id
    print("\nRunning with a specific thread_id (for potential conversation history):")
    convo_thread_id = "my-test-conversation-123"
    input1 = HelloAgentInput(query="What is 10 + 10?", thread_id=convo_thread_id)
    output1 = agent.run(input1)
    print(f"Input Query: '{input1.query}' (Thread: {convo_thread_id})\nAgent Answer: '{output1.answer}'")

    # Potentially, a follow-up on the same thread (MemorySaver would keep state)
    # For this agent, most interactions are single-shot math, but if it had memory:
    # input2 = HelloAgentInput(query="And what about adding 5 to that?", thread_id=convo_thread_id)
    # output2 = agent.run(input2)
    # print(f"Input Query: '{input2.query}' (Thread: {convo_thread_id})\nAgent Answer: '{output2.answer}'")
    print("-" * 50)

    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set. LLM calls might fail if not configured otherwise.")
        print("Please set it as an environment variable if using OpenAI models without explicit API key config.")
