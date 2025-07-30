# 🤖 DevOps-in-a-Box: THE ONLY INTEGRATION GUIDE YOU NEED

> **"One container, many minds—zero manual toil."**

## 🎯 START HERE - IGNORE ALL OTHER GUIDES

**This is the SINGLE SOURCE OF TRUTH.** All other READMEs are deprecated. If you see conflicting information elsewhere, use this guide only.

## ⚡ 2-Minute Setup (Copy & Paste)

### Step 1: Copy the R2D Action to Your Repository

You only need to copy the action definition file to your repository:

#### Option A: Quick Setup (Recommended)
```bash
# In your repository root, create the action directory
mkdir -p .github/actions/r2d

# Copy the action.yml file
cat > .github/actions/r2d/action.yml << 'EOF'
name: 'DevOps-in-a-Box: R2D Action'
description: 'Repo-to-Deployment automation with self-healing capabilities'
branding:
  icon: 'cloud'
  color: 'blue'

inputs:
  repo_url:
    description: 'GitHub repository URL to deploy'
    required: false
    default: ${{ github.repository }}
  repo:
    description: 'DEPRECATED - use repo_url instead'
    required: false
  package_version:
    description: 'diagram-to-iac package version to use (e.g., v1.0.0). Uses latest if not specified.'
    required: false
    default: ''
  dry_run:
    description: 'Run in dry-run mode (safe testing)'
    required: false
    default: 'true'
  branch:
    description: 'Branch name for deployment'
    required: false
    default: ''
  branch_name:
    description: 'DEPRECATED - use branch instead'
    required: false
  thread_id:
    description: 'GitHub issue thread ID for continuation'
    required: false
    default: ''
  trigger_label:
    description: 'Label that triggers R2D workflow'
    required: false
    default: 'r2d-request'

outputs:
  success:
    description: 'Whether the R2D workflow completed successfully'
  issues_opened:
    description: 'Number of GitHub issues opened for error handling'
  terraform_summary:
    description: 'Summary of Terraform operations performed'
  branch_created:
    description: 'Whether a new branch was created'
  artifacts_path:
    description: 'Path to collected artifacts (logs, plans, summaries)'

runs:
  using: 'docker'
  image: 'ghcr.io/amartyamandal/diagram-to-iac-r2d:latest'
  args:
    - ${{ inputs.repo_url || inputs.repo }}
    - ${{ inputs.package_version }}
  env:
    INPUT_DRY_RUN: ${{ inputs.dry_run }}
    INPUT_BRANCH_NAME: ${{ inputs.branch || inputs.branch_name }}
    INPUT_THREAD_ID: ${{ inputs.thread_id }}
    INPUT_TRIGGER_LABEL: ${{ inputs.trigger_label }}
EOF
```

#### Option B: Manual Copy
**⚠️ Important**: Copy the action.yml content from the CRITICAL_USER_FIXES_REQUIRED.md document, not from GitHub URLs.

1. Use the `action.yml` content provided in [`CRITICAL_USER_FIXES_REQUIRED.md`](CRITICAL_USER_FIXES_REQUIRED.md)
2. Create `.github/actions/r2d/action.yml` in your repository with that content

#### Option C: Direct Copy from Critical Fixes
```bash
# Create directory first
mkdir -p .github/actions/r2d

# Copy the exact action.yml content from CRITICAL_USER_FIXES_REQUIRED.md
# This ensures you get the correct, tested version
```

> **Note**: You don't need `Dockerfile`, `entrypoint.sh`, or other files because the action uses a pre-built container from DockerHub.

### Step 2: Create the Unified Workflow

Create `.github/workflows/r2d-unified.yml` in your repository with this **exact content**:

