"""
Internal Plugins (Step 10) — tool functions available to sub-agents internally.
Each plugin is a pure function with a clear interface (name, description, inputs, output).
External plugin stubs (Claude.com/plugins) are declared at the bottom.
"""

import json
from pathlib import Path

# --- Plugin Registry ---

PLUGIN_REGISTRY: dict[str, dict] = {}


def register_plugin(name: str, description: str):
    """Decorator: registers a function as a named plugin."""
    def decorator(fn):
        PLUGIN_REGISTRY[name] = {"description": description, "fn": fn}
        return fn
    return decorator


# --- Internal Plugins ---

@register_plugin(
    name="expense_summary",
    description="Return a JSON summary of income, expenses, savings for a customer.",
)
def expense_summary_plugin(customer_name: str) -> str:
    from backend.sample_data import CUSTOMERS
    from backend.analyzer import compute_summary
    if customer_name not in CUSTOMERS:
        return json.dumps({"error": "Customer not found"})
    d = CUSTOMERS[customer_name]
    summary = compute_summary(d["monthly_income"], d["expenses"])
    return json.dumps(summary)


@register_plugin(
    name="category_breakdown",
    description="Return per-category spend vs benchmark as a JSON list.",
)
def category_breakdown_plugin(customer_name: str) -> str:
    from backend.sample_data import CUSTOMERS
    from backend.analyzer import identify_high_spend
    if customer_name not in CUSTOMERS:
        return json.dumps({"error": "Customer not found"})
    d = CUSTOMERS[customer_name]
    flagged = identify_high_spend(d["monthly_income"], d["expenses"])
    return json.dumps(flagged)


@register_plugin(
    name="saving_tips",
    description="Return top saving tips for a customer's most overspent categories.",
)
def saving_tips_plugin(customer_name: str, top_n: int = 3) -> str:
    from backend.sample_data import CUSTOMERS
    from backend.analyzer import identify_high_spend, get_saving_suggestions
    if customer_name not in CUSTOMERS:
        return json.dumps({"error": "Customer not found"})
    d = CUSTOMERS[customer_name]
    flagged = identify_high_spend(d["monthly_income"], d["expenses"])
    suggestions = get_saving_suggestions(flagged, top_n=top_n)
    return json.dumps(suggestions)


@register_plugin(
    name="rag_lookup",
    description="Retrieve knowledge base articles relevant to a free-text query.",
)
def rag_lookup_plugin(query: str) -> str:
    from rag.rag_engine import retrieve
    docs = retrieve(query, top_k=3)
    return json.dumps([{"title": d["title"], "snippet": d["content"][:200]} for d in docs])


# --- External Plugin Stubs (claude.com/plugins) ---
# These are declared but delegated to the official Claude plugin runtime at execution time.

EXTERNAL_PLUGINS = [
    {
        "name": "wolfram_alpha",
        "source": "claude.com/plugins",
        "description": "Compute financial math (compound interest, loan amortisation) via Wolfram Alpha.",
        "status": "stub",
    },
    {
        "name": "web_search",
        "source": "claude.com/plugins",
        "description": "Fetch latest mutual fund NAVs, interest rates, or market news.",
        "status": "stub",
    },
]


def call_plugin(name: str, **kwargs) -> str:
    """Unified plugin caller. Dispatches to internal or logs stub for external."""
    if name in PLUGIN_REGISTRY:
        return PLUGIN_REGISTRY[name]["fn"](**kwargs)
    for ep in EXTERNAL_PLUGINS:
        if ep["name"] == name:
            return json.dumps({"status": "stub", "message": f"External plugin '{name}' requires Claude.com runtime."})
    return json.dumps({"error": f"Plugin '{name}' not found."})
