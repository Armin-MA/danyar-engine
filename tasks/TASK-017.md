# TASK-017: Implement Web Dashboard UI with 3D Graph & Milkdown

## 1. Scope & Single Responsibility
- **Target File Path:** `src/ui/static/index.html`
- **Action Type:** Create HTML5/CSS/JS Single-Page Web Dashboard
- **Responsibility:** Deliver responsive Persian RTL UI with 3d-force-graph canvas, Milkdown markdown note editor, and chat panel.
- **GitHub Issue:** #17
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `HTML5, WebGL, Milkdown JS, 3d-force-graph JS`
- **Allowed Imports:** HTML5, CSS3, vanilla JS or lightweight bundle, CDN for 3d-force-graph and Milkdown
- **Forbidden Imports:** Heavy complex framework dependencies (keep it lightweight and bug-free)

## 3. Technical Contract
- **Input Parameters:**
  - Browser user interaction (clicks, drags, chat typing, note edits)
- **Deterministic Output:**
  - Interactive 3D graph visualization and instant card editor
- **Error Handling:**
  - Console error logging and polite user notifications on network failure

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/ui/test_static_assets.py`
- **Required Test Cases:**
  1. *Happy Path:* Renders 3D force-directed graph with neon nodes and opens Milkdown editor on node click
  2. *Edge Case:* RTL layout properly aligns Persian text, bolding, and bullet lists
  3. *Failure State:* Shows reconnection banner if backend API is temporarily offline

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(ui): implement web_dashboard [TASK-017] (Closes #17)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
