import json
from typing import Any, Set


def _flatten(obj: Any) -> str:
    """Recursively convert a JSON object into a space separated string."""
    if isinstance(obj, dict):
        return " ".join(_flatten(v) for v in obj.values())
    if isinstance(obj, list):
        return " ".join(_flatten(i) for i in obj)
    return str(obj)


def classify_terraform_error(output: str) -> Set[str]:
    """Classify Terraform JSON error output into common categories.

    Parameters
    ----------
    output: str
        Raw JSON error string returned by Terraform.

    Returns
    -------
    Set[str]
        A set of tags describing the error. Possible tags include
        ``syntax_fmt``, ``needs_pat``, ``missing_backend`` and
        ``policy_block``.
    """
    text = output
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        # Try newline separated JSON objects
        parts = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                parts.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        if parts:
            text = " ".join(_flatten(p) for p in parts)
        else:
            text = output
    else:
        text = _flatten(data)

    lowered = text.lower()
    tags: Set[str] = set()

    if any(
        keyword in lowered for keyword in ["syntax", "invalid", "parse", "unexpected"]
    ):
        tags.add("syntax_fmt")

    if "token" in lowered and (
        "unauthorized" in lowered
        or "auth" in lowered
        or "permission" in lowered
        or "credential" in lowered
    ):
        tags.add("needs_pat")

    if "backend" in lowered and any(
        k in lowered for k in ["required", "missing", "no", "not configured"]
    ):
        tags.add("missing_backend")

    if "policy" in lowered and any(
        k in lowered for k in ["fail", "denied", "violation"]
    ):
        tags.add("policy_block")

    return tags
