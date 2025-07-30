"""
Enums for Alignerr Tools.

This module contains enumeration types used for promotion operations
and organization identifiers to ensure type safety and provide clear valid options.
"""

from enum import Enum


class ProjectStatus(str, Enum):
    """Valid project status values."""

    Calibration = "CALIBRATION"
    Paused = "PAUSED"
    Production = "PRODUCTION"
    Complete = "COMPLETE"


class AlignerrStatus(str, Enum):
    """Valid Alignerr user status values."""

    Calibration = "calibration"
    Production = "production"
    Paused = "paused"


class AlignerrEvaluationStatus(str, Enum):
    """Valid Alignerr evaluation status values."""

    Evaluation = "evaluation"
    Production = "production"


class Organization(str, Enum):
    """Organization identifiers."""

    Alignerr = "cm1pk2jhg0avt07z9h3b9fy9p"


class BillingMode(str, Enum):
    """Billing modes for project rates."""

    ByHour = "BY_HOUR"
    ByTask = "BY_TASK"


class RateType(str, Enum):
    """Rate types for project rates."""

    WorkerPay = "worker_pay"  # isBillRate: false
    CustomerBill = "customer_bill"  # isBillRate: true


class UserRole(str, Enum):
    """User roles for rate setting."""

    Labeler = "cjlvi914y1aa20714372uvzjv"
    Reviewer = "cjlvi919b1aa50714k75euii5"
    Customer = None  # No user role ID for customer billing


class ProjectMode(str, Enum):
    """Project modes for rate setting."""

    Production = "production"
    Calibration = "calibration"
