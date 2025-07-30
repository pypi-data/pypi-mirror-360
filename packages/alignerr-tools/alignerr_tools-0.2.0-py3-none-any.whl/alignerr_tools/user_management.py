"""
User management functions for Alignerr tools.

This module provides user-focused functionality for managing alignerrs
and user promotions within the Labelbox platform.

For general user and group management, use the native Labelbox SDK:
- User management: client.get_organization().users(), user.update_org_role(), etc.
- Group management: UserGroup.create(), user_group.members.add(), etc.
- Role management: client.get_roles(), user.upsert_project_role(), etc.
"""

from typing import Any, List

import labelbox as lb

from .models import ValidationMixin


def add_alignerr(client: lb.Client, user_ids: List[str]) -> Any:
    """
    Add users to the pre-approved alignerr list.

    This function allows users to be considered for alignerr roles without
    going through the full evaluation process.

    Args:
        client: The Labelbox client instance
        user_ids: List of user ID strings to add as pre-approved alignerrs

    Returns:
        dict: Response containing the added alignerrs with their details

    Raises:
        ValueError: If user_ids is empty or contains invalid user IDs
        ValueError: If any user ID is not a valid 25-character ID
        Exception: If the GraphQL mutation fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> user_ids = ["cm1pk2jhg0avt07z9h3b9user1", "cm1pk2jhg0avt07z9h3b9user2"]
        >>> result = add_alignerr(client, user_ids)
        >>> alignerrs = result['addPreApprovedAlignerrs']['alignerrs']
        >>> print(f"Added {len(alignerrs)} alignerrs")
        >>> for alignerr in result['addPreApprovedAlignerrs']['alignerrs']:
        ...     print(f"  - User ID: {alignerr['userId']} (ID: {alignerr['id']})")
    """
    # Validate input
    if not user_ids:
        raise ValueError("user_ids cannot be empty")

    if not isinstance(user_ids, list):
        raise ValueError("user_ids must be a list")

    # Validate each user ID
    validated_user_ids = []
    for user_id in user_ids:
        validated_user_id = ValidationMixin.validate_user_id(user_id)
        validated_user_ids.append(validated_user_id)

    mutation = """mutation AddPreApprovedAlignerrsAlnrPyApi($userIds: [String!]!) {
      addPreApprovedAlignerrs(userIds: $userIds) {
        alignerrs {
          id
          userId
          createdAt
          updatedAt
          deletedAt
        }
      }
    }"""

    variables = {"userIds": validated_user_ids}

    return client.execute(mutation, variables, experimental=True)


def promote_user_to_production(
    client: Any, project_id: str, user_ids: List[str]
) -> Any:
    """
    Promote specific users to production status for a project.

    Args:
        client: The Labelbox client instance
        project_id: The project ID to promote users for
        user_ids: List of user IDs to promote

    Returns:
        dict: Response from the GraphQL mutation

    Raises:
        ValueError: If project_id or user_ids are not valid 25-character IDs
        Exception: If the GraphQL mutation fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> user_ids = ["cjlvi914y1aa20714372uvzjv", "cjlvi919b1aa50714k75euii5"]
        >>> result = promote_user_to_production(
        ...     client, "cm1pk2jhg0avt07z9h3b9fy9p", user_ids
        ... )
    """
    # Validate project ID and user IDs
    validated_project_id = ValidationMixin.validate_project_id(project_id)
    validated_user_ids = ValidationMixin.validate_user_ids(user_ids)

    mutation = """
    mutation SetAlignerrProjectStatusAlnrPyApi(
        $input: CreateAlignerrProjectStatusInput!
    ) {
        createAlignerrProjectStatus(input: $input) {
            id
            userId
            projectId
            status
            createdAt
            updatedAt
        }
    }
    """

    variables = {
        "input": {
            "userIds": validated_user_ids,
            "projectId": validated_project_id,
            "status": "production",
        }
    }

    result = client.execute(mutation, variables, experimental=True)
    return result


def promote_all_users_to_production(client: Any, project_id: str) -> Any:
    """
    Promote all users in a project to production status.

    Args:
        client: The Labelbox client instance
        project_id: The project ID to promote users for

    Returns:
        dict: Response from the GraphQL mutation

    Raises:
        ValueError: If project_id is not a valid 25-character ID
        Exception: If the GraphQL mutation fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> result = promote_all_users_to_production(
        ...     client, "cm1pk2jhg0avt07z9h3b9fy9p"
        ... )
    """
    # Validate project ID
    validated_project_id = ValidationMixin.validate_project_id(project_id)

    mutation = """
    mutation SetAllAlignerrsToProductionAlnrPyApi($projectId: ID!) {
        setAllAlignerrsToProduction(projectId: $projectId)
    }
    """

    variables = {"projectId": validated_project_id}
    result = client.execute(mutation, variables, experimental=True)
    return result
