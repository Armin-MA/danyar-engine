# TASK-007: Implement Atomic Claim Extraction Logic

## 1. Scope & Single Responsibility
- **Target File Path:** `src/mechanics/extract_atomic_claims.py`
- **Action Type:** Pure Function Implementation
- **Responsibility:** Orchestrate prompt generation and output parsing to extract core Claims, Concepts, and Conditions from text chunks.
- **GitHub Issue:** #7
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `src.contracts.engine_contracts.IExtractionPipeline`
- **Allowed Imports:** typing, src.entities.domain_entities, src.utils.schema_validator
- **Forbidden Imports:** Hardcoded LLM client instances, UI dependencies

## 3. Technical Contract
- **Input Parameters:**
  - source: SourceEntity, raw_chunk: str, llm_invoker: Callable[[str], str]
- **Deterministic Output:**
  - list[ClaimEntity] with attached conditions and concepts
- **Error Handling:**
  - Raise ExtractionError if LLM output fails schema validation after retries

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/mechanics/test_extract_atomic_claims.py`
- **Required Test Cases:**
  1. *Happy Path:* Extracts atomic claims and conditions correctly from a book chapter snippet
  2. *Edge Case:* Handles short paragraphs with zero claims by returning empty list without error
  3. *Failure State:* Raises ExtractionError on completely un-parseable LLM output

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(mechanics): implement extract_atomic_claims [TASK-007] (Closes #7)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
