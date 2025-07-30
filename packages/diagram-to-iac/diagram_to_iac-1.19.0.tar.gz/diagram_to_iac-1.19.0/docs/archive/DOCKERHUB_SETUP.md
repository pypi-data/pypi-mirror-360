# 🐳 DevOps-in-a-Box Docker Hub Setup Guide

## Overview

The DevOps-in-a-Box R2D Action requires Docker Hub credentials to publish the container image. This guide explains how to set up the required GitHub secrets.

## Required Secrets

The workflow needs these base64-encoded GitHub secrets:

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `DOCKERHUB_USERNAME_ENCODED` | Base64-encoded Docker Hub username | ✅ Yes |
| `DOCKERHUB_API_KEY_ENCODED` | Base64-encoded Docker Hub personal access token | ✅ Yes |

## Step-by-Step Setup

### 1. Create Docker Hub Personal Access Token

1. Go to [Docker Hub Settings](https://hub.docker.com/settings/security)
2. Click "Create Access Token"
3. **Name**: `DevOps-in-a-Box R2D Action`
4. **Permissions**: Select `Read, Write, Delete`
5. Click "Create"
6. **Important**: Copy the token immediately - it won't be shown again!

### 2. Base64 Encode Your Credentials

```bash
# Encode your Docker Hub username
echo -n "your-dockerhub-username" | base64

# Encode your Docker Hub personal access token
echo -n "your-docker-hub-token" | base64
```

### 3. Add GitHub Secrets

1. Go to your repository settings
2. Navigate to `Secrets and variables` → `Actions`
3. Add the following secrets:

**DOCKERHUB_USERNAME_ENCODED**
```
# Example (this is base64 for "amartyamandal"):
YW1hcnR5YW1hbmRhbA==
```

**DOCKERHUB_API_KEY_ENCODED**
```
# Example (your actual token will be different):
ZGtyX3BhdF9abVYwTnpFeVMyRjJUVEZsZUROa1pXTjNOR0ZqWW1Oa01UQXdaVGMzWkE=
```

## Authentication Process

The workflow uses **username + personal access token** authentication:

- **Username**: Your Docker Hub username
- **Password**: Your Docker Hub personal access token (NOT your account password)

## Troubleshooting

### Error: "username and password required"

This means one or both secrets are missing or incorrectly encoded.

**Solution:**
1. Verify both secrets exist in GitHub repository settings
2. Check that values are properly base64 encoded
3. Ensure no extra spaces or newlines in the encoded values

### Error: "unauthorized: authentication required"

This means the credentials are invalid.

**Solution:**
1. Verify your Docker Hub username is correct
2. Generate a new personal access token
3. Ensure the token has `Read, Write, Delete` permissions
4. Re-encode and update the GitHub secrets

### Container builds but doesn't push

This is expected behavior when Docker Hub credentials are missing. The workflow will:
- ✅ Build the container locally
- ⚠️ Skip pushing to Docker Hub
- 📋 Show helpful instructions for setting up credentials

## Verification

After setting up the secrets, you can verify they work by:

1. Creating a new tag: `git tag v1.0.0 && git push origin v1.0.0`
2. Watching the workflow run
3. Checking that the container is pushed to Docker Hub

## Security Notes

- ✅ **Use personal access tokens** - never use your Docker Hub password
- ✅ **Base64 encoding** - protects secrets from accidental exposure in logs
- ✅ **Minimal permissions** - tokens only have access to your repositories
- ✅ **Rotation** - regenerate tokens periodically for security

## Example Workflow Log

When credentials are properly configured, you'll see:

```
✅ Docker Hub credentials found - container will be pushed
🏷️ Updating R2D action.yml to use published container: docker://amartyamandal/diagram-to-iac-r2d:1.0.0
📦 Container Image: https://hub.docker.com/r/amartyamandal/diagram-to-iac-r2d
```

---

**DevOps-in-a-Box**: "One container, many minds—zero manual toil." 🤖✨
