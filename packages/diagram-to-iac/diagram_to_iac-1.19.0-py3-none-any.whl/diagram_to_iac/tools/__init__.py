# This file makes the 'tools' module a package.

# Note: Agent-specific tools organization:
# - cal_utils, text_utils -> tools/hello/
# - git_tools -> tools/git/ (moved from agents/git_langgraph/tools/)
# - shell_tools -> agents/shell_langgraph/tools/

# You can expose shared tools here as needed
# For example:
# from .llm_utils import router (if router.py is in llm_utils subdirectory)
# from .cv_utils import some_vision_function
