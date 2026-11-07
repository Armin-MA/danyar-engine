# TASK-014: Implement Neo4j Annotation Repository

## 1. Scope & Single Responsibility
- **Target File Path:** `src/database/repositories/neo4j_annotation_repository.py`
- **Action Type:** Implement Repository Class
- **Responsibility:** Implement IAnnotationRepository to create, fetch, and attach UserNote nodes and dispute edges to claims.
- **GitHub Issue:** #14
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `src.contracts.engine_contracts.IAnnotationRepository`
- **Allowed Imports:** neo4j, typing, src.database.dto.graph_dtos
- **Forbidden Imports:** UI code, text normalizer mechanics

## 3. Technical Contract
- **Input Parameters:**
  - UserNoteDTO specifying target claim_id, content, and sentiment
- **Deterministic Output:**
  - Created UserNoteEntity with generated id and timestamp
- **Error Handling:**
  - Raise EntityNotFoundError if target claim_id does not exist

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/database/test_neo4j_annotation_repository.py`
- **Required Test Cases:**
  1. *Happy Path:* Attaches (:UserNote)-[:ANNOTATES]->(:Claim) successfully
  2. *Edge Case:* Creates [:DISPUTES] edge when user note disputes claim validity
  3. *Failure State:* Raises EntityNotFoundError when non-existent claim id is targeted

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(database): implement neo4j_annotation_repository [TASK-014] (Closes #14)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
