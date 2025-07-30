# 🤖 DevOps-in-a-Box: R2D User Guide

> **"One container, many minds—zero manual toil."**

The **R2D (Repo-to-Deployment) Action** is a self-healing, Terraform-first DevOps automation solution. Simply add one workflow file to your repository, and our AI-powered SupervisorAgent handles the complete deployment pipeline using the R2D container action.

## ⚡ Quick Start (2-Minute Setup)

This guide helps you integrate the R2D workflow into your repository using the recommended **Reusable Workflow** method.

### 1. Add the Reusable Workflow File

Create a new workflow file in your repository, for example, at `.github/workflows/devops-in-a-box.yml`:

```yaml
name: "🤖 DevOps-in-a-Box: R2D Deployment"

on:
  # Trigger on manual dispatch
  workflow_dispatch:
    inputs:
      repo_url:
        description: 'Repository URL to deploy (defaults to current repo)'
        required: false
        default: '' # Will default to github.server_url + github.repository
        type: string
      branch:
        description: 'Branch to deploy (defaults to main/master)'
        required: false
        default: '' # Defaults to default branch of the repo_url
        type: string
      dry_run:
        description: 'Run in dry-run mode (true/false)'
        required: false
        default: 'true' # Recommended to test with dry-run first
        type: boolean
      trigger_label:
        description: 'Issue label that triggers deployment (if using issue triggers)'
        required: false
        default: 'r2d-request'
        type: string

  # Trigger when issues are labeled (e.g., with 'r2d-request')
  issues:
    types: [labeled]

  # Trigger when Pull Requests are merged to the default branch
  pull_request:
    types: [closed]

jobs:
  r2d_deployment:
    name: "🚀 R2D Deployment"
    # Use the reusable workflow from the amartyamandal/diagram-to-iac repository
    uses: "amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main"
    secrets: inherit # IMPORTANT: This passes your repository secrets to the reusable workflow
    with:
      # Pass inputs to the reusable workflow
      repo_url: ${{ inputs.repo_url || format('{0}/{1}', github.server_url, github.repository) }}
      branch: ${{ inputs.branch }} # Let the reusable workflow handle default if empty
      dry_run: ${{ inputs.dry_run }}
      trigger_label: ${{ inputs.trigger_label }}
      # thread_id is managed by the reusable workflow
```

**Note:** Using `@main` will always run the latest version of the R2D workflow. For production, consider pinning to a specific release tag (e.g., `@v1.0.0`) once available.

### 2. Configure Required Secrets

Go to your repository's **Settings → Secrets and variables → Actions** and add the following secrets. **All secret values MUST be base64-encoded.**

#### **Required Secrets:**