```yaml
name: "DevOps-in-a-Box: R2D Unified Workflow"

on:
  # Issue-based triggers
  issues:
    types: [opened, edited, labeled, reopened]
  
  # PR merge triggers  
  pull_request:
    types: [closed]
  
  # Manual triggers for testing
  workflow_dispatch:
    inputs:
      trigger_type:
        description: 'Deployment trigger type'
        required: false
        default: 'manual'
        type: choice
        options:
          - 'manual'
          - 'issue'
          - 'pr_merge'
      repo_url:
        description: 'Repository to deploy (leave empty to use current repo)'
        required: false
        default: ''
      branch:
        description: 'Branch to deploy'
        required: false
        default: 'main'
      dry_run:
        description: 'Run in dry-run mode (safe for testing)'
        required: false
        default: true
        type: boolean
      trigger_label:
        description: 'Issue label that triggers deployment'
        required: false
        default: 'r2d-request'

jobs:
  # Smart routing job to determine if workflow should run
  route:
    name: "🧠 Smart Workflow Routing"
    runs-on: ubuntu-latest
    outputs:
      should_deploy: ${{ steps.routing.outputs.should_deploy }}
      deployment_type: ${{ steps.routing.outputs.deployment_type }}
      target_repo: ${{ steps.routing.outputs.target_repo }}
      target_branch: ${{ steps.routing.outputs.target_branch }}
      dry_run_mode: ${{ steps.routing.outputs.dry_run_mode }}
    
    steps:
      - name: "🧠 Determine workflow execution path"
        id: routing
        run: |
          echo "=== 🧠 SMART ROUTING ANALYSIS ==="
          
          # Initialize outputs
          SHOULD_DEPLOY="false"
          DEPLOYMENT_TYPE="none"
          TARGET_REPO="${{ github.repository }}"
          TARGET_BRANCH="main"
          DRY_RUN="true"  # Default safe mode
          
          # Determine trigger type and routing logic
          case "${{ github.event_name }}" in
            "workflow_dispatch")
              echo "🎮 Manual workflow dispatch detected"
              SHOULD_DEPLOY="true"
              DEPLOYMENT_TYPE="${{ inputs.trigger_type || 'manual' }}"
              TARGET_REPO="${{ inputs.repo_url || github.repository }}"
              TARGET_BRANCH="${{ inputs.branch || 'main' }}"
              DRY_RUN="${{ inputs.dry_run || 'true' }}"
              ;;
              
            "issues")
              echo "🏷️ Issue event detected: ${{ github.event.action }}"
              
              # Check if issue has required label
              if echo '${{ toJson(github.event.issue.labels.*.name) }}' | grep -q "${{ inputs.trigger_label || 'r2d-request' }}"; then
                echo "✅ Found required label: ${{ inputs.trigger_label || 'r2d-request' }}"
                
                # Security: Check author association
                AUTHOR_ASSOC="${{ github.event.issue.author_association }}"
                if [[ "$AUTHOR_ASSOC" =~ ^(OWNER|MEMBER|COLLABORATOR)$ ]]; then
                  SHOULD_DEPLOY="true"
                  DEPLOYMENT_TYPE="issue"
                  TARGET_REPO="${{ github.repository }}"
                  TARGET_BRANCH="main"
                  DRY_RUN="false"  # Real deployment for authorized issue triggers
                  echo "✅ Authorized issue trigger: ${{ github.event.issue.title }}"
                else
                  echo "❌ Unauthorized user: $AUTHOR_ASSOC"
                fi
              else
                echo "⏭️ Issue missing required label: ${{ inputs.trigger_label || 'r2d-request' }}"
              fi
              ;;
              
            "pull_request")
              echo "🔀 Pull request event detected: ${{ github.event.action }}"
              
              if [[ "${{ github.event.action }}" == "closed" && "${{ github.event.pull_request.merged }}" == "true" ]]; then
                echo "✅ PR merged to main branch"
                SHOULD_DEPLOY="true"
                DEPLOYMENT_TYPE="pr_merge"
                TARGET_REPO="${{ github.repository }}"
                TARGET_BRANCH="${{ github.event.pull_request.base.ref }}"
                DRY_RUN="false"  # Real deployment for PR merges
              else
                echo "⏭️ PR closed without merge, skipping deployment"
              fi
              ;;
              
            *)
              echo "⚠️ Unknown trigger: ${{ github.event_name }}"
              ;;
          esac
          
          # Output routing decisions
          echo "should_deploy=$SHOULD_DEPLOY" >> $GITHUB_OUTPUT
          echo "deployment_type=$DEPLOYMENT_TYPE" >> $GITHUB_OUTPUT  
          echo "target_repo=$TARGET_REPO" >> $GITHUB_OUTPUT
          echo "target_branch=$TARGET_BRANCH" >> $GITHUB_OUTPUT
          echo "dry_run_mode=$DRY_RUN" >> $GITHUB_OUTPUT
          
          echo "=== 🎯 ROUTING DECISION ==="
          echo "Should Deploy: $SHOULD_DEPLOY"
          echo "Deployment Type: $DEPLOYMENT_TYPE"
          echo "Target Repo: $TARGET_REPO"
          echo "Target Branch: $TARGET_BRANCH"
          echo "Dry Run Mode: $DRY_RUN"

  # Main deployment job - only runs if routing determines deployment should proceed
  deploy:
    name: "🚀 R2D Container Deployment"
    needs: route
    if: needs.route.outputs.should_deploy == 'true'
    runs-on: ubuntu-latest
    
    steps:
      - name: "📊 Display Deployment Info"
        run: |
          echo "=== 🚀 DEPLOYMENT STARTING ==="
          echo "Deployment Type: ${{ needs.route.outputs.deployment_type }}"
          echo "Target Repository: ${{ needs.route.outputs.target_repo }}"
          echo "Target Branch: ${{ needs.route.outputs.target_branch }}"
          echo "Dry Run Mode: ${{ needs.route.outputs.dry_run_mode }}"
          echo "================================"

      - name: "🐳 Login to DockerHub (for private containers)"
        continue-on-error: true
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: "🤖 Execute R2D Container Action"
        uses: ./.github/actions/r2d
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TFE_TOKEN: ${{ secrets.TF_CLOUD_TOKEN }}
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          DOCKERHUB_API_KEY: ${{ secrets.DOCKERHUB_TOKEN }}
          
          # AI API Keys (add the ones you plan to use)
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
        with:
          repo_url: ${{ needs.route.outputs.target_repo }}
          branch: ${{ needs.route.outputs.target_branch }}
          dry_run: ${{ needs.route.outputs.dry_run_mode }}
          thread_id: ${{ needs.route.outputs.thread_id }}
```

