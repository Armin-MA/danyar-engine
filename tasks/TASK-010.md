# TASK-010: Implement Structured Context Compiler

## 1. Scope & Single Responsibility
- **Target File Path:** `src/mechanics/compile_structured_context.py`
- **Action Type:** Pure Function Implementation
- **Responsibility:** Compile sub-graph claims, dialectical tensions, and consensus into a high-density, pre-digested prompt package for SLM.
- **GitHub Issue:** #10
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `Pure Service Function`
- **Allowed Imports:** typing, src.entities.domain_entities, src.database.dto.graph_dtos
- **Forbidden Imports:** LLM network calls, UI formatting

## 3. Technical Contract
- **Input Parameters:**
  - subgraph: SubGraphDTO, user_context: ConditionEntity
- **Deterministic Output:**
  - compiled_context_str: str
- **Error Handling:**
  - Raise ValueError if subgraph is completely empty

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/mechanics/test_compile_structured_context.py`
- **Required Test Cases:**
  1. *Happy Path:* Outputs clean structured markdown context with consensus, opposing views, and conditions
  2. *Edge Case:* Formats gracefully when only one source exists without contradictions
  3. *Failure State:* Raises ValueError on null subgraph input

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(mechanics): implement compile_structured_context [TASK-010] (Closes #10)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
