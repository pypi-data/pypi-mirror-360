# 🔧 Private Container Workflow Fix

If you're using a private GHCR container, GitHub Actions needs to authenticate before it can pull the container for the action. Here's how to fix it:

## Option 1: Pre-pull the Container

Add this step **before** your R2D action in the workflow:

```yaml
- name: "🐳 Pre-pull private container"
  run: |
    echo "Pulling private container for action..."
    docker pull ghcr.io/amartyamandal/diagram-to-iac-r2d:latest
    echo "✅ Container pulled successfully"

- name: "🤖 Execute R2D Action"
  id: r2d
  uses: ./.github/actions/r2d
  # ... rest of your action configuration
```

## Option 2: Convert to Composite Action

Update the action.yml to use a composite action instead of a Docker action:

```yaml
# .github/actions/r2d/action.yml
name: 'DevOps-in-a-Box: R2D Action'
description: 'Repo-to-Deployment automation with self-healing capabilities'

# ... inputs remain the same ...

runs:
  using: 'composite'
  steps:
    - name: "🔐 Login to GHCR"
      shell: bash
      run: |
        echo "${{ env.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
      env:
        GITHUB_TOKEN: ${{ env.GITHUB_TOKEN }}
    
    - name: "🤖 Run R2D Container"
      shell: bash
      run: |
        docker run --rm \
          -e GITHUB_TOKEN \
          -e TFE_TOKEN \
          -e OPENAI_API_KEY \
          -e ANTHROPIC_API_KEY \
          -e GOOGLE_API_KEY \
          -e INPUT_DRY_RUN \
          -e INPUT_BRANCH_NAME \
          -e INPUT_THREAD_ID \
          -e INPUT_TRIGGER_LABEL \
          -v ${{ github.workspace }}:/github/workspace \
          ghcr.io/amartyamandal/diagram-to-iac-r2d:latest \
          "${{ inputs.repo_url || inputs.repo }}" \
          "${{ inputs.package_version }}"
```

## Option 3: Make Container Public (Recommended)

The simplest solution is to make your GHCR container public:

1. Go to your GitHub repository
2. Navigate to **Packages** tab
3. Click on **diagram-to-iac-r2d** package
4. Go to **Package settings**
5. Change visibility to **Public**

This eliminates the authentication complexity while maintaining all the benefits of GHCR.
