import re
from typing import Tuple, List
from clappia_tools._models.model import Section

class ClappiaInputValidator:
    """Validates user inputs like app IDs, emails, etc."""

    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    APP_ID_PATTERN = r"^[A-Z0-9]+$"
    SUBMISSION_ID_PATTERN = r"^[A-Z0-9]+$"

    @staticmethod
    def validate_app_name(app_name: str) -> Tuple[bool, str]:
        if not app_name or not app_name.strip():
            return False, "App name is required and cannot be empty"
        if len(app_name.strip()) < 3:
            return False, "App name must be at least 3 characters long"
        return True, ""

    @staticmethod
    def validate_email(email: str) -> bool:
        if not email or not email.strip():
            return False
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email.strip()):
            return False
        return True

    @staticmethod
    def validate_app_structure(sections: List[Section]) -> Tuple[bool, str]:
        create_app_field_types = [
            "singleLineText",
            "multiLineText",
            "singleSelector",
            "multiSelector",
            "dropDown",
            "dateSelector",
            "timeSelector",
            "phoneNumber"  
        ]
        options_field_types = [
            "singleSelector",
            "multiSelector",
            "dropDown"
        ]
        
        if not sections or not isinstance(sections, list):
            return False, "Sections must be a non-empty list"
        for section in sections:
            if not section.sectionName or not section.sectionName.strip():
                return False, "Section name is required and cannot be empty"
            if not section.fields or not isinstance(section.fields, list):
                return False, f"Section '{section.sectionName}' must have a non-empty list of fields with fieldType, label and options (optional) as keys and fieldType must be one of {create_app_field_types} and options must be a list of strings if fieldType is one of {options_field_types}"
            for field in section.fields:
                if field.fieldType not in create_app_field_types:
                    return False, f"Invalid field type '{field.fieldType}' in section '{section.sectionName}, allowed field types are {create_app_field_types}"
                if not field.label or not field.label.strip():
                    return False, f"Field label is required in section '{section.sectionName}'"
        return True, ""

    @staticmethod
    def validate_email_list(email_ids: List[str]) -> Tuple[bool, str, List[str]]:
        """Validate a list of email addresses and return valid ones"""
        if not isinstance(email_ids, list):
            return False, "email_ids must be a list", []

        if not email_ids:
            return False, "email_ids cannot be empty", []

        valid_emails = []
        invalid_emails = []

        for email in email_ids:
            if not isinstance(email, str):
                invalid_emails.append(str(email))
                continue

            if ClappiaInputValidator.validate_email(email.strip()):
                valid_emails.append(email.strip())
            else:
                invalid_emails.append(email)

        if not valid_emails:
            return (
                False,
                f"No valid email addresses found. Invalid emails: {invalid_emails}",
                [],
            )

        if invalid_emails:
            return (
                True,
                f"Some emails were invalid and skipped: {invalid_emails}",
                valid_emails,
            )

        return True, "", valid_emails

    @staticmethod
    def validate_app_id(app_id: str) -> Tuple[bool, str]:
        """Validate Clappia app ID format"""
        if not app_id or not isinstance(app_id, str) or not app_id.strip():
            return False, "App ID is required and cannot be empty"

        if not re.match(ClappiaInputValidator.APP_ID_PATTERN, app_id.strip()):
            return False, "App ID must contain only uppercase letters and numbers"

        return True, ""

    @staticmethod
    def validate_submission_id(submission_id: str) -> Tuple[bool, str]:
        """Validate Clappia submission ID format"""
        if (
            not submission_id
            or not isinstance(submission_id, str)
            or not submission_id.strip()
        ):
            return False, "Submission ID is required and cannot be empty"

        if not re.match(
            ClappiaInputValidator.SUBMISSION_ID_PATTERN, submission_id.strip()
        ):
            return (
                False,
                "Submission ID must contain only uppercase letters and numbers",
            )

        return True, ""
