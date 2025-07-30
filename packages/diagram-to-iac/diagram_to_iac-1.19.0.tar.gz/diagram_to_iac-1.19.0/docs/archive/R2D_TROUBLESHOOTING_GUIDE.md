# R2D Workflow Troubleshooting Guide

## Issue: SupervisorAgent Routes Directly to ROUTE_TO_END

### Symptoms
```
2025-06-26 22:39:36 - SupervisorAgent - INFO - Supervisor planner decision: ROUTE_TO_END
```

The SupervisorAgent immediately decides there's nothing to do and ends the workflow without performing any repository analysis, code generation, or deployment.

### Root Causes

#### 1. **Empty or Incompatible Repository**
- **Problem**: Target repository has no infrastructure files or unsupported stack
- **Solution**: Ensure target repo has some code/infrastructure files to analyze
- **Test**: Try with a repo that has some `.tf` files, `package.json`, `requirements.txt`, etc.

#### 2. **Deployment Type Recognition**
- **Problem**: SupervisorAgent doesn't recognize new deployment types (`issue_labeled`, `issue_closed`, etc.)
- **Current**: Agent may be expecting legacy deployment types like `issue`, `manual`, etc.
- **Solution**: Update SupervisorAgent's planner prompt to handle new deployment types

#### 3. **Missing LLM Instructions**
- **Problem**: SupervisorAgent's system prompt doesn't include clear instructions for different deployment types
- **Solution**: Enhance the agent's understanding of what to do with each deployment type

#### 4. **Configuration Issues**
- **Problem**: Missing or incorrect shell/tool configurations
- **Current**: Warnings about shell configuration, but uses defaults
- **Impact**: May affect tool execution but shouldn't cause immediate exit

### Immediate Fixes Applied

#### Enhanced Deployment Context
```yaml
DEPLOYMENT_CONTEXT: |
  {
    "deployment_type": "${{ needs.route.outputs.deployment_type }}",
    "trigger_event": "${{ github.event_name }}",
    "trigger_action": "${{ github.event.action || 'N/A' }}",
    "repository": "${{ github.repository }}",
    "target_repo": "${{ needs.route.outputs.target_repo }}",
    "branch": "${{ needs.route.outputs.target_branch }}",
    "thread_id": "${{ needs.route.outputs.thread_id }}",
    "dry_run": "${{ needs.route.outputs.dry_run_mode }}",
    "workflow_run_id": "${{ github.run_id }}",
    "instructions": "Analyze repository, detect infrastructure stack, create/update Terraform configuration, and deploy via Terraform Cloud"
  }
```

#### Additional Environment Variables
```yaml
R2D_OPERATION_MODE: "full_deployment"
R2D_DEPLOYMENT_TYPE: ${{ needs.route.outputs.deployment_type }}
R2D_DRY_RUN: ${{ needs.route.outputs.dry_run_mode }}
```

#### Enhanced Debug Output
- Added routing decision debugging
- Added deployment context JSON output
- Added trigger action tracking

### Testing Strategy

#### 1. **Test with Simple Repository**
- Create test repo with basic `main.tf` file
- Label issue with `r2d-request` 
- Monitor if SupervisorAgent recognizes infrastructure

#### 2. **Test with Different Deployment Types**
- Manual workflow dispatch: `deployment_type: "manual"`
- Issue labeled: `deployment_type: "issue_labeled"`
- PR merge: `deployment_type: "pr_merge"`

#### 3. **Debug Container Execution**
- Check if container receives correct environment variables
- Verify deployment context JSON is properly formed
- Monitor SupervisorAgent's initial decision making

### Expected Workflow Steps

The SupervisorAgent should follow this sequence:

1. **ROUTE_TO_GIT_AGENT**: Clone and analyze repository
2. **ROUTE_TO_TERRAFORM_AGENT**: Create/update infrastructure code
3. **ROUTE_TO_DEPLOYMENT**: Deploy via Terraform Cloud
4. **ROUTE_TO_COMPLETION**: Finalize and report results

If it skips directly to `ROUTE_TO_END`, something is wrong with the initial analysis.

### Next Steps

#### Short-term (Workflow Fixes)
- ✅ Enhanced deployment context with clear instructions
- ✅ Added operation mode environment variables  
- ✅ Improved debugging output
- 🔄 Test with simple repository containing infrastructure files

#### Medium-term (Agent Improvements)
- 🔲 Update SupervisorAgent's planner prompt to handle new deployment types
- 🔲 Add specific handling for `issue_labeled`, `issue_closed`, etc.
- 🔲 Improve repository analysis logic to detect more stack types

#### Long-term (Platform Enhancements)
- 🔲 Add agent configuration validation
- 🔲 Create test suite for different repository types
- 🔲 Implement agent health checks and diagnostics

### Verification Commands

#### Check Container Environment
```bash
# In container, verify environment variables are set
env | grep -E "(R2D_|DEPLOYMENT_|TFE_|GITHUB_)"
```

#### Test Repository Analysis
```bash
# Verify git clone and repository detection
git ls-remote $REPO_URL
```

#### Monitor Agent Decisions
```bash
# Check agent logs for decision points
grep -E "(ROUTE_TO_|planner decision)" /workspace/logs/*
```

This troubleshooting should help identify whether the issue is with:
- Repository content
- Agent configuration  
- LLM decision making
- Environment setup
