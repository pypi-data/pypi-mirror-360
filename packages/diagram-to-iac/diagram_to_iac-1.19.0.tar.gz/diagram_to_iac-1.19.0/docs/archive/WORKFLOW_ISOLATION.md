# Workflow Isolation for R2D Testing Workflows

## Overview

The diagram-to-iac repository contains three R2D testing workflows that are designed to test the R2D action functionality. However, during active development of the diagram-to-iac project itself, these workflows can interfere with the development process by triggering unnecessarily.

This document describes the workflow isolation feature that prevents R2D testing workflows from running during diagram-to-iac development while preserving their testing capabilities.

## Problem Statement

**Issue**: The R2D testing workflows (`manual-r2d.yml`, `r2d_prmerge.yml`, `r2d_trigger.yml`) would trigger during:
- Development PRs being merged into diagram-to-iac
- Issues opened in the diagram-to-iac repository 
- Manual testing of the diagram-to-iac project

**Impact**: This created noise, unnecessary workflow runs, and potential interference with development processes.

## Solution

### Repository Context Detection

Each R2D workflow now includes repository context checking that:
1. **Automatically skips** when running in a repository containing `diagram-to-iac` in the name
2. **Allows manual override** via the `force_run_in_dev_repo` input parameter
3. **Runs normally** in all other repositories (the intended use case)

## Affected Workflows

1. **Manual R2D Test** (`manual-r2d.yml`)
2. **PR Merge Triggered R2D** (`r2d_prmerge.yml`) 
3. **Issue Triggered R2D** (`r2d_trigger.yml`)

## Implementation Details

### 1. Manual R2D Workflow (`manual-r2d.yml`)

**New Input Parameter**:
```yaml
force_run_in_dev_repo:
  description: 'Force run in diagram-to-iac development repo (for testing the action itself)'
  required: false
  default: false
  type: boolean
```

**Conditional Execution**:
```yaml
jobs:
  run-r2d:
    if: ${{ !contains(github.repository, 'diagram-to-iac') || inputs.force_run_in_dev_repo }}
```

### 2. PR Merge R2D Workflow (`r2d_prmerge.yml`)

**New Input Parameter**:
```yaml
force_run_in_dev_repo:
  description: 'Force run in diagram-to-iac development repo (for testing the action itself)'
  required: false
  default: false
  type: boolean
```

**Enhanced Conditional Execution**:
```yaml
jobs:
  deploy:
    if: |
      ((!contains(github.repository, 'diagram-to-iac') || inputs.force_run_in_dev_repo) &&
       ((github.event_name == 'pull_request' && 
         github.event.pull_request.merged == true &&
         github.event.pull_request.base.ref == github.event.repository.default_branch) ||
        github.event_name == 'workflow_dispatch'))
```

### 3. Issue Triggered R2D Workflow (`r2d_trigger.yml`)

**New Input Parameter**:
```yaml
force_run_in_dev_repo:
  description: 'Force run in diagram-to-iac development repo (for testing the action itself)'
  required: false
  default: false
  type: boolean
```

**Enhanced Conditional Execution**:
```yaml
jobs:
  deploy:
    if: |
      ((!contains(github.repository, 'diagram-to-iac') || inputs.force_run_in_dev_repo) &&
       ((github.event_name == 'issues' && 
         contains(github.event.issue.labels.*.name, 'r2d-request') &&
         (github.event.issue.author_association == 'MEMBER' || 
          github.event.issue.author_association == 'COLLABORATOR' ||
          github.event.issue.author_association == 'OWNER')) ||
        github.event_name == 'workflow_dispatch'))
```

## Usage Scenarios

### In Development Repository (diagram-to-iac)
- **Default behavior**: Workflows are skipped automatically
- **Manual testing**: Use `force_run_in_dev_repo: true` to run workflows for action testing
- **Development safety**: No accidental triggering during normal development activities

### In External Repositories  
- **Normal operation**: All workflows function as designed
- **Full functionality**: Complete R2D action capabilities available
- **No restrictions**: Workflows respond to all configured triggers

## Usage Examples

### Testing the Action During Development
When you need to test the R2D action functionality:

