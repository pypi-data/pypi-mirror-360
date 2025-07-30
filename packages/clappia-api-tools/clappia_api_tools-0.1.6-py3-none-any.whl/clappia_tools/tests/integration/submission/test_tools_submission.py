from unittest.mock import patch, Mock
from clappia_tools.client.submission_client import SubmissionClient


def dummy_submission_client():
    """Helper function to create a dummy submission client for testing"""
    return SubmissionClient(
        api_key="dummy_api_key",
        base_url="https://api.clappia.com",
        workplace_id="dummy_workplace_id",
        timeout=30
    )

class Condition:
    def __init__(self, operator, filterKeyType, key, value):
        self.operator = operator
        self.filterKeyType = filterKeyType
        self.key = key
        self.value = value
    
    def to_dict(self):
        return {
            "operator": self.operator, 
            "filterKeyType": self.filterKeyType, 
            "key": self.key, 
            "value": self.value
        }


class Query:
    def __init__(self, conditions, operator=None):
        self.conditions = conditions
        self.operator = operator
    
    def to_dict(self):
        d = {"conditions": [c.to_dict() for c in self.conditions]}
        if self.operator:
            d["operator"] = self.operator
        return d


class QueryGroup:
    def __init__(self, queries):
        self.queries = queries
    
    def to_dict(self):
        return {"queries": [q.to_dict() for q in self.queries]}


class TestFilters:
    def __init__(self, queries):
        self.queries = queries
    
    def to_dict(self):
        return {"queries": [q.to_dict() for q in self.queries]}


