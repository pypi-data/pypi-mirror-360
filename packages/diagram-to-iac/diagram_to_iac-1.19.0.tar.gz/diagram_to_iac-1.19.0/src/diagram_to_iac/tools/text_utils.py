"""
Text utilities for cleaning and enhancing error messages and issue titles.

This module provides utilities for:
- Cleaning ANSI color codes from terminal output
- Generating organic, context-aware issue titles
- Text processing for better user experience
"""

import re
from typing import Dict, List, Optional
from datetime import datetime


def clean_ansi_codes(text: str) -> str:
    """
    Remove ANSI color codes and escape sequences from text.
    
    Args:
        text: Text that may contain ANSI escape sequences
        
    Returns:
        Clean text without ANSI codes
    """
    if not text or not isinstance(text, str):
        return text
    
    # Pattern to match ANSI escape sequences
    ansi_pattern = re.compile(r'\x1b\[[0-9;]*[mK]')
    
    # Also clean up the escaped unicode sequences that appear in logs
    unicode_pattern = re.compile(r'�\[\d+m')
    
    # Remove ANSI codes
    clean_text = ansi_pattern.sub('', text)
    
    # Remove escaped unicode sequences
    clean_text = unicode_pattern.sub('', clean_text)
    
    return clean_text


def generate_organic_issue_title(error_context: Dict[str, any]) -> str:
    """
    Generate an organic, context-aware issue title based on error details.
    
    This function analyzes the error context and creates a meaningful title
    that feels like it was written by a thoughtful developer who understands
    the problem.
    
    Args:
        error_context: Dictionary containing error details with keys:
            - error_type: Type of error (terraform_init, auth_failed, etc.)
            - stack_detected: Dict of detected infrastructure files
            - error_message: The actual error message
            - repo_url: Repository URL
            - branch_name: Branch name (optional)
            
    Returns:
        Human-friendly, organic issue title
    """
    error_type = error_context.get('error_type', 'unknown')
    stack_detected = error_context.get('stack_detected', {})
    error_message = error_context.get('error_message', '')
    repo_url = error_context.get('repo_url', '')
    branch_name = error_context.get('branch_name', '')
    
    # Clean the error message first
    clean_error = clean_ansi_codes(error_message)
    
    # Extract repository name for context
    repo_name = "repository"
    if repo_url:
        repo_match = re.search(r'/([^/]+)\.git$', repo_url)
        if repo_match:
            repo_name = repo_match.group(1)
    
    # Analyze stack for context
    stack_context = _analyze_stack_context(stack_detected)
    
    # Generate title based on error type and context
    if 'terraform init' in clean_error.lower() or error_type == 'terraform_init':
        if 'token' in clean_error.lower() or 'login' in clean_error.lower():
            return f"Terraform Cloud authentication required for {repo_name} deployment"
        elif 'backend' in clean_error.lower():
            return f"Terraform backend configuration issue in {repo_name}"
        else:
            return f"Terraform initialization failed in {repo_name} {stack_context}"
    
    elif 'terraform plan' in clean_error.lower() or error_type == 'terraform_plan':
        return f"Terraform plan validation errors in {repo_name} {stack_context}"
    
    elif 'terraform apply' in clean_error.lower() or error_type == 'terraform_apply':
        return f"Terraform deployment failed for {repo_name} {stack_context}"
    
    elif 'auth' in clean_error.lower() or error_type == 'auth_failed':
        if 'github' in clean_error.lower():
            return f"GitHub access permissions needed for {repo_name}"
        else:
            return f"Authentication issue preventing {repo_name} deployment"
    
    elif 'api key' in clean_error.lower() or error_type == 'api_key_error':
        if 'openai' in clean_error.lower():
            return f"OpenAI API configuration required for {repo_name} automation"
        elif 'github' in clean_error.lower():
            return f"GitHub API token configuration needed for {repo_name}"
        else:
            return f"API authentication configuration required for {repo_name}"
    
    elif 'llm error' in clean_error.lower() or error_type == 'llm_error':
        return f"AI service connectivity issue affecting {repo_name} automation"
    
    elif 'network' in clean_error.lower() or 'timeout' in clean_error.lower() or error_type == 'network_error':
        return f"Network connectivity issue during {repo_name} deployment"
    
    elif 'timeout' in clean_error.lower() or error_type == 'timeout_error':
        return f"Service timeout issue affecting {repo_name} automation"
    
    elif 'permission' in clean_error.lower() or 'forbidden' in clean_error.lower() or error_type == 'permission_error':
        return f"Access permissions needed for {repo_name} deployment"
    
    elif 'planner error' in clean_error.lower() or error_type == 'planner_error':
        return f"Workflow planning issue in {repo_name} automation"
    
    elif 'workflow error' in clean_error.lower() or error_type == 'workflow_error':
        return f"System workflow failure affecting {repo_name}"
    
    elif stack_context and any(tf_count > 0 for tf_count in stack_detected.values() if isinstance(tf_count, int)):
        return f"Infrastructure deployment issue in {repo_name} {stack_context}"
    
    else:
        # Generic but still organic fallback
        action = "deployment" if stack_detected else "workflow"
        return f"Automated {action} issue detected in {repo_name}"


