import json
from .base_client import BaseClappiaClient
from clappia_tools._utils.validators import ClappiaInputValidator
from clappia_tools._utils.logging_utils import get_logger

logger = get_logger(__name__)


class AppDefinitionClient(BaseClappiaClient):
    """Client for managing Clappia app definitions.
    
    This client handles retrieving and managing application definitions,
    including forms, fields, sections, and metadata.
    """

    def get_definition(self, app_id: str, language: str = "en", 
                      strip_html: bool = True, include_tags: bool = True) -> str:
        """Fetches complete definition of a Clappia application including forms, fields, sections, and metadata.

        Retrieves structure and configuration of a Clappia app to understand available fields,
        validation rules, and workflow logic before creating charts, filtering submissions, or planning integrations.

        Args:
            app_id: Unique application identifier in uppercase letters and numbers format (e.g., QGU236634). Use this to specify which Clappia app definition to retrieve.
            language: Language code for field labels and translations. Available options: "en" (English, default), "es" (Spanish), "fr" (French), "de" (German). Use "es" for Spanish reports or "fr" for French localization.
            strip_html: Whether to remove HTML formatting from text fields. True (default) removes HTML tags for clean text, False preserves HTML formatting for display purposes.
            include_tags: Whether to include metadata tags in response. True (default) includes full metadata tags, False returns basic structure only for lightweight responses.

        Returns:
            str: Formatted response with app definition details and complete structure
        """
        is_valid, error_msg = ClappiaInputValidator.validate_app_id(app_id)
        if not is_valid:
            return f"Error: Invalid app_id - {error_msg}"

        params = {
            "appId": app_id.strip(),
            "workplaceId": self.api_utils.workplace_id,
            "language": language,
            "stripHtml": str(strip_html).lower(),
            "includeTags": str(include_tags).lower(),
        }

        logger.info(
            f"Getting app definition for app_id: {app_id} with params: {params}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="GET",
            endpoint="appdefinitionv2/getAppDefinition",
            params=params,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return f"Error: {error_message}"


        app_info = {
            "appId": response_data.get("appId") if response_data else None,
            "version": response_data.get("version") if response_data else None,
            "state": response_data.get("state") if response_data else None,
            "pageCount": len(response_data.get("pageIds", [])) if response_data else 0,
            "sectionCount": (
                len(response_data.get("sectionIds", [])) if response_data else 0
            ),
            "fieldCount": (
                len(response_data.get("fieldDefinitions", {})) if response_data else 0
            ),
            "appName": (
                response_data.get("metadata", {}).get("sectionName", "Unknown")
                if response_data
                else "Unknown"
            ),
            "description": (
                response_data.get("metadata", {}).get("description", "")
                if response_data
                else ""
            ),
        }

        return f"Successfully retrieved app definition:\n\nSUMMARY:\n{json.dumps(app_info, indent=2)}\n\nFULL DEFINITION:\n{json.dumps(response_data, indent=2)}"