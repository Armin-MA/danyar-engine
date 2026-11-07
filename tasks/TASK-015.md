# TASK-015: Implement Socratic Advisory Presenter

## 1. Scope & Single Responsibility
- **Target File Path:** `src/ui/presenters/socratic_presenter.py`
- **Action Type:** Pure Presenter Class
- **Responsibility:** Format structured SLM outputs into warm, professional Persian advisory messages with citations and contradiction badges.
- **GitHub Issue:** #15
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `None (Presenter Layer)`
- **Allowed Imports:** typing, src.entities.domain_entities
- **Forbidden Imports:** Database calls, HTTP request handlers

## 3. Technical Contract
- **Input Parameters:**
  - advisory_payload: dict, citations: list[SourceEntity]
- **Deterministic Output:**
  - formatted_markdown_response: str
- **Error Handling:**
  - Return fallback polite response if payload is empty

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/ui/test_socratic_presenter.py`
- **Required Test Cases:**
  1. *Happy Path:* Renders structured sections: اجماع بزرگان، نقاط تضاد، نسخه اختصاصی شما
  2. *Edge Case:* Properly links citations to source nodes with markdown footnotes
  3. *Failure State:* Handles empty citations gracefully without breaking text layout

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(ui): implement socratic_presenter [TASK-015] (Closes #15)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
