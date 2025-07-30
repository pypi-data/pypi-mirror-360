from typing import Any, Dict, Optional, List
from abc import ABC, abstractmethod
import json
import os
from pathlib import Path

try:
    from .config_loader import get_config_value
except ImportError:
    # Fallback for tests or standalone usage
    def get_config_value(path: str, default: Any = None) -> Any:
        return default

# Abstract base for memory implementations
class MemoryInterface(ABC):
    """Abstract interface for agent memory systems."""
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Retrieve the current state."""
        pass
    
    @abstractmethod
    def update_state(self, key: str, value: Any) -> None:
        """Update a specific key in the state."""
        pass
    
    @abstractmethod
    def replace_state(self, new_state: Dict[str, Any]) -> None:
        """Replace the entire state with a new one."""
        pass
    
    @abstractmethod
    def clear_state(self) -> None:
        """Clear the state."""
        pass
    
    @abstractmethod
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        pass
    
    @abstractmethod
    def add_to_conversation(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to conversation history."""
        pass


class InMemoryMemory(MemoryInterface):
    """
    Simple in-memory implementation of the memory interface.
    Data is lost when the process ends.
    """
    
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._conversation_history: List[Dict[str, Any]] = []

    def get_state(self) -> Dict[str, Any]:
        """Retrieve the current state."""
        return self._state.copy()

    def update_state(self, key: str, value: Any) -> None:
        """Update a specific key in the state."""
        self._state[key] = value

    def replace_state(self, new_state: Dict[str, Any]) -> None:
        """Replace the entire state with a new one."""
        self._state = new_state.copy()

    def clear_state(self) -> None:
        """Clear the state."""
        self._state = {}
        self._conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self._conversation_history.copy()
    
    def add_to_conversation(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": self._get_timestamp(),
            "metadata": metadata or {}
        }
        self._conversation_history.append(message)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        from datetime import datetime
        return datetime.now().isoformat()


class PersistentFileMemory(MemoryInterface):
    """
    File-based memory implementation that persists state to disk.
    Useful for maintaining state across agent restarts.
    """
    
    def __init__(self, file_path: Optional[str] = None):
        if file_path is None:
            # Get workspace base from environment variable first, then config with fallback
            workspace_base = os.environ.get("WORKSPACE_BASE") or get_config_value("system.workspace_base", "/workspace")
            
            # Default to workspace or /tmp directory for container safety
            try:
                # Try workspace first (from environment or config)
                base_dir = Path(workspace_base) if Path(workspace_base).exists() else Path("/tmp/diagram_to_iac")
                
                # Safety check: Never use Python installation paths
                cwd = Path.cwd()
                if "/usr/local/lib/python" in str(cwd) or "/site-packages" in str(cwd):
                    # Force use of /tmp if current directory is in Python installation
                    base_dir = Path("/tmp/diagram_to_iac")
                
                data_dir = base_dir / "data" / "db"
                data_dir.mkdir(parents=True, exist_ok=True)
                file_path = data_dir / "agent_memory.json"
            except (PermissionError, OSError):
                # Fallback to /tmp for container environments
                data_dir = Path("/tmp") / "diagram_to_iac" / "data" / "db"
                data_dir.mkdir(parents=True, exist_ok=True)
                file_path = data_dir / "agent_memory.json"
        
        self.file_path = Path(file_path)
        self._state: Dict[str, Any] = {}
        self._conversation_history: List[Dict[str, Any]] = []
        self._load_data()

    def _load_data(self) -> None:
        """Load state from the file."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    self._state = data.get('state', {})
                    self._conversation_history = data.get('conversation_history', [])
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load memory from {self.file_path}: {e}")
                self._state = {}
                self._conversation_history = []
        else:
            self._state = {}
            self._conversation_history = []

    def _save_data(self) -> None:
        """Save current state to the file."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'state': self._state,
                'conversation_history': self._conversation_history
            }
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save memory to {self.file_path}: {e}")

    def get_state(self) -> Dict[str, Any]:
        """Retrieve the current state."""
        return self._state.copy()

    def update_state(self, key: str, value: Any) -> None:
        """Update a specific key in the state."""
        self._state[key] = value
        self._save_data()

    def replace_state(self, new_state: Dict[str, Any]) -> None:
        """Replace the entire state with a new one."""
        self._state = new_state.copy()
        self._save_data()

    def clear_state(self) -> None:
        """Clear the state and remove the file."""
        self._state = {}
        self._conversation_history = []
        # Remove the file completely
        if self.file_path.exists():
            try:
                self.file_path.unlink()
            except Exception as e:
                print(f"Warning: Could not remove memory file {self.file_path}: {e}")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self._conversation_history.copy()
    
    def add_to_conversation(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": self._get_timestamp(),
            "metadata": metadata or {}
        }
        self._conversation_history.append(message)
        self._save_data()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        from datetime import datetime
        return datetime.now().isoformat()


