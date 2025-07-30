"""
Shell Agent - Multi-Agent Architecture

This agent specializes in secure shell command execution and serves as a shared service
for other agents (Git, Terraform, etc.) that need to execute shell commands.

Exports shell tools for now. Agent implementation coming later.
"""

from diagram_to_iac.tools.shell import shell_exec, ShellExecutor
from .agent import ShellAgent, ShellAgentInput, ShellAgentOutput
from .detector import build_stack_histogram

__all__ = [
    "shell_exec",
    "ShellExecutor",
    "ShellAgent",
    "ShellAgentInput",
    "ShellAgentOutput",
    "build_stack_histogram",
]
