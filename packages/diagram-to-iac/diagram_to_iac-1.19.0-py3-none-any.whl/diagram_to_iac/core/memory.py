from typing import Any, Dict, List, Optional
import json
import os
from pathlib import Path
from subprocess import check_output, CalledProcessError, TimeoutExpired
# Intended to be a thin wrapper over LangGraph's StateGraph node store.
# For now, a simple dictionary-based state.

class Memory:
    """
    Thin wrapper over LangGraph’s StateGraph node store;
    later could be swapped for Redis or another persistent store.
    LangGraph nodes can read/write via graph.state.
    This class provides a conceptual placeholder for that state management.
    """
    def __init__(self):
        self._state: Dict[str, Any] = {}

    def get_state(self) -> Dict[str, Any]:
        """Retrieves the current state."""
        return self._state

    def update_state(self, key: str, value: Any) -> None:
        """Updates a specific key in the state."""
        self._state[key] = value

    def replace_state(self, new_state: Dict[str, Any]) -> None:
        """Replaces the entire state with a new one."""
        self._state = new_state

    def clear_state(self) -> None:
        """Clears the state."""
        self._state = {}

# Enhanced memory system - import the new capabilities
from .enhanced_memory import (
    MemoryInterface, 
    InMemoryMemory, 
    PersistentFileMemory, 
    LangGraphMemoryAdapter,
    create_memory
)

# Add conversation tracking to the original Memory class
class EnhancedMemory(Memory):
    """
    Enhanced version of the original Memory class with conversation tracking.
    Provides backward compatibility while adding new features.
    """
    
    def __init__(self):
        super().__init__()
        self._conversation_history: List[Dict[str, Any]] = []
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self._conversation_history.copy()
    
    def add_to_conversation(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to conversation history."""
        from datetime import datetime
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self._conversation_history.append(message)
    
    def clear_state(self) -> None:
        """Clear both state and conversation history."""
        super().clear_state()
        self._conversation_history = []

# Example of how it might be used with LangGraph (conceptual)
# from langgraph.graph import StateGraph
#
# class AgentState(TypedDict):
#     input_query: str
#     processed_data: Any
#     final_result: str
#
# graph = StateGraph(AgentState)
# memory_instance = Memory() # This would be integrated with the graph's actual state mechanism

# --- Agent state persistence helpers ---

def _get_workspace_aware_agent_state_path() -> Path:
    """Get workspace-aware path for agent state file."""
    # Check for workspace base environment variable first
    workspace_base = os.environ.get("WORKSPACE_BASE", "")
    
    # Avoid Python installation paths
    if (workspace_base and 
        "/usr/local/lib/python" not in workspace_base and
        "/site-packages" not in workspace_base and
        "site-packages" not in workspace_base):
        return Path(workspace_base) / "data" / "state" / ".agent_state" / "agent_state.json"
    
    # Try current working directory if it's not a Python installation path
    try:
        cwd = Path.cwd()
        if ("/usr/local/lib/python" not in str(cwd) and "/site-packages" not in str(cwd)):
            return cwd / "data" / "state" / ".agent_state" / "agent_state.json"
    except (OSError, PermissionError):
        pass
    
    # Container workspace path
    if Path("/workspace").exists():
        return Path("/workspace") / "data" / "state" / ".agent_state" / "agent_state.json"
    
    # Fallback to /tmp for container environments
    return Path("/tmp") / "diagram_to_iac" / "state" / ".agent_state" / "agent_state.json"

# Default path for the persistent agent state JSON file. Allows override via
# `AGENT_STATE_FILE` environment variable for testing.
_DEFAULT_AGENT_STATE_PATH = _get_workspace_aware_agent_state_path()
AGENT_STATE_PATH = Path(os.environ.get("AGENT_STATE_FILE", _DEFAULT_AGENT_STATE_PATH))


def agent_state_enabled() -> bool:
    """Return ``True`` if persistent agent state should be used."""
    return os.environ.get("AGENT_STATE_ENABLED", "0") == "1"


def load_agent_state() -> Dict[str, Any]:
    """Load agent state from ``AGENT_STATE_PATH`` if it exists and persistence is enabled."""
    if not agent_state_enabled():
        return {}
    if AGENT_STATE_PATH.exists():
        try:
            with open(AGENT_STATE_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_agent_state(state: Dict[str, Any]) -> None:
    """Persist agent state to ``AGENT_STATE_PATH`` if persistence is enabled."""
    if not agent_state_enabled():
        return
    AGENT_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AGENT_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def current_git_sha() -> Optional[str]:
    """Return the current git commit SHA, or ``None`` if unavailable."""
    try:
        return check_output(
            ["git", "rev-parse", "HEAD"], 
            text=True, 
            timeout=5,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        ).strip()
    except Exception:
        return None

