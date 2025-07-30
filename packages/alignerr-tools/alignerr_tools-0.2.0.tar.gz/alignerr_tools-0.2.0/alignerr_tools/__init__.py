"""
Alignerr Tools - Labelbox project automation utilities.

This package provides Alignerr-specific utilities for working with Labelbox projects,
including user management, project management, and rates management.

For general user and group management, use the native Labelbox Python SDK.

Usage:
    from alignerr_tools import user_management, project_management, rates

    user_management.add_alignerr(client, user_ids)
    user_management.promote_user_to_production(client, project_id, user_ids)
    project_management.share_project_with_alignerr(client, project_id)
    project_management.promote_project_to_production(client, project_id)
    rates.get_project_rates(client, project_id)
"""

__version__ = "0.1.0"
__author__ = "Labelbox Alignerr Team"
__email__ = "support@labelbox.com"

from .enums import (
    AlignerrEvaluationStatus,
    AlignerrStatus,
    BillingMode,
    Organization,
    ProjectMode,
    ProjectStatus,
    RateType,
    UserRole,
)
from .models import ValidationMixin
from .project_management import (
    get_alignerr_project_statuses,
    promote_project_to_production,
    promote_project_to_status,
    share_project_with_alignerr,
    unshare_project_from_alignerr,
)
from .rates import (
    bulk_set_project_alignerr_rates,
    evaluation_export,
    get_evaluation_project,
    get_project_rates,
    set_country_multiplier,
    set_project_alignerr_rate,
    set_project_rates,
)

# Import modules for organized access
from .user_management import (
    add_alignerr,
    promote_all_users_to_production,
    promote_user_to_production,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "promote_all_users_to_production",
    "promote_user_to_production",
    "promote_project_to_production",
    "promote_project_to_status",
    "get_alignerr_project_statuses",
    "share_project_with_alignerr",
    "unshare_project_from_alignerr",
    "get_project_rates",
    "get_evaluation_project",
    "evaluation_export",
    "set_project_rates",
    "set_project_alignerr_rate",
    "bulk_set_project_alignerr_rates",
    "set_country_multiplier",
    "add_alignerr",
    "ValidationMixin",
    "ProjectStatus",
    "AlignerrStatus",
    "AlignerrEvaluationStatus",
    "Organization",
    "BillingMode",
    "RateType",
    "UserRole",
    "ProjectMode",
]
