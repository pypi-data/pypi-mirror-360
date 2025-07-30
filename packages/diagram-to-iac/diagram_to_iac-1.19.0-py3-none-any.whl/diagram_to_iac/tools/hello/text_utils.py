import re
from typing import List

def extract_numbers_from_text(text: str) -> List[int]:
    """
    Extract all integer numbers from a given text string, handling various formats.

    This function finds sequences of digits and also extracts numbers from patterns
    like "number operator number" (e.g., "4*5", "7 + 3"). It returns a list of unique
    integers found, preserving the order of their first appearance in the text.

    Args:
        text: The input string from which to extract numbers.

    Returns:
        A list of unique integers found in the text, in order of appearance.
        Returns an empty list if no numbers are found.

    Supports:
    - Space-separated numbers: "4 + 5", "add 7 and 3"
    - Adjacent numbers with operators: "4*5", "6+2"
    - Basic extraction of digit sequences.
    """
    numbers = []

    # First, find all digit sequences using regex, avoiding phone number confusion
    digit_matches = re.findall(r'\b\d+\b', text)
    numbers.extend([int(match) for match in digit_matches])

    # Handle cases where numbers are adjacent to operators like "4*5" or "7+3"
    # Use specific operators (not dash) to avoid phone number confusion
    operator_adjacent = re.findall(r'(\d+)\s*[+*/×÷%]\s*(\d+)', text)
    for match in operator_adjacent:
        numbers.extend([int(match[0]), int(match[1])])

    # Handle negative numbers in explicit mathematical contexts
    # Look for patterns like "What is -10 + 5?" but avoid phone numbers
    math_negative = re.findall(r'(?:is|add|subtract|plus|minus|\+|\*|/)\s+(-\d+)', text, re.IGNORECASE)
    for match in math_negative:
        numbers.append(int(match))
    
    # Also catch negative numbers at the start of mathematical expressions
    start_negative = re.findall(r'(?:^|\s)(-\d+)\s*[+*/×÷%]', text)
    for match in start_negative:
        numbers.append(int(match))

    # Remove duplicates while preserving order of first appearance
    seen = set()
    unique_numbers = []
    for num_val in numbers: # Renamed 'num' to 'num_val' to avoid conflict if 'num' was a global
        if num_val not in seen:
            unique_numbers.append(num_val)
            seen.add(num_val)

    return unique_numbers

def extract_numbers_from_text_with_duplicates(text: str) -> List[int]:
    """
    Extract all integer numbers from a given text string, preserving duplicates.

    This function is similar to extract_numbers_from_text but preserves duplicate
    numbers, which is useful for operations like "10 * 10" where both numbers
    are needed even if they're the same.

    Args:
        text: The input string from which to extract numbers.

    Returns:
        A list of integers found in the text, in order of appearance, including duplicates.
        Returns an empty list if no numbers are found.

    Examples:
        >>> extract_numbers_from_text_with_duplicates("Calculate 10 * 10")
        [10, 10]
        >>> extract_numbers_from_text_with_duplicates("What is 5 + 7?")
        [5, 7]
    """
    # Use a comprehensive regex to find all numbers (positive and negative) in one pass
    # This regex matches:
    # 1. Negative numbers in math contexts: "What is -10 + 5?"
    # 2. Regular positive numbers: "10", "5", etc.
    # 3. Avoids phone number dashes by being specific about negative contexts
    
    results = []
    
    # Combined pattern that captures both positive and negative numbers
    # Negative numbers: preceded by math keywords or operators, followed by math operators
    # Positive numbers: standalone digit sequences
    pattern = r'(?:(?:is|add|subtract|plus|minus|\+|\*|/|^|\s)[-\s]*(-\d+)(?=\s*[+\-*/×÷%\s]|$))|(?:\b(\d+)\b)'
    
    for match in re.finditer(pattern, text, re.IGNORECASE):
        if match.group(1):  # Negative number
            results.append(int(match.group(1)))
        elif match.group(2):  # Positive number
            results.append(int(match.group(2)))
    
    return results
