# Using Your Private DockerHub Container with DevOps-in-a-Box

## 🎯 Current Architecture

The R2D unified workflow currently uses:
- **Workflow**: `amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main`
- **Action**: `./.github/actions/r2d` (from the amartyamandal repository)
- **Container**: `docker://ghcr.io/amartyamandal/diagram-to-iac-r2d:1.0.1`

## 🐳 Option 1: Fork and Modify (Recommended)

### Step 1: Fork the Repository
```bash
# Fork amartyamandal/diagram-to-iac to your GitHub account
# Let's say your username is "yourusername"
```

### Step 2: Modify Your Fork's Action
In your fork, edit `.github/actions/r2d/action.yml`:

```yaml
runs:
  using: 'docker'
  image: 'docker://yourdockerhub/your-private-repo:tag'  # Your private container
  args:
    - ${{ inputs.repo_url || inputs.repo }}
    - ${{ inputs.package_version }}
```

### Step 3: Set Up DockerHub Authentication
In your fork's repository, add these secrets:
- `DOCKERHUB_USERNAME` - Your DockerHub username
- `DOCKERHUB_TOKEN` - Your DockerHub access token

### Step 4: Use Your Fork in Other Repositories
In any repository where you want to deploy, use:

```yaml
# .github/workflows/devops-in-a-box.yml
name: "🤖 DevOps-in-a-Box"

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [closed]
  workflow_dispatch:

jobs:
  deploy:
    name: "🚀 Deploy Infrastructure"
    uses: yourusername/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets: inherit
```

## 🔐 Option 2: Direct Container Action (Advanced)

Create your own action that directly uses your private container:

```yaml
# .github/workflows/my-devops-workflow.yml
name: "My DevOps Workflow"

on:
  issues:
    types: [opened, labeled]
  workflow_dispatch:

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
        uses: docker://yourdockerhub/your-private-repo:tag
        with:
          args: ${{ github.repository }} latest
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TFE_TOKEN: ${{ secrets.TF_CLOUD_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          INPUT_DRY_RUN: 'false'
          INPUT_BRANCH_NAME: 'main'
          INPUT_TRIGGER_LABEL: 'r2d-request'
```

## 🔧 Required Secrets for Private DockerHub

### In Your Repository Settings:
| Secret | Description | Required |
|--------|-------------|----------|
| `DOCKERHUB_USERNAME` | Your DockerHub username | ✅ Yes (for private repos) |
| `DOCKERHUB_TOKEN` | DockerHub access token | ✅ Yes (for private repos) |
| `TF_CLOUD_TOKEN` | Terraform Cloud token | ✅ Yes |
| `OPENAI_API_KEY` | OpenAI API key | ❌ Optional |

## 🏗️ Building and Pushing Your Container

### Step 1: Build Your Container
```bash
# From the diagram-to-iac repository root
docker build -f .github/actions/r2d/Dockerfile -t yourdockerhub/your-private-repo:latest .

# Or with a specific version
docker build -f .github/actions/r2d/Dockerfile -t yourdockerhub/your-private-repo:v1.0.0 .
```

### Step 2: Push to Your Private DockerHub
```bash
# Login to DockerHub
docker login

# Push the container
docker push yourdockerhub/your-private-repo:latest
docker push yourdockerhub/your-private-repo:v1.0.0
```

### Step 3: Test Your Container
```bash
# Test locally
docker run --rm \
  -e GITHUB_TOKEN="your-token" \
  -e TFE_TOKEN="your-tf-token" \
  yourdockerhub/your-private-repo:latest \
  "https://github.com/your-test-repo" \
  "latest"
```

## 📋 Complete Example: Using Your Private Container

### Your Fork's Modified Action (`.github/actions/r2d/action.yml`):
```yaml
name: 'DevOps-in-a-Box: R2D Action'
description: 'Repo-to-Deployment automation with self-healing capabilities'

inputs:
  repo_url:
    description: 'GitHub repository URL to deploy'
    required: false
    default: ${{ github.repository }}
  # ... other inputs ...

runs:
  using: 'docker'
  image: 'docker://yourdockerhub/diagram-to-iac-private:latest'
  args:
    - ${{ inputs.repo_url }}
    - ${{ inputs.package_version }}
  env:
    INPUT_DRY_RUN: ${{ inputs.dry_run }}
    INPUT_BRANCH_NAME: ${{ inputs.branch }}
    # ... other environment variables ...
```

### Using Your Fork in Another Repository:
```yaml
# .github/workflows/deploy.yml
name: "Deploy with My Private Container"

on:
  issues:
    types: [opened, labeled]

jobs:
  deploy:
    uses: yourusername/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      TF_CLOUD_TOKEN: ${{ secrets.TF_CLOUD_TOKEN }}
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
```

## 🎯 Benefits of Using Your Private Container

✅ **Full Control**: You control the container image and its updates
✅ **Private Dependencies**: Include proprietary tools or configurations
✅ **Custom Modifications**: Modify the R2D agents for your specific needs
✅ **Security**: Your container stays in your private DockerHub repository
✅ **Versioning**: Use specific tags for stable deployments

## 🚨 Important Notes

1. **Authentication**: Private DockerHub repos require authentication in GitHub Actions
2. **Secrets Management**: Ensure DockerHub credentials are properly secured
3. **Container Updates**: You're responsible for updating and maintaining your container
4. **Compatibility**: Ensure your modifications maintain compatibility with the R2D system

---

> **"One container, many minds—zero manual toil."** 🤖
> 
> *Now with your private container!*
