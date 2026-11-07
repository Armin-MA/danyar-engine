# TASK-009: Implement Socratic Diagnostic Formulator

## 1. Scope & Single Responsibility
- **Target File Path:** `src/mechanics/formulate_socratic_inquiry.py`
- **Action Type:** Pure Function Implementation
- **Responsibility:** Analyze user question against graph sub-conditions; if context is missing, generate up to 2 diagnostic clarifying questions.
- **GitHub Issue:** #9
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `src.contracts.engine_contracts.ISocraticAdvisor`
- **Allowed Imports:** typing, src.entities.domain_entities
- **Forbidden Imports:** UI rendering code, database queries

## 3. Technical Contract
- **Input Parameters:**
  - user_query: str, matched_conditions: list[ConditionEntity]
- **Deterministic Output:**
  - tuple[bool, list[str]] (is_sufficient, diagnostic_questions)
- **Error Handling:**
  - Return is_sufficient=True if no opposing conditions exist

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/mechanics/test_formulate_socratic_inquiry.py`
- **Required Test Cases:**
  1. *Happy Path:* Generates 2 clarifying questions when query lacks company size and market phase
  2. *Edge Case:* Returns is_sufficient=True when query already explicitly specifies constraints
  3. *Failure State:* Returns graceful default question if condition list contains malformed entries

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(mechanics): implement formulate_socratic_inquiry [TASK-009] (Closes #9)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
