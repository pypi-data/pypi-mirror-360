# Example: Using Your Private DockerHub Container

## 🎯 Practical Implementation Example

### Scenario
- Your DockerHub: `yourusername/my-devops-container:v1.0.0` (private repository)
- Your fork: `yourusername/diagram-to-iac`
- Target repo: `yourusername/my-infrastructure`

## 📋 Step-by-Step Implementation

### Step 1: Fork and Modify Action

**File**: `yourusername/diagram-to-iac/.github/actions/r2d/action.yml`

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
  package_version:
    description: 'diagram-to-iac package version to use'
    required: false
    default: ''
  dry_run:
    description: 'Run in dry-run mode'
    required: false
    default: 'false'
  branch:
    description: 'Branch name for operations'
    required: false
    default: 'main'
  thread_id:
    description: 'Thread ID for conversation tracking'
    required: false
    default: ''
  trigger_label:
    description: 'Issue label that triggers the workflow'
    required: false
    default: 'r2d-request'

runs:
  using: 'docker'
  image: 'docker://yourusername/my-devops-container:v1.0.0'  # ← YOUR PRIVATE CONTAINER
  args:
    - ${{ inputs.repo_url }}
    - ${{ inputs.package_version }}
  env:
    INPUT_DRY_RUN: ${{ inputs.dry_run }}
    INPUT_BRANCH_NAME: ${{ inputs.branch }}
    INPUT_THREAD_ID: ${{ inputs.thread_id }}
    INPUT_TRIGGER_LABEL: ${{ inputs.trigger_label }}
```

### Step 2: Modify Unified Workflow for Authentication

**File**: `yourusername/diagram-to-iac/.github/workflows/r2d-unified.yml`

Add DockerHub login step before using the action:

```yaml
# Add this step before the "🤖 Execute R2D Action" step
- name: "🐳 Login to DockerHub"
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: "🤖 Execute R2D Action"
  id: r2d
  uses: ./.github/actions/r2d
  with:
    repo_url: ${{ format('{0}/{1}', github.server_url, needs.route.outputs.target_repo) }}
    branch: ${{ needs.route.outputs.target_branch }}
    thread_id: ${{ needs.route.outputs.thread_id }}
    trigger_label: ${{ inputs.trigger_label || 'r2d-request' }}
    dry_run: ${{ needs.route.outputs.dry_run_mode }}
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    TFE_TOKEN: ${{ secrets.TF_CLOUD_TOKEN }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

### Step 3: Configure Secrets in Your Fork

In `yourusername/diagram-to-iac` repository settings, add:

| Secret | Value | Purpose |
|--------|-------|---------|
| `DOCKERHUB_USERNAME` | `yourusername` | DockerHub authentication |
| `DOCKERHUB_TOKEN` | `dckr_pat_xyz...` | DockerHub access token |

### Step 4: Use Your Fork in Target Repository

**File**: `yourusername/my-infrastructure/.github/workflows/devops.yml`

```yaml
name: "🤖 My DevOps-in-a-Box"

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [closed]
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Run in dry-run mode'
        required: false
        default: true
        type: boolean

jobs:
  deploy:
    name: "🚀 Deploy Infrastructure"
    uses: yourusername/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets: inherit  # This passes all secrets to the workflow
    with:
      dry_run: ${{ inputs.dry_run || false }}
```

### Step 5: Configure Secrets in Target Repository

In `yourusername/my-infrastructure` repository settings, add:

| Secret | Value | Purpose |
|--------|-------|---------|
| `TF_CLOUD_TOKEN` | `xxx.atlasv1.yyy` | Terraform Cloud access |
| `OPENAI_API_KEY` | `sk-xxx` | AI capabilities (optional) |
| `DOCKERHUB_USERNAME` | `yourusername` | Container access |
| `DOCKERHUB_TOKEN` | `dckr_pat_xyz` | Container access |

## 🐳 Building Your Private Container

### Build Script
```bash
#!/bin/bash
# build-and-push.sh

set -e

# Configuration
DOCKERHUB_REPO="yourusername/my-devops-container"
VERSION="v1.0.0"
LATEST_TAG="latest"

echo "🏗️ Building DevOps-in-a-Box container..."

# Build the container
docker build \
  -f .github/actions/r2d/Dockerfile \
  -t ${DOCKERHUB_REPO}:${VERSION} \
  -t ${DOCKERHUB_REPO}:${LATEST_TAG} \
  .

echo "✅ Container built successfully"

# Login to DockerHub
echo "🔐 Logging in to DockerHub..."
docker login

# Push the container
echo "📤 Pushing to DockerHub..."
docker push ${DOCKERHUB_REPO}:${VERSION}
docker push ${DOCKERHUB_REPO}:${LATEST_TAG}

echo "🎉 Container pushed successfully!"
echo "📦 Available at: docker://yourusername/my-devops-container:${VERSION}"
```

### Automated Build Workflow
**File**: `yourusername/diagram-to-iac/.github/workflows/build-container.yml`

```yaml
name: "🐳 Build and Push Container"

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: yourusername/my-devops-container
          tags: |
            type=ref,event=tag
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: .github/actions/r2d/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## 🔄 Complete Workflow Flow

```
1. User creates issue in yourusername/my-infrastructure
   ↓
2. GitHub triggers yourusername/diagram-to-iac/.github/workflows/r2d-unified.yml@main
   ↓
3. Workflow logs into DockerHub using DOCKERHUB_USERNAME/DOCKERHUB_TOKEN
   ↓
4. Workflow pulls yourusername/my-devops-container:v1.0.0
   ↓
5. Container executes with environment variables (TFE_TOKEN, etc.)
   ↓
6. SupervisorAgent orchestrates deployment
   ↓
7. Results posted back to GitHub issue
```

## 🎯 Benefits of This Approach

✅ **Private Control**: Your container, your rules
✅ **Custom Modifications**: Add proprietary tools or configurations
✅ **Version Control**: Tag specific versions for stable deployments
✅ **Security**: Container stays in your private DockerHub
✅ **Flexibility**: Modify R2D agents for your specific needs

## 🚨 Security Best Practices

1. **Use Access Tokens**: Never use your DockerHub password directly
2. **Scope Permissions**: Create tokens with minimal required permissions
3. **Rotate Regularly**: Update DockerHub tokens periodically
4. **Monitor Usage**: Track container pulls and usage
5. **Keep Updated**: Regularly update your container with security patches

---

> **"One container, many minds—zero manual toil."** 🤖
> 
> *Now powered by your private container!*
