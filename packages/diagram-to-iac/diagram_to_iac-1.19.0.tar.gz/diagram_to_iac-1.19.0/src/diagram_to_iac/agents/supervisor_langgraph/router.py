from typing import Dict

STACK_SUPPORT_THRESHOLD = 0.7


def route_on_stack(histogram: Dict[str, float]) -> bool:
    """Return True if any stack falls below the configured support threshold."""
    return any(value < STACK_SUPPORT_THRESHOLD for value in histogram.values())

