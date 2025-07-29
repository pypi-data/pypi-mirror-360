from clappia_tools._utils.validators import ClappiaInputValidator
from clappia_tools._models.model import Section, Field


class TestClappiaInputValidator:
    """Test cases for ClappiaInputValidator"""

    def test_validate_email_valid(self):
        """Test validate_email with valid email addresses"""
        assert ClappiaInputValidator.validate_email("test@example.com") == True
        assert ClappiaInputValidator.validate_email("user.name+tag@domain.co.uk") == True
        assert ClappiaInputValidator.validate_email("user123@test-domain.org") == True
        assert ClappiaInputValidator.validate_email("simple@test.io") == True

    def test_validate_email_invalid(self):
        """Test validate_email with invalid email addresses"""
        assert ClappiaInputValidator.validate_email("invalid-email") == False
        assert ClappiaInputValidator.validate_email("@domain.com") == False
        assert ClappiaInputValidator.validate_email("user@") == False
        assert ClappiaInputValidator.validate_email("user@domain") == False
        assert ClappiaInputValidator.validate_email("") == False
        assert ClappiaInputValidator.validate_email(None) == False
        assert ClappiaInputValidator.validate_email("   ") == False
        assert ClappiaInputValidator.validate_email("user space@domain.com") == False

    def test_validate_app_id_valid(self):
        """Test validate_app_id with valid app IDs"""
        is_valid, error = ClappiaInputValidator.validate_app_id("MFX093412")
        assert is_valid == True
        assert error == ""

        is_valid, error = ClappiaInputValidator.validate_app_id("APP123")
        assert is_valid == True
        assert error == ""

        is_valid, error = ClappiaInputValidator.validate_app_id("TEST001")
        assert is_valid == True
        assert error == ""

    def test_validate_app_id_invalid(self):
        """Test validate_app_id with invalid app IDs"""
        is_valid, error = ClappiaInputValidator.validate_app_id("invalid-id")
        assert is_valid == False
        assert "uppercase letters and numbers" in error

        is_valid, error = ClappiaInputValidator.validate_app_id("app123")
        assert is_valid == False
        assert "uppercase letters and numbers" in error

        is_valid, error = ClappiaInputValidator.validate_app_id("")
        assert is_valid == False
        assert "required and cannot be empty" in error

        is_valid, error = ClappiaInputValidator.validate_app_id(None)
        assert is_valid == False
        assert "required and cannot be empty" in error

        is_valid, error = ClappiaInputValidator.validate_app_id("   ")
        assert is_valid == False
        assert "required and cannot be empty" in error

    def test_validate_submission_id_valid(self):
        """Test validate_submission_id with valid submission IDs"""
        is_valid, error = ClappiaInputValidator.validate_submission_id("HGO51464561")
        assert is_valid == True
        assert error == ""

        is_valid, error = ClappiaInputValidator.validate_submission_id("SUB123456")
        assert is_valid == True
        assert error == ""

    def test_validate_submission_id_invalid(self):
        """Test validate_submission_id with invalid submission IDs"""
        is_valid, error = ClappiaInputValidator.validate_submission_id("invalid-id")
        assert is_valid == False
        assert "uppercase letters and numbers" in error

        is_valid, error = ClappiaInputValidator.validate_submission_id("")
        assert is_valid == False
        assert "required and cannot be empty" in error

        is_valid, error = ClappiaInputValidator.validate_submission_id(None)
        assert is_valid == False
        assert "required and cannot be empty" in error

    def test_validate_app_name_valid(self):
        """Test validate_app_name with valid app names"""
        is_valid, error = ClappiaInputValidator.validate_app_name("Employee Survey")
        assert is_valid == True
        assert error == ""

        is_valid, error = ClappiaInputValidator.validate_app_name("Test App")
        assert is_valid == True
        assert error == ""

    def test_validate_app_name_invalid(self):
        """Test validate_app_name with invalid app names"""
        is_valid, error = ClappiaInputValidator.validate_app_name("")
        assert is_valid == False
        assert "required and cannot be empty" in error

        is_valid, error = ClappiaInputValidator.validate_app_name("AB")
        assert is_valid == False
        assert "at least 3 characters" in error

        is_valid, error = ClappiaInputValidator.validate_app_name("   ")
        assert is_valid == False
        assert "required and cannot be empty" in error

    def test_validate_email_list_valid(self):
        """Test validate_email_list with valid email lists"""
        is_valid, msg, valid_emails = ClappiaInputValidator.validate_email_list([
            "user1@test.com", "user2@test.com"
        ])
        assert is_valid == True
        assert msg == ""
        assert len(valid_emails) == 2
        assert "user1@test.com" in valid_emails
        assert "user2@test.com" in valid_emails

    def test_validate_email_list_mixed_valid_invalid(self):
        """Test validate_email_list with mixed valid/invalid emails"""
        is_valid, msg, valid_emails = ClappiaInputValidator.validate_email_list([
            "user1@test.com", "invalid-email", "user2@test.com"
        ])
        assert is_valid == True
        assert "Some emails were invalid" in msg
        assert len(valid_emails) == 2
        assert "invalid-email" in msg

    def test_validate_email_list_all_invalid(self):
        """Test validate_email_list with all invalid emails"""
        is_valid, msg, valid_emails = ClappiaInputValidator.validate_email_list([
            "invalid1", "invalid2"
        ])
        assert is_valid == False
        assert "No valid email addresses found" in msg
        assert len(valid_emails) == 0

    def test_validate_email_list_empty(self):
        """Test validate_email_list with empty list"""
        is_valid, msg, valid_emails = ClappiaInputValidator.validate_email_list([])
        assert is_valid == False
        assert "cannot be empty" in msg
        assert len(valid_emails) == 0

    def test_validate_email_list_not_list(self):
        """Test validate_email_list with non-list input"""
        is_valid, msg, valid_emails = ClappiaInputValidator.validate_email_list("not-a-list")
        assert is_valid == False
        assert "must be a list" in msg
        assert len(valid_emails) == 0

    def test_validate_app_structure_valid(self):
        """Test validate_app_structure with valid structure"""
        field1 = Field(fieldType="singleLineText", label="Name")
        field2 = Field(fieldType="multiLineText", label="Description")
        section1 = Section(sectionName="Personal Info", fields=[field1, field2])
        
        is_valid, error = ClappiaInputValidator.validate_app_structure([section1])
        assert is_valid == True
        assert error == ""

    def test_validate_app_structure_empty_sections(self):
        """Test validate_app_structure with empty sections"""
        is_valid, error = ClappiaInputValidator.validate_app_structure([])
        assert is_valid == False
        assert "non-empty list" in error

    def test_validate_app_structure_invalid_field_type(self):
        """Test validate_app_structure with invalid field type"""
        field1 = Field(fieldType="counter", label="Counter")  # Not allowed in create_app
        section1 = Section(sectionName="Test Section", fields=[field1])
        
        is_valid, error = ClappiaInputValidator.validate_app_structure([section1])
        assert is_valid == False
        assert "Invalid field type" in error
