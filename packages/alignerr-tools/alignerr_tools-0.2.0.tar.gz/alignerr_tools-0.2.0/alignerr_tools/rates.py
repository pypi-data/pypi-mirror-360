"""
Rate management functions for Alignerr tools.

This module provides functions to query, set, and manage project rates
within the Labelbox platform, including support for both worker pay
rates and customer billing rates.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import labelbox as lb

from .enums import BillingMode, ProjectMode, RateType, UserRole
from .models import ValidationMixin


def _format_datetime(dt: datetime) -> str:
    """
    Format datetime to ISO string with Z suffix for GraphQL.

    Args:
        dt: datetime object (should be in UTC)

    Returns:
        str: ISO formatted string with Z suffix (e.g., "2024-01-15T10:30:00Z")
    """
    # If datetime is naive, assume UTC. If aware, convert to UTC.
    if dt.tzinfo is None:
        # Naive datetime - assume UTC
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        # Aware datetime - convert to UTC and format
        utc_dt = dt.utctimetuple()
        return datetime(*utc_dt[:6]).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_project_rates(client: lb.Client, project_id: str) -> Any:
    """
    Retrieve project rates for both production and evaluation projects.

    Args:
        client: The Labelbox client instance
        project_id: The project ID to query rates for

    Returns:
        dict: Project rates data including production and evaluation project rates

    Raises:
        ValueError: If project_id is not a valid 25-character ID
        Exception: If the GraphQL query fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> rates = get_project_rates(client, "cm1pk2jhg0avt07z9h3b9fy9p")
        >>> print(rates)
    """
    # Validate project ID
    validated_project_id = ValidationMixin.validate_project_id(project_id)

    query = """query GetProjectRatesV2AlnrPyApi($projectId: ID!) {
      project(where: { id: $projectId }) {
        id
        name
        labelingFrontend { name }
        evaluationProject {
          id
          name
          ratesV2 {
            id
            userRole { id name }
            isBillRate
            billingMode
            rate
            effectiveSince
            effectiveUntil
          }
        }
        ratesV2 {
          id
          userRole { id name }
          isBillRate
          billingMode
          rate
          effectiveSince
          effectiveUntil
        }
      }
    }"""

    params = {"projectId": validated_project_id}

    return client.execute(query, params=params, experimental=True)


def _set_project_rate_internal(
    client: lb.Client,
    project_id: str,
    rate: float,
    rate_type: RateType,
    effective_from: Optional[datetime] = None,
    user_role_id: Optional[str] = None,
    billing_mode: BillingMode = BillingMode.ByHour,
    effective_until: Optional[datetime] = None,
) -> Any:
    """
    Internal function to set project rates using the SetProjectRateV2 mutation.
    This is used by the public set_project_rates function.
    """
    # Validate project ID
    validated_project_id = ValidationMixin.validate_project_id(project_id)

    # Validate rate
    if not isinstance(rate, (int, float)) or rate <= 0 or rate > 1000:
        raise ValueError("Rate cannot exceed $1000")

    # Validate rate type and user_role_id requirements
    is_bill_rate = rate_type == RateType.CustomerBill

    if not is_bill_rate and not user_role_id:
        raise ValueError("user_role_id is required for worker pay rates")

    if is_bill_rate and user_role_id:
        raise ValueError("user_role_id must be null for customer bill rates")

    # Validate user_role_id if provided
    validated_user_role_id = None
    if user_role_id:
        validated_user_role_id = ValidationMixin.validate_user_id(
            user_role_id
        )  # Reusing user validation for role IDs

    mutation = """mutation SetProjectRateV2AlnrPyApi($input: SetProjectRateV2Input!) {
      setProjectRateV2(input: $input) {
        success
      }
    }"""

    input_data = {
        "projectId": validated_project_id,
        "isBillRate": is_bill_rate,
        "billingMode": billing_mode.value,
        "rate": float(rate),
    }

    if effective_from:
        input_data["effectiveSince"] = _format_datetime(effective_from)

    if validated_user_role_id:
        input_data["userRoleId"] = validated_user_role_id

    if effective_until:
        input_data["effectiveUntil"] = _format_datetime(effective_until)

    params = {"input": input_data}

    return client.execute(mutation, params=params, experimental=True)


def set_project_alignerr_rate(
    client: lb.Client,
    project_id: str,
    user_id: str,
    effective_from: datetime,
    multiplier_rate: Optional[float] = None,
    absolute_rate: Optional[float] = None,
    effective_until: Optional[datetime] = None,
) -> Any:
    """
    Set an individual Alignerr rate for a specific user.

    Args:
        client: Labelbox client instance
        project_id: ID of the project (25-character string)
        user_id: ID of the user (25-character string)
        effective_from: Start date (UTC datetime, required)
        multiplier_rate: Multiplier applied to base rate (e.g., 1.25 = 125%)
        absolute_rate: Fixed rate that overrides calculations (e.g., 25.0 = $25/hour)
        effective_until: End date (UTC datetime, optional)

    Returns:
        dict: Response from the GraphQL mutation

    Raises:
        ValueError: If project_id or user_id are not valid 25-character IDs
        ValueError: If both multiplier_rate and absolute_rate are provided
        ValueError: If neither multiplier_rate nor absolute_rate are provided
        ValueError: If rates are invalid
        Exception: If the mutation fails

    Example:
        >>> from datetime import datetime
        >>> start_date = datetime(2024, 1, 15, 0, 0, 0)  # UTC
        >>>
        >>> # Set multiplier rate (125% of base rate)
        >>> set_project_alignerr_rate(
        ...     client,
        ...     "cm1pk2jhg0avt07z9h3b9fy9p",
        ...     "cjlvi914y1aa20714372uvzjv",
        ...     effective_from=start_date,
        ...     multiplier_rate=1.25
        ... )
        >>>
        >>> # Set absolute rate ($30/hour)
        >>> set_project_alignerr_rate(
        ...     client,
        ...     "cm1pk2jhg0avt07z9h3b9fy9p",
        ...     "cjlvi914y1aa20714372uvzjv",
        ...     effective_from=start_date,
        ...     absolute_rate=30.0
        ... )
    """
    # Validate IDs
    validated_project_id = ValidationMixin.validate_project_id(project_id)
    validated_user_id = ValidationMixin.validate_user_id(user_id)

    # Validate rate parameters - must have exactly one
    if multiplier_rate is not None and absolute_rate is not None:
        raise ValueError("Cannot specify both multiplier_rate and absolute_rate.")

    if multiplier_rate is None and absolute_rate is None:
        raise ValueError("Must specify either multiplier_rate or absolute_rate.")

    # Validate rate values
    if multiplier_rate is not None:
        if not isinstance(multiplier_rate, (int, float)) or multiplier_rate <= 0:
            raise ValueError("multiplier_rate must be a positive number")

    if absolute_rate is not None:
        if not isinstance(absolute_rate, (int, float)) or absolute_rate <= 0:
            raise ValueError("absolute_rate must be a positive number")

    mutation = """mutation SetProjectAlignerrRateAlnrPyApi(
        $input: SetProjectAlignerrRateInput!
    ) {
      setProjectAlignerrRate(input: $input) {
        success
      }
    }"""

    input_data: Dict[str, Any] = {
        "projectId": validated_project_id,
        "userId": validated_user_id,
        "effectiveSince": _format_datetime(effective_from),
    }

    # Add the appropriate rate type
    if multiplier_rate is not None:
        input_data["multiplierRate"] = float(multiplier_rate)
    elif absolute_rate is not None:
        input_data["absoluteRate"] = float(absolute_rate)

    if effective_until:
        input_data["effectiveUntil"] = _format_datetime(effective_until)

    params = {"input": input_data}

    return client.execute(mutation, params=params, experimental=True)


def bulk_set_project_alignerr_rates(
    client: lb.Client,
    project_id: str,
    user_rates: List[Dict[str, Any]],
    effective_from: datetime,
    effective_until: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Set Alignerr rates for multiple users in bulk.

    Args:
        client: Labelbox client instance
        project_id: ID of the project (25-character string)
        user_rates: List of dicts with 'userId' and rate keys
        effective_from: Start date (UTC datetime, required)
        effective_until: End date (UTC datetime, optional)

    Returns:
        list: List of responses from individual rate settings

    Raises:
        ValueError: If project_id or user IDs are not valid 25-character IDs
        ValueError: If user_rates is empty or has invalid structure
        ValueError: If rate entries have both or neither rate types
        Exception: If any mutation fails

    Example:
        >>> from datetime import datetime
        >>> start_date = datetime(2024, 1, 15, 0, 0, 0)  # UTC
        >>> user_rates = [
        ...     {"userId": "cjlvi914y1aa20714372uvzjv", "absoluteRate": 25.0},
        ...     {"userId": "cjlvi919b1aa50714k75euii5", "multiplierRate": 1.25}
        ... ]
        >>> bulk_set_project_alignerr_rates(
        ...     client,
        ...     "cm1pk2jhg0avt07z9h3b9fy9p",
        ...     user_rates,
        ...     effective_from=start_date
        ... )
    """
    # Validate project ID first
    validated_project_id = ValidationMixin.validate_project_id(project_id)

    if not user_rates:
        raise ValueError("user_rates cannot be empty")

    results = []
    for user_rate in user_rates:
        if not isinstance(user_rate, dict):
            raise ValueError("Each user_rate must be a dictionary")

        if "userId" not in user_rate:
            raise ValueError("Each user_rate must contain 'userId' key")

        # Check for rate type keys
        has_multiplier = "multiplierRate" in user_rate
        has_absolute = "absoluteRate" in user_rate

        if not has_multiplier and not has_absolute:
            raise ValueError(
                "Each user_rate must contain 'multiplierRate' or 'absoluteRate' key"
            )

        if has_multiplier and has_absolute:
            raise ValueError("Each user_rate cannot contain both rate keys")

        user_id = user_rate["userId"]

        # Validate user ID
        validated_user_id = ValidationMixin.validate_user_id(user_id)

        # Extract rate values
        multiplier_rate = user_rate.get("multiplierRate")
        absolute_rate = user_rate.get("absoluteRate")

        # Validate rate limits
        if absolute_rate is not None and absolute_rate > 1000:
            raise ValueError(f"Absolute rate for user {user_id} cannot exceed $1000")

        # Set the rate for this user
        result = set_project_alignerr_rate(
            client=client,
            project_id=validated_project_id,
            user_id=validated_user_id,
            effective_from=effective_from,
            multiplier_rate=multiplier_rate,
            absolute_rate=absolute_rate,
            effective_until=effective_until,
        )
        results.append(result)

    return results


