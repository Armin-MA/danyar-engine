# TASK-001: Implement App, LLM & Neo4j Config

## 1. Scope & Single Responsibility
- **Target File Path:** `src/config/app_config.py`
- **Action Type:** Define Configuration Data Classes
- **Responsibility:** Read and validate environment variables for Neo4j URI/auth and Frontier/SLM API keys with safe defaults.
- **GitHub Issue:** #1
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `None (Base Config Layer)`
- **Allowed Imports:** os, typing, pydantic_settings or dataclasses
- **Forbidden Imports:** UI frameworks, database drivers, LLM SDK network calls

## 3. Technical Contract
- **Input Parameters:**
  - Environment variables (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, GEMINI_API_KEY)
- **Deterministic Output:**
  - Immutable AppConfig instance with typed sub-configs
- **Error Handling:**
  - Raise ValueError on missing required production credentials

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/config/test_app_config.py`
- **Required Test Cases:**
  1. *Happy Path:* Loads valid config object when env variables are populated
  2. *Edge Case:* Applies localhost defaults when optional env vars are omitted in development
  3. *Failure State:* Raises ValueError with clear message if NEO4J_PASSWORD is empty in strict mode

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(config): implement app_config [TASK-001] (Closes #1)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
