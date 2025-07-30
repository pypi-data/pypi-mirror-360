import os
import time
import logging

from . import __name__ as pkg_name
from diagram_to_iac.agents.git_langgraph import GitAgentInput


def request_and_wait_for_pat(repo_url: str, git_agent, poll_interval: int = 30, timeout: int = 600) -> bool:
    """Request TF_TOKEN_APP_TERRAFORM_IO from the user and wait until provided.

    Parameters
    ----------
    repo_url: str
        Repository URL used for context in the GitHub issue comment.
    git_agent: GitAgent
        Agent used to post a comment requesting the token.
    poll_interval: int, optional
        How often to check for the environment variable, in seconds.
    timeout: int, optional
        Maximum time to wait before giving up, in seconds.

    Returns
    -------
    bool
        ``True`` if the token was detected before timeout, ``False`` otherwise.
    """
    logger = logging.getLogger(f"{pkg_name}.pat_loop")
    message = (
        "Please add the Terraform Cloud token `TF_TOKEN_APP_TERRAFORM_IO` as an "
        "environment variable and reply 'retry init' once done."
    )

    try:
        git_agent.run(
            GitAgentInput(
                query=f"open issue {message} for repository {repo_url}",
            )
        )
    except Exception as e:  # pragma: no cover - log but continue
        logger.error(f"Failed to post PAT request comment: {e}")

    env_name = "TF_TOKEN_APP_TERRAFORM_IO"
    end = time.time() + timeout
    while time.time() < end:
        if os.environ.get(env_name):
            return True
        time.sleep(poll_interval)
    return False
