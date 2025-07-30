# Developer Guide: diagram-to-iac (DevOps-in-a-Box)

Welcome, developer! This guide provides information on how to contribute to the `diagram-to-iac` project, set up your local development environment, understand the architecture, and follow our coding standards.

## 1. Project Overview & Architecture

The `diagram-to-iac` project, also known as DevOps-in-a-Box, is a containerized multi-agent system designed to automate "Repo-to-Deployment" (R2D) workflows. It leverages AI (primarily through LLMs) to analyze repositories, manage infrastructure as code (IaC) with Terraform, and interact with GitHub.

**Key Architectural Components:**

*   **Multi-Agent System:** Built with Python and LangGraph, featuring specialized agents (Supervisor, Git, Shell, Terraform, Policy, etc.) that inherit from a common `AgentBase`. For details, see [Agent Architecture](./AGENT_ARCHITECTURE.md).
*   **Containerization:** The system runs within Docker containers, both for local development and for GitHub Actions.
    *   Local Dev: `docker/dev/Dockerfile`
    *   GitHub Action: `.github/actions/r2d/Dockerfile` (uses `ghcr.io/amartyamandal/diagram-to-iac-r2d:latest`)
*   **Configuration:** Managed via YAML files (see `config/` and `src/diagram_to_iac/config.yaml`) and environment variables. Secrets are handled via GitHub Actions secrets (base64 encoded) and SOPS for local development.
*   **LLM Integration:** A router (`src/diagram_to_iac/tools/llm_utils/router.py`) manages interactions with various LLM providers (OpenAI, Anthropic, Google).

For a deeper dive into the project's technical aspects and philosophy, refer to the `PROJECT_KNOWLEDGE_SUMMARY.md` (though note its container strategy might be slightly outdated; this guide and `R2D_USER_GUIDE.md` reflect the GHCR-primary approach).

## 2. Local Development Environment Setup

### Prerequisites
*   Python 3.11+
*   Docker & Docker Compose
*   Git
*   Terraform CLI (1.8+)
*   GitHub CLI (`gh`)
*   SOPS (for managing encrypted secrets locally)

### Initial Setup Scripts
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/amartyamandal/diagram-to-iac.git
    cd diagram-to-iac
    ```
2.  **Set up Python virtual environment & install dependencies:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    ```
    This installs the project in editable mode along with development dependencies.
3.  **Install external tools:**
    ```bash
    ./setup/setup_tools.sh
    ```
    This script helps install tools like Terraform and `gh` if they are not already present.
4.  **Initialize SOPS (for encrypted secrets):**
    If you need to work with encrypted secrets locally (usually `config/secrets.yaml`):
    ```bash
    ./setup/init_sops.sh
    ```
    This typically involves setting up GPG keys. Follow SOPS documentation if you're new to it.
    To decrypt: `./scripts/decrypt_secrets.sh`
    To encrypt: `./scripts/encrypt_secrets.sh`

### Using the Development Docker Container
For a consistent and isolated development environment, use the provided Docker Compose setup:
```bash
cd docker/dev
docker-compose up -d  # Starts the development container in detached mode
docker-compose exec app bash # Enters the running container's shell
```
Inside the container, the project code is mounted, and most tools should be available.

### GitHub Copilot Setup
If you are using GitHub Copilot, the `setup/build_copilot.sh` script is designed for your environment. It handles setup robustly, even with limited network access.
Refer to `docs/COPILOT_SETUP_GUIDE.md` for detailed instructions on using this script and configuring your environment for optimal Copilot interaction.

## 3. Coding Standards & Guidelines

Please adhere to the following when contributing:

### General
*   **Modularity & Single Responsibility:** Especially for LangGraph tools, ensure each function has a single, clearly-defined responsibility. Aim for functions ≤40 lines where practical.
*   **Typing with Pydantic:** All agent inputs/outputs, tool parameters, and return types must use explicitly defined Pydantic models for clarity and validation.
*   **LLM Integration:** Planners should consistently use explicit route tokens (e.g., `ROUTE_TO_TOOL_NAME`) defined in prompts.
*   **Configuration:**
    *   New secrets should be added to `config/secrets_example.yaml` and documented.
    *   Application settings go into `src/diagram_to_iac/config.yaml`.
    *   Follow existing configuration hierarchy (app config < environment variables < GitHub secrets).

