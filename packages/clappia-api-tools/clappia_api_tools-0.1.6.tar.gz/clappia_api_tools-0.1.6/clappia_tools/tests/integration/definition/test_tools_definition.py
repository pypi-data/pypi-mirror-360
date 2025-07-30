from unittest.mock import patch, Mock
from clappia_tools.client.app_definition_client import AppDefinitionClient
from clappia_tools.client.app_management_client import AppManagementClient
from clappia_tools.client.submission_client import SubmissionClient
from clappia_tools._models.model import Field, Section


def dummy_app_definition_client():
    """Helper function to create a dummy app definition client for testing"""
    return AppDefinitionClient(
        api_key="dummy_api_key",
        base_url="https://api.clappia.com",
        workplace_id="dummy_workplace_id",
        timeout=30
    )


def dummy_app_management_client():
    """Helper function to create a dummy app management client for testing"""
    return AppManagementClient(
        api_key="dummy_api_key",
        base_url="https://api.clappia.com",
        workplace_id="dummy_workplace_id",
        timeout=30
    )


def dummy_submission_client():
    """Helper function to create a dummy submission client for testing"""
    return SubmissionClient(
        api_key="dummy_api_key",
        base_url="https://api.clappia.com",
        workplace_id="dummy_workplace_id",
        timeout=30
    )