class TestSubmissionToolsIntegration:
    """Test cases for SubmissionClient integration"""

    @patch("clappia_tools.client.submission_client.SubmissionClient")
    def test_create_submission_tool(self, mock_client_class):
        """Test create_submission with successful response"""
        # Setup mock
        mock_client = Mock()
        mock_client.create_submission.return_value = (
            "Success: Created submission TEST123"
        )
        mock_client_class.return_value = mock_client

        # Call tool
        client = dummy_submission_client()
        result = client.create_submission(
            "MFX093412",
            {"name": "Test User"},
            "test@example.com",
        )

        # Verify
        assert "Success: Created submission TEST123" in result
        mock_client.create_submission.assert_called_once_with(
            "MFX093412", {"name": "Test User"}, "test@example.com"
        )

    @patch("clappia_tools.client.submission_client.SubmissionClient")
    def test_create_submission_with_complex_data(self, mock_client_class):
        """Test create_submission with complex data structure"""
        # Setup mock
        mock_client = Mock()
        mock_client.create_submission.return_value = "Success: Created submission COMPLEX123"
        mock_client_class.return_value = mock_client

        # Call tool with complex data
        complex_data = {
            "employee_name": "John Doe",
            "department": "Engineering", 
            "salary": 75000,
            "start_date": "20-02-2025",
            "skills": ["Python", "JavaScript"],
            "is_manager": True
        }
        
        client = dummy_submission_client()
        result = client.create_submission("MFX093412", complex_data, "hr@example.com")

        assert "Success: Created submission COMPLEX123" in result
        mock_client.create_submission.assert_called_once_with("MFX093412", complex_data, "hr@example.com")

    @patch("clappia_tools.client.submission_client.SubmissionClient")
    def test_edit_submission_tool(self, mock_client_class):
        """Test edit_submission with successful response"""
        # Setup mock
        mock_client = Mock()
        mock_client.edit_submission.return_value = "Success: Edited submission TEST123"
        mock_client_class.return_value = mock_client

        # Call tool
        client = dummy_submission_client()
        result = client.edit_submission(
            "MFX093412",
            "HGO51464561",
            {"name": "Updated User"},
            "test@example.com",
        )

        # Verify
        assert "Success: Edited submission TEST123" in result
        mock_client.edit_submission.assert_called_once_with(
            "MFX093412", "HGO51464561", {"name": "Updated User"}, "test@example.com"
        )

    @patch("clappia_tools.client.submission_client.SubmissionClient")
    def test_edit_submission_partial_update(self, mock_client_class):
        """Test edit_submission with partial field updates"""
        # Setup mock
        mock_client = Mock()
        mock_client.edit_submission.return_value = "Success: Partially edited submission PARTIAL123"
        mock_client_class.return_value = mock_client

        # Call tool with partial update
        update_data = {"salary": 80000, "department": "Senior Engineering"}
        
        client = dummy_submission_client()
        result = client.edit_submission("MFX093412", "HGO51464561", update_data, "manager@example.com")

        assert "Success: Partially edited submission PARTIAL123" in result
        mock_client.edit_submission.assert_called_once_with(
            "MFX093412", "HGO51464561", update_data, "manager@example.com"
        )

    @patch("clappia_tools.client.submission_client.SubmissionClient")
    def test_update_submission_owners_tool(self, mock_client_class):
        """Test update_owners with successful response"""
        # Setup mock
        mock_client = Mock()
        mock_client.update_owners.return_value = (
            "Success: Updated submission owners for TEST123"
        )
        mock_client_class.return_value = mock_client

        # Call tool
        client = dummy_submission_client()
        result = client.update_owners(
            "MFX093412",
            "HGO51464561",
            "admin@example.com",
            ["user1@company.com", "user2@company.com"],
        )
        
        assert "Success: Updated submission owners for TEST123" in result
        mock_client.update_owners.assert_called_once_with(
            "MFX093412",
            "HGO51464561",
            "admin@example.com",
            ["user1@company.com", "user2@company.com"],
        )

    @patch("clappia_tools.client.submission_client.SubmissionClient")
    def test_update_submission_owners_multiple_users(self, mock_client_class):
        """Test update_owners with multiple users"""
        # Setup mock
        mock_client = Mock()
        mock_client.update_owners.return_value = "Success: Updated owners for 5 users"
        mock_client_class.return_value = mock_client

        # Call tool with multiple users
        email_list = [
            "user1@company.com", "user2@company.com", "user3@company.com",
            "manager@company.com", "admin@company.com"
        ]
        
        client = dummy_submission_client()
        result = client.update_owners("MFX093412", "HGO51464561", "admin@example.com", email_list)

        assert "Success: Updated owners for 5 users" in result
        mock_client.update_owners.assert_called_once_with(
            "MFX093412", "HGO51464561", "admin@example.com", email_list
        )

    @patch("clappia_tools.client.submission_client.SubmissionClient")
    def test_update_submission_status_tool(self, mock_client_class):
        """Test update_status with successful response"""
        # Setup mock
        mock_client = Mock()
        mock_client.update_status.return_value = (
            "Success: Updated submission status for TEST123"
        )
        mock_client_class.return_value = mock_client

        # Call tool
        client = dummy_submission_client()
        result = client.update_status(
            "MFX093412",
            "HGO51464561",
            "admin@example.com",
            "Approved",
            "Reviewed and approved by manager",
        )

        assert "Success: Updated submission status for TEST123" in result
        mock_client.update_status.assert_called_once_with(
            "MFX093412",
            "HGO51464561",
            "admin@example.com",
            "Approved",
            "Reviewed and approved by manager",
        )

    @patch("clappia_tools.client.submission_client.SubmissionClient")
    def test_update_submission_status_different_statuses(self, mock_client_class):
        """Test update_status with different status values"""
        # Setup mock
        mock_client = Mock()
        mock_client.update_status.return_value = "Success: Status updated to Pending"
        mock_client_class.return_value = mock_client

        # Test different status transitions
        status_transitions = [
            ("Pending", "Under review by team lead"),
            ("In Review", "Technical review in progress"),
            ("Rejected", "Missing required documentation"),
            ("Approved", "All criteria met")
        ]

        client = dummy_submission_client()
        
        for status, comment in status_transitions:
            result = client.update_status("MFX093412", "HGO51464561", "admin@example.com", status, comment)
            assert "Success: Status updated to Pending" in result
    
    @patch("clappia_tools.client.submission_client.SubmissionClient")
    def test_submission_error_handling(self, mock_client_class):
        """Test submission client error handling"""
        # Setup mock to return error
        mock_client = Mock()
        mock_client.create_submission.return_value = "Error: Invalid app_id format"
        mock_client_class.return_value = mock_client

        client = dummy_submission_client()
        result = client.create_submission("invalid-id", {"name": "Test"}, "test@example.com")
        
        assert "Error: Invalid app_id" in result
        mock_client.create_submission.assert_called_once_with("invalid-id", {"name": "Test"}, "test@example.com")