def _analyze_stack_context(stack_detected: Dict[str, any]) -> str:
    """
    Analyze detected stack files to provide meaningful context.
    
    Args:
        stack_detected: Dictionary of detected file types and counts
        
    Returns:
        Human-friendly description of the stack
    """
    if not stack_detected:
        return ""
    
    contexts = []
    
    # Check for Terraform
    tf_count = stack_detected.get('*.tf', 0)
    if tf_count > 0:
        if tf_count == 1:
            contexts.append("(single Terraform configuration)")
        elif tf_count <= 5:
            contexts.append(f"({tf_count} Terraform files)")
        else:
            contexts.append(f"(complex Terraform setup with {tf_count} files)")
    
    # Check for other infrastructure files
    yml_count = stack_detected.get('*.yml', 0) + stack_detected.get('*.yaml', 0)
    if yml_count > 0:
        contexts.append(f"with {yml_count} YAML configs")
    
    ps1_count = stack_detected.get('*.ps1', 0)
    if ps1_count > 0:
        contexts.append(f"and {ps1_count} PowerShell scripts")
    
    sh_count = stack_detected.get('*.sh', 0)
    if sh_count > 0:
        contexts.append(f"and {sh_count} shell scripts")
    
    if contexts:
        return " " + " ".join(contexts)
    
    return ""


def enhance_error_message_for_issue(error_message: str, context: Optional[Dict[str, any]] = None) -> str:
    """
    Clean and enhance error message for GitHub issue body.
    
    Args:
        error_message: Raw error message that may contain ANSI codes
        context: Optional context for better error formatting
        
    Returns:
        Clean, well-formatted error message suitable for GitHub issues
    """
    # Clean ANSI codes first
    clean_msg = clean_ansi_codes(error_message)
    
    # Split into lines and clean up
    lines = clean_msg.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove empty lines and excessive whitespace
        line = line.strip()
        if line:
            # Format error blocks with proper markdown
            if line.startswith('Error:') or line.startswith('╷') or line.startswith('│'):
                cleaned_lines.append(line)
            elif line.startswith('╵'):
                cleaned_lines.append(line)
                cleaned_lines.append('')  # Add space after error blocks
            else:
                cleaned_lines.append(line)
    
    # Join back and format as code block for better readability
    enhanced_msg = '\n'.join(cleaned_lines)
    
    # Wrap in code block if it looks like terminal output
    if any(indicator in enhanced_msg for indicator in ['$', '╷', '│', 'Error:', 'Initializing']):
        enhanced_msg = f"```\n{enhanced_msg}\n```"
    
    return enhanced_msg


def create_issue_metadata_section(context: Dict[str, any]) -> str:
    """
    Create a metadata section for GitHub issues with deployment context.
    
    Args:
        context: Issue context including repo, branch, stack info
        
    Returns:
        Formatted metadata section for issue body
    """
    repo_url = context.get('repo_url', 'Unknown')
    branch_name = context.get('branch_name', 'Unknown')
    stack_detected = context.get('stack_detected', {})
    
    metadata_lines = [
        "## Deployment Context",
        "",
        f"**Repository:** {repo_url}",
        f"**Branch:** {branch_name}",
        f"**Detected Stack:** {_format_stack_detection(stack_detected)}",
        f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "---",
        "",
        "## Error Details",
        ""
    ]
    
    return '\n'.join(metadata_lines)


def _format_stack_detection(stack_detected: Dict[str, any]) -> str:
    """
    Format stack detection results for display.
    
    Args:
        stack_detected: Dictionary of detected file types and counts
        
    Returns:
        Human-friendly stack description
    """
    if not stack_detected:
        return "No infrastructure files detected"
    
    items = []
    for file_type, count in stack_detected.items():
        if isinstance(count, int) and count > 0:
            if count == 1:
                items.append(f"1 {file_type} file")
            else:
                items.append(f"{count} {file_type} files")
    
    if not items:
        return "No infrastructure files detected"
    
    return ", ".join(items)