class TestDefinitionToolsIntegration:
    """Test cases for App Definition and Management tools"""

    @patch("clappia_tools.client.app_definition_client.AppDefinitionClient")
    def test_get_definition_tool_basic(self, mock_client_class):
        """Test get_definition with basic parameters"""
        # Setup mock
        mock_client = Mock()
        mock_client.get_definition.return_value = "App definition for MFX093412"
        mock_client_class.return_value = mock_client

        # Call tool
        client = dummy_app_definition_client()
        result = client.get_definition("MFX093412")

        # Verify
        assert "App definition for MFX093412" in result
        mock_client.get_definition.assert_called_once_with(
            "MFX093412", "en", True, True
        )

    @patch("clappia_tools.client.app_definition_client.AppDefinitionClient")
    def test_get_definition_tool_with_language(self, mock_client_class):
        """Test get_definition with different language"""
        # Setup mock
        mock_client = Mock()
        mock_client.get_definition.return_value = "Definición de aplicación para MFX093412"
        mock_client_class.return_value = mock_client

        # Call tool with Spanish language
        client = dummy_app_definition_client()
        result = client.get_definition("MFX093412", language="es")

        # Verify
        assert "Definición de aplicación para MFX093412" in result
        mock_client.get_definition.assert_called_once_with(
            "MFX093412", "es", True, True
        )

    @patch("clappia_tools.client.app_definition_client.AppDefinitionClient")
    def test_get_definition_tool_custom_options(self, mock_client_class):
        """Test get_definition with custom strip_html and include_tags options"""
        # Setup mock
        mock_client = Mock()
        mock_client.get_definition.return_value = "Raw app definition with HTML tags"
        mock_client_class.return_value = mock_client

        # Call tool with custom options
        client = dummy_app_definition_client()
        result = client.get_definition(
            "MFX093412", 
            language="fr", 
            strip_html=False, 
            include_tags=False
        )

        # Verify
        assert "Raw app definition with HTML tags" in result
        mock_client.get_definition.assert_called_once_with(
            "MFX093412", "fr", False, False
        )

    @patch("clappia_tools.client.app_definition_client.AppDefinitionClient")
    def test_get_definition_tool_error_handling(self, mock_client_class):
        """Test get_definition error handling"""
        # Setup mock to return error
        mock_client = Mock()
        mock_client.get_definition.return_value = "Error: Invalid app_id - APP123"
        mock_client_class.return_value = mock_client

        # Call tool with invalid app ID
        client = dummy_app_definition_client()
        result = client.get_definition("invalid-app-id")

        # Verify error is handled
        assert "Error: Invalid app_id" in result

    @patch("clappia_tools.client.app_management_client.AppManagementClient")
    def test_add_field_tool_basic(self, mock_client_class):
        """Test add_field with basic parameters"""
        # Setup mock
        mock_client = Mock()
        mock_client.add_field.return_value = "Success: Added field TEST_FIELD"
        mock_client_class.return_value = mock_client

        # Call tool
        client = dummy_app_management_client()
        result = client.add_field(
            app_id="MFX093412",
            requesting_user_email_address="admin@example.com",
            section_index=0,
            field_index=1,
            field_type="singleLineText",
            label="Employee Name",
            required=True
        )

        # Verify
        assert "Success: Added field TEST_FIELD" in result
        mock_client.add_field.assert_called_once_with(
            app_id="MFX093412",
            requesting_user_email_address="admin@example.com",
            section_index=0,
            field_index=1,
            field_type="singleLineText",
            label="Employee Name",
            required=True,
            description=None,
            block_width_percentage_desktop=None,
            block_width_percentage_mobile=None,
            display_condition=None,
            retain_values=None,
            is_editable=None,
            editability_condition=None,
            validation=None,
            default_value=None,
            options=None,
            style=None,
            number_of_cols=None,
            allowed_file_types=None,
            max_file_allowed=None,
            image_quality=None,
            image_text=None,
            file_name_prefix=None,
            formula=None,
            hidden=None,
        )

    @patch("clappia_tools.client.app_management_client.AppManagementClient")
    def test_add_field_tool_with_options(self, mock_client_class):
        """Test add_field with optional parameters"""
        # Setup mock
        mock_client = Mock()
        mock_client.add_field.return_value = "Success: Added dropdown field DROPDOWN_FIELD"
        mock_client_class.return_value = mock_client

        # Call tool with options
        client = dummy_app_management_client()
        result = client.add_field(
            app_id="MFX093412",
            requesting_user_email_address="admin@example.com",
            section_index=0,
            field_index=2,
            field_type="dropDown",
            label="Department",
            required=True,
            description="Select employee department",
            options=["Engineering", "Marketing", "Sales", "HR"],
            block_width_percentage_desktop=50
        )

        # Verify
        assert "Success: Added dropdown field DROPDOWN_FIELD" in result

    @patch("clappia_tools.client.app_management_client.AppManagementClient")
    def test_add_field_tool_selector_field(self, mock_client_class):
        """Test add_field with selector field types"""
        # Setup mock
        mock_client = Mock()
        mock_client.add_field.return_value = "Success: Added radio button field RADIO_FIELD"
        mock_client_class.return_value = mock_client

        # Call tool with radio button field
        client = dummy_app_management_client()
        result = client.add_field(
            app_id="MFX093412",
            requesting_user_email_address="admin@example.com",
            section_index=1,
            field_index=0,
            field_type="singleSelector",
            label="Employment Type",
            required=True,
            options=["Full-time", "Part-time", "Contract", "Intern"],
            style="horizontal",
            number_of_cols=2
        )

        # Verify
        assert "Success: Added radio button field RADIO_FIELD" in result

    @patch("clappia_tools.client.app_management_client.AppManagementClient")
    def test_add_field_tool_file_field(self, mock_client_class):
        """Test add_field with file upload field"""
        # Setup mock
        mock_client = Mock()
        mock_client.add_field.return_value = "Success: Added file upload field FILE_FIELD"
        mock_client_class.return_value = mock_client

        # Call tool with file field
        client = dummy_app_management_client()
        result = client.add_field(
            app_id="MFX093412",
            requesting_user_email_address="admin@example.com",
            section_index=2,
            field_index=0,
            field_type="file",
            label="Resume Upload",
            required=False,
            allowed_file_types=["pdf", "doc", "docx"],
            max_file_allowed=1,
            file_name_prefix="resume_"
        )

        # Verify
        assert "Success: Added file upload field FILE_FIELD" in result

    @patch("clappia_tools.client.app_management_client.AppManagementClient")
    def test_add_field_tool_validation_error(self, mock_client_class):
        """Test add_field with validation error"""
        # Setup mock to return validation error
        mock_client = Mock()
        mock_client.add_field.return_value = "Error: field_type 'invalidFieldType"
        mock_client_class.return_value = mock_client

        # Call tool with invalid field type
        client = dummy_app_management_client()
        result = client.add_field(
            app_id="MFX093412",
            requesting_user_email_address="admin@example.com",
            section_index=0,
            field_index=0,
            field_type="invalidFieldType",
            label="Invalid Field",
            required=True
        )

        # Verify error is handled
        assert "Error: field_type 'invalidFieldType'" in result

    @patch("clappia_tools.client.app_management_client.AppManagementClient")
    def test_create_app_tool_basic(self, mock_client_class):
        """Test create_app with basic configuration"""
        # Setup mock
        mock_client = Mock()
        mock_client.create_app.return_value = "App created successfully: App ID: APP123"
        mock_client_class.return_value = mock_client

        sections = [
            {
                "sectionName": "Personal Information",
                "fields": [
                    {"fieldType": "singleLineText", "label": "Full Name", "options": None, "required": False},
                    {"fieldType": "singleLineText", "label": "Email Address", "options": None, "required": False}
                ]
            }
        ]

        client = dummy_app_management_client()
        result = client.create_app(
            app_name="Employee Registration",
            requesting_user_email_address="admin@example.com",
            sections=sections
        )
        
        assert "App created successfully" in result
        mock_client.create_app.assert_called_once_with(
            "Employee Registration", "admin@example.com", sections
        )

    @patch("clappia_tools.client.app_management_client.AppManagementClient")
    def test_create_app_tool_multiple_sections(self, mock_client_class):
        """Test create_app with multiple sections and field types"""
        # Setup mock
        mock_client = Mock()
        mock_client.create_app.return_value = "Complex app created successfully: App ID: COMPLEX123"
        mock_client_class.return_value = mock_client

        sections = [
            {
                "sectionName": "Personal Information",
                "fields": [
                    {"fieldType": "singleLineText", "label": "Full Name", "options": None},
                    {"fieldType": "singleLineText", "label": "Email", "options": None}
                ]
            },
            {
                "sectionName": "Employment Details",
                "fields": [
                    {"fieldType": "singleLineText", "label": "Department", "options": ["Engineering", "Marketing"]},
                    {"fieldType": "singleLineText", "label": "Position", "options": ["Junior", "Senior", "Lead"]}
                ]
            },
            {
                "sectionName": "Additional Information",
                "fields": [
                    {"fieldType": "singleLineText", "label": "Comments", "options": None}
                ]
            }
        ]

        client = dummy_app_management_client()
        result = client.create_app(
            app_name="Comprehensive Employee Survey",
            requesting_user_email_address="hr@example.com",
            sections=sections
        )
        
        assert "Complex app created successfully" in result

    @patch("clappia_tools.client.app_management_client.AppManagementClient")
    def test_create_app_tool_validation_error(self, mock_client_class):
        """Test create_app with validation error"""
        # Setup mock to return validation error
        mock_client = Mock()
        mock_client.create_app.return_value = "Error: Invalid app_name - App name must be at least 3 characters"
        mock_client_class.return_value = mock_client

        sections = [{"sectionName": "Test", "fields": [{"fieldType": "singleLineText", "label": "Test Field"}]}]

        client = dummy_app_management_client()
        result = client.create_app(
            app_name="AB",  # Too short
            requesting_user_email_address="admin@example.com",
            sections=sections
        )
        
        assert "Error: Invalid app_name" in result

    @patch("clappia_tools.client.app_management_client.AppManagementClient")
    def test_create_app_tool_email_validation_error(self, mock_client_class):
        """Test create_app with invalid email"""
        # Setup mock to return email validation error
        mock_client = Mock()
        mock_client.create_app.return_value = "Error: requesting_user_email_address must be a valid email address"
        mock_client_class.return_value = mock_client

        sections = [{"sectionName": "Test Section", "fields": [{"fieldType": "singleLineText", "label": "Test Field"}]}]

        client = dummy_app_management_client()
        result = client.create_app(
            app_name="Valid App Name",
            requesting_user_email_address="invalid-email",
            sections=sections
        )
        
        assert "Error: requesting_user_email_address must be a valid email address" in result

    @patch("clappia_tools.client.app_management_client.AppManagementClient")
    def test_add_field_tool_formula_field(self, mock_client_class):
        """Test add_field with formula/calculation field"""
        # Setup mock
        mock_client = Mock()
        mock_client.add_field.return_value = "Success: Added calculation field CALC_FIELD"
        mock_client_class.return_value = mock_client

        # Call tool with calculation field
        client = dummy_app_management_client()
        result = client.add_field(
            app_id="MFX093412",
            requesting_user_email_address="admin@example.com",
            section_index=1,
            field_index=3,
            field_type="calculationsAndLogic",
            label="Total Salary",
            required=False,
            formula="base_salary + bonus",
            hidden=False
        )

        # Verify
        assert "Success: Added calculation field CALC_FIELD" in result

    @patch("clappia_tools.client.app_management_client.AppManagementClient")
    def test_add_field_tool_conditional_field(self, mock_client_class):
        """Test add_field with conditional display and editability"""
        # Setup mock
        mock_client = Mock()
        mock_client.add_field.return_value = "Success: Added conditional field COND_FIELD"
        mock_client_class.return_value = mock_client

        # Call tool with conditional field
        client = dummy_app_management_client()
        result = client.add_field(
            app_id="MFX093412",
            requesting_user_email_address="admin@example.com",
            section_index=0,
            field_index=5,
            field_type="singleLineText",
            label="Manager Name",
            required=False,
            display_condition="employment_type == 'Full-time'",
            is_editable=True,
            editability_condition="user_role == 'admin'",
            description="Enter manager name for full-time employees"
        )

        # Verify
        assert "Success: Added conditional field COND_FIELD" in result