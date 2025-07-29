from unittest.mock import patch, Mock
from clappia_tools.client.base_client import BaseClappiaClient
from clappia_tools.client.submission_client import SubmissionClient
from clappia_tools.client.app_definition_client import AppDefinitionClient
from clappia_tools.client.clappia_client import ClappiaClient


class TestBaseClappiaClient:
    """Test cases for BaseClappiaClient"""

    @patch('clappia_tools._utils.api_utils.ClappiaAPIUtils')
    def test_init_with_defaults(self, mock_api_utils):
        """Test BaseClappiaClient initialization with default parameters"""
        client = BaseClappiaClient()
        assert client.api_utils is not None
        mock_api_utils.assert_called_once_with(None, None, None, 30)

    @patch('clappia_tools._utils.api_utils.ClappiaAPIUtils')
    def test_init_with_custom_params(self, mock_api_utils):
        """Test BaseClappiaClient initialization with custom parameters"""
        client = BaseClappiaClient(
            api_key="test_key",
            base_url="https://test.com",
            workplace_id="TEST123",
            timeout=60,
        )
        assert client.api_utils is not None
        mock_api_utils.assert_called_once_with("test_key", "https://test.com", "TEST123", 60)


class TestSubmissionClient:
    """Test cases for SubmissionClient"""

    def test_create_submission_validation_error(self):
        """Test create_submission with invalid app_id"""
        client = SubmissionClient()
        result = client.create_submission("invalid-id", {}, "test@example.com")
        assert "Error: Invalid app_id" in result

    def test_create_submission_empty_email(self):
        """Test create_submission with empty email"""
        client = SubmissionClient()
        result = client.create_submission("MFX093412", {"test": "data"}, "")
        assert "Error: email is required" in result

    def test_create_submission_invalid_email(self):
        """Test create_submission with invalid email format"""
        client = SubmissionClient()
        result = client.create_submission(
            "MFX093412", {"test": "data"}, "invalid-email"
        )
        assert "Error: email must be a valid email address" in result

    def test_create_submission_empty_data(self):
        """Test create_submission with empty data"""
        client = SubmissionClient()
        result = client.create_submission("MFX093412", {}, "test@example.com")
        assert "Error: data cannot be empty" in result

    def test_create_submission_invalid_data_type(self):
        """Test create_submission with non-dictionary data"""
        client = SubmissionClient()
        result = client.create_submission("MFX093412", "invalid", "test@example.com")
        assert "Error: data must be a dictionary" in result

    @patch("clappia_tools._utils.api_utils.ClappiaAPIUtils.make_request")
    def test_create_submission_success(self, mock_request):
        """Test successful create_submission"""
        # Mock successful API response
        mock_request.return_value = (True, None, {"submissionId": "TEST123"})

        client = SubmissionClient(
            api_key="test_key",
            base_url="https://test.com",
            workplace_id="TEST123",
            timeout=60
        )
        result = client.create_submission(
            "MFX093412", {"name": "Test User"}, "test@example.com"
        )

        assert "Successfully created submission" in result
        assert "TEST123" in result
        mock_request.assert_called_once()

    @patch("clappia_tools._utils.api_utils.ClappiaAPIUtils.make_request")
    def test_create_submission_api_error(self, mock_request):
        """Test create_submission with API error"""
        # Mock API error response
        mock_request.return_value = (False, "API Error: Invalid request", None)

        client = SubmissionClient(
            api_key="test_key",
            base_url="https://test.com",
            workplace_id="TEST123",
            timeout=60
        )
        result = client.create_submission(
            "MFX093412", {"name": "Test User"}, "test@example.com"
        )

        assert "Error: API Error: Invalid request" in result

    def test_edit_submission_invalid_submission_id(self):
        """Test edit_submission with invalid submission ID"""
        client = SubmissionClient()
        result = client.edit_submission(
            "MFX093412", "invalid-id", {"name": "Updated"}, "test@example.com"
        )
        assert "Error: Invalid submission_id" in result


class TestAppDefinitionClient:
    """Test cases for AppDefinitionClient"""

    def test_get_definition_invalid_app_id(self):
        """Test get_definition with invalid app_id"""
        client = AppDefinitionClient()
        result = client.get_definition("invalid-app-id")
        assert "Error: Invalid app_id" in result

    @patch("clappia_tools._utils.api_utils.ClappiaAPIUtils.make_request")
    def test_get_definition_success(self, mock_request):
        """Test successful get_definition"""
        mock_response = {
            "appId": "MFX093412",
            "version": "1.0",
            "state": "active",
            "pageIds": ["page1", "page2"],
            "sectionIds": ["section1"],
            "fieldDefinitions": {"field1": {}, "field2": {}},
            "metadata": {"sectionName": "Test App", "description": "Test Description"}
        }
        mock_request.return_value = (True, None, mock_response)

        client = AppDefinitionClient()
        result = client.get_definition("MFX093412")

        assert "Successfully retrieved app definition" in result
        assert "MFX093412" in result
        mock_request.assert_called_once()