class LangGraphMemoryAdapter(MemoryInterface):
    """
    Adapter to integrate custom memory with LangGraph's checkpointer system.
    Provides a bridge between our memory interface and LangGraph's state management.
    """
    
    def __init__(self, base_memory: MemoryInterface):
        self.base_memory = base_memory
    
    def get_state(self) -> Dict[str, Any]:
        """Retrieve the current state."""
        return self.base_memory.get_state()
    
    def update_state(self, key: str, value: Any) -> None:
        """Update a specific key in the state."""
        self.base_memory.update_state(key, value)
    
    def replace_state(self, new_state: Dict[str, Any]) -> None:
        """Replace the entire state with a new one."""
        self.base_memory.replace_state(new_state)
    
    def clear_state(self) -> None:
        """Clear the state."""
        self.base_memory.clear_state()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.base_memory.get_conversation_history()
    
    def add_to_conversation(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to conversation history."""
        self.base_memory.add_to_conversation(role, content, metadata)
    
    def sync_from_langgraph_state(self, langgraph_state: Dict[str, Any]) -> None:
        """
        Sync state from LangGraph state format to memory.
        
        Args:
            langgraph_state: State dictionary from LangGraph
        """
        # Store the entire LangGraph state
        self.base_memory.update_state("langgraph_state", langgraph_state)
        
        # Also extract and store specific components for convenience
        if "tool_output" in langgraph_state and langgraph_state["tool_output"]:
            self.base_memory.update_state("last_tool_outputs", langgraph_state["tool_output"])
        
        # Add timestamp for sync tracking
        from datetime import datetime
        self.base_memory.update_state("last_sync", datetime.now().isoformat())
    
    def sync_to_langgraph_state(self, base_langgraph_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync state from our memory to LangGraph state format.
        
        Args:
            base_langgraph_state: Base LangGraph state to merge memory context into
            
        Returns:
            Updated LangGraph state with memory context
        """
        # Start with the base state
        updated_state = base_langgraph_state.copy()
        
        # Get current memory state and conversation
        state = self.get_state()
        conversation = self.get_conversation_history()
        
        # Create memory context
        memory_context = {}
        
        # Add conversation history to memory context
        if conversation:
            memory_context["conversation_history"] = conversation
        
        # Add other memory state (excluding special keys)
        for key, value in state.items():
            if key not in ["langgraph_state", "last_sync"]:
                memory_context[key] = value
        
        # Add memory context to the updated state
        updated_state["memory_context"] = memory_context
        
        return updated_state
    
    def get_checkpoint_metadata(self) -> Dict[str, Any]:
        """Get metadata for LangGraph checkpoint."""
        return {
            "conversation_length": len(self.get_conversation_history()),
            "state_keys": list(self.get_state().keys()),
            "last_updated": self.base_memory._get_timestamp() if hasattr(self.base_memory, '_get_timestamp') else None
        }


# Factory function for easy memory creation
def create_memory(memory_type: str = "in_memory", **kwargs) -> MemoryInterface:
    """
    Factory function to create memory instances.
    
    Args:
        memory_type: Type of memory to create ("in_memory", "memory", "persistent", or "langgraph")
        **kwargs: Additional arguments for memory initialization
    
    Returns:
        MemoryInterface: Configured memory instance
    """
    if memory_type in ("in_memory", "memory"):
        return InMemoryMemory()
    elif memory_type == "persistent":
        return PersistentFileMemory(**kwargs)
    elif memory_type == "langgraph":
        # Create LangGraph adapter with specified base memory type
        base_memory_type = kwargs.pop('base_memory_type', 'in_memory')
        if base_memory_type == "persistent":
            base_memory = PersistentFileMemory(**kwargs)
        else:
            base_memory = InMemoryMemory()
        return LangGraphMemoryAdapter(base_memory)
    else:
        raise ValueError(f"Unknown memory type: {memory_type}")
