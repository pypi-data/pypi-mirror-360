"""Utility functions for TicketPlease."""

import os
from pathlib import Path

import pyperclip


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard."""
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def expand_file_path(file_path: str) -> str:
    """Expand file path to absolute path, handling ~ and relative paths."""
    if not file_path or not file_path.strip():
        return ""

    # Expand user home directory (~) and convert to absolute path
    expanded = os.path.expanduser(file_path.strip())
    absolute_path = os.path.abspath(expanded)
    return absolute_path


def read_file_content(file_path: str) -> list[str]:
    """Read content from a file and return as list of lines."""
    try:
        # Expand the path to handle ~ and relative paths
        expanded_path = expand_file_path(file_path)
        path = Path(expanded_path)

        if not path.exists():
            return []

        with open(path, encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return [line.strip() for line in content.split("\n") if line.strip()]
    except Exception:
        return []


def validate_file_path(file_path: str) -> bool:
    """Validate if a file path exists and is readable."""
    try:
        # Expand the path to handle ~ and relative paths
        expanded_path = expand_file_path(file_path)
        path = Path(expanded_path)
        return path.exists() and path.is_file()
    except Exception:
        return False


def format_acceptance_criteria(criteria: list[str]) -> str:
    """Format acceptance criteria for display."""
    if not criteria:
        return "No criteria provided"

    formatted = []
    for i, criterion in enumerate(criteria, 1):
        formatted.append(f"{i}. {criterion}")

    return "\n".join(formatted)


def format_definition_of_done(dod_items: list[str]) -> str:
    """Format definition of done items for display."""
    if not dod_items:
        return "No items provided"

    formatted = []
    for i, item in enumerate(dod_items, 1):
        formatted.append(f"{i}. {item}")

    return "\n".join(formatted)
