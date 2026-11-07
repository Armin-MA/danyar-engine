# TASK-003: Implement Strict JSON Schema Validator

## 1. Scope & Single Responsibility
- **Target File Path:** `src/utils/schema_validator.py`
- **Action Type:** Pure Function Implementation
- **Responsibility:** Extract and validate JSON schema from raw LLM markdown blocks, guaranteeing structure compliance.
- **GitHub Issue:** #3
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `None (Utility Layer)`
- **Allowed Imports:** json, re, typing, pydantic
- **Forbidden Imports:** External network calls, direct LLM SDK calls

## 3. Technical Contract
- **Input Parameters:**
  - raw_response: str, expected_model: type[BaseModel]
- **Deterministic Output:**
  - Validated Pydantic instance of expected_model
- **Error Handling:**
  - Raise SchemaValidationError with detailed path on invalid JSON or missing fields

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/utils/test_schema_validator.py`
- **Required Test Cases:**
  1. *Happy Path:* Parses JSON enclosed in markdown code fences '`json ... `' into valid model
  2. *Edge Case:* Handles leading/trailing non-json conversational text from LLMs
  3. *Failure State:* Raises SchemaValidationError when required schema fields are missing

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(utils): implement schema_validator [TASK-003] (Closes #3)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