### Security & Safety (Key points from `.github/copilot-instructions.md`)
*   **Shell Command Execution (`shell_exec`):**
    *   Only allow binaries explicitly listed in `config/shell_tools_config.yaml` (or a similar allowlist).
    *   Always set `GIT_TERMINAL_PROMPT=0`.
    *   Enforce execution within the `/workspace` container directory.
    *   Implement subprocess timeouts (default 30 seconds).
*   **Secret Management:**
    *   Use GitHub Actions secrets for CI/CD (base64 encoded).
    *   Use SOPS for local encrypted secrets.
    *   Never log or output raw secrets.
*   **Error Handling:** Tools must handle subprocess failures gracefully, typically raising `RuntimeError` with meaningful `stderr` output. Planner nodes should catch errors and route appropriately (e.g., to open an issue or attempt an auto-fix).

### Testing
*   **Unit Tests:**
    *   All new tools and significant functions must have accompanying unit tests.
    *   Use `pytest`.
    *   Mock external dependencies (subprocess calls, LLM API calls, file system interactions where appropriate).
    *   Tests should be fast and isolated.
*   **Integration Tests:** (To be expanded) Cover interactions between agents and key workflow paths.
*   **Running Tests:**
    ```bash
    pytest  # Runs all tests
    pytest tests/agents/your_agent/ # Run specific agent tests
    pytest --cov=src/diagram_to_iac # Run with coverage
    ```

### Documentation
*   Provide clear docstrings for all classes, methods, and functions.
*   Update relevant user documentation in the `docs/` directory if your changes affect user setup or behavior.
*   For new agents or tools, create a README.md in their respective directories.

## 4. Key Development Tasks

### Adding a New Agent
1.  Create a new directory under `src/diagram_to_iac/agents/` (e.g., `my_new_agent_langgraph/`).
2.  Implement the agent class, ensuring it inherits from `AgentBase` (`src/diagram_to_iac/core/agent_base.py`) and implements `plan`, `run`, and `report` methods.
3.  If the agent uses specific tools, create them in a `tools/` subdirectory or use existing tools from `src/diagram_to_iac/tools/`.
4.  Add agent-specific configuration to a `config.yaml` within its directory.
5.  Update the `SupervisorAgent`'s routing logic and planner prompts if it needs to invoke this new agent.
6.  Create comprehensive unit tests for the new agent and its tools.
7.  Add a `README.md` for your agent.
8.  Update `docs/AGENT_ARCHITECTURE.md` to include your new agent.

### Adding a New Tool
1.  Identify the appropriate location (either under a specific agent's `tools/` directory or in the shared `src/diagram_to_iac/tools/` if generally applicable).
2.  Adhere to the single responsibility principle.
3.  Use Pydantic models for inputs and outputs.
4.  If it executes shell commands, ensure the command is added to the allowlist and all security practices are followed.
5.  Write unit tests with mocked dependencies.

## 5. Build Process & Scripts

Refer to `PROJECT_KNOWLEDGE_SUMMARY.md` for an extensive list of utility scripts in `scripts/` and `setup/`. Key ones include:

*   `./scripts/build_wheel.sh`: Builds the Python package.
*   `./scripts/update_deps.py`: Manages dependencies.
*   `./scripts/encrypt_secrets.sh` & `./scripts/decrypt_secrets.sh`: For SOPS.

## 6. Versioning and Releases

(Details to be added - typically involves version bumping in `pyproject.toml`, tagging, and letting the build workflow handle publishing).

---

This guide provides a starting point for developers. For more in-depth information on specific components, always refer to their respective READMEs and the source code itself.
Happy automating!
