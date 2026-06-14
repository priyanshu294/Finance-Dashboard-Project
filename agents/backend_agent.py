"""
Backend Sub-Agent (Step 4).
Responsible for all data processing, analysis computation, and chatbot responses.
Enforces isolation: receives only a sanitised customer snapshot, returns structured results.
"""

from backend.analyzer import compute_summary, identify_high_spend, get_saving_suggestions, get_health_score
from backend.chatbot import Chatbot
from backend.sample_data import CUSTOMERS
from rag.rag_engine import augmented_answer

# Isolation: each session owns its own Chatbot (and ContextManager inside it)
_sessions: dict[str, Chatbot] = {}


def _get_chatbot(session_id: str) -> Chatbot:
    if session_id not in _sessions:
        _sessions[session_id] = Chatbot()
    return _sessions[session_id]


# --- Public delegation interface ---

def analyze_customer(customer_name: str) -> dict:
    """
    Full analysis for a customer. Returns a structured result dict consumed
    by the frontend agent or Streamlit directly.
    """
    if customer_name not in CUSTOMERS:
        return {"error": f"Customer '{customer_name}' not found."}

    data     = CUSTOMERS[customer_name]
    income   = data["monthly_income"]
    expenses = data["expenses"]

    summary     = compute_summary(income, expenses)
    flagged     = identify_high_spend(income, expenses)
    suggestions = get_saving_suggestions(flagged, top_n=3)
    health_label, health_color = get_health_score(summary["savings_pct"])

    return {
        "customer_name": customer_name,
        "profile": data["profile"],
        "summary": summary,
        "flagged_categories": flagged,
        "suggestions": suggestions,
        "health_label": health_label,
        "health_color": health_color,
        "raw_expenses": expenses,
    }


def chat_response(session_id: str, customer_name: str, user_message: str) -> str:
    """
    Route a user chat message through the chatbot and optionally enrich
    the response using the RAG engine (Step 11 integration).
    """
    if customer_name not in CUSTOMERS:
        return "I couldn't find your profile. Please select a valid customer."
    data  = CUSTOMERS[customer_name]
    bot   = _get_chatbot(session_id)
    base  = bot.respond(user_message, customer_name, data["monthly_income"], data["expenses"])
    # RAG augmentation for knowledge-heavy queries
    enriched = augmented_answer(user_message, base)
    return enriched


def clear_session(session_id: str) -> None:
    if session_id in _sessions:
        _sessions[session_id].clear_history()
        del _sessions[session_id]
