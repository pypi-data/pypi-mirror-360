# Alignerr Tools

Labelbox project automation utilities for Alignerr user management, project management, and rates management.

## Features

### User Management
- `add_alignerr(client, user_ids)` - Add users to pre-approved alignerr list
- `promote_user_to_production(client, project_id, user_ids)` - Promote specific users to production
- `promote_all_users_to_production(client, project_id)` - Promote all users in a project to production

### Project Management
- `share_project_with_alignerr(client, project_id)` - Share a project with the Alignerr organization
- `unshare_project_from_alignerr(client, project_id)` - Unshare a project from the Alignerr organization
- `promote_project_to_production(client, project_id)` - Promote entire project to production
- `promote_project_to_status(client, project_id, status)` - Promote project to specific status
- `get_alignerr_project_statuses(client, user_ids, project_ids)` - Get status of users across projects

### General User & Group Management
For general user and group management, use the native [Labelbox Python SDK](https://github.com/Labelbox/labelbox-python):
- **User management**: `client.get_organization().users()`, `user.update_org_role()`, `user.upsert_project_role()`
- **Group management**: `UserGroup.create()`, `user_group.members.add()`, `user_group.update()`
- **Role management**: `client.get_roles()`, `user.remove_from_project()`

### Rates Management
- `get_project_rates(client, project_id)` - Get project rates including pay rates and bill rates
- `get_evaluation_project(client, project_id)` - Get the evaluation project for an Alignerr project, if it exists
- `set_project_rates(client, project_id, rate, user_role, mode, ...)` - Set rates using UI-friendly parameters

- `set_project_alignerr_rate(client, project_id, user_id, rate, effective_from, ...)` - Set individual Alignerr rates
- `bulk_set_project_alignerr_rates(client, project_id, user_rates, effective_from, ...)` - Set bulk Alignerr rates
- `set_country_multiplier(client, project_id, enabled)` - Set "Set relative geo rates" country multiplier for a project



## Installation

### From wheel (recommended for Google Colab)
```bash
pip install alignerr-tools
```

### From source (Private Repository)
**Note: This repository is private. You need proper GitHub access and authentication.**

```bash
# Using SSH (recommended for private repos)
git clone git@github.com:Labelbox/alignerr-tools.git
cd alignerr-tools
poetry install
```

**OR using HTTPS with personal access token:**
```bash
# Replace YOUR_TOKEN with your GitHub personal access token
git clone https://YOUR_TOKEN@github.com/Labelbox/alignerr-tools.git
cd alignerr-tools
poetry install
```

**OR if you have already cloned the repository:**
```bash
cd alignerr-tools
poetry install
```

## Usage

```python
import labelbox as lb
from datetime import datetime
from alignerr_tools import (
    # User management functions
    add_alignerr,
    promote_user_to_production,
    promote_all_users_to_production,
    # Project management functions
    share_project_with_alignerr,
    unshare_project_from_alignerr,
    promote_project_to_production,
    promote_project_to_status,
    get_alignerr_project_statuses,
    # Rates functions
    get_project_rates,
    get_evaluation_project,
    evaluation_export,
    set_project_rates,
    set_project_alignerr_rate,
    bulk_set_project_alignerr_rates,
    set_country_multiplier,
    # Enums
    ProjectStatus,
    AlignerrStatus,
    AlignerrEvaluationStatus,
    Organization,
    BillingMode,
    RateType,
    UserRole,
    ProjectMode
)

client = lb.Client(api_key="your_api_key")

# User management examples
add_alignerr(client, ["user1", "user2"])
promote_user_to_production(client, "project_id", ["user1", "user2"])
promote_all_users_to_production(client, "project_id")

# Project management examples
share_project_with_alignerr(client, "project_id")
promote_project_to_production(client, "project_id")
promote_project_to_status(client, "project_id", ProjectStatus.Calibration)

# Get user statuses across projects
statuses = get_alignerr_project_statuses(
    client,
    ["user_id_1", "user_id_2"],
    ["project_id_1", "project_id_2"]
)

## Alignerr Management

### Pre-Approved Alignerr System

The `add_alignerr` function adds users to a "pre-approved alignerr list" which allows them to skip or fast-track the evaluation process.

**What does "pre-approved alignerr" mean?**
- **Normal process**: Users typically need to go through evaluation/calibration before working on production tasks
- **Pre-approved process**: Trusted users can skip evaluation and start working immediately

**When to use `add_alignerr`:**
- Fast-track experienced users who don't need full evaluation
- Add trusted contractors who have already proven their skills
- Bulk approve users for urgent projects
- Migrate existing workers from other systems

### Examples

```python
# Add a single trusted user
result = add_alignerr(client, ["cm1pk2jhg0avt07z9h3b9user"])
print("✅ Added 1 pre-approved alignerr")

# Add multiple experienced users at once
experienced_users = [
    "cm1pk2jhg0avt07z9h3b9use1",  # John - experienced labeler
    "cm1pk2jhg0avt07z9h3b9use2",  # Sarah - expert reviewer
    "cm1pk2jhg0avt07z9h3b9use3"   # Mike - trusted contractor
]
result = add_alignerr(client, experienced_users)
print(f"Added {len(result['addPreApprovedAlignerrs']['alignerrs'])} pre-approved alignerrs")

# Process the results
for alignerr in result['addPreApprovedAlignerrs']['alignerrs']:
    print(f"✅ User {alignerr['userId']} is now pre-approved (ID: {alignerr['id']})")
    print(f"   Added on: {alignerr['createdAt']}")

# Real-world scenario: Onboarding trusted contractors for a new project
trusted_contractors = [
    "cm1pk2jhg0avt07z9contractor1",  # Alice - 2 years experience
    "cm1pk2jhg0avt07z9contractor2",  # Bob - expert in medical data
    "cm1pk2jhg0avt07z9contractor3",  # Carol - fast and accurate
]
result = add_alignerr(client, trusted_contractors)
print("✅ All contractors are now pre-approved and ready to work!")
```

**What happens after calling `add_alignerr`:**
1. Users become "pre-approved alignerrs" in the system
2. They can be assigned to projects without full evaluation
3. They get an internal alignerr ID (different from their user ID)
4. Project managers can see them in the pre-approved list
5. They can start working on tasks immediately

## User and Group Management

For general user and group management, use the native Labelbox SDK. See the [Labelbox API documentation](https://docs.labelbox.com/reference) for comprehensive guides on:

The alignerr-tools package focuses on Alignerr-specific functionality that is not available in the standard Labelbox SDK.

## Organized Module Access

You can also import functions by their modules for better organization:

```python
from alignerr_tools import user_management, project_management, rates

# User management
user_management.add_alignerr(client, ["user1", "user2"])
user_management.promote_user_to_production(client, "project_id", ["user1", "user2"])

# Project management
project_management.share_project_with_alignerr(client, "project_id")
project_management.promote_project_to_production(client, "project_id")

# Rates management
rates.get_project_rates(client, "project_id")
rates.set_project_rates(client, "project_id", 25.0, UserRole.Labeler, ProjectMode.Production)
```

**Note**: For general project sharing with individual users, use the native Labelbox SDK. See the [Labelbox API documentation](https://docs.labelbox.com/reference) for user and project management.

## Rate Management

### Querying Rates

```python
# Query project rates
rates_data = get_project_rates(client, "project_id")

# Get evaluation project information
eval_project = get_evaluation_project(client, "project_id")
if eval_project:
    print(f"Evaluation project ID: {eval_project.uid}")
    print(f"Evaluation project name: {eval_project.name}")
    print(f"Project status: {eval_project.status}")
else:
    print("No evaluation project exists for this project")

# Export data from evaluation project
export_params = {
    "attachments": True,
    "metadata_fields": True,
    "data_row_details": True,
    "project_details": True,
    "label_details": True,
    "performance_details": True,
}

export_filters = {
    "last_activity_at": ["2000-01-01 00:00:00", "2050-01-01 00:00:00"],
    "workflow_status": "InReview",
}

# Export evaluation project data (raises exception if no evaluation project exists)
eval_data = evaluation_export(client, "project_id", params=export_params, filters=export_filters)
print(f"Exported {len(eval_data)} data rows from evaluation project")

# Export with default parameters (no filters)
eval_data_simple = evaluation_export(client, "project_id")
for row in eval_data_simple:
    print(f"Data row ID: {row['data_row']['id']}")

# Access production project rates
production_rates = rates_data["project"]["ratesV2"]
for rate in production_rates:
    if not rate["isBillRate"] and rate["userRole"]:
        print(f"Pay rate - {rate['userRole']['name']}: ${rate['rate']}/{rate['billingMode']}")
    elif rate["isBillRate"]:
        print(f"Bill rate: ${rate['rate']}/{rate['billingMode']}")

# Get available user roles (using Labelbox SDK)
roles = client.get_roles()
```

### Setting Rates

```python
# Create datetime objects for rate effective dates
start_date = datetime(2024, 1, 15, 0, 0, 0)  # UTC
end_date = datetime(2024, 12, 31, 23, 59, 59)  # UTC

# Set project rates (mirrors UI exactly)
# Set production rates
set_project_rates(
    client,
    project_id="your_main_project_id",
    rate=25.0,
    user_role=UserRole.Labeler,
    mode=ProjectMode.Production,
    effective_from=start_date
)

set_project_rates(
    client,
    project_id="your_main_project_id",
    rate=30.0,
    user_role=UserRole.Reviewer,
    mode=ProjectMode.Production,
    effective_from=start_date
)

set_project_rates(
    client,
    project_id="your_main_project_id",
    rate=75.0,
    user_role=UserRole.Customer,
    mode=ProjectMode.Production,
    effective_from=start_date
)

# Set calibration rates (automatically uses calibration project)
set_project_rates(
    client,
    project_id="your_main_project_id",
    rate=20.0,
    user_role=UserRole.Labeler,
    mode=ProjectMode.Calibration,
    effective_from=start_date
)

# Set individual Alignerr rate with absolute rate (fixed amount)
set_project_alignerr_rate(
    client,
    project_id="your_project_id",
    user_id="user_id",
    effective_from=start_date,
    absolute_rate=30.0,  # $30/hour fixed rate
    effective_until=end_date
)

# Set individual Alignerr rate with multiplier rate (percentage of base rate)
set_project_alignerr_rate(
    client,
    project_id="your_project_id",
    user_id="user_id",
    effective_from=start_date,
    multiplier_rate=1.25,  # 125% of base rate
    effective_until=end_date
)

# Bulk set Alignerr rates (mix of absolute and multiplier rates)
user_rates = [
    {"userId": "user_id_1", "absoluteRate": 25.0},    # $25/hour fixed
    {"userId": "user_id_2", "multiplierRate": 1.5}    # 150% of base rate
]
bulk_set_project_alignerr_rates(
    client,
    project_id="your_project_id",
    user_rates=user_rates,
    effective_from=start_date,
    effective_until=end_date
)

# Set country multiplier
set_country_multiplier(client, "your_project_id", enabled=True)   # Enable country multiplier
set_country_multiplier(client, "your_project_id", enabled=False)  # Disable country multiplier
```

## Available Enums

### ProjectStatus
- `Calibration` = "CALIBRATION"
- `Paused` = "PAUSED"
- `Production` = "PRODUCTION"
- `Complete` = "COMPLETE"

### AlignerrStatus
- `Calibration` = "calibration"
- `Production` = "production"
- `Paused` = "paused"

### AlignerrEvaluationStatus
- `Evaluation` = "evaluation"
- `Production` = "production"

### Organization
- `Alignerr` = "cm1pk2jhg0avt07z9h3b9fy9p"

### BillingMode
- `ByHour` = "BY_HOUR"
- `ByTask` = "BY_TASK"

### RateType
- `WorkerPay` = "worker_pay" (for labeler/reviewer pay rates)
- `CustomerBill` = "customer_bill" (for customer billing rates)

### UserRole
- `Labeler` = "cjlvi914y1aa20714372uvzjv"
- `Reviewer` = "cjlvi919b1aa50714k75euii5"
- `Customer` = None

### ProjectMode
- `Production` = "production"
- `Calibration` = "calibration"

## Requirements

- Python 3.9+
- labelbox

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Build package
poetry build
```
