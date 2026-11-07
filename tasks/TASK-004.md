# TASK-004: Implement Pure Domain Entities

## 1. Scope & Single Responsibility
- **Target File Path:** `src/entities/domain_entities.py`
- **Action Type:** Define Domain Data Classes
- **Responsibility:** Define pure state-holding domain entities: Source, Author, Claim, Condition, Outcome, UserNote, SynthesisResult.
- **GitHub Issue:** #4
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `None (Domain Entity Layer)`
- **Allowed Imports:** dataclasses, typing, datetime
- **Forbidden Imports:** Pydantic (optional, prefer pure dataclasses), database ORM, UI libraries

## 3. Technical Contract
- **Input Parameters:**
  - Entity field attributes with strict type hints
- **Deterministic Output:**
  - Instantiated immutable domain entities
- **Error Handling:**
  - Raise TypeError on missing required entity fields

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/entities/test_domain_entities.py`
- **Required Test Cases:**
  1. *Happy Path:* Instantiates ClaimEntity with id, statement, type, and confidence_score
  2. *Edge Case:* UserNoteEntity handles optional sentiment and custom tags
  3. *Failure State:* Raises TypeError when mandatory id or statement is omitted

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(entities): implement domain_entities [TASK-004] (Closes #4)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