def set_country_multiplier(client: lb.Client, project_id: str, enabled: bool) -> Any:
    """
    Set the "Set relative geo rates" country multiplier for a project.

    Args:
        client: The Labelbox client instance
        project_id: The project ID to set country multiplier for
        enabled: True to enable country multiplier, False to disable

    Returns:
        dict: Response from the GraphQL mutation

    Raises:
        ValueError: If project_id is not a valid 25-character ID
        Exception: If the GraphQL mutation fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> # Enable country multiplier
        >>> result = set_country_multiplier(client, "cm1pk2jhg0avt07z9h3b9fy9p", True)
        >>> # Disable country multiplier
        >>> result = set_country_multiplier(client, "cm1pk2jhg0avt07z9h3b9fy9p", False)
    """
    # Validate project ID
    validated_project_id = ValidationMixin.validate_project_id(project_id)

    mutation = """mutation UpdateProjectBoostWorkforceAlnrPyApi(
        $input: UpdateProjectBoostWorkforceInput!
    ) {
      updateProjectBoostWorkforce(input: $input) {
        success
      }
    }"""

    input_data = {
        "projectId": validated_project_id,
        "disabledCountryRateMultipliers": not enabled,  # Invert for disabled
    }

    params = {"input": input_data}

    return client.execute(mutation, params=params, experimental=True)


