# TASK-005: Define Abstract Layer Contracts

## 1. Scope & Single Responsibility
- **Target File Path:** `src/contracts/engine_contracts.py`
- **Action Type:** Define Abstract Base Classes
- **Responsibility:** Define IExtractionPipeline, IDialecticalSynthesizer, ICredibilityCalculator, ISocraticAdvisor, IGraphRepository, IAnnotationRepository.
- **GitHub Issue:** #5
- **Milestone:** Milestone 4: Core Implementation & Verification

## 2. Dependencies & Contracts
- **Interfaces to Implement / Consume:** `ABC, @abstractmethod`
- **Allowed Imports:** abc, typing, src.entities.domain_entities, src.database.dto
- **Forbidden Imports:** Any runtime business logic, database queries, web code

## 3. Technical Contract
- **Input Parameters:**
  - Pure method signatures with complete type annotations
- **Deterministic Output:**
  - Pure abstract protocols
- **Error Handling:**
  - Python TypeError if un-implemented abstract methods are instantiated

## 4. Acceptance Criteria & Test Contract
- **Test File Path:** `tests/contracts/test_engine_contracts.py`
- **Required Test Cases:**
  1. *Happy Path:* Subclasses implementing all abstract methods instantiate successfully
  2. *Edge Case:* Type hints verify cleanly under mypy strict checking
  3. *Failure State:* Instantiating contract directly raises TypeError

## 5. Git & GitHub Progression Contract
- **Atomic Commit Message:** `feat(contracts): define engine_contracts [TASK-005] (Closes #5)`
- **Verification Rule:** Commit and push occur ONLY after test suite passes 100%. If tests fail, rollback uncommitted changes.