| Secret Name      | Description                                                                                                | How to Get                                                                                                |
| :--------------- | :--------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| `REPO_API_KEY`   | GitHub Personal Access Token (PAT) used for repository operations and GHCR authentication.                   | [GitHub Settings](https://github.com/settings/tokens?type=beta). Scopes: `repo`, `read:packages`. `write:packages` if building from a fork. |
| `TF_API_KEY`     | Terraform Cloud API Token for managing workspaces and deployments.                                           | [Terraform Cloud User Settings](https://app.terraform.io/app/settings/tokens).                             |
| `OPENAI_API_KEY` | OpenAI API Key. (At least one AI provider key is typically required for the SupervisorAgent's capabilities). | [OpenAI Platform](https://platform.openai.com/api-keys).                                                  |

#### **Optional AI Provider Secrets (Base64 Encoded):**

You can use other AI providers. If so, add their respective API keys:

| Secret Name         | Description                |
| :------------------ | :------------------------- |
| `ANTHROPIC_API_KEY` | Anthropic Claude API Key   |
| `GOOGLE_API_KEY`    | Google AI / Gemini API Key |

#### **How to Base64 Encode Your Secrets:**

**Linux/macOS:**
```bash
echo -n "your-actual-secret-value" | base64
```
*(Ensure you use `echo -n` to avoid adding a newline character to the encoded value.)*

**Windows (PowerShell):**
```powershell
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("your-actual-secret-value"))
```

**Example: Encoding and Adding `REPO_API_KEY`**
1.  Generate PAT `ghp_YourTokenValue` from GitHub.
2.  Encode it: `echo -n "ghp_YourTokenValue" | base64`  (Result will be like `Z2hwX1lvdXJТоa2VuVmFsdWU=`)
3.  In GitHub repository secrets, create `REPO_API_KEY` with the encoded value.

### 3. Trigger Your First Deployment!

You can trigger the R2D workflow in several ways (as configured in the `on:` section of your workflow file):

*   **Manual Dispatch:** Go to your repository's "Actions" tab, select "🤖 DevOps-in-a-Box: R2D Deployment", and click "Run workflow".
*   **Issue Labeling:** Create a new GitHub issue and add the label `r2d-request` (or your custom `trigger_label`).
*   **Pull Request Merge:** Merge a pull request into your default branch.

## 🎯 What the R2D Action Does

The R2D Action, orchestrated by the reusable workflow, performs the following:

1.  **Clones & Analyzes:** Accesses your specified repository to analyze its structure and content (Terraform, Ansible, PowerShell, Bash, etc.).
2.  **Validates Secrets:** Checks for necessary API keys and configurations early in the process.
3.  **Plans & Deploys Infrastructure:** Primarily uses Terraform Cloud to plan and apply infrastructure changes.
4.  **Manages Issues & PRs:**
    *   Automatically creates GitHub Issues for complex problems or when human intervention is needed.
    *   May suggest or create Pull Requests for common, auto-fixable issues.
5.  **Provides Observability:** Generates summaries, logs, and updates the triggering GitHub Issue with progress.

## 🔧 Understanding Key Configurations

### Secret Handling and Mapping
The R2D system expects specific environment variable names inside its container (e.g., `GITHUB_TOKEN`, `TFE_TOKEN`). The reusable workflow and the underlying R2D action handle the mapping from your repository secrets:

| Your GitHub Secret | Mapped to Container Env Var | Purpose                                         |
| :----------------- | :-------------------------- | :---------------------------------------------- |
| `REPO_API_KEY`     | `GITHUB_TOKEN`              | GitHub API operations, GHCR authentication      |
| `TF_API_KEY`       | `TFE_TOKEN`                 | Terraform Cloud API access                      |
| `OPENAI_API_KEY`   | `OPENAI_API_KEY`            | OpenAI API access                               |
| (Other AI Keys)  | (Respective Env Var)        | Other AI provider access                        |

You only need to set the secrets in your repository as defined (e.g., `REPO_API_KEY`). The system takes care of the rest.

### Container Image Source (GHCR)
The R2D action uses a container image hosted on GitHub Container Registry (GHCR): `ghcr.io/amartyamandal/diagram-to-iac-r2d:latest`.
*   **Primary Source:** GHCR is the primary source for pulling the container image.
*   **Authentication:** If this image is private, the reusable workflow (using your `REPO_API_KEY`) handles authentication to GHCR. Ensure your `REPO_API_KEY` (PAT) has the `read:packages` scope.
*   **No Docker Hub Needed:** For standard usage, you do not need to configure Docker Hub credentials.

## ⚙️ How to Use R2D: Triggering Deployments

The R2D workflow is designed to be flexible. Here's how you can trigger and interact with it (based on the example workflow file provided):

*   **Manual Dispatch (`workflow_dispatch`):**
    *   Navigate to "Actions" tab in your repository.
    *   Select the workflow (e.g., "🤖 DevOps-in-a-Box: R2D Deployment").
    *   Click "Run workflow".
    *   You can often specify parameters like `repo_url`, `branch`, `dry_run` directly in the GitHub UI.

*   **Issue Labeling (`issues: types: [labeled]`):**
    *   Create a new GitHub issue describing the desired deployment or task.
    *   Add the specified trigger label (default: `r2d-request`) to this issue.
    *   The R2D workflow will pick up this event and start processing. The SupervisorAgent will use the issue for communication.

*   **Pull Request Merges (`pull_request: types: [closed]`):**
    *   When a pull request is merged into your repository's default branch, the workflow can be triggered to deploy the changes.

*   **Interactive Commands via Issue Comments (`issue_comment: types: [created]` - if configured):**
    *   The `r2d-unified.yml` workflow from `amartyamandal/diagram-to-iac` supports commands like:
        *   `/r2d run` or `/r2d deploy`: Initiates a full deployment based on the issue's context.
        *   `/r2d status`: Requests a status update for the deployment related to the issue.
    *   These commands must be made by users with appropriate repository permissions.

## 📊 Understanding R2D Outputs

R2D provides feedback and results through several channels:

*   **GitHub Issue Updates:** The primary mode of communication. The SupervisorAgent will post comments detailing its plan, progress, any errors, and final results directly in the GitHub issue that triggered the run (or a new issue it creates).
*   **GitHub Actions Workflow Log:** Detailed logs from the workflow run, including R2D container logs, are available in the "Actions" tab.
*   **Step Summary Dashboard:** A Markdown file (`step-summary.md`) is often generated and uploaded as an artifact, providing a high-level overview of the deployment, including Terraform changes, security findings, and metrics.
*   **Workflow Artifacts:** Other files like Terraform plans, detailed logs, and generated reports may be uploaded as artifacts associated with the workflow run.

## 🛡️ Security Considerations

*   **PAT Scopes:** Ensure the `REPO_API_KEY` (Personal Access Token) has the minimum necessary scopes. Typically `repo` (for accessing repository code) and `read:packages` (for pulling from GHCR). If you fork the project and build/push your own R2D images to GHCR, your PAT will also need `write:packages`.
*   **Secret Encoding:** Always base64-encode secrets stored in GitHub.
*   **Reusable Workflow Trust:** You are running code from the `amartyamandal/diagram-to-iac` repository. Ensure you trust this source or pin to a specific commit SHA or release tag for stability and security.
*   **Non-Root Container:** The R2D container runs as a non-root user for enhanced security.
*   **Command Allowlisting:** The ShellAgent within R2D operates with a command allowlist to restrict arbitrary command execution.

## 🆘 Troubleshooting Common Issues

1.  **Workflow Not Triggering:**
    *   Check workflow file syntax (`.github/workflows/devops-in-a-box.yml`).
    *   Ensure correct event triggers are configured (e.g., issue label matches, PR merged to correct branch).
    *   For issue-based triggers, verify the user labeling/commenting has sufficient repository permissions (Member, Collaborator, or Owner).

2.  **"Container not found" or "Authentication required" for GHCR:**
    *   Ensure `REPO_API_KEY` is correctly set in secrets and is base64 encoded.
    *   Verify the `REPO_API_KEY` (PAT) has the `read:packages` scope.
    *   Check that the image path `ghcr.io/amartyamandal/diagram-to-iac-r2d:latest` is correct and accessible.

3.  **Missing Secrets (e.g., "TF_API_KEY not found"):**
    *   Double-check all required secrets (`REPO_API_KEY`, `TF_API_KEY`, at least one AI key) are present in your repository's Actions secrets.
    *   Confirm they are correctly base64 encoded.
    *   Verify secret names are exact (case-sensitive).

4.  **Terraform Cloud Errors:**
    *   Ensure `TF_API_KEY` is valid and has permissions for the relevant TFC workspace.
    *   Check Terraform code within the target repository for syntax errors.

5.  **SupervisorAgent routes directly to ROUTE_TO_END:**
    *   The target repository might be empty or not contain a recognizable IaC stack.
    *   The LLM might not have clear instructions or context. Ensure your issue description (if using issue trigger) is clear.
    *   Check AI API key validity and that the model is accessible.

### Getting Help
1.  **Review Workflow Logs:** Check the detailed output in the GitHub Actions run.
2.  **Examine the GitHub Issue:** The R2D agent posts updates and errors in the associated issue.
3.  **Check `step-summary.md` artifact:** This can provide clues about what the agent attempted.
4.  **Consult `DUAL_REGISTRY_STRATEGY.md` and other docs** in the `amartyamandal/diagram-to-iac` repository for deeper architectural insights if troubleshooting complex issues.

---

This guide provides the essentials for integrating and using the R2D DevOps-in-a-Box system. For more advanced topics, developer guides, or architectural details, please refer to the main `amartyamandal/diagram-to-iac` repository.
