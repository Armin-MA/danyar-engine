"""Unit Tests for FastAPI API Routers [TASK-016].

Verifies REST API endpoints (/api/chat, /api/ingest, /api/graph, /api/notes)
using FastAPI TestClient and mocked repository/advisory services.
"""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from src.database.dto.graph_dtos import NodeDTO, EdgeDTO, SubGraphDTO
from src.entities.domain_entities import UserNoteEntity
from src.ui.api.routes import create_app


@pytest.fixture
def test_client():
    mock_graph_repo = MagicMock()
    mock_annotation_repo = MagicMock()
    mock_advisor = MagicMock()

    # Configure defaults
    subgraph = SubGraphDTO(
        nodes=[NodeDTO(id="claim_1", label="Claim", properties={"statement": "تست گزاره"})],
        edges=[],
    )
    mock_graph_repo.fetch_related_subgraph.return_value = subgraph
    mock_graph_repo.fetch_full_graph.return_value = subgraph
    mock_graph_repo.save_claim_cluster.return_value = True

    mock_advisor.assess_context_sufficiency.return_value = (True, [])

    mock_annotation_repo.add_user_note.return_value = UserNoteEntity(
        id="note_001",
        claim_id="claim_1",
        content="یادداشت تست",
        disputes=False,
    )

    app = create_app(
        graph_repo=mock_graph_repo,
        annotation_repo=mock_annotation_repo,
        advisor=mock_advisor,
    )
    return TestClient(app)


def test_happy_path_post_chat_returns_advisory(test_client):
    """Happy Path: POST /api/chat returns advisory message and matched subgraph nodes."""
    payload = {
        "query": "چگونه تیم فنی را در فاز رشد توسعه دهیم؟",
        "condition_category": "market_phase",
        "condition_description": "فاز رشد پس از PMF",
    }
    response = test_client.post("/api/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "response" in data
    assert "subgraph" in data
    assert len(data["subgraph"]["nodes"]) >= 1


def test_edge_case_post_notes_annotate_returns_201(test_client):
    """Edge Case: POST /api/notes/annotate successfully creates user note and returns 201."""
    payload = {
        "id": "note_001",
        "claim_id": "claim_1",
        "content": "این گزاره در استارتاپ‌های سخت‌افزاری صادق نیست.",
        "dispute_type": "Dispute",
        "credibility_impact": -0.2,
    }
    response = test_client.post("/api/notes/annotate", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "created"
    assert data["note_id"] == "note_001"


def test_failure_state_invalid_body_returns_422(test_client):
    """Failure State: Returns 422 Unprocessable Entity on invalid request body."""
    # Missing required query field
    response = test_client.post("/api/chat", json={})
    assert response.status_code == 422


def test_ingest_endpoint(test_client):
    """Verifies POST /api/ingest persists valid claim payload."""
    payload = {
        "statement": "تفکر نقادانه پیش‌نیاز تصمیم‌گیری استراتژیک است.",
        "source_title": "اصول دالیو",
        "author_name": "ری دالیو",
        "concepts": ["تفکر نقادانه"],
        "condition_category": "leadership",
        "condition_description": "رهبری سازمان",
    }
    response = test_client.post("/api/ingest", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_graph_endpoints(test_client):
    """Verifies GET /api/graph/full and GET /api/graph/subgraph."""
    full_resp = test_client.get("/api/graph/full")
    assert full_resp.status_code == 200
    assert "nodes" in full_resp.json()

    sub_resp = test_client.get("/api/graph/subgraph?concepts=تست")
    assert sub_resp.status_code == 200
    assert "nodes" in sub_resp.json()