def set_project_rates(
    client: lb.Client,
    project_id: str,
    rate: float,
    user_role: UserRole,
    mode: ProjectMode,
    effective_from: Optional[datetime] = None,
    billing_mode: BillingMode = BillingMode.ByHour,
    effective_until: Optional[datetime] = None,
) -> Any:
    """
    Set project rates using UI-friendly parameters.

    Args:
        client: The Labelbox client instance
        project_id: The main project ID
        rate: The rate amount (maximum $1000)
        user_role: User role (UserRole.Labeler, UserRole.Reviewer, or UserRole.Customer)
        mode: Project mode (ProjectMode.Production or ProjectMode.Calibration)
        effective_from: Optional start date for the rate (UTC datetime)
        billing_mode: Billing mode (defaults to BY_HOUR)
        effective_until: Optional end date for the rate (UTC datetime)

    Returns:
        dict: Response from the GraphQL mutation

    Raises:
        ValueError: If project_id is not a valid 25-character ID
        ValueError: If rate exceeds $1000 limit
        ValueError: If calibration project doesn't exist when mode is Calibration
        Exception: If the GraphQL mutation fails

    Example:
        >>> from datetime import datetime
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> start_date = datetime(2024, 1, 15, 10, 30, 0)  # UTC
        >>>
        >>> # Set labeler production rate
        >>> result = set_project_rates(
        ...     client,
        ...     "cm1pk2jhg0avt07z9h3b9fy9p",
        ...     rate=25.0,
        ...     user_role=UserRole.Labeler,
        ...     mode=ProjectMode.Production,
        ...     effective_from=start_date
        ... )
        >>>
        >>> # Set customer calibration rate
        >>> result = set_project_rates(
        ...     client,
        ...     "cm1pk2jhg0avt07z9h3b9fy9p",
        ...     rate=75.0,
        ...     user_role=UserRole.Customer,
        ...     mode=ProjectMode.Calibration,
        ...     effective_from=start_date
        ... )
    """
    # Validate project ID
    validated_project_id = ValidationMixin.validate_project_id(project_id)

    # Validate rate
    if not isinstance(rate, (int, float)) or rate <= 0 or rate > 1000:
        raise ValueError("Rate cannot exceed $1000")

    # Determine target project ID based on mode
    target_project_id = validated_project_id
    if mode == ProjectMode.Calibration:
        # Get calibration project using the dedicated function
        evaluation_project = get_evaluation_project(client, validated_project_id)
        if not evaluation_project:
            raise ValueError("Calibration project does not exist for this project")
        target_project_id = evaluation_project.uid

    # Determine rate type and user role ID
    is_bill_rate = user_role == UserRole.Customer
    rate_type = RateType.CustomerBill if is_bill_rate else RateType.WorkerPay
    user_role_id = user_role.value if user_role != UserRole.Customer else None

    # Use the internal set_project_rate function
    return _set_project_rate_internal(
        client=client,
        project_id=target_project_id,
        rate=rate,
        rate_type=rate_type,
        effective_from=effective_from,
        user_role_id=user_role_id,
        billing_mode=billing_mode,
        effective_until=effective_until,
    )