1. **Manual R2D Test**:
   ```
   Go to Actions → Manual R2D Test → Run workflow
   Set "Force run in diagram-to-iac development repo" to true
   ```

2. **PR Merge Test**:
   ```
   Go to Actions → PR Merge Triggered R2D → Run workflow  
   Set "Force run in diagram-to-iac development repo" to true
   ```

3. **Issue Trigger Test**:
   ```
   Go to Actions → Issue Triggered R2D → Run workflow
   Set "Force run in diagram-to-iac development repo" to true
   ```

### Normal Development Activities
During regular development:
- Push commits: Only `diagram-to-iac-build.yml` runs
- Merge PRs: R2D workflows are automatically skipped
- Create issues: R2D workflows are automatically skipped
- Tag releases: Normal build and release process

## Benefits

1. **Clean Development Environment**: No interference from testing workflows during development
2. **Intentional Testing**: Explicit opt-in required to test action functionality  
3. **External Compatibility**: Full functionality preserved when action is used in other repositories
4. **Safety**: Prevents accidental resource deployments during development

## Implementation Details

The isolation uses GitHub Actions conditional expressions:
```yaml
if: ${{ !contains(github.repository, 'diagram-to-iac') || inputs.force_run_in_dev_repo }}
```

This condition:
- Checks if repository name contains 'diagram-to-iac'
- Allows override with the force flag
- Maintains backward compatibility for external usage

## Troubleshooting

### Workflow Not Running in External Repository
- Verify the repository name doesn't contain 'diagram-to-iac'
- Check that trigger conditions are met (labels, permissions, etc.)

### Need to Test Action During Development
- Use manual workflow dispatch with `force_run_in_dev_repo: true`
- Ensure you have the necessary secrets configured for testing

### Workflow Still Running During Development
- Check if `force_run_in_dev_repo` was accidentally set to true
- Verify the repository name contains 'diagram-to-iac'

## Implementation Status

✅ **COMPLETED** - R2D Workflow Isolation has been successfully implemented and validated.

### Summary of Changes Made

1. **Manual R2D Workflow** (`manual-r2d.yml`):
   - Added `force_run_in_dev_repo` boolean input parameter
   - Implemented job-level isolation condition
   - Status: ✅ **FULLY IMPLEMENTED**

2. **PR Merge Triggered R2D** (`r2d_prmerge.yml`):
   - Added `force_run_in_dev_repo` boolean input parameter  
   - Updated existing guard clause with isolation logic
   - Status: ✅ **FULLY IMPLEMENTED**

3. **Issue Triggered R2D** (`r2d_trigger.yml`):
   - Added `force_run_in_dev_repo` boolean input parameter
   - Updated existing guard clause with isolation logic
   - Status: ✅ **FULLY IMPLEMENTED**

4. **Build Workflow** (`diagram-to-iac-build.yml`):
   - Verified to be unaffected by isolation changes
   - Status: ✅ **VALIDATED**

### Validation Results

All workflows have been validated using both automated tests and manual verification:

- ✅ Repository context checking implemented (`contains(github.repository, 'diagram-to-iac')`)
- ✅ Manual override capability available (`inputs.force_run_in_dev_repo`)
- ✅ Boolean input parameters properly configured (type: boolean, default: false)
- ✅ Job-level conditional execution implemented
- ✅ Build workflow remains unaffected
- ✅ YAML syntax validation passed

### Testing Performed

1. **YAML Syntax Validation**: All workflow files validated for proper YAML syntax
2. **Repository Context Detection**: Verified that workflows detect `diagram-to-iac` in repository name
3. **Input Parameter Validation**: Confirmed all `force_run_in_dev_repo` inputs properly configured
4. **Conditional Logic Testing**: Validated job-level conditions include both repository check and force override
5. **Build Workflow Isolation**: Verified main build workflow remains unaffected

### Deployment Status

The workflow isolation feature is now **LIVE** and **ACTIVE**:
- ✅ All R2D testing workflows will automatically skip during diagram-to-iac development
- ✅ Manual override capability available for intentional testing
- ✅ External repositories using the R2D action are unaffected
- ✅ Development workflow is now clean and isolated

---

**Implementation completed on**: December 2024  
**Next maintenance**: No immediate action required - feature is fully operational
