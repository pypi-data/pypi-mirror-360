#!/usr/bin/env python3
"""
R2D (Repo-to-Deployment) CLI - DevOps-in-a-Box Entry Point

This is the main CLI for the R2D workflow, which orchestrates the complete
Repo-to-Deployment process using the SupervisorAgent.

Usage:
    diagram-to-iac <repository_url>
    r2d-agent <repository_url>

The CLI will:
1. Validate the repository URL
2. Initialize the SupervisorAgent
3. Execute the complete R2D workflow
4. Handle errors gracefully with GitHub Issues
5. Generate observability artifacts

Mission: "One container, many minds—zero manual toil."
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
import os

def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the R2D CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def print_banner() -> None:
    """Print the DevOps-in-a-Box banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║  🤖 DevOps-in-a-Box: R2D CLI                                                 ║
║  "One container, many minds—zero manual toil."                               ║
║                                                                              ║
║  Mission: Self-healing, Terraform-first DevOps automation                    ║
║  Workflow: Clone → Classify → Validate → Deploy → Auto-fix → Summarize       ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def validate_repository_url(repo_url: str) -> bool:
    """Validate that the repository URL is properly formatted."""
    if not repo_url:
        return False
    
    # Basic validation for common Git URL formats
    valid_patterns = [
        'https://github.com/',
        'https://gitlab.com/',
        'git@github.com:',
        'git@gitlab.com:',
        'https://bitbucket.org/',
    ]
    
    return any(repo_url.startswith(pattern) for pattern in valid_patterns)

def validate_environment_variables() -> tuple[bool, list[str]]:
    """
    Validate required environment variables for R2D workflow.
    
    Returns:
        tuple: (is_valid, list of missing/invalid variables)
    """
    errors = []
    
    # Check for required GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        errors.append("GITHUB_TOKEN is required for repository operations and issue creation")
    
    # Check for at least one AI API key
    ai_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
    }
    
    available_keys = [key for key, value in ai_keys.items() if value]
    
    if not available_keys:
        errors.append(
            "At least one AI API key is required (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY)\n"
            "  The SupervisorAgent and other agents require AI capabilities for decision-making"
        )
    
    return len(errors) == 0, errors

def print_environment_status() -> None:
    """Print the status of environment variables."""
    print("🔍 Environment Validation")
    print("═══════════════════════")
    
    # GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        print("✅ GITHUB_TOKEN: configured")
    else:
        print("❌ GITHUB_TOKEN: missing")
    
    # AI API keys
    ai_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'), 
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
    }
    
    available_ai_keys = []
    for key, value in ai_keys.items():
        if value:
            print(f"✅ {key}: configured")
            available_ai_keys.append(key)
        else:
            print(f"⚪ {key}: not configured")
    
    if available_ai_keys:
        print(f"✅ AI capabilities: enabled via {', '.join(available_ai_keys)}")
    else:
        print("❌ AI capabilities: no API keys configured")
    
    # Optional tokens
    tf_token = os.getenv('TFE_TOKEN')
    if tf_token:
        print("✅ TFE_TOKEN: configured (Terraform Cloud operations enabled)")
    else:
        print("⚪ TFE_TOKEN: not configured (Terraform Cloud operations disabled)")
    
    print("")

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser for R2D CLI."""
    parser = argparse.ArgumentParser(
        prog='diagram-to-iac',
        description='DevOps-in-a-Box R2D CLI - Automated Repo-to-Deployment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://github.com/user/repo
  %(prog)s https://github.com/user/infra-repo --dry-run
  %(prog)s git@github.com:user/terraform-config.git --branch-name production
  
Environment Variables:
  GITHUB_TOKEN        - GitHub personal access token (required)
  TFE_TOKEN      - Terraform Cloud API token (recommended)
  
  AI API Keys (at least one required):
  OPENAI_API_KEY      - OpenAI API key (for GPT models)
  ANTHROPIC_API_KEY   - Anthropic API key (for Claude models)  
  GOOGLE_API_KEY      - Google API key (for Gemini models)
  
Mission: "One container, many minds—zero manual toil."
        """
    )
    
    # Positional argument for repository URL
    parser.add_argument(
        'repository_url',
        help='Repository URL to process (GitHub, GitLab, Bitbucket supported)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode - simulate actions without making changes'
    )
    parser.add_argument(
        '--branch-name',
        type=str,
        help='Custom branch name for operations (auto-generated if not provided)'
    )
    parser.add_argument(
        '--thread-id',
        type=str,
        help='Thread ID for conversation tracking and resumption'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Skip interactive prompts'
    )
    parser.add_argument(
        '--config-path',
        type=str,
        help='Path to custom configuration file'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0 - DevOps-in-a-Box R2D CLI',
        help='Show version information and exit'
    )
    
    return parser

