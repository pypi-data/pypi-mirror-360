import json
from typing import List, Dict, Any, Optional
from .base_client import BaseClappiaClient
from clappia_tools._utils.validators import ClappiaInputValidator
from clappia_tools._utils.logging_utils import get_logger
from clappia_tools._models.model import Section
from clappia_tools._models.model import Field

logger = get_logger(__name__)


class AppManagementClient(BaseClappiaClient):
    """Client for creating and modifying Clappia applications.
    
    This client handles application creation, field management, and other 
    app structure modifications.
    """

    def create_app(self, app_name: str, requesting_user_email_address: str, 
                   sections: List[Dict[str, Any]]) -> str:
        """Create a new Clappia application with specified sections and fields.

        Args:
            app_name: Name of the new application (e.g., "Employee Survey", "Inventory Management"). Minimum 10 characters.
            requesting_user_email_address: Email address of the user creating the app (becomes the app owner).
            sections: List of Section objects defining the app structure. Each section contains fields with specific types and properties.

            Example:
            {
                "sections": [
                    {
                        "sectionName": "Section 1",
                        "fields": [{"fieldType": "singleLineText", "label": "Field 1", "options": ["Option 1", "Option 2"]}, {"fieldType": "multiLineText", "label": "Field 2", "options": ["Option 3", "Option 4"]}]
                    }
                ]
            }

        Returns:
            str: Success message with app ID and URL, or error message if the request fails.
        """
        is_valid, error_msg = ClappiaInputValidator.validate_app_name(app_name)
        if not is_valid:
            return f"Error: Invalid app_name - {error_msg}"

        if not ClappiaInputValidator.validate_email(requesting_user_email_address):
            return "Error: requesting_user_email_address must be a valid email address"

        # Convert sections dict to Section objects
        section_objects: List[Section] = []
        for section_dict in sections:
            fields = []
            for field_dict in section_dict.get("fields", []):
                field = Field(
                    fieldType=field_dict["fieldType"],
                    label=field_dict["label"],
                    options=field_dict.get("options")
                )
                fields.append(field)
            
            section = Section(
                sectionName=section_dict["sectionName"],
                fields=fields
            )
            section_objects.append(section)

        is_valid, error_msg = ClappiaInputValidator.validate_app_structure(section_objects)
        if not is_valid:
            return f"Error: Invalid sections - {error_msg}"

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return f"Error: {env_error}"

        payload = {
            "workplaceId": self.api_utils.workplace_id,
            "appName": app_name.strip(),
            "requestingUserEmailAddress": requesting_user_email_address.strip(),
            "sections": [section.to_dict() for section in section_objects],
        }

        logger.info(f"Creating app with payload: {json.dumps(payload, indent=2)}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinition-external/createApp",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return f"Error: {error_message}"
        

        app_id = response_data.get("appId") if response_data else None
        app_url = response_data.get("appUrl") if response_data else None
        result = {
            "appId": app_id,
            "appName": app_name,
            "appUrl": app_url,
            "status": "created"
        }
        return f"App created successfully:\nSUMMARY:\n{json.dumps(result, indent=2)}\n\nFULL RESPONSE:\n{json.dumps(response_data, indent=2)}"

    def add_field(self, app_id: str, requesting_user_email_address: str,
                  section_index: int, field_index: int, field_type: str, 
                  label: Optional[str] = None, required: Optional[bool] = None,  description: Optional[str] = None,
                  block_width_percentage_desktop: Optional[int] = None,
                  block_width_percentage_mobile: Optional[int] = None,
                  display_condition: Optional[str] = None,
                  retain_values: Optional[bool] = None,
                  is_editable: Optional[bool] = None,
                  editability_condition: Optional[str] = None,
                  validation: Optional[str] = None,
                  default_value: Optional[str] = None,
                  options: Optional[List[str]] = None,
                  style: Optional[str] = None,
                  number_of_cols: Optional[int] = None,
                  allowed_file_types: Optional[List[str]] = None,
                  max_file_allowed: Optional[int] = None,
                  image_quality: Optional[str] = None,
                  image_text: Optional[str] = None,
                  file_name_prefix: Optional[str] = None,
                  formula: Optional[str] = None,
                  hidden: Optional[bool] = None) -> str:
        """Add a new field to an existing Clappia application at a specific position.

        Args:
            app_id: Application ID (e.g., "MFX093412").
            requesting_user_email_address: Email address of the user adding the field.
            section_index: Index of the section to add the field to (starts from 0).
            field_index: Position within the section for the new field (starts from 0).
            field_type: Type of field (e.g., "singleLineText", "singleSelector").
            label: Display label for the field.
            required: Whether the field is required.
            description: Field description or help text.
            block_width_percentage_desktop: Width percentage on desktop.
            block_width_percentage_mobile: Width percentage on mobile.
            display_condition: Condition for when to show the field.
            retain_values: Whether to retain values when field is hidden.
            is_editable: Whether the field can be edited.
            editability_condition: Condition for when field is editable.
            validation: Validation type.
            default_value: Default value for the field.
            options: List of options for selector fields.
            style: Style for selector fields.
            number_of_cols: Number of columns for selector fields.
            allowed_file_types: List of allowed file types for file fields.
            max_file_allowed: Maximum files allowed.
            image_quality: Image quality for file fields.
            image_text: Text overlay for image fields.
            file_name_prefix: Prefix for uploaded file names.
            formula: Formula for calculation fields.
            hidden: Whether the field is hidden.

        Returns:
            str: Success message with generated field name or error message if the request fails.
        """
        add_field_to_app_field_types = [
            "singleLineText",
            "multiLineText",
            "singleSelector",
            "multiSelector",
            "dropDown",
            "dateSelector",
            "timeSelector",
            "phoneNumber",
            "uniqueNumbering",
            "file",
            "gpsLocation",
            "html",
            "calculationsAndLogic",
            "codeScanner",
            "counter",
            "slider",
            "signature",
            "validation",
            "liveTracking",
            "nfcReader",
            "address"          
        ]
            
        is_valid, error_msg = ClappiaInputValidator.validate_app_id(app_id)
        if not is_valid:
            return f"Error: Invalid app_id - {error_msg}"
        
        if not requesting_user_email_address or not requesting_user_email_address.strip():
            return "Error: requesting_user_email_address is required and cannot be empty"
        
        if not ClappiaInputValidator.validate_email(requesting_user_email_address):
            return "Error: requesting_user_email_address must be a valid email address"
        
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return f"Error: {env_error}"
        
        if field_type not in add_field_to_app_field_types:
            return f"Error: field_type '{field_type}' is not allowed to be added to app, allowed field types are {add_field_to_app_field_types}"

        payload = {
            "workplaceId": self.api_utils.workplace_id,
            "appId": app_id.strip(),
            "requestingUserEmailAddress": requesting_user_email_address.strip(),
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "fieldType": field_type,
        }
        
        # Add optional parameters if provided
        if description is not None:
            payload["description"] = description.strip()

        if required is not None:
            payload["required"] = required

        if label is not None:
            payload["label"] = label.strip()

        if block_width_percentage_desktop is not None:
            payload["blockWidthPercentageDesktop"] = block_width_percentage_desktop
        if block_width_percentage_mobile is not None:
            payload["blockWidthPercentageMobile"] = block_width_percentage_mobile
        if display_condition is not None:
            payload["displayCondition"] = display_condition.strip()
        if retain_values is not None:
            payload["retainValues"] = retain_values
        if is_editable is not None:
            payload["isEditable"] = is_editable
        if editability_condition is not None:
            payload["editabilityCondition"] = editability_condition.strip()
        if validation is not None:
            payload["validation"] = validation
        if default_value is not None and field_type == "singleLineText":
            payload["defaultValue"] = default_value.strip()
        if options is not None and field_type in ["singleSelector", "multiSelector", "dropDown"]:
            payload["options"] = options
        if style is not None and field_type in ["singleSelector", "multiSelector"]:
            payload["style"] = style
        if number_of_cols is not None and field_type in ["singleSelector", "multiSelector"]:
            payload["numberOfCols"] = number_of_cols
        if allowed_file_types is not None and field_type == "file":
            payload["allowedFileTypes"] = allowed_file_types
        if max_file_allowed is not None and field_type == "file":
            payload["maxFileAllowed"] = max_file_allowed
        if image_quality is not None and field_type == "file":
            payload["imageQuality"] = image_quality
        if image_text is not None and field_type == "file":
            payload["imageText"] = image_text.strip()
        if file_name_prefix is not None and field_type == "file":
            payload["fileNamePrefix"] = file_name_prefix.strip()
        if formula is not None and field_type == "calculationsAndLogic":
            payload["formula"] = formula.strip()
        if hidden is not None and field_type == "formula":
            payload["hidden"] = hidden
        
        logger.info(f"Adding field to app_id: {app_id} with payload: {payload}")
        
        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )
        
        if not success:
            logger.error(f"Error: {error_message}")
            return f"Error: {error_message}"
        
        
        field_name = response_data.get("fieldName") if response_data else None
        result = f"Successfully added field.\nField Name: {field_name}\n\nFULL RESPONSE:\n{json.dumps(response_data, indent=2)}"
        return result
    
    def update_field(self, app_id: str, requesting_user_email_address: str, field_name: str,
                    label: Optional[str] = None, description: Optional[str] = None,
                    required: Optional[bool] = None, block_width_percentage_desktop: Optional[int] = None,
                    block_width_percentage_mobile: Optional[int] = None, display_condition: Optional[str] = None,
                    retain_values: Optional[bool] = None, is_editable: Optional[bool] = None,
                    editability_condition: Optional[str] = None, validation: Optional[str] = None,
                    default_value: Optional[str] = None, options: Optional[List[str]] = None,
                    style: Optional[str] = None, number_of_cols: Optional[int] = None,
                    allowed_file_types: Optional[List[str]] = None, max_file_allowed: Optional[int] = None,
                    image_quality: Optional[str] = None, image_text: Optional[str] = None,
                    file_name_prefix: Optional[str] = None, formula: Optional[str] = None,
                    hidden: Optional[bool] = None) -> str:
        """Updates an existing field in a Clappia application with new configuration.

        Modifies the properties of an existing field in a Clappia app, enabling dynamic form updates,
        A/B testing, and iterative improvements without recreating the entire app.

        Args:
            app_id: Application ID in uppercase letters and numbers format (e.g., "MFX093412").
            requesting_user_email_address: Email address of the user updating the field.
                This user must have permission to modify the app. Must be a valid email format.
            field_name: Variable name of the existing field to update (e.g., "employeeName", "department").
            label: New display label for the field.
            description: New field description/help text.
            required: Whether the field is mandatory.
            block_width_percentage_desktop: Width percentage on desktop (1-100).
            block_width_percentage_mobile: Width percentage on mobile (1-100).
            display_condition: Condition for when to show the field.
            retain_values: Whether to retain values when field is hidden.
            is_editable: Whether the field can be edited.
            editability_condition: Condition for when field is editable.
            validation: Validation type - "none", "number", "email", "url", "custom".
            default_value: Default value for the field (applicable only for singleLineText).
            options: List of options for selector fields (applicable for singleSelector/multiSelector/dropDown).
            style: Style for selector fields - "Standard" or "Chips" (applicable for singleSelector/multiSelector).
            number_of_cols: Number of columns for selector fields (applicable for singleSelector/multiSelector).
            allowed_file_types: List of allowed file types (applicable for file fields).
                Valid values: "images_camera_upload", "images_gallery_upload", "videos", "documents".
            max_file_allowed: Maximum files allowed, between 1-10 (applicable for file fields).
            image_quality: Image quality - "low", "medium", "high" (applicable for file fields).
            image_text: Text overlay for image fields (applicable for file fields).
            file_name_prefix: Prefix for uploaded file names (applicable for file fields).
            formula: Formula for calculation fields (applicable for calculationsAndLogic fields).
            hidden: Whether the field is hidden (applicable for formula fields).

        Returns:
            str: Formatted response with field update details and status.

        Examples:
            Update field label and make required:
                >>> client.update_field("APP123", "user@company.com", "employeeName", 
                ...                    label="Full Employee Name", required=True)

            Update dropdown options:
                >>> client.update_field("APP123", "user@company.com", "department",
                ...                    options=["HR", "IT", "Finance", "Marketing"])

            Change validation and add description:
                >>> client.update_field("APP123", "user@company.com", "emailField",
                ...                    validation="email", 
                ...                    description="Enter your corporate email")
        """
        # Validation
        is_valid, error_msg = ClappiaInputValidator.validate_app_id(app_id)
        if not is_valid:
            return f"Error: Invalid app_id - {error_msg}"

        if not requesting_user_email_address or not requesting_user_email_address.strip():
            return "Error: requesting_user_email_address is required and cannot be empty"

        if not ClappiaInputValidator.validate_email(requesting_user_email_address):
            return "Error: requesting_user_email_address must be a valid email address"

        if not field_name or not field_name.strip():
            return "Error: field_name is required and cannot be empty"

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return f"Error: {env_error}"

        # Validate optional parameters
        if validation and validation not in ["none", "number", "email", "url", "custom"]:
            return f"Error: Invalid validation type '{validation}'. Valid types: none, number, email, url, custom"

        if style and style not in ["Standard", "Chips"]:
            return f"Error: Invalid style '{style}'. Valid styles: Standard, Chips"

        if image_quality and image_quality not in ["low", "medium", "high"]:
            return f"Error: Invalid image quality '{image_quality}'. Valid qualities: low, medium, high"

        if allowed_file_types:
            valid_file_types = {"images_camera_upload", "images_gallery_upload", "videos", "documents"}
            for file_type in allowed_file_types:
                if file_type not in valid_file_types:
                    return f"Error: Invalid file type '{file_type}'. Valid types: {', '.join(valid_file_types)}"

        if max_file_allowed is not None and (max_file_allowed < 1 or max_file_allowed > 10):
            return "Error: max_file_allowed must be between 1 and 10"

        # Build payload with only non-None values
        payload = {
            "workplaceId": self.api_utils.workplace_id,
            "appId": app_id.strip(),
            "requestingUserEmailAddress": requesting_user_email_address.strip(),
            "fieldName": field_name.strip()
        }

        # Add optional fields only if they have values (not None)
        if label is not None:
            payload["label"] = label.strip()

        if required is not None:
            payload["required"] = required

        if description is not None:
            payload["description"] = description.strip()

        if block_width_percentage_desktop is not None:
            payload["blockWidthPercentageDesktop"] = block_width_percentage_desktop

        if block_width_percentage_mobile is not None:
            payload["blockWidthPercentageMobile"] = block_width_percentage_mobile

        if display_condition is not None:
            payload["displayCondition"] = display_condition.strip()

        if retain_values is not None:
            payload["retainValues"] = retain_values

        if is_editable is not None:
            payload["isEditable"] = is_editable

        if editability_condition is not None:
            payload["editabilityCondition"] = editability_condition.strip()

        if validation is not None:
            payload["validation"] = validation

        if default_value is not None:
            payload["defaultValue"] = default_value.strip()

        if options is not None:
            payload["options"] = options

        if style is not None:
            payload["style"] = style

        if number_of_cols is not None:
            payload["numberOfCols"] = number_of_cols

        if allowed_file_types is not None:
            payload["allowedFileTypes"] = allowed_file_types

        if max_file_allowed is not None:
            payload["maxFileAllowed"] = max_file_allowed

        if image_quality is not None:
            payload["imageQuality"] = image_quality

        if image_text is not None:
            payload["imageText"] = image_text.strip()

        if file_name_prefix is not None:
            payload["fileNamePrefix"] = file_name_prefix.strip()

        if formula is not None:
            payload["formula"] = formula.strip()

        if hidden is not None:
            payload["hidden"] = hidden

        logger.info(f"Updating field '{field_name}' in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return f"Error: {error_message}"
        
        updated_properties = []
        if label is not None:
            updated_properties.append("label")
        if description is not None:
            updated_properties.append("description")
        if required is not None:
            updated_properties.append("required")

        if block_width_percentage_desktop is not None:
            updated_properties.append("block_width_percentage_desktop")
        if block_width_percentage_mobile is not None:
            updated_properties.append("block_width_percentage_mobile")
        if display_condition is not None:
            updated_properties.append("display_condition")
        if retain_values is not None:
            updated_properties.append("retain_values")
        if is_editable is not None:
            updated_properties.append("is_editable")
        if editability_condition is not None:
            updated_properties.append("editability_condition")
        if validation is not None:
            updated_properties.append("validation")
        if default_value is not None:
            updated_properties.append("default_value")
        if options is not None:
            updated_properties.append("options")
        if style is not None:
            updated_properties.append("style")
        if number_of_cols is not None:
            updated_properties.append("number_of_cols")
        if allowed_file_types is not None:
            updated_properties.append("allowed_file_types")
        if max_file_allowed is not None:
            updated_properties.append("max_file_allowed")
        if image_quality is not None:
            updated_properties.append("image_quality")
        if image_text is not None:
            updated_properties.append("image_text")
        if file_name_prefix is not None:
            updated_properties.append("file_name_prefix")
        if formula is not None:
            updated_properties.append("formula")
        if hidden is not None:
            updated_properties.append("hidden")

        update_info = {
            "fieldName": field_name,
            "appId": app_id,
            "requestingUser": requesting_user_email_address,
            "updatedProperties": updated_properties,
            "status": "updated",
        }

        return f"Successfully updated field:\n\nSUMMARY:\n{json.dumps(update_info, indent=2)}\n\nFULL RESPONSE:\n{json.dumps(response_data, indent=2)}"