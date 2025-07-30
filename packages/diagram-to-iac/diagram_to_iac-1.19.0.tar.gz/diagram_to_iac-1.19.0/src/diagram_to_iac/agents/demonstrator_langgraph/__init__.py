"""
DemonstratorAgent for intelligent interactive dry-run demonstrations.

This agent handles all dry-run interactions in an organic, agentic way,
keeping the SupervisorAgent clean and focused.
"""

from .agent import DemonstratorAgent, DemonstratorAgentInput, DemonstratorAgentOutput

__all__ = ["DemonstratorAgent", "DemonstratorAgentInput", "DemonstratorAgentOutput"]
