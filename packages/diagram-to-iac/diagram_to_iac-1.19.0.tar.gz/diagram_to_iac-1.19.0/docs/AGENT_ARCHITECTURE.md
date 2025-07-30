# Agent Architecture in DevOps-in-a-Box (diagram-to-iac)

This document provides an overview of the agent system within the `diagram-to-iac` project. The system is built upon a base agent class and includes several specialized agents that collaborate to automate Repo-to-Deployment (R2D) workflows.

## Core Concept: `AgentBase`

All specialized agents in this project inherit from the `AgentBase` class (`src/diagram_to_iac/core/agent_base.py`). This class serves as a foundational blueprint and defines a common interface that all agents must implement.

*   **Purpose**: `AgentBase` establishes consistency and modularity, making it easier to manage and integrate different agents into the larger system.
*   **Abstract Base Class (ABC)**: It's an abstract class and is not meant to be instantiated directly. Concrete agent classes must implement its abstract methods.
*   **Key Abstract Methods**:
    *   `plan(self, *args, **kwargs)`: Outlines the steps or strategy the agent will take to accomplish a given task. For example, analyzing an input diagram or breaking down IaC generation into smaller actions.
    *   `run(self, *args, **kwargs)`: The primary execution method. It carries out the actions defined in the plan, which might involve invoking LLMs, calling specific tools, processing data, or interacting with other agents.
    *   `report(self, *args, **kwargs)`: Used by the agent to communicate its findings, results, progress, or any issues encountered. This could be returning generated IaC code, a summary of actions, or status signals.

By enforcing this structure, `AgentBase` ensures that all agents within the `diagram-to-iac` system have a predictable set of capabilities and can be orchestrated effectively.

## The Agent Team

The R2D workflow is orchestrated by a `SupervisorAgent` which coordinates a team of specialized agents. Each agent has a distinct role:

| Agent             | Primary Responsibilities                                                                 | Location                                                    | README                                                                       |
| :---------------- | :--------------------------------------------------------------------------------------- | :---------------------------------------------------------- | :--------------------------------------------------------------------------- |
| **SupervisorAgent** | Orchestrates the overall R2D workflow, manages state, routes tasks to other agents.      | `src/diagram_to_iac/agents/supervisor_langgraph/`           | [Details](../src/diagram_to_iac/agents/supervisor_langgraph/README.md)     |
| **GitAgent**        | Handles all Git-related operations: cloning repositories, managing branches, creating PRs. | `src/diagram_to_iac/agents/git_langgraph/`                  | [Details](../src/diagram_to_iac/agents/git_langgraph/README.md)            |
| **ShellAgent**      | Securely executes shell commands, detects repository stack (Terraform, etc.).            | `src/diagram_to_iac/agents/shell_langgraph/`                | [Details](../src/diagram_to_iac/agents/shell_langgraph/README.md)          |
| **TerraformAgent**  | Manages Terraform operations: `init`, `plan`, `apply`. Classifies errors, performs cost scans. | `src/diagram_to_iac/agents/terraform_langgraph/`            | [Details](../src/diagram_to_iac/agents/terraform_langgraph/README.md)      |
| **PolicyAgent**     | Performs security and compliance checks, typically using tools like `tfsec` and OPA.     | `src/diagram_to_iac/agents/policy_agent/`                   | [Details](../src/diagram_to_iac/agents/policy_agent/README.md)             |
| **VisionAgent**     | (If applicable) Analyzes visual diagrams (e.g., PNGs of architectures) to extract IaC requirements. | `src/diagram_to_iac/agents/vision_agent_README.md` (Conceptual)    | [Details](../src/diagram_to_iac/agents/vision_agent_README.md)             |
| **HelloAgent**      | A simple example agent demonstrating core agent capabilities and LangGraph usage.        | `src/diagram_to_iac/agents/hello_langgraph/`                | [Details](../src/diagram_to_iac/agents/hello_langgraph/README.md)          |

*(Note: The VisionAgent README is at `src/diagram_to_iac/agents/vision_agent_README.md` as it's conceptual and doesn't have its own sub-directory.)*

## Agent Interaction Model

Typically, a user request (e.g., via a GitHub Issue) triggers the `SupervisorAgent`.
1.  The `SupervisorAgent` plans the necessary steps.
2.  It then invokes other specialized agents (GitAgent, ShellAgent, TerraformAgent, etc.) in sequence or based on conditional logic.
3.  Each agent performs its task and reports back to the Supervisor.
4.  The `SupervisorAgent` consolidates results, manages error handling (e.g., creating GitHub issues for human intervention), and provides a final report.

This multi-agent system allows for complex DevOps workflows to be broken down into manageable, specialized tasks, handled by agents optimized for those tasks. The use of LangGraph facilitates the definition and execution of these stateful, graph-based agent interactions.

For developers looking to understand or contribute to specific agents, please refer to their individual README files linked above and the [Developer Guide](./DEVELOPER_GUIDE.md).
