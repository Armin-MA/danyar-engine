# TASK-018: Implement System IoC Container & Bootstrap Orchestrator

## 1. Scope & Single Responsibility
- **Target File Path:** `src/core/orchestrator.py`
- **Action Type:** Implement Bootstrap Container Class
- **Responsibility:** Wire all contracts to concrete implementations, initialize Neo4j connection pool, and bootstrap the FastAPI app.
- **GitHub Issue:** #18
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `None (Core Orchestrator)`
- **Allowed Imports:** typing, src.config, src.contracts, src.database, src.mechanics, src.ui
- **Forbidden Imports:** Hardcoded credentials (must load from AppConfig)

## 3. Technical Contract
- **Input Parameters:**
  - AppConfig instance
- **Deterministic Output:**
  - Fully wired, ready-to-serve FastAPI application instance
- **Error Handling:**
  - Raise BootError if Neo4j connection or LLM client fails health check

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/core/test_orchestrator.py`
- **Required Test Cases:**
  1. *Happy Path:* Bootstraps system cleanly and verifies all repository bindings
  2. *Edge Case:* Provides graceful shutdown hook to close Neo4j connection pool
  3. *Failure State:* Raises BootError with clear diagnosis when Neo4j is unreachable

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(core): implement orchestrator [TASK-018] (Closes #18)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
