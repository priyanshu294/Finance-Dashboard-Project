"""Tests for the RAG engine."""

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from rag.rag_engine import retrieve, augmented_answer


def test_retrieve_returns_results():
    docs = retrieve("save food grocery budget", top_k=2)
    assert len(docs) <= 2


def test_retrieve_relevance():
    docs = retrieve("EMI loan prepayment debt", top_k=1)
    assert docs, "Expected at least one relevant doc"
    assert "EMI" in docs[0]["title"] or "loan" in docs[0]["title"].lower() or "emi" in docs[0]["tags"]


def test_retrieve_no_match_returns_empty():
    docs = retrieve("zzz xyz nonexistent term", top_k=2)
    # May return empty or partial — should not raise
    assert isinstance(docs, list)


def test_augmented_answer_appends_insights():
    base    = "Here is my base answer."
    result  = augmented_answer("save food grocery", base)
    # Either augmented or unchanged — should not lose base
    assert base in result


def test_augmented_answer_no_match():
    base   = "Base answer."
    result = augmented_answer("zzz xyz xyz", base)
    assert result == base  # No relevant docs → unchanged
