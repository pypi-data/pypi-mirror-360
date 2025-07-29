from unittest.mock import patch, Mock
from clappia_tools.client.app_definition_client import AppDefinitionClient
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

def dummy_submission_client():
    """Helper function to create a dummy submission client for testing"""
    return SubmissionClient(
        api_key="dummy_api_key",
        base_url="https://api.clappia.com",
        workplace_id="dummy_workplace_id",
        timeout=30
    )


class TestDefinitionToolsIntegration:
    """Test cases for App Definition tools"""

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