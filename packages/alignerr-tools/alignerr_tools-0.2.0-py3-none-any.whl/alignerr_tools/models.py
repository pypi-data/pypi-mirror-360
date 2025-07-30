"""
Simple validation functions for Labelbox IDs and data structures.

This module provides basic validation for Labelbox IDs and other data structures
used throughout the alignerr-tools package.
"""

from typing import List


def validate_labelbox_id(id_str: str, id_type: str = "ID") -> str:
    """
    Validate a Labelbox ID is exactly 25 alphanumeric characters.

    Args:
        id_str: The ID string to validate
        id_type: Description of the ID type for error messages

    Returns:
        str: The validated ID string

    Raises:
        ValueError: If the ID is invalid
    """
    if not isinstance(id_str, str):
        raise ValueError(f"{id_type} must be a string")
    if len(id_str) != 25:
        raise ValueError(f"{id_type} must be exactly 25 characters long")
    if not id_str.isalnum():
        raise ValueError(f"{id_type} must contain only alphanumeric characters")
    return id_str


class ValidationMixin:
    """Helper class providing validation methods."""

    @staticmethod
    def validate_project_id(project_id: str) -> str:
        """Validate and return a project ID."""
        return validate_labelbox_id(project_id, "Project ID")

    @staticmethod
    def validate_user_id(user_id: str) -> str:
        """Validate and return a user ID."""
        return validate_labelbox_id(user_id, "User ID")

    @staticmethod
    def validate_user_ids(user_ids: List[str]) -> List[str]:
        """Validate and return a list of user IDs."""
        return [ValidationMixin.validate_user_id(uid) for uid in user_ids]
