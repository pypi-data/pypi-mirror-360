"""CLI entrypoint for SupervisorAgent."""

import argparse
import json
import sys
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from diagram_to_iac.agents.supervisor_langgraph import (
    SupervisorAgent,
    SupervisorAgentInput,
)
from diagram_to_iac.agents.supervisor_langgraph.github_listener import (
    GitHubListener,
    RetryContext,
    CommentEvent,
    create_github_listener
)
from diagram_to_iac.core.registry import RunRegistry, RunStatus
from diagram_to_iac.services import get_log_path, generate_step_summary, reset_log_bus


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="supervisor-agent",
        description="SupervisorAgent CLI - R2D (Repo-to-Deployment) automation",
    )
    parser.add_argument("--repo-url", help="Repository URL to operate on")
    parser.add_argument("--branch-name", help="Branch name (deprecated - supervisor skips branch creation)")
    parser.add_argument("--thread-id", help="Optional thread id")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--no-interactive", action="store_true", help="Skip interactive prompts")
    parser.add_argument("--dry-run", action="store_true", help="Print issue text instead of creating it")
    
    # Comment listener options
    parser.add_argument("--listen-comments", action="store_true", 
                       help="Enable GitHub comment listening for retry commands")
    parser.add_argument("--issue-id", type=int, help="Issue ID to monitor for comments")
    parser.add_argument("--poll-interval", type=int, default=30, 
                       help="Comment polling interval in seconds (default: 30)")
    parser.add_argument("--max-polls", type=int, 
                       help="Maximum number of polls (default: infinite)")
    
    return parser


def prompt_for_repo_url() -> str:
    """Prompt the user for a repository URL."""
    try:
        return input("Repository URL: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n⚠️  Repository URL required")
        sys.exit(1)


def format_output(result: object) -> str:
    try:
        if hasattr(result, "model_dump"):
            return json.dumps(result.model_dump(), indent=2)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logging.warning(f"Failed to serialize output: {e}")
        return str(result)


def handle_resume_workflow(context: RetryContext) -> bool:
    """
    Handle resuming an existing workflow.
    
    Args:
        context: RetryContext with resumption information
        
    Returns:
        True if resumption was successful, False otherwise
    """
    logger = logging.getLogger("supervisor_entry")
    
    if not context.existing_run:
        logger.error("No existing run to resume")
        return False
    
    try:
        logger.info(f"Resuming run {context.existing_run.run_key}")
        
        # Initialize registry and SupervisorAgent
        registry = RunRegistry()
        agent = SupervisorAgent(registry=registry)
        
        # Update run status to clear wait reason if PAT is now available
        pat_available = os.getenv('TFE_TOKEN') is not None
        if pat_available and context.existing_run.status == RunStatus.WAITING_FOR_PAT:
            logger.info("PAT token now available, clearing wait reason")
            registry.update(context.existing_run.run_key, {
                'status': RunStatus.IN_PROGRESS,
                'wait_reason': None
            })
        
        # Resume the workflow from where it left off
        reset_log_bus()
        result = agent.resume_workflow(
            context.existing_run.run_key,
            context.target_sha or context.existing_run.commit_sha
        )
        
        logger.info(f"Resume workflow result: {result.success}")
        return result.success
        
    except Exception as e:
        logger.error(f"Error resuming workflow: {e}")
        return False


def handle_new_workflow(context: RetryContext) -> bool:
    """
    Handle starting a new workflow for manual retry requests.
    
    Args:
        context: RetryContext with new workflow information
        
    Returns:
        True if new workflow was started successfully, False otherwise
    """
    logger = logging.getLogger("supervisor_entry")
    
    try:
        logger.info(f"Starting new workflow for SHA {context.target_sha[:7] if context.target_sha else 'unknown'}")
        
        # Initialize SupervisorAgent
        agent = SupervisorAgent()
        
        # Start new workflow
        reset_log_bus()
        result = agent.run(SupervisorAgentInput(
            repo_url=context.comment_event.repo_url,
            branch_name="main",  # Placeholder - supervisor handles this
            thread_id=f"retry-{context.comment_event.comment_id}",
            commit_sha=context.target_sha
        ))
        
        logger.info(f"New workflow result: {result.success}")
        return result.success
        
    except Exception as e:
        logger.error(f"Error starting new workflow: {e}")
        return False


