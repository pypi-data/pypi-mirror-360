# This file makes the 'agents' module a package
# and can be used to expose specific agents or functionalities.

# Import agents from their new organized locations
# HelloAgent has heavyweight optional dependencies (langchain).
# Wrap import in a try/except so basic functionality works even when
# those packages are missing (e.g. during lightweight test runs).
try:
    from .hello_langgraph.agent import HelloAgent
except Exception:  # pragma: no cover - optional dependency may be missing
    HelloAgent = None

try:
    from .git_langgraph.agent import GitAgent
except Exception:  # pragma: no cover - optional dependency may be missing
    GitAgent = None
from .supervisor_langgraph.agent import (
    SupervisorAgent,
    SupervisorAgentInput,
    SupervisorAgentOutput,
)

# Maintain backward compatibility with old names
HelloLangGraphAgent = HelloAgent
GitAgent = GitAgent

# Export all agent classes
__all__ = ["GitAgent", "SupervisorAgent", "SupervisorAgentInput", "SupervisorAgentOutput"]
if HelloAgent is not None:
    __all__.extend(["HelloAgent", "HelloLangGraphAgent"])
