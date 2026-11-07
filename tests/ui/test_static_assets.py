"""Unit Tests for Web Dashboard Static Assets [TASK-017].

Verifies presence, Persian RTL semantics, 3d-force-graph canvas,
Milkdown editor integration, and offline resilience in static dashboard assets.
"""

from __future__ import annotations

import os
import pytest

STATIC_DIR = os.path.join("src", "ui", "static")
INDEX_PATH = os.path.join(STATIC_DIR, "index.html")


def test_index_html_exists():
    """Verify index.html exists in static directory."""
    assert os.path.isfile(INDEX_PATH), f"File {INDEX_PATH} does not exist"


def test_happy_path_contains_3d_graph_and_editor_containers():
    """Happy Path: Contains 3D force-graph canvas container, Milkdown editor, and chat stream."""
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Containers
    assert 'id="3d-graph"' in html or 'id="graph-canvas"' in html
    assert 'id="milkdown-editor"' in html or 'id="note-editor"' in html
    assert 'id="chat-messages"' in html or 'id="chat-container"' in html

    # CDN / Scripts
    assert "3d-force-graph" in html
    assert "danyar" in html.lower()


def test_edge_case_persian_rtl_layout_semantics():
    """Edge Case: Document specifies dir='rtl', Persian language, and appropriate typography."""
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    assert 'dir="rtl"' in html
    assert 'lang="fa"' in html
    assert "دانیار" in html
    assert "اجماع" in html or "تضاد" in html or "یادداشت" in html


def test_failure_state_reconnection_banner_and_error_handling():
    """Failure State: Contains reconnection banner or offline status element."""
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    assert "reconnection-banner" in html or "offline-banner" in html or "status-indicator" in html
