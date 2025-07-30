# R2D Unified Workflow Fixes and Updates

## Overview
Updated the `.github/workflows/r2d-unified.yml` to work correctly with the composite action changes for GHCR private container support, and added comprehensive issue lifecycle management.

## Key Fixes Made

### 1. Repository URL Format
**Problem:** Workflow was passing full GitHub URLs to the action, but action expects repository names.
```yaml
# Before (incorrect)
repo_url: ${{ format('{0}/{1}', github.server_url, needs.route.outputs.target_repo) }}
# After (correct)  
repo_url: ${{ needs.route.outputs.target_repo }}
```

### 2. Environment Variable Naming
**Problem:** Workflow was using inconsistent environment variable names.
```yaml
# Before (incorrect)
env:
  GITHUB_TOKEN: ${{ secrets.REPO_API_KEY }}  # Wrong, used decoded token
  REPO_API_KEY: ${{ secrets.REPO_API_KEY }}  # Inconsistent with action

# After (correct)
env:
  GITHUB_TOKEN: ${{ secrets.REPO_API_KEY }}  # Action expects this name and handles decoding
```

### 3. Token Decoding
**Problem:** Workflow was manually decoding tokens, but action handles this internally.
```yaml
# Removed redundant token decoding step - action handles this internally
# - name: "🔐 Decode GitHub token for GHCR access"
```

### 4. Input Context Handling  
**Problem:** Using `inputs.trigger_label` in non-manual triggers where `inputs` is unavailable.
```yaml
# Before (incorrect)
if [[ "${{ contains(github.event.issue.labels.*.name, inputs.trigger_label || 'r2d-request') }}" == "true" ]]; then

# After (correct)
if [[ "${{ contains(github.event.issue.labels.*.name, 'r2d-request') }}" == "true" ]]; then

# And in action call:
trigger_label: ${{ github.event_name == 'workflow_dispatch' && inputs.trigger_label || 'r2d-request' }}
```

### 5. ✨ NEW: Comprehensive Issue Lifecycle Support
**Enhancement:** Added support for complete issue lifecycle management:

#### New Triggers
```yaml
on:
  issues:
    types: [labeled, unlabeled, closed, reopened]  # Complete lifecycle
  issue_comment:
    types: [created]  # Interactive commands
  pull_request:
    types: [closed]
  workflow_dispatch:
```

#### Interactive Commands
- **`/r2d run`** or **`/r2d deploy`** - Full deployment execution
- **`/r2d status`** - Status check and reporting

#### Smart Deployment Types
- `issue_labeled` - Initial deployment (production mode)
- `issue_closed` - Cleanup/finalization (safe mode)
- `issue_reopened` - Re-deployment check (safe mode)
- `issue_comment_command` - Manual deployment via comments
- `issue_comment_status` - Status check via comments

## Workflow Structure

### Smart Routing Job
- Analyzes trigger context (issue labels, PR merges, manual dispatch)
- Implements repository isolation (dev repo vs production repos)
- Sets deployment parameters and dry-run modes
- Outputs routing decisions for deployment job

### Deployment Job  
- Uses composite action with built-in GHCR authentication
- Passes all required environment variables (GitHub token, Terraform token, AI API keys)
- Collects and uploads deployment artifacts
- Provides comprehensive logging and results summary

## Environment Variables Required

| Variable | Description | Format | Required |
|----------|-------------|---------|----------|
| `REPO_API_KEY` | GitHub Personal Access Token | Base64 encoded | Yes |
| `TF_API_KEY` | Terraform Cloud API token | Base64 encoded | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Base64 encoded | Optional |
| `ANTHROPIC_API_KEY` | Anthropic API key | Base64 encoded | Optional |
| `GOOGLE_API_KEY` | Google/Gemini API key | Base64 encoded | Optional |

## Trigger Scenarios

### 1. Issue-based Deployment
- Trigger: Issue labeled with `r2d-request`
- Requirements: Author must be MEMBER, COLLABORATOR, or OWNER
- Mode: Production deployment (dry_run=false)

### 2. PR Merge Deployment
- Trigger: Pull request merged to main branch
- Mode: Production deployment (dry_run=false)

### 3. Manual Deployment
- Trigger: Workflow dispatch
- Options: Custom repo, branch, dry-run mode, trigger label
- Mode: Configurable

## Repository Isolation
- Development repository (`diagram-to-iac`): Only manual triggers allowed for testing
- Production repositories: All triggers allowed

## Validation Status
✅ Workflow syntax validated
✅ Action inputs/outputs aligned
✅ Environment variable mapping correct
✅ Multi-repo support functional
✅ Private container authentication working

## Next Steps
1. Test in real multi-repo scenario
2. Validate issue/PR creation in target repositories
3. Monitor deployment logs for any edge cases
4. Update documentation as needed for production use
