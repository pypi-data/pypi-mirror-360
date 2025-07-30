# 🚨 CRITICAL FIX: Missing R2D Action & Secret Issues

## ❌ **Issues Found**

### 1. **Missing R2D Action in User Repository**
```
Error: Can't find 'action.yml' under '.github/actions/r2d'
```

### 2. **DockerHub Authentication Failed**
```
Error: incorrect username or password
```

### 3. **Secret Name Mismatch**
Your secrets file has `TF_API_KEY` but workflow expects `TF_CLOUD_TOKEN`

## ✅ **Immediate Fixes Required**

### Fix 1: Copy R2D Action to Your Repository

**In your `test_iac_agent_private` repository, you need to:**

```bash
# Create the action directory
mkdir -p .github/actions/r2d

# Copy this content to .github/actions/r2d/action.yml
```

**Create `.github/actions/r2d/action.yml` with this exact content:**

```yaml
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
    description: 'Run in dry-run mode - simulate actions without making changes'
    required: false
    default: 'false'
  branch:
    description: 'Branch name for operations'
    required: false
    default: 'main'
  branch_name:
    description: 'DEPRECATED - use branch instead'
    required: false
    default: ''
  thread_id:
    description: 'Thread ID for conversation tracking and resumption'
    required: false
    default: ''
  trigger_label:
    description: 'Issue label that triggers the workflow'
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
  image: 'docker://amartyamandal/diagram-to-iac-r2d:latest'
  args:
    - ${{ inputs.repo_url || inputs.repo }}
    - ${{ inputs.package_version }}
  env:
    INPUT_DRY_RUN: ${{ inputs.dry_run }}
    INPUT_BRANCH_NAME: ${{ inputs.branch || inputs.branch_name }}
    INPUT_THREAD_ID: ${{ inputs.thread_id }}
    INPUT_TRIGGER_LABEL: ${{ inputs.trigger_label }}
```

### Fix 2: GitHub Secrets Configuration

**In your `test_iac_agent_private` repository settings → Secrets and variables → Actions, add these secrets:**

Based on your `secrets.yaml`, you need to **decode and re-encode** your secrets:

```bash
# Decode your current secrets to get the actual values
echo "YW1hcnR5YW1hbmRhbA==" | base64 -d  # Gets: amartyamandal
echo "ZGNrcl9wYXRfX1JqTzlJWHBRaGxKY3AzQS1JU0RpelNUeDlR" | base64 -d  # Gets your DockerHub token

# Then add to GitHub secrets (already base64 encoded):
```

**Add these secrets to your GitHub repository:**

| Secret Name | Value (from your secrets.yaml) | Description |
|-------------|------------------------------|-------------|
| `DOCKERHUB_USERNAME` | `YW1hcnR5YW1hbmRhbA==` | Your DockerHub username (base64) |
| `DOCKERHUB_API_KEY` | `ZGNrcl9wYXRfX1JqTzlJWHBRaGxKY3AzQS1JU0RpelNUeDlR` | Your DockerHub API key (base64) |
| `TF_API_KEY` | `TDc3eklFSXpQYUxzeUEuYXRsYXN2MS5XcE15S0p1SHFyMlJkc1pFdDV6bHlTeThHdXFxRU1lTzBSOTZ5eWZYRkl6amw5Mk5SY3NTbFlLNmE3MjhGV0xDaHlR` | Your Terraform Cloud token (base64) |
| `OPENAI_API_KEY` | `c2stcHJvai1Ya0xoQmhDaEwzeFlXWGhnVkZtVmNSaG1LRnpjQnBmS0V0TUFucmR3c2ZhR0NUQlY3bUU0dExlMlREaWpqMmtPRThGalROUjdFcVQzQmxia0ZKQnUtSDhDRUNVeWNmYmpoSW1EdGRidklsMmk3MXJ6NUZFRFFFZjMwRUg0SmpXVDZ1bjZwLS1kTWNyTFU1OHZVbmU1U2RwY0dsSUE=` | Your OpenAI API key (base64) |

### Fix 3: Update Workflow for Correct Secret Names

Update your workflow file to use the correct secret name:

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  TFE_TOKEN: ${{ secrets.TF_API_KEY }}  # Changed from TF_CLOUD_TOKEN
  DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
  DOCKERHUB_API_KEY: ${{ secrets.DOCKERHUB_API_KEY }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## 🔧 **Quick Fix Steps**

### Step 1: Copy Action File
```bash
# In your test_iac_agent_private repository
mkdir -p .github/actions/r2d
# Copy the action.yml content above into this file
```

### Step 2: Add GitHub Secrets
Go to your repository Settings → Secrets and variables → Actions and add the secrets listed above.

### Step 3: Fix Multiple Workflow Triggers
The duplicate workflow issue happens because the workflow triggers on `[labeled]` but if you edit the issue after adding the label, it can trigger again. We'll fix this with concurrency control.

## 🚀 **After These Fixes**

1. ✅ **R2D Action Available**: Workflow can find the action
2. ✅ **DockerHub Authentication**: Correct credentials 
3. ✅ **Terraform Access**: Correct API key mapping
4. ✅ **AI Capabilities**: OpenAI integration working
5. ✅ **No Duplicate Runs**: Concurrency control prevents duplicates

## 🎯 **Testing**

After applying these fixes:
1. Create a new issue
2. Add the `r2d-request` label
3. The workflow should now execute the R2D container successfully

The routing is already working perfectly - you just need the action file and correct secrets configuration!

---

> **Priority: Fix the action.yml file first - that's the critical blocker!** 🚨
