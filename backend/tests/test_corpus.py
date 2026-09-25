"""
Unit and integration tests for the LexGuard 500-document corpus inventory.
Verifies that all 500 documents are present, have valid metadata, and are structurally sound.
"""

import pytest

try:
    from backend.app.core.corpus import (
        corpus_registry,
        ALL_CORPUS_DOCUMENTS,
        TEMPLATES,
        PUBLIC_LAWS,
        DEMO_DOCUMENTS,
    )
except ImportError:
    from app.core.corpus import (
        corpus_registry,
        ALL_CORPUS_DOCUMENTS,
        TEMPLATES,
        PUBLIC_LAWS,
        DEMO_DOCUMENTS,
    )


def test_corpus_total_count():
    """Verify exactly 500 documents are cataloged."""
    assert corpus_registry.total_count == 500
    assert len(ALL_CORPUS_DOCUMENTS) == 500


def test_corpus_subcategories_count():
    """Verify 200 templates, 285 public statutes, and 15 demo documents."""
    assert len(TEMPLATES) == 200
    assert len(PUBLIC_LAWS) == 285
    assert len(DEMO_DOCUMENTS) == 15
    assert corpus_registry.templates_count == 200
    assert corpus_registry.public_laws_count == 285
    assert corpus_registry.demo_documents_count == 15


def test_corpus_integrity_report():
    """Verify 100% integrity score with zero structural errors."""
    report = corpus_registry.verify_integrity()
    assert report["status"] == "PASSED"
    assert report["integrity_score"] == 100.0
    assert len(report["errors"]) == 0


def test_corpus_no_duplicate_ids():
    """Verify that all document IDs are strictly unique."""
    ids = [d.id for d in ALL_CORPUS_DOCUMENTS]
    assert len(ids) == len(set(ids))


def test_corpus_metadata_validity():
    """Verify that every document contains non-empty title, category, jurisdiction, and positive word/page counts."""
    for doc in ALL_CORPUS_DOCUMENTS:
        assert len(doc.id.strip()) > 0
        assert len(doc.title.strip()) >= 5
        assert len(doc.category.strip()) > 0
        assert len(doc.jurisdiction.strip()) > 0
        assert doc.word_count > 0
        assert doc.page_count > 0
        assert len(doc.summary.strip()) > 0
        assert doc.accessible is True
        assert doc.analyzable is True


def test_primary_demo_document_present():
    """Verify primary demo document 'doc-saas-v42' is present and fully defined."""
    doc = corpus_registry.get_by_id("doc-saas-v42")
    assert doc is not None
    assert doc.id == "doc-saas-v42"
    assert "SaaS" in doc.title
    assert doc.jurisdiction == "Delaware Law"
    assert doc.page_count == 18
    assert doc.word_count == 14820
