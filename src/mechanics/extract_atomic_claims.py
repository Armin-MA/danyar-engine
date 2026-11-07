"""Atomic Claim Extraction Logic for Danyar Engine.

Orchestrates prompt engineering and strict JSON schema parsing to extract atomic,
canonical concepts, conditions, and claims from unstructured text sources.
"""

from __future__ import annotations

import uuid
from typing import Callable
from pydantic import BaseModel, Field

from src.contracts.engine_contracts import IExtractionPipeline
from src.entities.domain_entities import SourceEntity, ClaimEntity, ConditionEntity, ConceptEntity
from src.utils.schema_validator import validate_json_schema, SchemaValidationError


class ExtractionError(Exception):
    """Raised when atomic claim extraction fails validation or parsing."""
    pass


class RawExtractedClaim(BaseModel):
    statement: str = Field(..., description="Atomic, self-contained statement without unresolved pronouns.")
    type: str = Field(default="Actionable_Advice", description="Fact, Hypothesis, or Actionable_Advice")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    concepts: list[str] = Field(default_factory=list, description="Canonical concept names mentioned")
    condition_category: str = Field(default="general", description="Crisis, Growth, Startup, Enterprise, etc.")
    condition_description: str = Field(default="", description="Situational constraint description")


class ExtractionResponse(BaseModel):
    claims: list[RawExtractedClaim] = Field(default_factory=list)


EXTRACTION_SYSTEM_PROMPT = """You are an elite cognitive knowledge extractor for Danyar Engine (Dialectical GraphRAG).
Analyze the text snippet and extract distinct, atomic propositions (Claims) along with their boundary Conditions and Concepts.

Rules:
1. De-contextualize pronouns (Coreference Resolution): Replace "it", "this method" with explicit concept names.
2. Formulate atomic claims: One clear rule, advice, or empirical finding per claim.
3. Identify boundary conditions: When does this claim apply (e.g., market downturn, early-stage team)?
4. Return pure JSON matching the ExtractionResponse schema.

Output JSON format:
{
  "claims": [
    {
      "statement": "...",
      "type": "Actionable_Advice",
      "confidence_score": 0.9,
      "concepts": ["مستندسازی", "مدیریت بحران"],
      "condition_category": "crisis",
      "condition_description": "استارتاپ‌های نوپا در بحران مالی"
    }
  ]
}
"""


class AtomicClaimExtractor(IExtractionPipeline):
    """Extracts atomic claims and conditions from text using LLM invokers."""

    def __init__(self, max_retries: int = 2) -> None:
        self.max_retries = max_retries

    def extract_from_text(
        self,
        source: SourceEntity,
        raw_text: str,
        llm_invoker: Callable[[str], str] | None = None,
    ) -> list[ClaimEntity]:
        """Transform raw text into validated ClaimEntity objects.

        Args:
            source: The parent source metadata.
            raw_text: The unstructured text chunk.
            llm_invoker: Callable executing prompt against Frontier LLM.

        Returns:
            List of populated ClaimEntity instances.

        Raises:
            ExtractionError: If extraction fails schema validation after retries.
        """
        if not raw_text or not raw_text.strip():
            return []

        if llm_invoker is None:
            raise ExtractionError("llm_invoker is required for atomic claim extraction")

        prompt = f"{EXTRACTION_SYSTEM_PROMPT}\n\n[Text Snippet from '{source.title}']:\n{raw_text}\n"

        attempts = 0
        last_error = None

        while attempts <= self.max_retries:
            try:
                raw_response = llm_invoker(prompt)
                parsed: ExtractionResponse = validate_json_schema(raw_response, ExtractionResponse)
                
                result_claims: list[ClaimEntity] = []
                for item in parsed.claims:
                    claim_id = f"claim_{uuid.uuid4().hex[:8]}"
                    cond_id = f"cond_{uuid.uuid4().hex[:8]}" if item.condition_description else None

                    claim = ClaimEntity(
                        id=claim_id,
                        statement=item.statement.strip(),
                        claim_type=item.type,
                        confidence_score=item.confidence_score,
                        source_id=source.id,
                        concept_ids=item.concepts,
                        condition_ids=[cond_id] if cond_id else [],
                    )
                    result_claims.append(claim)

                return result_claims

            except (SchemaValidationError, ValueError, Exception) as exc:
                last_error = exc
                attempts += 1

        raise ExtractionError(f"Failed to extract atomic claims after {self.max_retries + 1} attempts: {last_error}")


# Pure functional convenience alias
def extract_atomic_claims(
    source: SourceEntity,
    raw_text: str,
    llm_invoker: Callable[[str], str],
    max_retries: int = 1,
) -> list[ClaimEntity]:
    extractor = AtomicClaimExtractor(max_retries=max_retries)
    return extractor.extract_from_text(source, raw_text, llm_invoker)


__all__ = [
    "ExtractionError",
    "RawExtractedClaim",
    "ExtractionResponse",
    "AtomicClaimExtractor",
    "extract_atomic_claims",
]
