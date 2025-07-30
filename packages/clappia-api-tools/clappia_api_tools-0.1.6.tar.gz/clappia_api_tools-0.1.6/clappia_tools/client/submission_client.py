import json
from typing import Dict, Any, List, Optional
from .base_client import BaseClappiaClient          
from clappia_tools._utils.validators import ClappiaInputValidator
from clappia_tools._utils.logging_utils import get_logger

logger = get_logger(__name__)


class SubmissionClient(BaseClappiaClient):
    """Client for managing Clappia submissions.
    
    This client handles all submission-related operations including creating,
    editing, retrieving, and managing submission ownership and status.
    """

    def create_submission(self, app_id: str, data: Dict[str, Any], requesting_user_email_address: str) -> str:
        """Creates a new submission in a Clappia application with specified field data.

        Submits form data to create a new record in the specified Clappia app.
        Use this to programmatically add entries, automate data collection, or integrate external systems.

        Args:
            app_id: Application ID in uppercase letters and numbers format (e.g., MFX093412). Use this to specify which Clappia app to create the submission in.
            data: Dictionary of field data to submit. Keys should match field names from the app definition, values should match expected field types. Example: {"employee_name": "John Doe", "department": "Engineering", "salary": 75000, "start_date": "2024-01-15"}. For file fields, use format: {"image_field_name": [{"s3Path": {"bucket": "my-files-bucket", "key": "images/photo.jpg", "makePublic": false}}]}.
            requesting_user_email_address (or email): Email address of the user creating the submission. This user becomes the submission owner and must have access to the specified app. Must be a valid email format.

        Returns:
            str: Formatted response with submission details and status
        """
        is_valid, error_msg = ClappiaInputValidator.validate_app_id(app_id)
        if not is_valid:
            return f"Error: Invalid app_id - {error_msg}"

        if not requesting_user_email_address or not requesting_user_email_address.strip():
            return "Error: requesting_user_email_address is required and cannot be empty"

        if not ClappiaInputValidator.validate_email(requesting_user_email_address):
            return "Error: requesting_user_email_address must be a valid email address"

        if not isinstance(data, dict):
            return "Error: data must be a dictionary"

        if not data:
            return "Error: data cannot be empty - at least one field is required"
        
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return f"Error: {env_error}"

        payload = {
            "workplaceId": self.api_utils.workplace_id,
            "appId": app_id.strip(),
            "requestingUserEmailAddress": requesting_user_email_address.strip(),
            "data": data,
        }

        logger.info(
            f"Creating submission for app_id: {app_id} with data: {data} and requesting_user_email_address: {requesting_user_email_address}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/create", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return f"Error: {error_message}"

        submission_id = response_data.get("submissionId") if response_data else None

        submission_info = {
            "submissionId": submission_id,
            "status": "created",
            "appId": app_id,
            "owner": requesting_user_email_address,
            "fieldsSubmitted": len(data),
        }

        return f"Successfully created submission:\n\nSUMMARY:\n{json.dumps(submission_info, indent=2)}\n\nFULL RESPONSE:\n{json.dumps(response_data, indent=2)}"

    def edit_submission(self, app_id: str, submission_id: str, data: Dict[str, Any], requesting_user_email_address: str) -> str:
        """Edits an existing Clappia submission by updating specified field values.

        Modifies field data in an existing submission record while preserving other field values.
        Use this to update form data, correct information, or add missing details to submissions.

        Args:
            app_id: Application ID in uppercase letters and numbers format (e.g., MFX093412). Use this to specify which Clappia app contains the submission.
            submission_id: Unique identifier of the submission to update (e.g., HGO51464561). This identifies the specific submission record to modify.
            data: Dictionary of field data to update. Keys should match field names from the app definition, values should match expected field types. Only specified fields will be updated. Example: {"employee_name": "Jane Doe", "department": "Marketing", "salary": 80000, "start_date": "20-02-2025"}.
            requesting_user_email_address: Email address of the user requesting the edit. This user must have permission to modify the submission. Must be a valid email format.

        Returns:
            str: Formatted response with edit details and status
        """
        is_valid, error_msg = ClappiaInputValidator.validate_app_id(app_id)
        if not is_valid:
            return f"Error: Invalid app_id - {error_msg}"

        is_valid, error_msg = ClappiaInputValidator.validate_submission_id(submission_id)
        if not is_valid:
            return f"Error: Invalid submission_id - {error_msg}"

        if not requesting_user_email_address or not requesting_user_email_address.strip():
            return "Error: requesting_user_email_address is required and cannot be empty"

        if not ClappiaInputValidator.validate_email(requesting_user_email_address):
            return "Error: requesting_user_email_address must be a valid email address"

        if not isinstance(data, dict):
            return "Error: data must be a dictionary"

        if not data:
            return "Error: data cannot be empty - at least one field is required"

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return f"Error: {env_error}"

        payload = {
            "workplaceId": self.api_utils.workplace_id,
            "appId": app_id.strip(),
            "submissionId": submission_id.strip(),
            "requestingUserEmailAddress": requesting_user_email_address.strip(),
            "data": data,
        }

        logger.info(
            f"Editing submission {submission_id} for app_id: {app_id} with data: {data} and requesting_user_email_address: {requesting_user_email_address}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/edit", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return f"Error: {error_message}"

        edit_info = {
            "submissionId": submission_id,
            "appId": app_id,
            "requestingUser": requesting_user_email_address,
            "fieldsUpdated": len(data),
            "updatedFields": list(data.keys()),
            "status": "updated",
        }

        return f"Successfully edited submission:\n\nSUMMARY:\n{json.dumps(edit_info, indent=2)}\n\nFULL RESPONSE:\n{json.dumps(response_data, indent=2)}"
    
    def update_owners(self, app_id: str, submission_id: str, requesting_user_email_address: str, 
                     email_ids: List[str]) -> str:
        """Updates the ownership of a Clappia submission by adding new owners to share access.

        Modifies submission ownership to include additional users who can view and edit the submission.
        Use this to collaborate on submissions, delegate work, or transfer ownership.

        Args:
            app_id: Application ID in uppercase letters and numbers format (e.g., MFX093412). Use this to specify which Clappia app contains the submission.
            submission_id: Unique identifier of the submission to update (e.g., HGO51464561). This identifies the specific submission record to modify.
            requesting_user_email_address: Email address of the user making the ownership change. This user must have permission to modify the submission. Must be a valid email format.
            email_ids: List of email addresses to add as new owners. Each email must be valid and the users should have access to the app. Example: ["user1@company.com", "user2@company.com"]. Invalid emails will be skipped with a warning.

        Returns:
            str: Formatted response with update details and status
        """
        is_valid, error_msg = ClappiaInputValidator.validate_app_id(app_id)
        if not is_valid:
            return f"Error: Invalid app_id - {error_msg}"

        is_valid, error_msg = ClappiaInputValidator.validate_submission_id(submission_id)
        if not is_valid:
            return f"Error: Invalid submission_id - {error_msg}"

        if not requesting_user_email_address or not requesting_user_email_address.strip():
            return "Error: requesting_user_email_address is required and cannot be empty"

        if not ClappiaInputValidator.validate_email(requesting_user_email_address):
            return "Error: requesting_user_email_address must be a valid email address"

        is_valid, validation_msg, valid_emails = ClappiaInputValidator.validate_email_list(email_ids)
        if not is_valid:
            return f"Error: {validation_msg}"

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return f"Error: {env_error}"

        payload = {
            "workplaceId": self.api_utils.workplace_id,
            "appId": app_id.strip(),
            "submissionId": submission_id.strip(),
            "requestingUserEmailAddress": requesting_user_email_address.strip(),
            "emailIds": valid_emails,
        }

        logger.info(
            f"Updating submission owners for app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="submissions/updateSubmissionOwners",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return f"Error: {error_message}"

        owners_info = {
            "submissionId": submission_id,
            "appId": app_id,
            "requestingUser": requesting_user_email_address,
            "newOwnersCount": len(valid_emails),
            "newOwners": valid_emails,
            "status": "updated",
        }

        result = f"Successfully updated submission owners:\n\nSUMMARY:\n{json.dumps(owners_info, indent=2)}"
        if validation_msg:
            result += f"\n\nWARNING: {validation_msg}"
        result += f"\n\nFULL RESPONSE:\n{json.dumps(response_data, indent=2)}"
        return result

    def update_status(self, app_id: str, submission_id: str, requesting_user_email_address: str, 
                     status_name: str, comments: str) -> str:
        """Updates the status of a Clappia submission to track workflow progress and approvals.

        Changes the submission status to indicate current stage in workflow (e.g., pending, approved, rejected).
        Use this to manage approval workflows, track processing stages, or update submission lifecycle.

        Args:
            app_id: Application ID in uppercase letters and numbers format (e.g., MFX093412). Use this to specify which Clappia app contains the submission.
            submission_id: Unique identifier of the submission to update (e.g., HGO51464561). This identifies the specific submission record to modify.
            requesting_user_email_address: Email address of the user making the status change. This user must have permission to modify the submission. Must be a valid email format.
            status_name: Name of the new status to apply to the submission.
            comments: Optional comments to include with the status change.

        Returns:
            str: Formatted response with update details and status
        """
        is_valid, error_msg = ClappiaInputValidator.validate_app_id(app_id)
        if not is_valid:
            return f"Error: Invalid app_id - {error_msg}"

        is_valid, error_msg = ClappiaInputValidator.validate_submission_id(submission_id)
        if not is_valid:
            return f"Error: Invalid submission_id - {error_msg}"

        if not requesting_user_email_address or not requesting_user_email_address.strip():
            return "Error: requesting_user_email_address is required and cannot be empty"

        if not ClappiaInputValidator.validate_email(requesting_user_email_address):
            return "Error: requesting_user_email_address must be a valid email address"

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return f"Error: {env_error}"

        if not status_name or not status_name.strip():
            return "Error: status_name is required and cannot be empty"
        
        status = {
            "name": status_name.strip(),
            "comments": comments.strip() if comments else None,
        }

        payload = {
            "workplaceId": self.api_utils.workplace_id,
            "appId": app_id.strip(),
            "submissionId": submission_id.strip(),
            "requestingUserEmailAddress": requesting_user_email_address.strip(),
            "status": status,
        }

        logger.info(f"Updating submission status for app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="submissions/updateStatus",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return f"Error: {error_message}"

        status_info = {
            "submissionId": submission_id,
            "appId": app_id,
            "requestingUser": requesting_user_email_address,
            "newStatus": status_name,
            "comments": comments,
            "updateStatus": "completed",
        }

        result = f"Successfully updated submission status:\n\nSUMMARY:\n{json.dumps(status_info, indent=2)}"
        result += f"\n\nFULL RESPONSE:\n{json.dumps(response_data, indent=2)}"
        return result