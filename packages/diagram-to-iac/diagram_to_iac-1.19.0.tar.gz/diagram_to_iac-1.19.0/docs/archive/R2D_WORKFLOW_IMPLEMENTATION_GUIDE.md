# 🚀 R2D Workflow Implementation Guide

## Overview
This guide explains how to implement the DevOps-in-a-Box R2D (Repo-to-Deployment) workflow in other repositories using GitHub Container Registry (GHCR).

## ✅ What's Updated (GHCR Migration Complete)

- **✅ Container Registry**: Migrated to **dual-registry strategy**
  - **Primary**: GitHub Container Registry (GHCR) for pulls
  - **Backup**: Docker Hub for redundancy (pushes only)
- **✅ Action**: Uses `ghcr.io/amartyamandal/diagram-to-iac-r2d:latest`
- **✅ Authentication**: Seamless GHCR authentication via GitHub PAT
- **✅ Secrets**: Simplified secret configuration
- **✅ Reliability**: Dual-registry ensures high availability

## 📋 Implementation Steps

### 1. Copy the Workflow File

Copy `.github/workflows/r2d-unified.yml` to your target repository:

```bash
# In your target repository
mkdir -p .github/workflows
curl -o .github/workflows/r2d-unified.yml \
  https://raw.githubusercontent.com/amartyamandal/diagram-to-iac/main/.github/workflows/r2d-unified.yml
```

### 2. Configure Required Secrets

In your target repository, go to **Settings** → **Secrets and variables** → **Actions** and add:

#### **Required Secrets (Base64 Encoded):**

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `REPO_API_KEY` | GitHub Personal Access Token | [GitHub Settings](https://github.com/settings/tokens) with `repo`, `write:packages`, `read:packages` scopes |
| `TF_API_KEY` | Terraform Cloud API Token | [Terraform Cloud Settings](https://app.terraform.io/app/settings/tokens) |
| `OPENAI_API_KEY` | OpenAI API Key | [OpenAI Platform](https://platform.openai.com/api-keys) |

#### **Optional Secrets (Base64 Encoded):**

| Secret Name | Description |
|-------------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic Claude API Key |
| `GOOGLE_API_KEY` | Google AI API Key |

#### **How to Base64 Encode Secrets:**

```bash
# Encode your secrets before adding to GitHub
echo "your_secret_value" | base64
```

### 3. Trigger the Workflow

The R2D workflow can be triggered in three ways:

#### **Option 1: Manual Trigger**
- Go to **Actions** tab in your repository
- Select **"DevOps-in-a-Box: R2D Unified Workflow"**
- Click **"Run workflow"**
- Configure options and run

#### **Option 2: Issue-Based Trigger**
- Create an issue in your repository
- Add the label `r2d-request` (or custom label)
- The workflow will automatically deploy

#### **Option 3: PR Merge Trigger**
- Merge a pull request to the default branch
- The workflow will automatically deploy

## 🐳 Container Details

**Current Container**: `ghcr.io/amartyamandal/diagram-to-iac-r2d:latest` (Private)

**Important**: This container is **private** and requires authentication. The action handles this automatically using a **composite action approach** that authenticates internally before pulling the container.

**Benefits of GHCR + Docker Hub Strategy:**
- ✅ **GHCR Primary** - Native GitHub Actions integration with private container support
- ✅ **Docker Hub Backup** - Public visibility and cross-platform compatibility
- ✅ **High Availability** - Redundancy across two major container registries
- ✅ **Secure Access** - Private containers with proper authentication
- ✅ **Migration Safety** - Gradual transition with fallback options

## 🔐 Security Notes

1. **All secrets should be base64 encoded** before adding to GitHub repository secrets
2. **GitHub Personal Access Token** needs specific scopes:
   - `repo` - Repository access
   - `write:packages` - Push to GHCR (for build workflows)
   - `read:packages` - Pull from GHCR
3. **Secrets are automatically masked** in workflow logs
4. **Container runs as non-root** user for security

## 📊 Expected Workflow Behavior

### **Smart Routing:**
- ✅ **Development repos**: Only manual triggers (prevents accidental deployments)
- ✅ **Production repos**: All trigger types work
- ✅ **Permission checks**: Only authorized users can trigger via issues
- ✅ **Branch targeting**: Automatic branch detection and targeting

### **Deployment Outputs:**
- 📊 **Step Summary**: Rich markdown dashboard
- 📋 **GitHub Issues**: Automatic issue creation for errors
- 🌿 **Pull Requests**: Auto-generated fixes for common issues
- 📦 **Artifacts**: Logs, Terraform plans, generated files

## 🎯 Migration from Docker Hub

If you're migrating from an older version that used Docker Hub:

### **What Changed:**
- ❌ **Removed**: Docker Hub login step for pulls (backup registry still receives pushes)
- ❌ **Removed**: `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets requirement
- ✅ **Added**: GHCR container reference as primary registry
- ✅ **Added**: Dual-registry redundancy strategy  
- ✅ **Updated**: Secret naming to match project conventions

### **Action Required:**
1. **Remove** old Docker Hub secrets (optional cleanup)
2. **Update** workflow file to latest version
3. **Test** with manual trigger first

## 🧪 Testing Your Implementation

1. **Manual Test**: Run workflow manually with dry-run enabled
2. **Issue Test**: Create test issue with `r2d-request` label
3. **PR Test**: Create test PR and merge to trigger deployment

## 📚 Additional Resources

- **Main Repository**: [amartyamandal/diagram-to-iac](https://github.com/amartyamandal/diagram-to-iac)
- **Action Documentation**: [R2D Action README](../github/actions/r2d/README.md)
- **Container Registry**: [GHCR Package](https://github.com/amartyamandal/diagram-to-iac/pkgs/container/diagram-to-iac-r2d)

## 🆘 Troubleshooting

### **Common Issues:**

1. **"Container not found" or "unauthorized"**
   - This indicates the private GHCR container requires authentication
   - Ensure your `REPO_API_KEY` secret is properly base64-encoded
   - Verify the token has `read:packages` scope for GHCR access
   - The action now handles GHCR authentication internally using a composite action approach

2. **"Missing secrets"**
   - Verify all required secrets are base64 encoded and added to repository
   - Check secret names match exactly (case-sensitive)

3. **"Permission denied"**
   - Ensure GitHub token has correct scopes: `repo`, `write:packages`, `read:packages`
   - Check that the user has access to the private container

4. **"Workflow not triggering"**
   - Check repository permissions and user associations
   - Verify issue labels match configuration
   - Ensure PR is merged to default branch

### **Private Container Troubleshooting:**

If you get "unauthorized" errors with the private GHCR container:

```bash
# Test your token locally
echo "YOUR_BASE64_REPO_API_KEY" | base64 -d | docker login ghcr.io -u your-username --password-stdin
docker pull ghcr.io/amartyamandal/diagram-to-iac-r2d:latest
```

**Alternative**: If private container issues persist, you can temporarily use a public fallback by updating the action.yml to use a public container.

---

**🎉 Ready to deploy!** The R2D workflow is now configured to use GitHub Container Registry for reliable, authentication-free container access.
