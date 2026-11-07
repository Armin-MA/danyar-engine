"""Tests for strict JSON schema validator utility."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, Field

from src.utils.schema_validator import SchemaValidationError, validate_json_schema


class UserProfile(BaseModel):
    user_id: int
    name: str
    is_active: bool = True
    tags: list[str] = Field(default_factory=list)


class ComplexReport(BaseModel):
    report_id: str
    author: UserProfile
    score: float


class TestValidateJsonSchema:
    """Test suite for validate_json_schema function."""

    def test_happy_path_pure_json(self):
        """Test parsing and validating pure JSON string matching model."""
        raw_input = '{"user_id": 101, "name": "Sina", "is_active": true, "tags": ["admin", "lead"]}'
        result = validate_json_schema(raw_input, UserProfile)

        assert isinstance(result, UserProfile)
        assert result.user_id == 101
        assert result.name == "Sina"
        assert result.is_active is True
        assert result.tags == ["admin", "lead"]

    def test_code_fence_with_chatter(self):
        """Test JSON enclosed in ```json ... ``` with leading/trailing conversational filler."""
        raw_input = (
            "Greetings! Here is the user profile you requested:\n\n"
            "```json\n"
            "{\n"
            '  "user_id": 202,\n'
            '  "name": "Danyar",\n'
            '  "is_active": false,\n'
            '  "tags": ["ai", "mentor"]\n'
            "}\n"
            "```\n\n"
            "Let me know if you need any adjustments!"
        )
        result = validate_json_schema(raw_input, UserProfile)

        assert isinstance(result, UserProfile)
        assert result.user_id == 202
        assert result.name == "Danyar"
        assert result.is_active is False
        assert result.tags == ["ai", "mentor"]

    def test_generic_code_fence_without_language_specifier(self):
        """Test JSON enclosed in plain ``` ... ``` code fence."""
        raw_input = (
            "```\n"
            '{"user_id": 303, "name": "Maryam"}\n'
            "```"
        )
        result = validate_json_schema(raw_input, UserProfile)

        assert result.user_id == 303
        assert result.name == "Maryam"
        assert result.is_active is True
        assert result.tags == []

    def test_conversational_text_without_code_fences(self):
        """Test extraction when JSON object is embedded directly in conversational text."""
        raw_input = (
            "Sure! Based on the query, the result is "
            '{"user_id": 404, "name": "Reza", "is_active": true} '
            "which represents the requested entity."
        )
        result = validate_json_schema(raw_input, UserProfile)

        assert result.user_id == 404
        assert result.name == "Reza"

    def test_conversational_text_with_extraneous_curly_braces(self):
        """Test extraction when conversational text includes non-JSON curly braces."""
        raw_input = (
            "In response to request template {user_request}: "
            '{"user_id": 505, "name": "Ali"} '
            "with placeholder {extra_param} completed."
        )
        result = validate_json_schema(raw_input, UserProfile)

        assert result.user_id == 505
        assert result.name == "Ali"

    def test_nested_model_validation(self):
        """Test extraction and validation of nested Pydantic models."""
        raw_input = (
            "```json\n"
            "{\n"
            '  "report_id": "REP-999",\n'
            '  "author": {\n'
            '    "user_id": 777,\n'
            '    "name": "Sara",\n'
            '    "tags": ["reviewer"]\n'
            "  },\n"
            '  "score": 98.5\n'
            "}\n"
            "```"
        )
        result = validate_json_schema(raw_input, ComplexReport)

        assert isinstance(result, ComplexReport)
        assert result.report_id == "REP-999"
        assert result.author.user_id == 777
        assert result.author.name == "Sara"
        assert result.score == 98.5

    def test_missing_required_field_raises_error(self):
        """Test that missing required fields raise SchemaValidationError with diagnostic info."""
        raw_input = '{"name": "Incomplete User"}'  # user_id is required!

        with pytest.raises(SchemaValidationError) as exc_info:
            validate_json_schema(raw_input, UserProfile)

        error_message = str(exc_info.value)
        assert "Schema validation failed for UserProfile" in error_message
        assert "user_id" in error_message

    def test_invalid_field_type_raises_error(self):
        """Test that invalid field types raise SchemaValidationError."""
        raw_input = '{"user_id": "not-an-integer", "name": "TypeError User"}'

        with pytest.raises(SchemaValidationError) as exc_info:
            validate_json_schema(raw_input, UserProfile)

        error_message = str(exc_info.value)
        assert "Schema validation failed for UserProfile" in error_message
        assert "user_id" in error_message

    def test_malformed_json_syntax_raises_error(self):
        """Test that malformed JSON syntax raises SchemaValidationError."""
        raw_input = (
            "```json\n"
            '{"user_id": 100, "name": "Broken",\n'
            "```"
        )
        with pytest.raises(SchemaValidationError) as exc_info:
            validate_json_schema(raw_input, UserProfile)

        error_message = str(exc_info.value)
        assert "Malformed JSON" in error_message or "No valid JSON" in error_message

    def test_empty_string_raises_error(self):
        """Test that empty string raises SchemaValidationError."""
        with pytest.raises(SchemaValidationError) as exc_info:
            validate_json_schema("", UserProfile)

        assert "empty or contains only whitespace" in str(exc_info.value)

    def test_whitespace_string_raises_error(self):
        """Test that whitespace-only string raises SchemaValidationError."""
        with pytest.raises(SchemaValidationError) as exc_info:
            validate_json_schema("   \n\t  \r\n  ", UserProfile)

        assert "empty or contains only whitespace" in str(exc_info.value)

    def test_no_json_content_raises_error(self):
        """Test that conversational response with no JSON structure raises SchemaValidationError."""
        raw_input = "Hello! I am an AI assistant and I cannot find any data for this."
        with pytest.raises(SchemaValidationError) as exc_info:
            validate_json_schema(raw_input, UserProfile)

        assert "No JSON object or array found in response" in str(exc_info.value)

    def test_json_with_escaped_quotes_and_brackets(self):
        """Test JSON containing escaped characters, quotes, and brackets in string values."""
        raw_input = (
            '{"user_id": 888, "name": "Escaped \\"Quote\\" with {brackets} and [array]", "tags": []}'
        )
        result = validate_json_schema(raw_input, UserProfile)

        assert result.user_id == 888
        assert result.name == 'Escaped "Quote" with {brackets} and [array]'
