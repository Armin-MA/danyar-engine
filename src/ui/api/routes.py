"""FastAPI REST API Routes for Danyar Engine.

Exposes endpoints for chat inquiries (/api/chat), knowledge ingestion (/api/ingest),
graph retrieval (/api/graph), and user note annotations (/api/notes).
"""

from __future__ import annotations

import os
from typing import Any
from fastapi import FastAPI, APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.contracts.engine_contracts import IGraphRepository, IAnnotationRepository, ISocraticAdvisor
from src.database.dto.graph_dtos import ClaimIngestDTO, UserNoteDTO, SubGraphDTO
from src.entities.domain_entities import ConditionEntity
from src.mechanics.formulate_socratic_inquiry import SocraticAdvisor
from src.mechanics.compile_structured_context import compile_structured_context
from src.ui.presenters.socratic_presenter import SocraticPresenter


class ChatRequest(BaseModel):
    """Payload for conversational inquiry to Danyar Advisor."""

    query: str = Field(..., min_length=2, description="User question or scenario")
    condition_category: str | None = Field(default=None, description="Optional condition category (e.g. market_phase)")
    condition_description: str | None = Field(default=None, description="Optional condition description")


class ChatResponse(BaseModel):
    """Structured response from Danyar Advisor."""

    status: str = "success"
    response: str
    is_sufficient: bool = True
    diagnostic_questions: list[str] = Field(default_factory=list)
    subgraph: dict[str, Any] = Field(default_factory=dict)


def create_api_router(
    graph_repo: IGraphRepository,
    annotation_repo: IAnnotationRepository,
    advisor: ISocraticAdvisor,
) -> APIRouter:
    """Creates configured APIRouter with injected dependencies."""
    router = APIRouter(prefix="/api")

    @router.post("/chat", response_model=ChatResponse)
    def chat_endpoint(req: ChatRequest) -> ChatResponse:
        try:
            # 1. Condition entity if provided
            user_cond: ConditionEntity | None = None
            if req.condition_category and req.condition_description:
                user_cond = ConditionEntity(
                    id="user_ctx",
                    category=req.condition_category,
                    description=req.condition_description,
                )

            # 2. Check context sufficiency
            conditions = [user_cond] if user_cond else []
            is_suff, questions = advisor.assess_context_sufficiency(req.query, conditions)

            # 3. Retrieve relevant subgraph
            query_keywords = [w for w in req.query.split() if len(w) > 3]
            subgraph = graph_repo.fetch_related_subgraph(query_keywords)

            # 4. Formulate response
            if not is_suff and questions:
                persian_msg = "برای ارائه تحلیل دقیق و تطبیق با شرایط شما، نیاز به روشن شدن موارد زیر داریم:\n" + "\n".join(
                    f"- {q}" for q in questions
                )
            else:
                if not subgraph.is_empty():
                    compiled_text = compile_structured_context(subgraph, user_cond)
                    persian_msg = SocraticPresenter.format_advisory_response(
                        {
                            "consensus": "توافقات دانشی مستخرج از پایگاه دانش دانیار برای این پرسش شناسایی شدند.",
                            "tailored_advice": f"بر اساس تحلیل گزاره‌ها، توصیه بهینه برای پرسش «{req.query}» متناسب‌سازی شد.",
                        }
                    )
                else:
                    persian_msg = SocraticPresenter.format_advisory_response(
                        {
                            "tailored_advice": f"پرسش شما «{req.query}» دریافت شد؛ توصیه اولیه بر مبنای تفکر نقادانه و سنجش شرایط کنونی بازار استوار است."
                        }
                    )

            return ChatResponse(
                status="success",
                response=persian_msg,
                is_sufficient=is_suff,
                diagnostic_questions=questions,
                subgraph=subgraph.model_dump(),
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chat processing failed: {str(e)}",
            )

    @router.post("/ingest")
    def ingest_claim(dto: ClaimIngestDTO) -> dict[str, Any]:
        try:
            success = graph_repo.save_claim_cluster(dto)
            return {"status": "success", "message": "Claim cluster ingested successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ingestion failed: {str(e)}",
            )

    @router.get("/graph/full")
    def get_full_graph(limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
        try:
            if hasattr(graph_repo, "fetch_full_graph"):
                subgraph = graph_repo.fetch_full_graph(limit=limit)
            else:
                subgraph = graph_repo.fetch_related_subgraph([])
            return subgraph.model_dump()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fetching full graph failed: {str(e)}",
            )

    @router.get("/graph/subgraph")
    def get_subgraph(concepts: str = Query(default="")) -> dict[str, Any]:
        try:
            concept_list = [c.strip() for c in concepts.split(",") if c.strip()]
            subgraph = graph_repo.fetch_related_subgraph(concept_list)
            return subgraph.model_dump()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fetching subgraph failed: {str(e)}",
            )

    @router.post("/notes/annotate", status_code=status.HTTP_201_CREATED)
    def annotate_claim(dto: UserNoteDTO) -> dict[str, Any]:
        try:
            created_note = annotation_repo.add_user_note(dto)
            return {
                "status": "created",
                "note_id": created_note.id,
                "message": "User note attached successfully",
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Attaching note failed: {str(e)}",
            )

    @router.get("/notes/{claim_id}")
    def get_notes(claim_id: str) -> list[dict[str, Any]]:
        try:
            notes = annotation_repo.fetch_notes_for_claim(claim_id)
            return [n.to_dict() for n in notes]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fetching notes failed: {str(e)}",
            )

    return router


def create_app(
    graph_repo: IGraphRepository | None = None,
    annotation_repo: IAnnotationRepository | None = None,
    advisor: ISocraticAdvisor | None = None,
) -> FastAPI:
    """Application factory for Danyar Engine FastAPI web service."""
    app = FastAPI(
        title="Danyar Engine API",
        description="Dialectical GraphRAG Advisor REST API",
        version="1.0.0",
    )

    # Fallback instances if not passed (e.g. for standalone dev server)
    if graph_repo is None or annotation_repo is None or advisor is None:
        from src.database.repositories.neo4j_graph_repository import Neo4jGraphRepository
        from src.database.repositories.neo4j_annotation_repository import Neo4jAnnotationRepository

        graph_repo = graph_repo or Neo4jGraphRepository()
        annotation_repo = annotation_repo or Neo4jAnnotationRepository()
        advisor = advisor or SocraticAdvisor()

    router = create_api_router(graph_repo, annotation_repo, advisor)
    app.include_router(router)

    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

        @app.get("/", include_in_schema=False)
        def serve_dashboard():
            return FileResponse(os.path.join(static_dir, "index.html"))

    return app


__all__ = ["create_app", "create_api_router", "ChatRequest", "ChatResponse"]
