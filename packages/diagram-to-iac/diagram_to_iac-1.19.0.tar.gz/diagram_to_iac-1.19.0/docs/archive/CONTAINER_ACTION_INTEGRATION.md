# 🤖 DevOps-in-a-Box: THE DEFINITIVE INTEGRATION GUIDE

> **"One container, many minds—zero manual toil."**

## 🎯 USE THIS GUIDE ONLY

**This is the ONLY guide you need.** All other READMEs point here. If you see conflicting information elsewhere, use this guide.

## ⚡ 2-Minute Setup

### Step 1: Copy the Unified Workflow

Create `.github/workflows/r2d-unified.yml` in your repository with the **exact content** from our reference implementation:
        type: boolean

jobs:
  deploy:
    name: "🚀 Deploy Infrastructure"
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets: inherit
    with:
      dry_run: ${{ inputs.dry_run || false }}
```

### Step 2: Configure Required Secrets

Go to your repository **Settings → Secrets and variables → Actions** and add:

| Secret Name | Value | Required |
|-------------|-------|----------|
| `TF_CLOUD_TOKEN` | Your [Terraform Cloud API token](https://app.terraform.io/app/settings/tokens) | ✅ **Yes** |
| `OPENAI_API_KEY` | Your OpenAI API key | ❌ Optional |
| `DOCKERHUB_USERNAME` | Your DockerHub username | ❌ Optional* |
| `DOCKERHUB_TOKEN` | Your DockerHub access token | ❌ Optional* |

> **Note**: `GITHUB_TOKEN` is automatically provided by GitHub Actions.
> 
> ***DockerHub secrets**: Only needed if using private containers (see Private Container section below).

### Step 3: Deploy!

Choose your deployment method:

**🏷️ Issue-Based (Recommended)**
1. Create a new issue in your repository
2. Add the label `r2d-request` to the issue
3. Watch the deployment happen automatically! ✨

**🔀 PR-Based**
- Merge any PR to your main branch
- Deployment triggers automatically

**🎮 Manual**
- Go to `Actions` → `🤖 DevOps-in-a-Box` → `Run workflow`
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

## 🐳 Using Private DockerHub Containers

If you want to use your own private container instead of the public one:

### Option 1: Fork and Modify (Recommended)

1. **Fork** `amartyamandal/diagram-to-iac` to your GitHub account
2. **Modify** `.github/actions/r2d/action.yml` in your fork:
   ```yaml
   runs:
     using: 'docker'
     image: 'docker://yourusername/your-private-container:tag'  # Your container
   ```
3. **Use your fork** in the workflow:
   ```yaml
   jobs:
     deploy:
       uses: yourusername/diagram-to-iac/.github/workflows/r2d-unified.yml@main
   ```
4. **Add DockerHub secrets** to your repository (see secrets table above)

### Option 2: Direct Container Usage

```yaml
name: "My DevOps Workflow"
on:
  issues:
    types: [opened, labeled]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Run R2D Container
        uses: docker://yourusername/your-private-container:tag
        with:
          args: ${{ github.repository }} latest
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TFE_TOKEN: ${{ secrets.TF_CLOUD_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## 🔧 Environment Variable Mapping

**Important**: The system automatically handles environment variable mapping:

| Repository Secret | Internal Environment Variable | Purpose |
|-------------------|-------------------------------|---------|
| `TF_CLOUD_TOKEN` | `TFE_TOKEN` | Terraform Cloud API access |
| `GITHUB_TOKEN` | `GITHUB_TOKEN` | GitHub API access |
| `DOCKERHUB_TOKEN` | `DOCKERHUB_API_KEY` | DockerHub API access |
| `OPENAI_API_KEY` | `OPENAI_API_KEY` | OpenAI API access |

You set user-friendly secret names, the system maps them to expected variables internally.

## 🚨 Troubleshooting

### "TFE_TOKEN not found"
**Solution**: Set `TF_CLOUD_TOKEN` as a repository secret (not `TFE_TOKEN`)

### Workflow doesn't trigger on issues
**Solution**: Ensure the issue has the `r2d-request` label

### "Docker pull access denied"
**Solution**: For private containers, set `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets

### Permission denied errors
**Solution**: Check that `TF_CLOUD_TOKEN` has proper permissions in Terraform Cloud

### No AI capabilities
**Solution**: Add at least one AI API key (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)

## 🎛️ Advanced Configurations

### Custom Labels
```yaml
jobs:
  deploy:
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets: inherit
    with:
      trigger_label: 'deploy-prod'  # Custom label instead of 'r2d-request'
```

### Multi-Environment Setup
```yaml
name: "Multi-Environment Deployment"
on:
  issues:
    types: [labeled]

jobs:
  deploy-dev:
    if: contains(github.event.issue.labels.*.name, 'deploy-dev')
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets:
      TF_CLOUD_TOKEN: ${{ secrets.TF_CLOUD_TOKEN_DEV }}
      
  deploy-prod:
    if: contains(github.event.issue.labels.*.name, 'deploy-prod')
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets:
      TF_CLOUD_TOKEN: ${{ secrets.TF_CLOUD_TOKEN_PROD }}
```

### External Repository Deployment
```yaml
jobs:
  deploy:
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets: inherit
    with:
      repo_url: 'https://github.com/other-org/infrastructure-repo'
```

## 🏗️ Building Your Own Container

### Build Script
```bash
#!/bin/bash
# Build your custom container

# Clone the repository
git clone https://github.com/amartyamandal/diagram-to-iac.git
cd diagram-to-iac

# Build the container
docker build -f .github/actions/r2d/Dockerfile -t yourusername/your-container:latest .

# Push to DockerHub
docker login
docker push yourusername/your-container:latest
```

### Automated Build Workflow
```yaml
name: "Build Container"
on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          file: .github/actions/r2d/Dockerfile
          push: true
          tags: yourusername/your-container:latest
```

## 🔍 What You'll See

When deployment runs, you get:

1. **📋 GitHub Issue**: Detailed deployment progress and results
2. **📊 Workflow Summary**: Step-by-step execution details  
3. **📦 Artifacts**: Logs, Terraform plans, and reports
4. **🤖 Auto-fixes**: PR suggestions for any issues found

## ✅ Success Checklist

After setup, verify everything works:

- ✅ Workflow file is in `.github/workflows/`
- ✅ Required secrets are configured
- ✅ Test with manual trigger first (dry-run mode)
- ✅ Create test issue with `r2d-request` label
- ✅ Check GitHub Actions logs for any issues

## 🎉 You're Done!

The DevOps-in-a-Box container action is now integrated into your repository! You can deploy infrastructure by:

- Creating labeled issues
- Merging pull requests  
- Running manual workflows

The AI-powered SupervisorAgent will handle the rest, orchestrating specialized agents for a complete repo-to-deployment experience.

## 📚 Additional Resources

- **[Complete User Guide](R2D_USER_GUIDE.md)** - Comprehensive features and options
- **[Migration Guide](MIGRATION_GUIDE.md)** - Moving from old workflows
- **[Private Container Examples](PRIVATE_CONTAINER_EXAMPLE.md)** - Detailed private container setup
- **[Troubleshooting](WORKING_EXAMPLES.md)** - Common issues and solutions

---

> **"One container, many minds—zero manual toil."** 🤖
> 
> *Ready for deployment in any repository!*
