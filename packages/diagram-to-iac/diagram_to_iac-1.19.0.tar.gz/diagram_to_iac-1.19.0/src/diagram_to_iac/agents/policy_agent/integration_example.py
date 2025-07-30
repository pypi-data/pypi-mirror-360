"""
PolicyAgent Integration Example

This example demonstrates how the PolicyAgent integrates with the existing
multi-agent workflow to provide security policy enforcement.
"""

# Example usage in supervisor workflow:

def enhanced_terraform_workflow_with_policy_gate(repo_path: str):
    """
    Enhanced terraform workflow with policy gate integration.
    
    This shows how the PolicyAgent integrates with the existing workflow
    to block terraform apply operations on critical security violations.
    """
    
    # Step 1: Standard terraform init and plan (existing workflow)
    terraform_result = terraform_agent.run(TerraformAgentInput(
        query=f"terraform plan in {repo_path}",
        thread_id=thread_id
    ))
    
    if terraform_result.error_message:
        # Handle terraform errors with existing error classification
        error_tags = classify_terraform_error(terraform_result.error_message)
        
        if "policy_block" in error_tags:
            # Route to PolicyAgent for detailed policy analysis
            policy_result = policy_agent.run(PolicyAgentInput(
                query="evaluate security policies and determine if apply should be blocked",
                repo_path=repo_path,
                operation_type="evaluate"
            ))
            
            if policy_result.should_block_apply:
                # Block terraform apply and create GitHub issue
                return create_policy_violation_issue(policy_result)
    
    # Step 2: Pre-apply policy scan (new step)
    policy_result = policy_agent.run(PolicyAgentInput(
        query="scan repository for security violations before terraform apply",
        repo_path=repo_path,
        operation_type="scan"
    ))
    
    if policy_result.should_block_apply:
        # Critical violations found - block apply
        logger.warning(f"Terraform apply blocked due to {policy_result.critical_findings} critical policy violations")
        
        # Create GitHub issue with policy findings
        return create_policy_blocking_issue(policy_result)
    
    # Step 3: Continue with terraform apply (existing workflow)
    if policy_result.policy_status == "PASS":
        apply_result = terraform_agent.run(TerraformAgentInput(
            query=f"terraform apply in {repo_path}",
            thread_id=thread_id
        ))
        
        # Step 4: Post-apply audit artifact (new step)
        policy_agent.run(PolicyAgentInput(
            query="create audit artifact with policy scan results",
            repo_path=repo_path,
            operation_type="report"
        ))
        
        return apply_result
    else:
        return policy_result


def create_policy_violation_issue(policy_result):
    """Create GitHub issue for policy violations."""
    issue_title = f"Security Policy Violations Detected - {policy_result.critical_findings} Critical Issues"
    
    issue_body = f"""
## Security Policy Violations

**Status:** {policy_result.policy_status}
**Critical Findings:** {policy_result.critical_findings}
**Total Findings:** {policy_result.findings_count}

### Action Required
Terraform apply has been blocked due to critical security policy violations.

### Audit Artifact
Policy findings have been saved to: `{policy_result.artifact_path}`

### Next Steps
1. Review the policy findings in the artifact file
2. Fix the security violations
3. Re-run the terraform workflow

### Technical Details
```
{policy_result.result}
```
"""
    
    return git_agent.run(GitAgentInput(
        query=f"open issue '{issue_title}' with policy violation details",
        issue_body=issue_body
    ))


# Example configuration integration:

POLICY_ENFORCEMENT_CONFIG = {
    "policy": {
        "tfsec": {
            "enabled": True,
            "block_on_severity": ["CRITICAL", "HIGH"],
            "artifact_on_severity": ["CRITICAL", "HIGH", "MEDIUM"],
            "timeout_seconds": 120
        },
        "artifacts": {
            "output_dir": "/workspace/.policy_findings",
            "json_filename": "policy_findings_{timestamp}.json"
        }
    },
    "integration": {
        "supervisor": {
            "pre_apply_scan": True,
            "post_apply_audit": True,
            "create_github_issues": True
        }
    }
}


# Example routing in supervisor planner:

def enhanced_supervisor_routing():
    """
    Enhanced supervisor routing with policy gate integration.
    
    This shows how the supervisor routes requests to the PolicyAgent
    based on terraform error classification and workflow state.
    """
    
    routing_keys = {
        "clone": "ROUTE_TO_CLONE",
        "stack_detect": "ROUTE_TO_STACK_DETECT", 
        "branch_create": "ROUTE_TO_BRANCH_CREATE",
        "terraform": "ROUTE_TO_TERRAFORM",
        "policy_scan": "ROUTE_TO_POLICY_SCAN",     # New routing
        "policy_gate": "ROUTE_TO_POLICY_GATE",     # New routing
        "issue": "ROUTE_TO_ISSUE",
        "end": "ROUTE_TO_END"
    }
    
    # Enhanced planner prompt with policy awareness
    planner_prompt = f"""
    You are the supervisor planner for a DevOps-in-a-Box system that manages
    Terraform-based IaC deployment pipelines with security policy enforcement.
    
    Available routing options:
    1. {routing_keys["clone"]} - Clone repository
    2. {routing_keys["stack_detect"]} - Detect technology stack  
    3. {routing_keys["branch_create"]} - Create feature branch
    4. {routing_keys["terraform"]} - Execute terraform operations
    5. {routing_keys["policy_scan"]} - Scan for security policy violations
    6. {routing_keys["policy_gate"]} - Evaluate policy gate for apply blocking
    7. {routing_keys["issue"]} - Create GitHub issue
    8. {routing_keys["end"]} - End workflow
    
    Security Policy Integration:
    - Before terraform apply, always route to policy_scan for security validation
    - If critical violations are found, route to policy_gate for apply blocking
    - Policy violations should create GitHub issues with detailed findings
    
    Route to the appropriate action based on the user input and workflow state.
    """
    
    return planner_prompt


if __name__ == "__main__":
    print("PolicyAgent Integration Example")
    print("===============================")
    print()
    print("This example shows how the PolicyAgent integrates with the existing")
    print("multi-agent workflow to provide security policy enforcement.")
    print()
    print("Key integration points:")
    print("1. Pre-apply security scanning")
    print("2. Policy-based apply blocking")
    print("3. GitHub issue creation for violations")
    print("4. Audit artifact generation")
    print("5. Enhanced supervisor routing")