def main() -> int:
    """Main entry point for the R2D CLI."""
    try:
        # Parse arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Set up logging
        setup_logging(args.verbose)
        logger = logging.getLogger(__name__)
        
        # Print banner
        print_banner()
        
        # Validate environment variables
        print_environment_status()
        env_valid, env_errors = validate_environment_variables()
        
        if not env_valid:
            print("❌ Environment validation failed:")
            for error in env_errors:
                print(f"   • {error}")
            print("")
            print("ℹ️ Please set the required environment variables and try again")
            print("💡 Tip: You can test API connectivity with: python -c 'from diagram_to_iac.tools.api_utils import test_all_apis; test_all_apis()'")
            return 1
        
        # Validate repository URL
        if not validate_repository_url(args.repository_url):
            print("❌ Error: Invalid repository URL format")
            print("ℹ️ Supported formats: https://github.com/user/repo, git@github.com:user/repo.git")
            return 1
        
        # Validate environment variables
        is_valid, validation_errors = validate_environment_variables()
        if not is_valid:
            print("❌ Error: Invalid environment configuration")
            for error in validation_errors:
                print(f"⚠️ {error}")
            print("ℹ️ Please set the required environment variables and try again")
            return 1
        
        print(f"🎯 Repository: {args.repository_url}")
        print(f"🧪 Dry run: {args.dry_run}")
        print(f"🌿 Branch: {args.branch_name or 'auto-generated'}")
        print("")
        
        # Import SupervisorAgent (delayed import for faster CLI startup)
        try:
            from diagram_to_iac.agents.supervisor_langgraph import (
                SupervisorAgent,
                SupervisorAgentInput,
            )
            from diagram_to_iac.services import (
                get_log_path,
                generate_step_summary,
                reset_log_bus
            )
        except ImportError as e:
            logger.error(f"Failed to import required modules: {e}")
            print("❌ Error: Required modules not available")
            print("ℹ️ Please ensure diagram-to-iac is properly installed")
            return 1
        
        # Initialize SupervisorAgent
        print("🚀 Initializing SupervisorAgent...")
        try:
            agent_kwargs = {}
            if args.config_path:
                agent_kwargs['config_path'] = args.config_path
                
            supervisor = SupervisorAgent(**agent_kwargs)
        except Exception as e:
            logger.error(f"Failed to initialize SupervisorAgent: {e}")
            print(f"❌ Error: Failed to initialize SupervisorAgent: {e}")
            return 1
        
        # Reset log bus for clean run
        reset_log_bus()
        
        # Prepare SupervisorAgent input
        supervisor_input = SupervisorAgentInput(
            repo_url=args.repository_url,
            branch_name=args.branch_name,
            thread_id=args.thread_id,
            dry_run=args.dry_run,
        )
        
        # Execute R2D workflow
        print("🔄 Executing R2D workflow...")
        print("┌─────────────────────────────────────────────────────────────────────────────┐")
        print("│ Workflow: Clone → Detect Stack → Branch Create → Terraform → Issue/PR       │")
        print("│ Agents: Git Agent | Shell Agent | Terraform Agent | Policy Agent             │")
        print("└─────────────────────────────────────────────────────────────────────────────┘")
        print("")
        
        result = supervisor.run(supervisor_input)
        
        # Generate step summary
        try:
            step_summary_path = Path("step-summary.md")
            generate_step_summary(get_log_path(), step_summary_path)
            print(f"📊 Step summary generated: {step_summary_path}")
        except Exception as e:
            logger.warning(f"Failed to generate step summary: {e}")
        
        # Display results
        print("")
        print("🏁 R2D Workflow Results")
        print("═══════════════════════")
        print(f"🎯 Repository: {result.repo_url}")
        print(f"✅ Success: {result.success}")
        print(f"🌿 Branch created: {result.branch_created}")
        print(f"📝 Issues opened: {result.issues_opened}")
        print(f"🏗️ Stack detected: {result.stack_detected}")
        
        if result.terraform_summary:
            print(f"⚡ Terraform summary: {result.terraform_summary}")
        
        if result.message:
            print(f"💬 Message: {result.message}")
        
        if not result.success:
            print("")
            print("⚠️ R2D workflow encountered issues")
            print("🔄 SupervisorAgent handles errors via GitHub Issues automatically")
            print("📋 Check created issues for error details and auto-fix suggestions")
        
        # Return appropriate exit code
        return 0 if result.success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error in R2D CLI: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}")
        print("🐛 Please report this issue to: https://github.com/amartyamandal/diagram-to-iac/issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
