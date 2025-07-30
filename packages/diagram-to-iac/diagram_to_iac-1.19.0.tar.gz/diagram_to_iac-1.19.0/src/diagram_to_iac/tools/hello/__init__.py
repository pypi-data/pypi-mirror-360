"""
Hello LangGraph Agent Tools Package

This package contains tools specific to the HelloAgent:
- cal_utils: Arithmetic operations (addition, multiplication)
- text_utils: Text processing utilities

These tools have been moved from agents/hello_langgraph/tools/ to provide
better organization and reusability across the codebase.
"""

# Import text utilities (no external dependencies)
from .text_utils import extract_numbers_from_text, extract_numbers_from_text_with_duplicates

# Import calculation utilities (requires langchain_core)
try:
    from .cal_utils import add_two, multiply_two
    _cal_utils_available = True
except ImportError:
    _cal_utils_available = False
    add_two = None
    multiply_two = None

__all__ = [
    "extract_numbers_from_text", 
    "extract_numbers_from_text_with_duplicates"
]

if _cal_utils_available:
    __all__.extend(["add_two", "multiply_two"])
