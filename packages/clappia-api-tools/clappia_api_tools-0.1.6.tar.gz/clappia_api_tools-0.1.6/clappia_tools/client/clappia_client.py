from typing import Optional, Dict, Any, List
from .submission_client import SubmissionClient
from .app_definition_client import AppDefinitionClient
from .app_management_client import AppManagementClient

class ClappiaClient:
    """Main Clappia client that provides unified access to all Clappia functionality.
    
    This client acts as a facade that combines all specialized clients (SubmissionClient,
    AppDefinitionClient, AppManagementClient) into a single, easy-to-use interface.
    
    Users can access functionality in two ways:
    1. Through specialized client properties (client.submissions.create_submission())
    2. Through direct methods for backward compatibility (client.create_submission())
    
    Attributes:
        submissions: SubmissionClient for managing submissions
        app_definition: AppDefinitionClient for retrieving app definitions  
        app_management: AppManagementClient for creating and modifying apps
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, 
                 workplace_id: Optional[str] = None, timeout: int = 30):
        """Initialize the main Clappia client with all specialized clients.

        Args:
            api_key: Clappia API key. If None, will be read from environment variables.
            base_url: API base URL. If None, will use default Clappia API URL.
            workplace_id: Workspace ID. If None, will be read from environment variables.
            timeout: Request timeout in seconds. Defaults to 30.
        """
        # Initialize all specialized clients
        self.submissions = SubmissionClient(api_key, base_url, workplace_id, timeout)
        self.app_definition = AppDefinitionClient(api_key, base_url, workplace_id, timeout)
        self.app_management = AppManagementClient(api_key, base_url, workplace_id, timeout)

    # =============================================================================
    # SUBMISSION METHODS - Direct access for backward compatibility
    # =============================================================================

    def create_submission(self, app_id: str, data: Dict[str, Any], email: str) -> str:
        """Creates a new submission in a Clappia application.
        
        This is a convenience method that delegates to self.submissions.create_submission().
        
        Args:
            app_id: Application ID in uppercase letters and numbers format.
            data: Dictionary of field data to submit.
            email: Email address of the user creating the submission.
            
        Returns:
            str: Formatted response with submission details and status.
        """
        return self.submissions.create_submission(app_id, data, email)

    def edit_submission(self, app_id: str, submission_id: str, data: Dict[str, Any], email: str) -> str:
        """Edits an existing Clappia submission.
        
        This is a convenience method that delegates to self.submissions.edit_submission().
        
        Args:
            app_id: Application ID in uppercase letters and numbers format.
            submission_id: Unique identifier of the submission to update.
            data: Dictionary of field data to update.
            email: Email address of the user requesting the edit.
            
        Returns:
            str: Formatted response with edit details and status.
        """
        return self.submissions.edit_submission(app_id, submission_id, data, email)
    
    def update_submission_owners(self, app_id: str, submission_id: str, 
                               requesting_user_email_address: str, email_ids: List[str]) -> str:
        """Updates the ownership of a Clappia submission.
        
        This is a convenience method that delegates to self.submissions.update_owners().
        
        Args:
            app_id: Application ID in uppercase letters and numbers format.
            submission_id: Unique identifier of the submission to update.
            requesting_user_email_address: Email address of the user making the change.
            email_ids: List of email addresses to add as new owners.
            
        Returns:
            str: Formatted response with update details and status.
        """
        return self.submissions.update_owners(app_id, submission_id, requesting_user_email_address, email_ids)

    def update_submission_status(self, app_id: str, submission_id: str, 
                               requesting_user_email_address: str, status_name: str, comments: str) -> str:
        """Updates the status of a Clappia submission.
        
        This is a convenience method that delegates to self.submissions.update_status().
        
        Args:
            app_id: Application ID in uppercase letters and numbers format.
            submission_id: Unique identifier of the submission to update.
            requesting_user_email_address: Email address of the user making the change.
            status_name: Name of the new status to apply.
            comments: Optional comments to include with the status change.
            
        Returns:
            str: Formatted response with update details and status.
        """
        return self.submissions.update_status(app_id, submission_id, requesting_user_email_address, status_name, comments)

    # =============================================================================
    # APP DEFINITION METHODS - Direct access for backward compatibility
    # =============================================================================

    def get_app_definition(self, app_id: str, language: str = "en", 
                          strip_html: bool = True, include_tags: bool = True) -> str:
        """Fetches complete definition of a Clappia application.
        
        This is a convenience method that delegates to self.app_definition.get_definition().
        
        Args:
            app_id: Unique application identifier in uppercase format.
            language: Language code for field labels and translations.
            strip_html: Whether to remove HTML formatting from text fields.
            include_tags: Whether to include metadata tags in response.
            
        Returns:
            str: Formatted response with app definition details and structure.
        """
        return self.app_definition.get_definition(app_id, language, strip_html, include_tags)

    # =============================================================================
    # APP MANAGEMENT METHODS - Direct access for backward compatibility
    # =============================================================================

    def create_app(self, app_name: str, requesting_user_email_address: str, 
                   sections: List[Dict[str, Any]]) -> str:
        """Creates a new Clappia application with specified sections and fields.
        
        This is a convenience method that delegates to self.app_management.create_app().
        
        Args:
            app_name: Name of the new application.
            requesting_user_email_address: Email address of the user creating the app.
            sections: List of Section objects defining the app structure.
            
        Returns:
            str: Success message with app ID and URL, or error message.
        """
        return self.app_management.create_app(app_name, requesting_user_email_address, sections)

    def add_field_to_app(self, app_id: str, requesting_user_email_address: str,
                        section_index: int, field_index: int, field_type: str, 
                        label: str, required: bool, **kwargs) -> str:
        """Adds a new field to an existing Clappia application.
        
        This is a convenience method that delegates to self.app_management.add_field().
        
        Args:
            app_id: Application ID.
            requesting_user_email_address: Email address of the user adding the field.
            section_index: Index of the section to add the field to.
            field_index: Position within the section for the new field.
            field_type: Type of field to add.
            label: Display label for the field.
            required: Whether the field is required.
            **kwargs: Additional optional parameters for field configuration.
            
        Returns:
            str: Success message with generated field name or error message.
        """
        return self.app_management.add_field(
            app_id, requesting_user_email_address, section_index, field_index, 
            field_type, label, required, **kwargs
        )

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    def get_client_info(self) -> Dict[str, Any]:
        """Returns information about the client and its configuration.
        
        Returns:
            dict: Dictionary containing client configuration information.
        """
        return {
            "client_type": "ClappiaClient",
            "version": "1.0.0",
            "specialized_clients": {
                "submissions": "SubmissionClient",
                "app_definition": "AppDefinitionClient", 
                "app_management": "AppManagementClient"
            },
            "api_config": {
                "base_url": self.submissions.api_utils.base_url,
                "workplace_id": self.submissions.api_utils.workplace_id,
                "timeout": self.submissions.api_utils.timeout
            }
        }

    def __repr__(self) -> str:
        """String representation of the ClappiaClient."""
        return f"ClappiaClient(workplace_id={self.submissions.api_utils.workplace_id})"

    def __str__(self) -> str:
        """Human-readable string representation of the ClappiaClient."""
        return f"Clappia API Client for workspace: {self.submissions.api_utils.workplace_id}"