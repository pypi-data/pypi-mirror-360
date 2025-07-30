#!/usr/bin/env python
"""
CLI entrypoint for TerraformAgent - Phase 4 Implementation

This module provides a command-line interface for manual execution of the TerraformAgent,
following the established patterns in the diagram-to-iac codebase.

Usage:
    python -m diagram_to_iac.actions.terraform_agent_entry --query "terraform init"
    python -m diagram_to_iac.actions.terraform_agent_entry --repo-path /workspace --operation init
    # Or via console script (after update_deps.py adds it to pyproject.toml):
    terraform-agent --query "terraform apply configuration"

Features:
- Argument parsing for terraform operations
- JSON output for programmatic consumption
- Proper error handling and logging
- Integration with existing TerraformAgent implementation
- Support for init, plan, apply operations
- GitHub issue creation for critical errors
"""

import argparse
import json
import sys
import logging
from typing import Optional

from diagram_to_iac.agents.terraform_langgraph.agent import TerraformAgent, TerraformAgentInput


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI entrypoint."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser following established patterns."""
    parser = argparse.ArgumentParser(
        prog='terraform-agent',
        description='TerraformAgent CLI - DevOps automation for terraform operations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query "terraform init"
  %(prog)s --query "terraform plan configuration"
  %(prog)s --query "terraform apply infrastructure"
  %(prog)s --repo-path /workspace --operation init --verbose
  %(prog)s --query "open issue for terraform authentication failure"
        """
    )
    
    # Primary input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--query',
        type=str,
        help='Terraform DevOps query (init, plan, apply, or error reporting)'
    )
    input_group.add_argument(
        '--repo-path',
        type=str,
        help='Repository path for terraform operations (requires --operation)'
    )
    
    # Operation type (required when using --repo-path)
    parser.add_argument(
        '--operation',
        type=str,
        choices=['init', 'plan', 'apply'],
        help='Terraform operation type (required with --repo-path)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--thread-id',
        type=str,
        help='Optional thread ID for conversation history'
    )
    parser.add_argument(
        '--context',
        type=str,
        help='Optional context information for error reporting'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--config-path',
        type=str,
        help='Path to YAML configuration file'
    )
    parser.add_argument(
        '--memory-type',
        type=str,
        choices=['persistent', 'memory', 'langgraph'],
        default='persistent',
        help='Type of memory to use (default: persistent)'
    )
    
    return parser


def format_output(result: object, indent: int = 2) -> str:
    """Format output as JSON with proper indentation."""
    try:
        if hasattr(result, 'model_dump'):
            # Pydantic model
            return json.dumps(result.model_dump(), indent=indent)
        else:
            # Regular object
            return json.dumps(result, indent=indent, default=str)
    except Exception as e:
        # Fallback to string representation
        logging.warning(f"Failed to serialize output as JSON: {e}")
        return str(result)


def construct_query_from_repo_path(repo_path: str, operation: str) -> str:
    """Construct a terraform query from repository path and operation."""
    operation_templates = {
        'init': f"terraform init in {repo_path}",
        'plan': f"terraform plan in {repo_path}",
        'apply': f"terraform apply in {repo_path}"
    }
    return operation_templates.get(operation, f"terraform {operation} in {repo_path}")


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate argument combinations following terraform agent requirements."""
    if args.repo_path and not args.operation:
        raise ValueError("--operation is required when using --repo-path")


def main() -> int:
    """Main entrypoint function following established CLI patterns."""
    try:
        # Parse arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Validate argument combinations
        validate_arguments(args)
        
        # Setup logging
        setup_logging(args.verbose)
        logger = logging.getLogger(__name__)
        
        # Construct query from arguments
        if args.repo_path:
            query = construct_query_from_repo_path(args.repo_path, args.operation)
            logger.info(f"Constructed query from repo path: {query}")
        else:
            query = args.query
            logger.info(f"Using provided query: {query}")
        
        # Initialize agent with optional configuration
        agent_kwargs = {}
        if args.config_path:
            agent_kwargs['config_path'] = args.config_path
        if args.memory_type:
            agent_kwargs['memory_type'] = args.memory_type
            
        logger.info(f"Initializing TerraformAgent with {agent_kwargs}")
        agent = TerraformAgent(**agent_kwargs)
        
        # Prepare input
        agent_input = TerraformAgentInput(
            query=query,
            thread_id=args.thread_id,
            context=args.context
        )
        
        logger.info(f"Running agent with input: {agent_input.query}")
        
        # Execute agent
        result = agent.run(agent_input)
        
        # Output results
        print(format_output(result))
        
        # Return appropriate exit code
        if result.error_message:
            logger.error(f"Agent execution failed: {result.error_message}")
            return 1
        else:
            logger.info("Agent execution completed successfully")
            return 0
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        logging.exception("Unexpected error in main()")
        return 1


if __name__ == "__main__":
    sys.exit(main())