def start_comment_listener(repo_url: str, issue_id: int, poll_interval: int = 30, 
                          max_polls: Optional[int] = None) -> None:
    """
    Start the GitHub comment listener.
    
    Args:
        repo_url: Repository URL to monitor
        issue_id: Issue ID to monitor for comments
        poll_interval: Seconds between polls
        max_polls: Maximum number of polls
    """
    logger = logging.getLogger("supervisor_entry")
    
    try:
        # Create GitHub listener with callbacks
        github_token = os.getenv('GITHUB_TOKEN')
        registry = RunRegistry()
        listener = create_github_listener(github_token=github_token, registry=registry)
        
        # Set up callbacks
        listener.set_callbacks(
            resume_callback=handle_resume_workflow,
            new_run_callback=handle_new_workflow
        )
        
        logger.info(f"Starting comment listener for issue #{issue_id} in {repo_url}")
        logger.info(f"Poll interval: {poll_interval}s, Max polls: {max_polls or 'infinite'}")
        
        # Start polling
        listener.poll_issue_comments(
            issue_id=issue_id,
            repo_url=repo_url,
            poll_interval=poll_interval,
            max_polls=max_polls
        )
        
    except Exception as e:
        logger.error(f"Error in comment listener: {e}")
        raise


def main() -> int:
    parser = create_argument_parser()
    args = parser.parse_args()

    setup_logging(args.verbose)

    # Handle comment listening mode
    if args.listen_comments:
        if not args.repo_url:
            parser.error("--repo-url is required when using --listen-comments")
        if not args.issue_id:
            parser.error("--issue-id is required when using --listen-comments")
        
        try:
            start_comment_listener(
                repo_url=args.repo_url,
                issue_id=args.issue_id,
                poll_interval=args.poll_interval,
                max_polls=args.max_polls
            )
            return 0
        except KeyboardInterrupt:
            print("\n⚠️  Comment listener stopped by user")
            return 0
        except Exception as e:
            logging.error(f"Comment listener failed: {e}")
            return 1

    # Handle normal workflow mode
    repo_url = args.repo_url
    if not repo_url and not args.no_interactive:
        repo_url = prompt_for_repo_url()
    elif not repo_url:
        parser.error("--repo-url is required when --no-interactive is used")

    # Branch name is no longer used since supervisor skips branch creation
    # All errors are handled via GitHub issues instead
    branch_name = args.branch_name or "main"  # Placeholder for compatibility

    agent = SupervisorAgent()

    while True:
        reset_log_bus()
        result = agent.run(
            SupervisorAgentInput(
                repo_url=repo_url,
                branch_name=branch_name,
                thread_id=args.thread_id,
                dry_run=args.dry_run,
                no_interactive=args.no_interactive,
            )
        )

        print(format_output(result))

        try:
            generate_step_summary(get_log_path(), Path("step-summary.md"))
        except Exception as e:  # noqa: BLE001
            logging.warning(f"Step summary generation failed: {e}")

        if result.success or args.no_interactive:
            break

        if args.dry_run:
            try:
                choice = input(
                    "Select an option: [1] Retry workflow, [2] Create GitHub issue, [3] Quit: "
                ).strip()
            except (KeyboardInterrupt, EOFError):
                choice = ""

            if choice == "1":
                repo_url = prompt_for_repo_url()
                continue
            elif choice == "2":
                reset_log_bus()
                # Directly create the issue using the last run's result to avoid
                # triggering the full workflow again (which would clone twice).
                error_state = {
                    "repo_url": repo_url,
                    "branch_name": branch_name,
                    "stack_detected": result.stack_detected,
                    "error_message": result.message,
                    "thread_id": args.thread_id,
                    "dry_run": False,
                    "no_interactive": True,
                }
                issue_result = agent._issue_create_node(error_state)
                from diagram_to_iac.agents.supervisor_langgraph.agent import SupervisorAgentOutput

                result = SupervisorAgentOutput(
                    repo_url=repo_url,
                    branch_created=False,
                    branch_name=branch_name,
                    stack_detected=result.stack_detected,
                    terraform_summary=None,
                    unsupported=False,
                    issues_opened=issue_result.get("issues_opened", 0),
                    success=issue_result.get("error_message") is None,
                    message=(
                        f"Issue creation failed: {issue_result.get('error_message')}"
                        if issue_result.get("error_message")
                        else f"GitHub issue created for error: {result.message}"
                    ),
                )

                print(format_output(result))

                try:
                    generate_step_summary(get_log_path(), Path("step-summary.md"))
                except Exception as e:  # noqa: BLE001
                    logging.warning(f"Step summary generation failed: {e}")

                break
            else:
                break
        else:
            try:
                choice = input("Retry workflow? [y/N]: ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                choice = ""

            if choice != "y":
                break

            repo_url = prompt_for_repo_url()
            # No longer prompt for branch name since supervisor skips branch creation

    # Treat workflows that created GitHub issues as successful CLI executions,
    # except when secrets were missing.
    if result.success:
        return 0
    if result.issues_opened > 0 and not getattr(result, "missing_secret", False):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())