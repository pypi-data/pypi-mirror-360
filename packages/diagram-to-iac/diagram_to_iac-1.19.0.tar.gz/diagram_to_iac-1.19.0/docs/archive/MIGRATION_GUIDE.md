# Migration Guide: Moving to Unified R2D Workflow

This guide helps you migrate from the old R2D workflows to the new unified approach.

## 🎯 Why Migrate?

The unified R2D workflow provides:
- ✅ **Simpler setup**: One workflow file instead of three
- ✅ **Smart routing**: Automatically handles different trigger types  
- ✅ **Better isolation**: Improved repository separation logic
- ✅ **Easier maintenance**: Single codebase to maintain
- ✅ **Clearer documentation**: Consolidated user guide

## 🔄 Migration Steps

### Step 1: Remove Old Workflows

If you have any of these old workflow files, remove them:

```bash
# Remove old workflows (if they exist in your repo)
rm .github/workflows/manual-r2d.yml
rm .github/workflows/r2d_prmerge.yml  
rm .github/workflows/r2d_trigger.yml
```

### Step 2: Add the Unified Workflow

Create the new unified workflow file:

```yaml
# .github/workflows/r2d-unified.yml
name: R2D - DevOps in a Box
on:
  issues:
    types: [opened, edited]
  pull_request:
    types: [closed]
  workflow_dispatch:
    inputs:
      repo_url:
        description: 'Repository URL to deploy'
        required: false
        type: string

jobs:
  r2d-deploy:
    uses: amartyamandal/diagram-to-iac/.github/workflows/r2d-unified.yml@main
    secrets: inherit
    with:
      repo_url: ${{ inputs.repo_url || github.server_url }}/${{ github.repository }}
```

### Step 3: Verify Your Secrets

Ensure you have the required secrets configured in your repository settings:

| Secret | Description | Required |
|--------|-------------|----------|
| `GITHUB_TOKEN` | GitHub API access (auto-provided) | ✅ Yes |
| `TF_CLOUD_TOKEN` | Terraform Cloud workspace token (**base64 encoded**) | ✅ Yes |
| `OPENAI_API_KEY` | OpenAI API key for AI features (**base64 encoded**) | ❌ Optional |
| `ANTHROPIC_API_KEY` | Claude API key for AI features (**base64 encoded**) | ❌ Optional |

> **🚨 CRITICAL**: All secret values must be **base64-encoded** before adding to GitHub.
> 
> ```bash
> # Encode your secrets
> echo -n "your-tf-cloud-token" | base64
> echo -n "your-openai-key" | base64
> ```
> 
> **Important**: The unified workflow automatically maps `TF_CLOUD_TOKEN` to the internal `TFE_TOKEN` environment variable.

### Step 4: Test the Migration

1. **Manual Test**: Go to Actions → R2D - DevOps in a Box → Run workflow
2. **Issue Test**: Create an issue with "deploy" in the title
3. **PR Test**: Create and merge a pull request

## 📋 Feature Mapping

| Old Workflow | Old Trigger | New Trigger | Notes |
|--------------|-------------|-------------|-------|
| `manual-r2d.yml` | Manual dispatch | Manual dispatch | ✅ Same trigger, improved UX |
| `r2d_trigger.yml` | Issue creation | Issue opened/edited | ✅ Enhanced issue detection |
| `r2d_prmerge.yml` | PR merge | PR closed | ✅ Same functionality |

## 🔒 Security Improvements

The unified workflow includes:

- **Repository Isolation**: Development repo workflows don't run unless explicitly triggered
- **Permission Validation**: Checks user permissions for issue-based triggers  
- **Better Error Handling**: Clearer failure modes and debugging information
- **Artifact Collection**: Comprehensive logging and artifact preservation

## 🧪 Testing Your Migration

### Manual Deployment Test

```yaml
# Test with workflow_dispatch
# 1. Go to Actions tab
# 2. Select "R2D - DevOps in a Box"  
# 3. Click "Run workflow"
# 4. Optionally specify a different repo URL
# 5. Click "Run workflow"
```

### Issue-Based Deployment Test

```markdown
# Create a new issue with this content:
Title: Deploy infrastructure updates
Body: Please deploy the latest changes to our infrastructure.
```

### PR-Based Deployment Test

```bash
# Create a test branch and PR
git checkout -b test-r2d-migration
echo "# Test change" >> README.md
git add README.md
git commit -m "Test R2D migration"
git push origin test-r2d-migration
# Create PR and merge it
```

## 🚨 Troubleshooting

### Common Issues

**Issue**: Workflow doesn't trigger on issues
- **Solution**: Ensure the issue title or body contains deployment keywords like "deploy", "infrastructure", or "terraform"

**Issue**: Permission denied errors
- **Solution**: Check that `TF_CLOUD_TOKEN` is correctly set with appropriate permissions

**Issue**: Repository isolation not working
- **Solution**: Verify you're not in the development repository (`amartyamandal/diagram-to-iac`) unless using manual override

**Issue**: Secrets not available
- **Solution**: Ensure secrets are configured at the repository level, not environment level

### Getting Help

1. **Check the logs**: Download workflow artifacts for detailed logs
2. **Review the User Guide**: See [R2D_USER_GUIDE.md](R2D_USER_GUIDE.md) for complete documentation
3. **Open an issue**: Create an issue in the diagram-to-iac repository for support

## 📈 What's Next?

After successful migration:

1. **Monitor deployments**: Watch the first few runs to ensure everything works
2. **Update documentation**: Update any internal docs that reference the old workflows
3. **Train your team**: Share the new trigger methods with your team
4. **Explore features**: Try the different deployment triggers and options

## 🎉 Migration Complete!

You're now using the simplified, unified R2D workflow! The system provides the same powerful DevOps automation with a much cleaner setup and better user experience.

---

> 📚 **Need more help?** See the complete [R2D User Guide](R2D_USER_GUIDE.md)
