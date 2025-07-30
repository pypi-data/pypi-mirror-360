# Clappia Tools

**LangChain integration for Clappia API**

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/clappia-tools)](https://pypi.org/project/clappia-tools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

Clappia Tools is a Python package that provides a unified client and a set of tools for seamless integration with the [Clappia API](https://www.clappia.com/). It enables developers to automate workflows, manage submissions, and interact with Clappia apps programmatically. The package is designed for use in automation, data integration, and agent-based systems (e.g., LangChain agents).

---

## Features

-  **Unified API Client**: One client for all Clappia API operations.
-  **Submission Management**: Create, edit, update owners, and change status of submissions.
-  **App Definition Retrieval**: Fetch complete app structure and metadata.
-  **Input Validation**: Built-in validation for IDs, emails, and status objects.
-  **Extensible Tools**: Modular functions for each operation, easily integrated into agents or scripts.
-  **Comprehensive Testing**: Includes unit and integration tests.

---

## Installation

```bash
pip install clappia-tools
```

Or, for development:

```bash
git clone https://github.com/clappia-dev/clappia-tools.git
cd clappia-tools
pip install -e .[dev]
```

---

## Configuration

You must provide your Clappia API credentials and workspace information directly when initializing the `ClappiaClient`:

-  `api_key`: Your Clappia API key
-  `base_url`: The base URL for the Clappia API (e.g., `https://api.clappia.com`)
-  `workplace_id`: Your Clappia workplace ID

**Example:**

```python
from clappia_tools import ClappiaClient

client = ClappiaClient(
    api_key="your-api-key",
    base_url="https://api.clappia.com",
    workplace_id="your-workplace-id"
)
```
---

## Usage

### Basic Client Usage

```python
from clappia_tools import ClappiaClient

client = ClappiaClient(
    api_key="your-api-key",
    base_url="https://api.clappia.com",
    workplace_id="your-workplace-id"
)

# Create a submission
result = client.create_submission(
    app_id="MFX093412",
    data={"employee_name": "John Doe", "department": "Engineering"},
    email="user@example.com"
)
print(result)

# Edit a submission
result = client.edit_submission(
    app_id="MFX093412",
    submission_id="HGO51464561",
    data={"department": "Marketing"},
    email="user@example.com"
)
print(result)

# Get app definition
result = client.get_app_definition(app_id="MFX093412")
print(result)
```

### Tool Functions

You can also use the modular tool functions directly:

```python
from clappia_tools._tools import (
    create_clappia_submission,
    edit_clappia_submission,
    get_app_definition,
    update_clappia_submission_owners,
    update_clappia_submission_status,
)

# Create a submission
data = {"employee_name": "Jane Doe", "department": "HR"}
response = create_clappia_submission("MFX093412", data, "user@example.com")
print(response)

# Update submission owners
response = update_clappia_submission_owners(
    "MFX093412", "HGO51464561", "admin@example.com", ["user1@company.com", "user2@company.com"]
)
print(response)

# Update submission status
response = update_clappia_submission_status(
    "MFX093412", "HGO51464561", "admin@example.com", {"statusName": "Approved", "comments": "Reviewed."}
)
print(response)
```

---

## Available Tools

-  `create_clappia_submission(app_id, data, email)`
-  `edit_clappia_submission(app_id, submission_id, data, email)`
-  `get_app_definition(app_id, language="en", strip_html=True, include_tags=True)`
-  `update_clappia_submission_owners(app_id, submission_id, requesting_user_email_address, email_ids)`
-  `update_clappia_submission_status(app_id, submission_id, requesting_user_email_address, status)`

See docstrings in each tool for detailed argument and return value descriptions.

---

## Input Validation

-  **App ID**: Must be uppercase letters and numbers (e.g., `MFX093412`).
-  **Submission ID**: Must be uppercase letters and numbers (e.g., `HGO51464561`).
-  **Email**: Must be a valid email address.
-  **Status**: Must be a dictionary with a non-empty `statusName` or `name` field.

Invalid inputs will return descriptive error messages.

---

## Testing

Run all tests (unit and integration):

```bash
pytest
```

---

## Contributing

1. Fork the repository and create your branch.
2. Write clear, well-documented code and tests.
3. Run `pytest` and ensure all tests pass.
4. Submit a pull request with a clear description of your changes.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