### Step 3: Configure Required Secrets

Go to your repository **Settings → Secrets and variables → Actions** and add these **base64-encoded** secrets:

| Secret Name | Value | Required | Encoding |
|-------------|-------|----------|----------|
| `TF_CLOUD_TOKEN` | Your [Terraform Cloud API token](https://app.terraform.io/app/settings/tokens) | ✅ **Yes** | **🔐 Base64** |
| `OPENAI_API_KEY` | Your OpenAI API key | ❌ Optional | **🔐 Base64** |
| `DOCKERHUB_USERNAME` | Your DockerHub username | ❌ Optional* | **🔐 Base64** |
| `DOCKERHUB_TOKEN` | Your DockerHub access token | ❌ Optional* | **🔐 Base64** |

> **🚨 CRITICAL**: All secret values must be **base64-encoded** before adding to GitHub.
> 
> **Note**: `GITHUB_TOKEN` is automatically provided by GitHub Actions.
> 
> ***DockerHub secrets**: Only needed if using private containers.

#### How to Base64 Encode Your Secrets

**Linux/macOS:**
```bash
# Example: Encode your Terraform Cloud token
echo -n "your-actual-tf-cloud-token" | base64

# Example: Encode your OpenAI API key  
echo -n "sk-your-openai-api-key" | base64

# Example: Encode your DockerHub username
echo -n "yourusername" | base64
```

**Windows (PowerShell):**
```powershell
# Example: Encode your Terraform Cloud token
[System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("your-actual-tf-cloud-token"))
```

**Online Tool (if needed):**
- Use [base64encode.org](https://www.base64encode.org) for quick encoding
- ⚠️ **Only use for non-sensitive testing values**

#### Example Secret Setup

1. **Get your Terraform Cloud token**: `abc123def456`
2. **Encode it**: `echo -n "abc123def456" | base64` → `YWJjMTIzZGVmNDU2`
3. **Add to GitHub**: Set `TF_CLOUD_TOKEN` = `YWJjMTIzZGVmNDU2`

### Step 4: Deploy!

Choose your deployment method:

**🏷️ Issue-Based (Recommended)**
1. Create a new issue in your repository
2. Add the label `r2d-request` to the issue
3. Watch the deployment happen automatically! ✨

**🔀 PR-Based**
- Merge any PR to your main branch
- Deployment triggers automatically

**🎮 Manual**
- Go to `Actions` → `DevOps-in-a-Box: R2D Unified Workflow` → `Run workflow`
- Choose dry-run mode for testing

## 🎯 What the Container Does

When triggered, the R2D container action:

1. **🔍 Analyzes** your repository (Terraform, Ansible, PowerShell, Bash)
2. **🔐 Validates** all secrets and dependencies upfront  
3. **🏗️ Deploys** infrastructure via Terraform Cloud
4. **🤖 Auto-fixes** common issues with Pull Requests
5. **📋 Creates** GitHub Issues for complex problems
6. **📊 Provides** rich summaries and observability

Everything happens in **one GitHub issue** per deployment for a clean narrative.

## 🔧 Critical Environment Variable Mapping

**FIXED**: The system automatically handles environment variable mapping:

| Repository Secret | Internal Environment Variable | Purpose |
|-------------------|-------------------------------|---------|
| `TF_CLOUD_TOKEN` | `TFE_TOKEN` | Terraform Cloud API access |
| `GITHUB_TOKEN` | `GITHUB_TOKEN` | GitHub API access |
| `DOCKERHUB_TOKEN` | `DOCKERHUB_API_KEY` | DockerHub API access |

You set user-friendly secret names, the system maps them internally.

## 🚨 Troubleshooting

### "TFE_TOKEN not found"
**✅ FIXED**: Set `TF_CLOUD_TOKEN` as a repository secret (the workflow maps it correctly)

### "Invalid token" or authentication errors  
**Solution**: Ensure your secret values are **base64-encoded**:
```bash
# Re-encode your token
echo -n "your-actual-token" | base64
```

### "base64: invalid input" errors
**Solution**: Check for extra spaces or newlines in your encoded secrets:
```bash
# Correct encoding (no newlines)
echo -n "your-token" | base64

# Wrong (includes newline)
echo "your-token" | base64
```

### Workflow doesn't trigger on issues
**Solution**: Ensure the issue has the `r2d-request` label

### "Docker pull access denied"
**Solution**: For private containers, set `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets (both base64-encoded)

### Permission denied errors
**Solution**: Check that `TF_CLOUD_TOKEN` has proper permissions in Terraform Cloud

### No AI capabilities
**Solution**: Add at least one AI API key (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) - remember to base64 encode them

## 🐳 Dual-Registry Container Strategy

This project uses a **dual-registry approach** for maximum reliability and redundancy:

### Current Registry Strategy

- **🎯 Primary (GHCR)**: `ghcr.io/amartyamandal/diagram-to-iac-r2d:latest` - Used for pulling in workflows
- **📦 Backup (Docker Hub)**: `amartyamandal/diagram-to-iac-r2d:latest` - Used for redundancy and pushes

### How the Current Setup Works

1. **Build Pipeline**: Pushes containers to **both** GHCR and Docker Hub for redundancy
2. **Action Definition**: Uses `ghcr.io/amartyamandal/diagram-to-iac-r2d:latest` (GHCR primary)
3. **Automatic Updates**: Build pipeline keeps both registries synchronized
4. **Workflow Authentication**: GHCR login handled automatically via `REPO_API_KEY`

### Benefits of Dual-Registry Strategy

- ✅ **GHCR Primary**: Fast GitHub Actions integration, native authentication
- ✅ **Docker Hub Backup**: Public visibility, cross-platform compatibility  
- ✅ **Zero Downtime**: Fallback registry if one service has issues
- ✅ **No Breaking Changes**: Smooth migration path for existing users

### Option 1: Use This Repository's Action (Recommended)

**Complete Setup:**
1. Copy the R2D action to your repository (Step 1 above)
2. Create the unified workflow (Step 2 above)  
3. The action automatically pulls the latest container from GHCR (GitHub Container Registry)

**Your workflow will use:**
```yaml
- name: "🤖 Execute R2D Container Action"
  uses: ./.github/actions/r2d  # Local copy of the action (uses GHCR internally)
```

### Option 2: Fork for Your Own Custom Container

If you want to use your own container registry:

1. **Fork** `amartyamandal/diagram-to-iac` to your GitHub account
2. **Set up GitHub Container Registry** (recommended) or Docker Hub secrets:
   - For GHCR: `REPO_API_KEY` (base64 encoded GitHub PAT with packages:write scope)
   - For Docker Hub: `DOCKERHUB_USERNAME_ENCODED` + `DOCKERHUB_API_KEY_ENCODED` (base64 encoded)
3. **Update container name** in your fork:
   ```yaml
   # In .github/actions/r2d/action.yml
   runs:
     using: 'docker'
     image: 'ghcr.io/yourusername/diagram-to-iac-r2d:latest'  # GHCR (recommended)
     # OR: image: 'docker://yourusername/your-container:latest'  # Docker Hub
   ```
4. **Update build pipeline** in your fork to push to your registry

### Option 3: Direct Container Usage

```yaml
- name: "🤖 Run R2D Container Directly"
  uses: docker://ghcr.io/amartyamandal/diagram-to-iac-r2d:latest  # GHCR primary
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    TFE_TOKEN: ${{ secrets.TF_CLOUD_TOKEN }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  with:
    repo_url: ${{ github.repository }}
    dry_run: true
```

### Registry Authentication Notes

- **GHCR (Primary)**: Uses GitHub's native authentication, no extra setup required for public containers
- **Docker Hub (Backup)**: Available for redundancy, but not required for basic usage
- **Private Containers**: Both registries support private containers with appropriate authentication

## ✅ Success Checklist

After setup, verify everything works:

- ✅ R2D action is copied to `.github/actions/r2d/action.yml` in your repository
- ✅ Workflow file is in `.github/workflows/r2d-unified.yml`
- ✅ Required secrets are configured (`TF_CLOUD_TOKEN` minimum)
- ✅ **All secrets are base64-encoded** (check with `echo "encoded_value" | base64 -d`)
- ✅ Test with manual trigger first (dry-run mode)
- ✅ Create test issue with `r2d-request` label
- ✅ Check GitHub Actions logs for any issues

## 🎉 You're Done!

The DevOps-in-a-Box container action is now integrated! You can deploy infrastructure by:

- Creating labeled issues (recommended)
- Merging pull requests  
- Running manual workflows

The AI-powered SupervisorAgent will handle the rest, orchestrating specialized agents for a complete repo-to-deployment experience.

---

> **"One container, many minds—zero manual toil."** 🤖
> 
> *Ready for deployment in any repository!*
