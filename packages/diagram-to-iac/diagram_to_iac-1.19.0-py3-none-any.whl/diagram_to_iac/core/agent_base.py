from abc import ABC, abstractmethod

class AgentBase(ABC):
    """Abstract base class for all agents."""

    @abstractmethod
    def plan(self, *args, **kwargs):
        """Generates a plan for the agent to execute."""
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        """Executes the agent's plan or a given task."""
        pass

    @abstractmethod
    def report(self, *args, **kwargs):
        """Reports the results or progress of the agent's execution."""
        pass
