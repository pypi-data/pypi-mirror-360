from __future__ import annotations

import os
import fnmatch
from typing import Dict

from .agent import ShellAgent, ShellAgentInput


def _count_files(pattern: str, repo_path: str, shell: ShellAgent) -> int:
    """Count files matching pattern using shell find with Python fallback."""
    try:
        result = shell.run(
            ShellAgentInput(
                command=f"bash -c \"find . -name '{pattern}' -type f | wc -l\"",
                cwd=repo_path,
            )
        )
        if result.exit_code == 0:
            return int(result.output.strip())
        raise RuntimeError(result.error_message or "find failed")
    except Exception:
        count = 0
        for root, _dirs, files in os.walk(repo_path):
            count += len(fnmatch.filter(files, pattern))
        return count


def build_stack_histogram(repo_path: str, shell: ShellAgent) -> Dict[str, float]:
    """Build a normalized stack histogram for Terraform and shell files."""
    tf_count = _count_files("*.tf", repo_path, shell)
    sh_count = _count_files("*.sh", repo_path, shell)

    # Apply weighting
    tf_weight = tf_count * 2
    if os.path.exists(os.path.join(repo_path, "main.tf")):
        tf_weight += 3
    sh_weight = sh_count

    weights = {}
    if tf_weight:
        weights["terraform"] = tf_weight
    if sh_weight:
        weights["shell"] = sh_weight

    total = sum(weights.values())
    if total == 0:
        return {}

    return {k: v / total for k, v in weights.items()}
