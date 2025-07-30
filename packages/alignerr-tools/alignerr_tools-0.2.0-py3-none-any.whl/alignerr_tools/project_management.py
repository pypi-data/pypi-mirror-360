"""
Project management functions for Alignerr tools.

This module provides project-focused functionality for managing project
sharing, promotion, and status within the Labelbox platform.
"""

from typing import Any, List

from .enums import Organization, ProjectStatus
from .models import ValidationMixin


def share_project_with_alignerr(client: Any, project_id: str) -> Any:
    """
    Share a project with the Alignerr organization.

    Args:
        client: The Labelbox client instance
        project_id: The project ID to share

    Returns:
        dict: Response from the GraphQL mutation

    Raises:
        ValueError: If project_id is not a valid 25-character ID
        Exception: If the GraphQL mutation fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> result = share_project_with_alignerr(client, "cm1pk2jhg0avt07z9h3b9fy9p")
    """
    # Validate project ID
    validated_project_id = ValidationMixin.validate_project_id(project_id)

    mutation = """
    mutation AddExternalOrgToProjectAlnrPyApi(
        $projectId: ID!, $organizationId: ID!
    ) {
        shareProjectWithExternalOrganization(data: {
            projectId: $projectId,
            organizationId: $organizationId
        }) {
            id
            sharedWithOrganizations {
                id
                name
            }
        }
    }
    """

    variables = {
        "projectId": validated_project_id,
        "organizationId": Organization.Alignerr,
    }

    result = client.execute(mutation, variables, experimental=True)
    return result


def unshare_project_from_alignerr(client: Any, project_id: str) -> Any:
    """
    Unshare a project from the Alignerr organization.

    Args:
        client: The Labelbox client instance
        project_id: The project ID to unshare

    Returns:
        dict: Response from the GraphQL mutation

    Raises:
        ValueError: If project_id is not a valid 25-character ID
        Exception: If the GraphQL mutation fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> result = unshare_project_from_alignerr(client, "cm1pk2jhg0avt07z9h3b9fy9p")
    """
    # Validate project ID
    validated_project_id = ValidationMixin.validate_project_id(project_id)

    mutation = """
    mutation RemoveExternalOrgFromProjectAlnrPyApi(
        $projectId: ID!, $organizationId: ID!
    ) {
        unshareProjectWithExternalOrganization(data: {
            projectId: $projectId,
            organizationId: $organizationId
        }) {
            id
            sharedWithOrganizations {
                id
                name
            }
        }
    }
    """

    variables = {
        "projectId": validated_project_id,
        "organizationId": Organization.Alignerr,
    }

    result = client.execute(mutation, variables, experimental=True)
    return result


def promote_project_to_production(client: Any, project_id: str) -> Any:
    """
    Promote a project to production status.

    Args:
        client: The Labelbox client instance
        project_id: The project ID to promote

    Returns:
        dict: Response from the GraphQL mutation

    Raises:
        ValueError: If project_id is not a valid 25-character ID
        Exception: If the GraphQL mutation fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> result = promote_project_to_production(client, "cm1pk2jhg0avt07z9h3b9fy9p")
    """
    # Validate project ID
    validated_project_id = ValidationMixin.validate_project_id(project_id)

    mutation = """
    mutation UpdateProjectBoostWorkforceStatusAlnrPyApi(
        $projectId: ID!, $status: ProjectBoostWorkforceStatus!
    ) {
        updateProjectBoostWorkforceStatus(
            data: { projectId: $projectId, status: $status }
        ) {
            success
        }
    }
    """

    variables = {"projectId": validated_project_id, "status": "PRODUCTION"}

    result = client.execute(mutation, variables, experimental=True)
    return result


def promote_project_to_status(
    client: Any, project_id: str, status: ProjectStatus
) -> Any:
    """
    Promote a project to a specific status.

    Args:
        client: The Labelbox client instance
        project_id: The project ID to promote
        status: Target status using ProjectStatus enum

    Returns:
        dict: Response from the GraphQL mutation

    Raises:
        ValueError: If project_id is not a valid 25-character ID
        Exception: If the GraphQL mutation fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> result = promote_project_to_status(
        ...     client, "cm1pk2jhg0avt07z9h3b9fy9p", ProjectStatus.Production
        ... )
    """
    # Validate project ID
    validated_project_id = ValidationMixin.validate_project_id(project_id)

    # Use the enum value directly
    status_value = status.value

    mutation = """
    mutation UpdateProjectBoostWorkforceStatusAlnrPyApi(
        $projectId: ID!, $status: ProjectBoostWorkforceStatus!
    ) {
        updateProjectBoostWorkforceStatus(
            data: { projectId: $projectId, status: $status }
        ) {
            success
        }
    }
    """

    variables = {"projectId": validated_project_id, "status": status_value}

    result = client.execute(mutation, variables, experimental=True)
    return result


def get_alignerr_project_statuses(
    client: Any, user_ids: List[str], project_ids: List[str]
) -> Any:
    """
    Get Alignerr project statuses for specific users and projects.

    Args:
        client: The Labelbox client instance
        user_ids: List of user IDs to check status for
        project_ids: List of project IDs to check status in

    Returns:
        dict: User and project status information

    Raises:
        ValueError: If user_ids or project_ids contain invalid 25-character IDs
        Exception: If the GraphQL query fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> user_ids = ["cjlvi914y1aa20714372uvzjv"]
        >>> project_ids = ["cm1pk2jhg0avt07z9h3b9fy9p"]
        >>> result = get_alignerr_project_statuses(client, user_ids, project_ids)
    """
    # Validate user IDs and project IDs
    validated_user_ids = ValidationMixin.validate_user_ids(user_ids)
    validated_project_ids = [
        ValidationMixin.validate_project_id(pid) for pid in project_ids
    ]

    query = """
    query GetAlignerrProjectStatusesAlnrPyApi(
        $userIds: [String!]!, $projectIds: [String!]!
    ) {
        getAlignerrProjectStatuses(userIds: $userIds, projectIds: $projectIds) {
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
        "userIds": validated_user_ids,
        "projectIds": validated_project_ids,
    }

    result = client.execute(query, variables, experimental=True)
    return result
