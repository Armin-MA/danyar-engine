"""Dialectical Conflict Evaluator for Danyar Engine.

Evaluates semantic, logical, and empirical relationships between a newly assimilated claim
and existing knowledge base claims, identifying SUPPORTS, CONTRADICTS, and REFINES edges.
"""

from __future__ import annotations

from typing import Callable, Literal
from pydantic import BaseModel, Field

from src.contracts.engine_contracts import IDialecticalSynthesizer
from src.entities.domain_entities import ClaimEntity, SynthesisResultEntity
from src.utils.schema_validator import validate_json_schema, SchemaValidationError


class SynthesisError(Exception):
    """Raised when dialectical synthesis or relationship classification fails."""
    pass


ValidRelationType = Literal["SUPPORTS", "CONTRADICTS", "REFINES", "UNRELATED"]
VALID_RELATIONS: set[str] = {"SUPPORTS", "CONTRADICTS", "REFINES", "UNRELATED"}


class RawRelationship(BaseModel):
    target_claim_id: str
    relation_type: str = Field(..., description="Must be one of SUPPORTS, CONTRADICTS, REFINES, UNRELATED")
    strength: float = Field(default=1.0, ge=0.0, le=1.0)
    conflict_nature: str = Field(default="", description="Theoretical, boundary-condition, or empirical difference")
    resolution_hint: str = Field(default="", description="How this tension is synthesized or explained")


class DialecticalSynthesisResponse(BaseModel):
    relationships: list[RawRelationship] = Field(default_factory=list)


DIALECTICAL_SYNTHESIS_PROMPT = """You are an expert dialectical philosopher and strategic analyst for Danyar Engine.
Compare the NEW CLAIM against the list of EXISTING CLAIMS from our Knowledge Graph.

Classify the relationship between the NEW CLAIM and each relevant EXISTING CLAIM:
- SUPPORTS: Claims agree, validate, or provide consensus evidence.
- CONTRADICTS: Claims offer opposing advice or mutually incompatible hypotheses.
- REFINES: New claim adds a crucial condition, nuance, or edge case to the existing claim.
- UNRELATED: No significant dialectical tension or synergy.

Output JSON format:
{
  "relationships": [
    {
      "target_claim_id": "claim_id_here",
      "relation_type": "CONTRADICTS",
      "strength": 0.9,
      "conflict_nature": "تفاوت در ماهیت سازمان و اندازه تیم",
      "resolution_hint": "در تیم‌های کوچک سرعت بقا اولویت دارد، در تیم‌های بزرگ مستندسازی پایداری می‌آورد"
    }
  ]
}
"""


class DialecticalConflictEvaluator(IDialecticalSynthesizer):
    """Evaluates dialectical relationships using Frontier LLM reasoning."""

    def analyze_relationship(
        self,
        new_claim: ClaimEntity,
        existing_claims: list[ClaimEntity],
        llm_invoker: Callable[[str], str] | None = None,
    ) -> list[SynthesisResultEntity]:
        """Classify dialectical relations between new_claim and existing_claims.

        Args:
            new_claim: The incoming claim entity.
            existing_claims: List of existing claims from related concepts.
            llm_invoker: Callable to execute prompt against Frontier LLM.

        Returns:
            List of SynthesisResultEntity objects representing valid edges.

        Raises:
            SynthesisError: If taxonomy is invalid or schema parsing fails.
        """
        if not existing_claims:
            return []

        if llm_invoker is None:
            raise SynthesisError("llm_invoker is required for dialectical evaluation")

        existing_block = "\n".join([
            f"- [{c.id}]: {c.statement} (Conditions: {', '.join(c.condition_ids)})"
            for c in existing_claims
        ])

        prompt = (
            f"{DIALECTICAL_SYNTHESIS_PROMPT}\n\n"
            f"[NEW CLAIM ({new_claim.id})]:\n{new_claim.statement}\n\n"
            f"[EXISTING CLAIMS]:\n{existing_block}\n"
        )

        try:
            raw_response = llm_invoker(prompt)
            parsed: DialecticalSynthesisResponse = validate_json_schema(
                raw_response, DialecticalSynthesisResponse
            )
        except (SchemaValidationError, ValueError, Exception) as exc:
            raise SynthesisError(f"Failed to parse dialectical synthesis output: {exc}") from exc

        results: list[SynthesisResultEntity] = []
        for rel in parsed.relationships:
            norm_rel = rel.relation_type.strip().upper()
            if norm_rel not in VALID_RELATIONS:
                raise SynthesisError(
                    f"Invalid relation taxonomy '{rel.relation_type}'. Must be one of {sorted(VALID_RELATIONS)}"
                )

            # Skip unrelated items
            if norm_rel == "UNRELATED":
                continue

            results.append(
                SynthesisResultEntity(
                    source_claim_id=new_claim.id,
                    target_claim_id=rel.target_claim_id,
                    relation_type=norm_rel,
                    strength=rel.strength,
                    resolution_hint=rel.resolution_hint or rel.conflict_nature,
                )
            )

        return results


# Pure functional convenience alias
def evaluate_dialectical_conflict(
    new_claim: ClaimEntity,
    existing_claims: list[ClaimEntity],
    llm_invoker: Callable[[str], str],
) -> list[SynthesisResultEntity]:
    evaluator = DialecticalConflictEvaluator()
    return evaluator.analyze_relationship(new_claim, existing_claims, llm_invoker)


__all__ = [
    "SynthesisError",
    "RawRelationship",
    "DialecticalSynthesisResponse",
    "DialecticalConflictEvaluator",
    "evaluate_dialectical_conflict",
]
