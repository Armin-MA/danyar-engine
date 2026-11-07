# TASK-006: Implement Dynamic Credibility Calculator

## 1. Scope & Single Responsibility
- **Target File Path:** `src/mechanics/calculate_dynamic_credibility.py`
- **Action Type:** Pure Function Implementation
- **Responsibility:** Compute FitScore and effective weight of a Claim based on author base reputation, condition match, and human feedback.
- **GitHub Issue:** #6
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `src.contracts.engine_contracts.ICredibilityCalculator`
- **Allowed Imports:** typing, src.entities.domain_entities
- **Forbidden Imports:** Network calls, database queries, global state mutations

## 3. Technical Contract
- **Input Parameters:**
  - claim: ClaimEntity, user_context: ConditionEntity, human_modifier: float = 1.0
- **Deterministic Output:**
  - effective_score: float (normalized between 0.0 and 1.0)
- **Error Handling:**
  - Raise ValueError if base weight or modifier is outside valid range [0.0, 10.0]

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/mechanics/test_calculate_dynamic_credibility.py`
- **Required Test Cases:**
  1. *Happy Path:* Calculates higher score when user context matches claim condition perfectly
  2. *Edge Case:* Defaults to base author reputation when user context is empty/unspecified
  3. *Failure State:* Raises ValueError if negative human_modifier is provided

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(mechanics): implement calculate_dynamic_credibility [TASK-006] (Closes #6)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
