# DevOps-in-a-Box: Working Examples

This document provides tested, working examples for implementing the R2D DevOps-in-a-Box system.

## ✅ Basic Working Example

Copy this exact workflow to get started immediately:

```yaml
# .github/workflows/devops-in-a-box.yml
name: "🤖 DevOps-in-a-Box"

on:
  # Issue-based deployment (recommended)
  issues:
    types: [opened, labeled]
  
  # PR-based deployment
  pull_request:
    types: [closed]
  
  # Manual deployment
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Run in dry-run mode for testing'
        required: false
        default: true
        type: boolean

jobs:
  deploy:
    name: "🚀 Deploy Infrastructure"
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets: inherit
    with:
      dry_run: ${{ inputs.dry_run || false }}
```

## 🔐 Required Secrets Setup

### Step 1: Get Terraform Cloud Token
1. Go to [Terraform Cloud Tokens](https://app.terraform.io/app/settings/tokens)
2. Create a new API token
3. Copy the token value

### Step 2: Add to Repository Secrets
1. Go to your repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add these secrets:

| Secret Name | Value | Notes |
|-------------|-------|-------|
| `TF_CLOUD_TOKEN` | Your Terraform Cloud API token (**base64 encoded**) | **Required** |
| `OPENAI_API_KEY` | Your OpenAI API key (**base64 encoded**) | Optional (for enhanced AI) |
| `DOCKERHUB_USERNAME` | Your DockerHub username (**base64 encoded**) | Optional (for private containers) |
| `DOCKERHUB_TOKEN` | Your DockerHub access token (**base64 encoded**) | Optional (for private containers) |

> **🚨 CRITICAL**: All secret values must be **base64-encoded** before adding to GitHub.
> 
> ```bash
> # Example: Encode your Terraform token
> echo -n "your-actual-token" | base64
> ```
> 
> **Note**: `GITHUB_TOKEN` is automatically provided by GitHub Actions.
> **DockerHub secrets**: Only needed if using private DockerHub containers.

## 🎯 How to Deploy

### Method 1: Issue-Based (Recommended)
1. Create a new issue in your repository
2. Add the label `r2d-request` to the issue
3. The deployment will start automatically

### Method 2: PR-Based
1. Create a pull request
2. Merge the PR to your main branch
3. Deployment triggers automatically

### Method 3: Manual
1. Go to Actions → "🤖 DevOps-in-a-Box"
2. Click "Run workflow"
3. Choose dry-run mode for testing

## 🔍 What You'll See

When deployment runs, you'll get:

1. **📋 GitHub Issue**: Detailed deployment progress and results
2. **📊 Workflow Summary**: Step-by-step execution details
3. **📦 Artifacts**: Logs, Terraform plans, and reports
4. **🤖 Auto-fixes**: PR suggestions for any issues found

## 🚨 Troubleshooting

### Issue: "TFE_TOKEN not found"
**Solution**: Ensure you've set `TF_CLOUD_TOKEN` as a repository secret (not `TFE_TOKEN`)

### Issue: Workflow doesn't trigger on issues
**Solution**: Make sure the issue has the `r2d-request` label

### Issue: Permission denied
**Solution**: Check that `TF_CLOUD_TOKEN` has proper permissions in Terraform Cloud

### Issue: "Docker pull access denied" or private container errors
**Solution**: For private DockerHub containers, ensure you've set:
- `DOCKERHUB_USERNAME` - Your DockerHub username
- `DOCKERHUB_TOKEN` - Your DockerHub access token (not password)

### Issue: DockerHub authentication fails
**Solution**: 
1. Verify your DockerHub token has the correct permissions
2. Use an access token, not your password
3. Ensure the container image path is correct in your action

## 🎉 Success!

If everything is working:
- ✅ Workflow runs without errors
- ✅ GitHub issue shows deployment progress
- ✅ Terraform resources are created/updated
- ✅ Security scans complete successfully

## 📚 Next Steps

- Read the [Complete User Guide](R2D_USER_GUIDE.md) for advanced features
- Check out [Migration Guide](MIGRATION_GUIDE.md) if moving from old workflows
- Explore multi-environment setups and custom configurations

---

> **"One container, many minds—zero manual toil."** 🤖
