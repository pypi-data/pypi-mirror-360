# R2D Enhanced Issue Lifecycle Support

## Overview
The R2D Unified Workflow now supports comprehensive issue lifecycle management, allowing for sophisticated deployment automation through GitHub issues and comments.

## Supported Triggers

### 🏷️ Issue Labels
- **Trigger**: `issues: [labeled]`
- **Action**: When an issue is labeled with `r2d-request`
- **Behavior**: Initiates full R2D deployment process
- **Authorization**: MEMBER, COLLABORATOR, or OWNER required
- **Mode**: Production deployment (`dry_run=false`)

### 🏷️ Issue Unlabels  
- **Trigger**: `issues: [unlabeled]`
- **Action**: When `r2d-request` label is removed
- **Behavior**: Potential cleanup trigger (currently logged only)
- **Future Enhancement**: Could implement resource cleanup

### 🔒 Issue Closure
- **Trigger**: `issues: [closed]`
- **Action**: When an R2D-labeled issue is closed
- **Behavior**: Runs finalization/cleanup operations
- **Mode**: Safe mode (`dry_run=true`)
- **Use Cases**: 
  - Resource cleanup
  - Cost reporting
  - Deployment summary
  - Archive artifacts

### 🔄 Issue Reopening
- **Trigger**: `issues: [reopened]`
- **Action**: When a closed R2D issue is reopened
- **Behavior**: Triggers re-deployment or status check
- **Authorization**: MEMBER, COLLABORATOR, or OWNER required
- **Mode**: Safe mode (`dry_run=true`)
- **Use Cases**:
  - Re-run failed deployments
  - Update existing infrastructure
  - Status verification

### 💬 Issue Comments - Interactive Commands
- **Trigger**: `issue_comment: [created]`
- **Authorization**: MEMBER, COLLABORATOR, or OWNER required
- **Supported Commands**:

#### `/r2d run` or `/r2d deploy`
- **Behavior**: Full deployment execution
- **Mode**: Production deployment (`dry_run=false`)
- **Use Case**: Manual trigger for deployment

#### `/r2d status`
- **Behavior**: Status check and reporting
- **Mode**: Safe mode (`dry_run=true`)
- **Use Case**: Check deployment status without changes

## Deployment Types Generated

| Trigger | Deployment Type | Dry Run | Purpose |
|---------|----------------|---------|---------|
| Issue labeled | `issue_labeled` | false | Initial deployment |
| Issue closed | `issue_closed` | true | Cleanup/finalization |
| Issue reopened | `issue_reopened` | true | Re-deployment check |
| Comment `/r2d run` | `issue_comment_command` | false | Manual deployment |
| Comment `/r2d status` | `issue_comment_status` | true | Status check |
| PR merged | `pr_merge` | false | Continuous deployment |
| Manual dispatch | `manual` | configurable | Testing/debugging |

## Security & Authorization

### Required Permissions
- **Repository Level**: `issues: write`, `pull-requests: write`, `contents: read`
- **User Level**: MEMBER, COLLABORATOR, or OWNER association required
- **Comment Commands**: Same authorization as issue actions

### Safety Features
- **Repository Isolation**: Dev repo only responds to manual triggers
- **Safe Mode**: Certain actions default to `dry_run=true`
- **Permission Check**: All interactive triggers validate user permissions
- **Audit Trail**: Comprehensive logging of all actions and decisions

## Usage Examples

### Basic Deployment Flow
1. **User creates issue** with description of infrastructure needs
2. **Maintainer labels issue** with `r2d-request` → Triggers deployment
3. **System deploys infrastructure** and reports status in issue comments
4. **Issue is closed** when deployment complete → Triggers cleanup/finalization

### Interactive Deployment
1. **Issue exists** with `r2d-request` label
2. **User comments** `/r2d status` → Gets current deployment status
3. **User comments** `/r2d run` → Triggers fresh deployment
4. **System responds** with deployment results

### Debugging/Re-deployment
1. **Closed issue with problems** 
2. **User reopens issue** → Triggers status check in safe mode
3. **User comments** `/r2d run` → Re-runs deployment
4. **Issue closed again** when resolved

## Future Enhancements

### Planned Features
- **Resource cleanup** on issue unlabeling/closure
- **Cost reporting** in issue comments
- **Deployment history** tracking
- **Advanced commands**: `/r2d rollback`, `/r2d destroy`, `/r2d plan`
- **Multi-environment support**: `/r2d deploy staging`, `/r2d deploy prod`
- **Approval workflows** for production deployments

### Integration Opportunities
- **GitHub Projects** integration for pipeline visualization
- **Slack/Teams** notifications for deployment events
- **Cost monitoring** alerts and reports
- **Security scanning** integration

## Migration Notes

### Breaking Changes
- **None** - All existing workflows continue to work
- **Enhanced** - Previous `issue` deployment type now `issue_labeled`

### New Capabilities
- **Issue lifecycle** fully supported
- **Interactive comments** for real-time control
- **Cleanup/finalization** on issue closure
- **Re-deployment** on issue reopening

This enhancement makes R2D a truly interactive DevOps platform where GitHub issues become powerful deployment control interfaces! 🚀
