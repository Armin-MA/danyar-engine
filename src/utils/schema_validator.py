"""Strict JSON Schema Validator for LLM textual responses.

Guarantees structure compliance and deterministic extraction from LLM outputs
surrounded by markdown blocks, conversational filler, or whitespace.
"""

from __future__ import annotations

import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class SchemaValidationError(Exception):
    """Raised when JSON schema extraction or validation fails."""

    pass


def _extract_balanced_json_substrings(text: str) -> list[str]:
    """Scan string for balanced JSON objects {...} and arrays [...]."""
    candidates: list[str] = []
    seen: set[str] = set()
    n = len(text)

    for start_idx in range(n):
        char = text[start_idx]
        if char not in ("{", "["):
            continue

        stack = [char]
        in_string = False
        escape = False

        for idx in range(start_idx + 1, n):
            c = text[idx]
            if escape:
                escape = False
                continue
            if c == "\\":
                if in_string:
                    escape = True
                continue
            if c == '"':
                in_string = not in_string
                continue
            if not in_string:
                if c in ("{", "["):
                    stack.append(c)
                elif c == "}":
                    if stack and stack[-1] == "{":
                        stack.pop()
                    else:
                        break
                elif c == "]":
                    if stack and stack[-1] == "[":
                        stack.pop()
                    else:
                        break

                if not stack:
                    candidate = text[start_idx : idx + 1].strip()
                    if candidate and candidate not in seen:
                        seen.add(candidate)
                        candidates.append(candidate)
                    break

    return candidates


def _collect_json_candidates(raw_response: str) -> list[str]:
    """Collect potential JSON string candidates from raw response in priority order."""
    candidates: list[str] = []
    seen: set[str] = set()

    def add_candidate(s: str) -> None:
        s_clean = s.strip()
        if s_clean and s_clean not in seen:
            seen.add(s_clean)
            candidates.append(s_clean)

    trimmed = raw_response.strip()

    # 1. If trimmed text starts and ends like JSON, prioritize it
    if (trimmed.startswith("{") and trimmed.endswith("}")) or (
        trimmed.startswith("[") and trimmed.endswith("]")
    ):
        add_candidate(trimmed)

    # 2. Extract from markdown code fences (```json ... ``` or ``` ... ```)
    fence_pattern = re.compile(
        r"```(?:[a-zA-Z0-9_\-\+]+)?\s*([\s\S]*?)\s*```", re.MULTILINE
    )
    code_blocks = fence_pattern.findall(raw_response)
    for block in code_blocks:
        add_candidate(block)
        for sub in _extract_balanced_json_substrings(block):
            add_candidate(sub)

    # 3. Extract balanced objects from the entire raw_response
    for sub in _extract_balanced_json_substrings(raw_response):
        add_candidate(sub)

    return candidates


def _format_validation_error(model_cls: type[Any], err: ValidationError) -> str:
    """Format Pydantic ValidationError into an informative diagnostic message."""
    details: list[str] = []
    for error in err.errors():
        loc = ".".join(str(item) for item in error.get("loc", []))
        msg = error.get("msg", "Validation error")
        if loc:
            details.append(f"{loc}: {msg}")
        else:
            details.append(msg)
    joined_details = "; ".join(details)
    model_name = getattr(model_cls, "__name__", str(model_cls))
    return f"Schema validation failed for {model_name}: {joined_details}"


def validate_json_schema(raw_response: str, expected_model: type[T]) -> T:
    """Extract and validate JSON schema from raw LLM textual responses.

    Args:
        raw_response: Raw string response received from LLM, possibly containing
                      markdown fences or conversational filler.
        expected_model: Target Pydantic model class to validate against.

    Returns:
        Validated instance of expected_model.

    Raises:
        SchemaValidationError: If response is empty, contains malformed JSON,
                               or fails Pydantic schema validation.
    """
    if not isinstance(raw_response, str) or not raw_response.strip():
        raise SchemaValidationError("Raw response is empty or contains only whitespace.")

    candidates = _collect_json_candidates(raw_response)

    if not candidates:
        raise SchemaValidationError(
            "No JSON object or array found in response."
        )

    last_json_error: json.JSONDecodeError | None = None
    last_validation_error: ValidationError | None = None
    parsed_candidates: list[tuple[str, Any]] = []

    # First pass: identify candidates that are valid JSON
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            parsed_candidates.append((candidate, parsed))
        except json.JSONDecodeError as err:
            if last_json_error is None:
                last_json_error = err

    # If no candidate could be parsed as JSON:
    if not parsed_candidates:
        if last_json_error is not None:
            raise SchemaValidationError(
                f"Malformed JSON in response: {last_json_error}"
            ) from last_json_error
        raise SchemaValidationError(
            "No valid JSON object or array could be extracted from response."
        )

    # Second pass: validate against expected_model
    for _, parsed_data in parsed_candidates:
        try:
            if hasattr(expected_model, "model_validate"):
                return expected_model.model_validate(parsed_data)
            elif hasattr(expected_model, "parse_obj"):
                return expected_model.parse_obj(parsed_data)
            elif callable(expected_model):
                if isinstance(parsed_data, dict):
                    return expected_model(**parsed_data)
                return expected_model(parsed_data)
            else:
                raise SchemaValidationError(
                    f"Provided expected_model {expected_model} is not a valid Pydantic model."
                )
        except ValidationError as err:
            last_validation_error = err
        except TypeError as err:
            raise SchemaValidationError(
                f"Type error while instantiating {getattr(expected_model, '__name__', str(expected_model))}: {err}"
            ) from err

    # Valid JSON was extracted, but failed schema validation
    if last_validation_error is not None:
        formatted = _format_validation_error(expected_model, last_validation_error)
        raise SchemaValidationError(formatted) from last_validation_error

    raise SchemaValidationError(
        f"Failed to validate response against {getattr(expected_model, '__name__', str(expected_model))}."
    )