def get_evaluation_project(client: lb.Client, project_id: str) -> Any:
    """
    Get the evaluation project for an Alignerr project, if it exists.

    Args:
        client: The Labelbox client instance
        project_id: The main project ID to get evaluation project for

    Returns:
        Project: Labelbox Project object for evaluation project, or None if none exists

    Raises:
        ValueError: If project_id is not a valid 25-character ID
        Exception: If the GraphQL query fails or if getting the project fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>> eval_project = get_evaluation_project(client, "cm1pk2jhg0avt07z9h3b9fy9p")
        >>> if eval_project:
        ...     print(f"Evaluation project ID: {eval_project.uid}")
        ...     print(f"Evaluation project name: {eval_project.name}")
        ... else:
        ...     print("No evaluation project exists for this project")
    """
    # Validate project ID
    validated_project_id = ValidationMixin.validate_project_id(project_id)

    query = """query getAlignerrProjectAlnrPyApi($projectId: ID!) {
      project(where: { id: $projectId }) {
        evaluationProject {
          id
        }
      }
    }"""

    variables = {"projectId": validated_project_id}
    result = client.execute(query, variables, experimental=True)

    # Check if evaluation project exists
    eval_project_data = result.get("project", {}).get("evaluationProject")
    if not eval_project_data:
        return None

    # Get the full Project object using the Labelbox SDK
    eval_project_id = eval_project_data["id"]
    return client.get_project(eval_project_id)


def evaluation_export(
    client: lb.Client,
    project_id: str,
    params: Optional[Dict[str, Any]] = None,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Export data from the evaluation project of an Alignerr project.

    This function gets the evaluation project for the given project ID and exports
    its data using the standard Labelbox export functionality with the same
    parameters and filters as project.export().

    Args:
        client: The Labelbox client instance
        project_id: The main project ID to get evaluation project for
        params: Export parameters (same as project.export() params)
        filters: Export filters (same as project.export() filters)

    Returns:
        List[Dict[str, Any]]: JSON array of exported data rows

    Raises:
        ValueError: If project_id is not a valid 25-character ID
        ValueError: If no evaluation project exists for the given project
        Exception: If the export fails

    Example:
        >>> client = labelbox.Client(api_key="your_api_key")
        >>>
        >>> # Export with basic parameters
        >>> export_params = {
        ...     "attachments": True,
        ...     "metadata_fields": True,
        ...     "data_row_details": True,
        ...     "project_details": True,
        ...     "label_details": True,
        ... }
        >>>
        >>> # Optional filters
        >>> export_filters = {
        ...     "last_activity_at": ["2000-01-01 00:00:00", "2050-01-01 00:00:00"],
        ...     "workflow_status": "InReview",
        ... }
        >>>
        >>> data = evaluation_export(
        ...     client,
        ...     "cm1pk2jhg0avt07z9h3b9fy9p",
        ...     params=export_params,
        ...     filters=export_filters
        ... )
        >>>
        >>> print(f"Exported {len(data)} data rows from evaluation project")
        >>> for row in data:
        ...     print(f"Data row ID: {row['data_row']['id']}")
    """
    # Get the evaluation project
    evaluation_project = get_evaluation_project(client, project_id)

    if not evaluation_project:
        raise ValueError(f"No evaluation project exists for project ID: {project_id}")

    # Use default parameters if none provided
    if params is None:
        params = {}

    if filters is None:
        filters = {}

    # Export data from the evaluation project
    export_task = evaluation_project.export(params=params, filters=filters)
    export_task.wait_till_done()

    # Check if export was successful
    if export_task.has_errors():
        error_details = []
        for error in export_task.get_buffered_stream(stream_type=lb.StreamType.ERRORS):
            error_details.append(str(error))
        raise Exception(f"Export failed with errors: {'; '.join(error_details)}")

    # Collect all exported data into a list
    export_json = [data_row.json for data_row in export_task.get_buffered_stream()]

    return export_json
