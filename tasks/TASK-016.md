# TASK-016: Implement FastAPI API Routers

## 1. Scope & Single Responsibility
- **Target File Path:** `src/ui/api/routes.py`
- **Action Type:** Define FastAPI Routers
- **Responsibility:** Expose REST endpoints for chat (/api/chat), ingestion (/api/ingest), graph traversal (/api/graph), and notes (/api/notes).
- **GitHub Issue:** #16
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `FastAPI APIRouter`
- **Allowed Imports:** fastapi, pydantic, src.core.orchestrator, src.database.dto
- **Forbidden Imports:** Direct Cypher queries inside route handlers

## 3. Technical Contract
- **Input Parameters:**
  - HTTP POST/GET requests with validated Pydantic bodies
- **Deterministic Output:**
  - JSON responses with HTTP 200/201/400/500 status codes
- **Error Handling:**
  - FastAPI HTTPException with clear error details

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/ui/test_routes.py`
- **Required Test Cases:**
  1. *Happy Path:* POST /api/chat returns advisory message and matched subgraph IDs
  2. *Edge Case:* POST /api/notes/annotate successfully creates user note and returns 201
  3. *Failure State:* Returns 422 Unprocessable Entity on invalid request body

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(ui): implement routes [TASK-016] (Closes #16)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
