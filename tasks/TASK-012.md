# TASK-012: Implement Parameterized Cypher Statements

## 1. Scope & Single Responsibility
- **Target File Path:** `src/database/queries/cypher_statements.py`
- **Action Type:** Define Query Constants and Builders
- **Responsibility:** Provide clean, parameterized Cypher statements for ingestion, sub-graph traversal, vector index queries, and note attachment.
- **GitHub Issue:** #12
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `None (Query Definition Layer)`
- **Allowed Imports:** typing
- **Forbidden Imports:** Direct database driver execution, SQL queries

## 3. Technical Contract
- **Input Parameters:**
  - Query name and parameter keys
- **Deterministic Output:**
  - Parameterized Cypher query string templates (NEVER string formatted or interpolated)
- **Error Handling:**
  - Prohibit raw string interpolation to eliminate Cypher injection risks

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/database/test_cypher_statements.py`
- **Required Test Cases:**
  1. *Happy Path:* Provides parameterized MERGE statements for Claim and Source nodes
  2. *Edge Case:* Traversal query handles variable hop depth with bound parameter
  3. *Failure State:* Raises AssertionError if dynamic string interpolation is attempted

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(database): implement cypher_statements [TASK-012] (Closes #12)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
