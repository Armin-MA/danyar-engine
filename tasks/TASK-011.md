# TASK-011: Define Graph Data Transfer Objects

## 1. Scope & Single Responsibility
- **Target File Path:** `src/database/dto/graph_dtos.py`
- **Action Type:** Define DTO Classes
- **Responsibility:** Define ClaimIngestDTO, SubGraphDTO, UserNoteDTO, and NodeNeighborDTO crossing repository boundaries.
- **GitHub Issue:** #11
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `None (DTO Layer)`
- **Allowed Imports:** pydantic or dataclasses, typing
- **Forbidden Imports:** Neo4j driver objects, UI widgets

## 3. Technical Contract
- **Input Parameters:**
  - Structured graph node and edge dictionaries
- **Deterministic Output:**
  - Immutable validated DTO instances
- **Error Handling:**
  - Raise ValidationError on malformed graph dictionary

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/database/test_graph_dtos.py`
- **Required Test Cases:**
  1. *Happy Path:* Instantiates SubGraphDTO with nodes and edges lists
  2. *Edge Case:* Serializes cleanly to JSON dictionary for API responses
  3. *Failure State:* Raises ValidationError when node id is missing

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(database): define graph_dtos [TASK-011] (Closes #11)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
