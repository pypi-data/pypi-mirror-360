#!/usr/bin/env python
"""
CLI entrypoint for GitAgent - Phase 5 Implementation

This module provides a command-line interface for manual execution of the GitAgent,
following the established patterns in the diagram-to-iac codebase.

Usage:
    python -m diagram_to_iac.actions.git_entry --repo-url https://github.com/user/repo
    # Or via console script (after update_deps.py adds it to pyproject.toml):
    git-agent --repo-url https://github.com/user/repo

Features:
- Argument parsing for git operations
- JSON output for programmatic consumption
- Proper error handling and logging
- Integration with existing GitAgent implementation
"""

import argparse
import json
import sys
import logging
from typing import Optional

from diagram_to_iac.agents.git_langgraph.agent import GitAgent, GitAgentInput


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
        prog='git-agent',
        description='GitAgent CLI - DevOps automation for git operations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --repo-url https://github.com/user/repo
  %(prog)s --query "clone https://github.com/user/repo"
  %(prog)s --query "open issue in repo: bug report" --verbose
        """
    )
    
    # Primary input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--repo-url',
        type=str,
        help='Git repository URL to clone'
    )
    input_group.add_argument(
        '--query',
        type=str,
        help='DevOps query (git clone, GitHub issue, shell command)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--thread-id',
        type=str,
        help='Optional thread ID for conversation history'
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


def construct_query_from_repo_url(repo_url: str) -> str:
    """Construct a git clone query from a repository URL."""
    return f"clone repository {repo_url}"


def main() -> int:
    """Main entrypoint function following established CLI patterns."""
    try:
        # Parse arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Setup logging
        setup_logging(args.verbose)
        logger = logging.getLogger(__name__)
        
        # Construct query from arguments
        if args.repo_url:
            query = construct_query_from_repo_url(args.repo_url)
            logger.info(f"Constructed query from repo URL: {query}")
        else:
            query = args.query
            logger.info(f"Using provided query: {query}")
        
        # Initialize agent with optional configuration
        agent_kwargs = {}
        if args.config_path:
            agent_kwargs['config_path'] = args.config_path
        if args.memory_type:
            agent_kwargs['memory_type'] = args.memory_type
            
        logger.info(f"Initializing GitAgent with {agent_kwargs}")
        agent = GitAgent(**agent_kwargs)
        
        # Prepare input
        agent_input = GitAgentInput(
            query=query,
            thread_id=args.thread_id
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
