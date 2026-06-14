"""
RAG Engine (Step 11) — keyword-based retrieval over the local knowledge base.
No vector embeddings required; uses TF-IDF-style keyword overlap for simplicity.
"""

import json
import re
from pathlib import Path
from functools import lru_cache

KB_PATH = Path(__file__).parent / "knowledge_base.json"


@lru_cache(maxsize=1)
def _load_kb() -> tuple[dict, ...]:
    """Load and cache the knowledge base. Returns empty tuple if file missing or malformed."""
    try:
        with open(KB_PATH, "r") as f:
            data = json.load(f)
        return tuple(data["documents"])
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return ()


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.lower()))


def retrieve(query: str, top_k: int = 2) -> list[dict]:
    """
    Retrieve the top_k most relevant knowledge base documents for `query`.
    Scoring is based on keyword overlap across title, content, and tags.
    """
    docs = list(_load_kb())
    query_tokens = _tokenize(query)
    scored = []
    for doc in docs:
        doc_text = f"{doc['title']} {doc['content']} {' '.join(doc['tags'])}"
        doc_tokens = _tokenize(doc_text)
        overlap = len(query_tokens & doc_tokens)
        scored.append((overlap, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored[:top_k] if score > 0]


def augmented_answer(query: str, base_answer: str) -> str:
    """
    Enrich a chatbot base_answer with retrieved knowledge base snippets.
    Appends a 'Learn more' section if relevant docs are found.
    """
    docs = retrieve(query, top_k=2)
    if not docs:
        return base_answer
    extras = "\n\n---\n**Relevant Knowledge Base Insights:**"
    for doc in docs:
        extras += f"\n- **{doc['title']}**: {doc['content'][:200]}..."
    return base_answer + extras
