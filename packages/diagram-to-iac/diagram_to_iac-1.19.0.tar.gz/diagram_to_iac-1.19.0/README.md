# diagram-to-iac

> **"One container, many minds—zero manual toil."**

An automated DevOps-in-a-Box system that intelligently handles complete Repo-to-Deployment (R2D) workflows. The project combines AI-powered infrastructure analysis with GitHub automation for self-healing deployments.

## 🚀 DevOps-in-a-Box: R2D Action

The **R2D (Repo-to-Deployment) Action** is a self-healing, Terraform-first DevOps automation solution powered by a sophisticated multi-agent system. Integrated via a GitHub Actions reusable workflow, it analyzes your repository and deploys your infrastructure, primarily using Terraform Cloud.

### 🎯 Quick Start

Integrate the R2D Action into your repository in minutes:

**Step 1: Add the Reusable Workflow File**

Create `.github/workflows/devops-in-a-box.yml` (or your preferred name) in your repository:

```yaml
name: "🤖 DevOps-in-a-Box: R2D Deployment"

on:
  workflow_dispatch: # Allows manual triggering
    inputs:
      repo_url:
        description: 'Repository URL to deploy (defaults to current repo)'
        required: false
        default: ''
        type: string
      branch:
        description: 'Branch to deploy (defaults to main/master)'
        required: false
        default: ''
        type: string
      dry_run:
        description: 'Run in dry-run mode (true/false)'
        required: false
        default: 'true'
        type: boolean
      trigger_label:
        description: 'Issue label for issue triggers'
        required: false
        default: 'r2d-request'
        type: string
  issues:
    types: [labeled] # Trigger on issue labeling
  pull_request:
    types: [closed] # Trigger on PR merge

jobs:
  r2d_deployment:
    name: "🚀 R2D Deployment"
    uses: "amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main"
    secrets: inherit # Passes your repository secrets to the reusable workflow
    with:
      repo_url: ${{ inputs.repo_url || format('{0}/{1}', github.server_url, github.repository) }}
      branch: ${{ inputs.branch }}
      dry_run: ${{ inputs.dry_run }}
      trigger_label: ${{ inputs.trigger_label }}
```

**Step 2: Configure Required Secrets**

Go to your repository's **Settings → Secrets and variables → Actions** and add the necessary secrets. All secrets must be **base64-encoded**.

**Key Secrets:**
*   `REPO_API_KEY`: Your GitHub Personal Access Token (PAT) for repository access and GHCR authentication.
*   `TF_API_KEY`: Your Terraform Cloud API Token.
*   An AI Provider API Key (e.g., `OPENAI_API_KEY`).

> 📚 For detailed instructions on secret setup (including PAT scopes and base64 encoding) and more, see the **[Complete R2D User Guide](docs/R2D_USER_GUIDE.md)**.

**Step 3: Trigger Deployment**
You can now deploy via manual dispatch, by labeling a GitHub issue (e.g., with `r2d-request`), or by merging a Pull Request.

### Key Features

- **🤖 AI-Powered & Self-Healing**: Automatically analyzes repositories, creates GitHub Issues for errors, and can suggest fixes.
- **🛡️ Secure & Isolated**: Runs in a non-root container with workspace isolation and command allowlisting.
- **🌍 IaC Focused**: Primarily supports Terraform deployments via Terraform Cloud, with capabilities for Ansible, PowerShell, and Bash.
- **📊 Observable**: Provides rich logging, step summaries, and deployment artifacts.
- **🔄 Flexible Triggers**: Supports manual, issue-based, and PR-merge triggers.

### The Cast: Specialized Agents

Our multi-agent system efficiently handles different aspects of the DevOps lifecycle:

| Agent             | Capability                                         | Never Does                     |
| :---------------- | :------------------------------------------------- | :----------------------------- |
| **SupervisorAgent** | Orchestrates workflow, manages state, routes tasks | Edit code directly             |
| **GitAgent**        | Clones repos, manages branches, creates PRs        | Guess network credentials      |
| **ShellAgent**      | Executes commands safely, detects stack            | Run non-allowlisted binaries |
| **TerraformAgent**  | `init/plan/apply`, classifies errors, cost scans   | Apply with critical sec issues |
| **PolicyAgent**     | Runs `tfsec` + OPA for security gates              | Ignore critical findings       |
| **VisionAgent**     | (If applicable) Analyzes diagrams for IaC generation | -                              |

*(For more details on agents, see `docs/AGENT_ARCHITECTURE.md`)*

## 📦 Installation (for CLI usage or development)

If you want to run the `diagram-to-iac` CLI tools locally or contribute to development:

```bash
# Clone the repository
git clone https://github.com/amartyamandal/diagram-to-iac.git
cd diagram-to-iac

# Create a virtual environment (Python 3.11+) and install
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```
> For detailed developer setup, see the **[Developer Guide](docs/DEVELOPER_GUIDE.md)**.

## 🖥️ Running the CLI (for local use)

The project provides CLI entry points for direct interaction with agents (primarily for development and testing):

```bash
# Main R2D CLI (simulates parts of the GitHub Action flow)
diagram-to-iac --repo-url https://github.com/user/repo --dry-run

# Get help
diagram-to-iac --help

# Individual agent CLIs (examples)
supervisor-agent --repo-url https://github.com/user/repo
git-agent --repo-url https://github.com/user/repo --branch my-feature
```

## 📊 Observability

R2D ensures you're informed about its operations:

*   **GitHub Issue Updates**: Detailed progress and results are posted in the triggering GitHub Issue.
*   **Structured Logging**: JSONL logs are generated for each run (available as workflow artifacts).
*   **Step Summary Dashboard**: A `step-summary.md` file is generated with Terraform changes, security findings, and metrics (available as a workflow artifact).
*   **GitHub Actions Artifacts**: Logs, plans, and reports are uploaded for download from the workflow run page.

## 📚 Documentation

*   **🎯 [R2D User Guide](docs/R2D_USER_GUIDE.md)**: Your primary guide for setting up and using the R2D Action.
*   **🛠️ [Developer Guide](docs/DEVELOPER_GUIDE.md)**: For contributors or those wanting to understand the internals and run tools locally.
*   **🤖 [Agent Architecture](docs/AGENT_ARCHITECTURE.md)**: Learn about the different AI agents and how they work.
*   **💡 [DevOps-in-a-Box: The Severance Protocol for Infrastructure](DEVOPS_IN_A_BOX_ARTICLE.md)**: A conceptual overview of the project's philosophy.

## 🤝 Contributing

Contributions are welcome! Please see our development guidelines (in `docs/DEVELOPER_GUIDE.md` and `.github/copilot-instructions.md`) for coding standards and contribution instructions.

---

> **"One container, many minds—zero manual toil."** 🤖
