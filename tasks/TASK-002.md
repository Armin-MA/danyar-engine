# TASK-002: Implement Persian Text Normalizer

## 1. Scope & Single Responsibility
- **Target File Path:** `src/utils/text_normalizer.py`
- **Action Type:** Pure Function Implementation
- **Responsibility:** Normalize Persian text, unifying Arabic/Persian Ye/Kaf, zero-width non-joiners (ZWNJ), and whitespace.
- **GitHub Issue:** #2
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `None (Utility Layer)`
- **Allowed Imports:** re, unicodedata
- **Forbidden Imports:** External network calls, database models

## 3. Technical Contract
- **Input Parameters:**
  - raw_text: str
- **Deterministic Output:**
  - cleaned_text: str (clean, standardized Persian text)
- **Error Handling:**
  - Return empty string if input is None or whitespace

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/utils/test_text_normalizer.py`
- **Required Test Cases:**
  1. *Happy Path:* Converts 'ي' to 'ی' and 'ك' to 'ک' and standardizes ZWNJ in 'می رود' to 'می‌رود'
  2. *Edge Case:* Handles mixed English-Persian sentences and emoji characters without corruption
  3. *Failure State:* Returns empty string gracefully when input is empty string

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(utils): implement text_normalizer [TASK-002] (Closes #2)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
