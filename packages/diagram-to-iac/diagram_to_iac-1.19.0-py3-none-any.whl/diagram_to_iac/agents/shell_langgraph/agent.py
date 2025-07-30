import uuid
import logging
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from diagram_to_iac.tools.shell import ShellExecInput, ShellExecutor
from diagram_to_iac.core.agent_base import AgentBase
from diagram_to_iac.core.memory import create_memory
from diagram_to_iac.services.observability import log_event


class ShellAgentInput(BaseModel):
    command: str = Field(..., description="Shell command to execute")
    cwd: Optional[str] = Field(None, description="Working directory")
    timeout: Optional[int] = Field(None, description="Execution timeout")
    thread_id: Optional[str] = Field(None, description="Optional thread id")


class ShellAgentOutput(BaseModel):
    output: str = Field(..., description="Command output")
    exit_code: int = Field(..., description="Exit code")
    thread_id: str = Field(..., description="Thread id used")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class ShellAgentState(TypedDict):
    input_message: HumanMessage
    cwd: Optional[str]
    timeout: Optional[int]
    result: str
    exit_code: int
    error_message: Optional[str]


class ShellAgent(AgentBase):
    """Minimal agent that executes a single shell command using ShellExecutor."""

    def __init__(self, memory_type: str = "persistent"):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        self.memory_type = memory_type
        self.memory = create_memory(memory_type)
        self.checkpointer = MemorySaver()
        self.shell_executor = ShellExecutor(memory_type=memory_type)
        self.runnable = self._build_graph()

    def _shell_node(self, state: ShellAgentState) -> ShellAgentState:
        shell_input = ShellExecInput(
            command=state["input_message"].content,
            cwd=state.get("cwd"),
            timeout=state.get("timeout"),
        )
        try:
            result = self.shell_executor.shell_exec(shell_input)
            state["result"] = result.output
            state["exit_code"] = result.exit_code
            state["error_message"] = None
        except Exception as e:
            state["result"] = ""
            state["exit_code"] = -1
            state["error_message"] = str(e)
        return state

    def _build_graph(self):
        graph_builder = StateGraph(ShellAgentState)
        graph_builder.add_node("shell_node", self._shell_node)
        graph_builder.set_entry_point("shell_node")
        graph_builder.add_edge("shell_node", END)
        return graph_builder.compile(checkpointer=self.checkpointer)

    def run(self, agent_input: ShellAgentInput) -> ShellAgentOutput:
        thread_id = agent_input.thread_id or str(uuid.uuid4())
        log_event(
            "shell_agent_run_start",
            command=agent_input.command,
            thread_id=thread_id,
        )
        initial_state: ShellAgentState = {
            "input_message": HumanMessage(content=agent_input.command),
            "cwd": agent_input.cwd,
            "timeout": agent_input.timeout,
            "result": "",
            "exit_code": 0,
            "error_message": None,
        }

        result_state = self.runnable.invoke(
            initial_state, config={"configurable": {"thread_id": thread_id}}
        )

        output = ShellAgentOutput(
            output=result_state.get("result", ""),
            exit_code=result_state.get("exit_code", -1),
            thread_id=thread_id,
            error_message=result_state.get("error_message"),
        )

        log_event(
            "shell_agent_run_end",
            thread_id=thread_id,
            exit_code=output.exit_code,
            error=output.error_message,
        )

        return output

    # AgentBase requirements
    def plan(self, *args, **kwargs):
        return {"description": "Execute shell command"}

    def report(self, *args, **kwargs):
        return {}
