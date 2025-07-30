# R2D Unified Workflow Usage Guide

## Overview

The R2D (Repo-to-Deployment) Unified Workflow is designed to automatically deploy infrastructure code when specific events occur in your target repositories. This workflow is **not intended to run in the `diagram-to-iac` development repository** but rather in repositories that contain infrastructure code you want to deploy.

## Repository Isolation

### 🚨 Important: Development Repository Behavior
- The workflow will **automatically skip execution** when running in any repository containing `diagram-to-iac` in its name
- This prevents accidental deployments during development and testing of the R2D system itself
- For testing R2D functionality, create a separate test repository

### ✅ Target Repository Behavior
- The workflow will **execute normally** in any other repository
- Triggers on push events and PR activities as configured
- Deploys infrastructure using the R2D containerized action

## Trigger Events

### 1. Push Events
```yaml
push:
  branches: [main, master, develop, 'release/*']
  paths-ignore: ['**.md', 'docs/**', '.gitignore']
```
- **When**: Code is pushed to main branches
- **Behavior**: Full deployment (`dry_run: false`)
- **Ignores**: Documentation-only changes

### 2. Pull Request Merges
```yaml
pull_request:
  types: [closed]  # Only when merged
```
- **When**: PR is merged (not just closed)
- **Behavior**: Full deployment to target branch (`dry_run: false`)
- **Target**: Base branch of the merged PR

### 3. Pull Request Approvals
```yaml
pull_request_review:
  types: [submitted]  # When approved
```
- **When**: PR receives an approval review
- **Behavior**: Validation deployment (`dry_run: true`)
- **Target**: Head branch of the approved PR

### 4. Manual Triggers
```yaml
workflow_dispatch:
```
- **When**: Manually triggered from GitHub Actions UI
- **Behavior**: Configurable (dry_run option available)
- **Use Case**: Testing and emergency deployments

## Setup Instructions

### For Target Repositories (Infrastructure Repos)

1. **Copy the workflow file** to your infrastructure repository:
   ```bash
   cp .github/workflows/r2d-unified.yml <your-repo>/.github/workflows/
   ```

2. **Copy the action definition**:
   ```bash
   cp -r .github/actions/r2d <your-repo>/.github/actions/
   ```

3. **Configure GitHub Secrets** in your target repository:
   - `REPO_API_KEY` - GitHub token with repo access
   - `TF_API_KEY` - Terraform Cloud API token
   - `OPENAI_API_KEY` - OpenAI API key for LLM operations

4. **Verify triggers** match your deployment strategy:
   - Adjust branch names if needed
   - Modify path ignores for your documentation structure
   - Set appropriate dry_run behavior for your workflow

### For Development/Testing

1. **Create a separate test repository** (not containing `diagram-to-iac` in the name)
2. **Install the workflow and action files** as described above
3. **Use manual triggers** for controlled testing
4. **Monitor logs** to verify correct behavior

## Expected Behavior Examples

### ✅ In Target Repository (`my-infrastructure`)
```bash
# Push to main → Triggers deployment
git push origin main

# Merge PR → Triggers deployment  
gh pr merge 123

# Approve PR → Triggers validation
gh pr review 123 --approve
```

### ⏭️ In Development Repository (`diagram-to-iac`)
```bash
# Any event → Workflow skips with message:
# "Skipping workflow in diagram-to-iac development repository"
```

## Monitoring and Debugging

### Check Workflow Execution
1. Go to **Actions** tab in your repository
2. Look for **"DevOps-in-a-Box: R2D Unified Workflow"**
3. Check the **"Smart Workflow Routing"** job for trigger analysis

### Expected Log Output

**In Target Repository:**
```
🧠 DevOps-in-a-Box: Smart Workflow Routing
================================================
📤 Push event trigger detected
✅ Push to branch: main
📋 Routing Decision:
  Should Deploy: true
  Deployment Type: push
```

**In Development Repository:**
```
🧠 DevOps-in-a-Box: Smart Workflow Routing
================================================
⏭️ Skipping workflow in diagram-to-iac development repository
   This workflow is intended for target repositories using the R2D action
```

## Troubleshooting

### Workflow Not Triggering
1. **Check repository name** - Ensure it doesn't contain `diagram-to-iac`
2. **Verify branch names** - Ensure pushes are to configured branches
3. **Check path filters** - Ensure changes aren't in ignored paths
4. **Review secrets** - Ensure required secrets are configured

### Deployment Failures
1. **Check R2D action logs** in the deployment job
2. **Verify Terraform Cloud configuration**
3. **Validate infrastructure code syntax**
4. **Check secret permissions and values**

### Manual Testing
Use the **workflow_dispatch** trigger with `dry_run: true` to safely test the workflow without actual deployments.

## Security Considerations

- The workflow has **repository isolation** to prevent accidental execution in development
- **Secrets are required** for deployment operations
- **PR approvals run in safe mode** by default
- **Path filters prevent** documentation-only triggers
- **Concurrency controls** prevent conflicting deployments

## Support

For issues with the R2D workflow:
1. Check the **Actions logs** in your repository
2. Review the **R2D action documentation**
3. Create an issue in the appropriate repository with logs and context
