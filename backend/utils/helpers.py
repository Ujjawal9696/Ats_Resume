"""
utils package - shared utility functions
"""

import re
from typing import Optional


def truncate(text: str, max_len: int = 100) -> str:
    """Truncate text with ellipsis."""
    return text[:max_len] + "..." if len(text) > max_len else text


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from filenames."""
    return re.sub(r'[^\w\-_. ]', '_', filename)


def score_to_color(score: float) -> str:
    """Map a 0–100 score to a hex color."""
    if score >= 70:
        return "#10b981"   # green
    elif score >= 40:
        return "#f59e0b"   # yellow
    return "#ef4444"       # red


def score_to_grade(score: float) -> str:
    """Convert numeric score to grade label."""
    if score >= 85: return "Excellent"
    if score >= 70: return "Good"
    if score >= 55: return "Fair"
    if score >= 40: return "Weak"
    return "Poor"


def format_list_for_prompt(items: list, max_n: int = 10) -> str:
    """Format a Python list as a comma-separated string for LLM prompts."""
    return ", ".join(str(i) for i in items[:max_n])
