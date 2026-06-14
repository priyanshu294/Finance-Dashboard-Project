"""
Context Manager — sub-agent memory allocation.

Step 8: Context Trimming
- Sub-agent memory is divided within the context window.
- History is summarised, keeping only a compressed summary (≤15% of corpus).
- The sliding window retains the latest 8-10 user prompts verbatim.
"""

from collections import deque

# Constants governing the context window
MAX_HISTORY_PROMPTS = 10        # latest prompts kept verbatim
SUMMARY_MAX_CHARS   = 600       # ~12-15% of a ~4000-char context budget


class ContextManager:
    """
    Manages per-session conversation context for the chatbot sub-agent.
    Stores a rolling window of recent user messages plus a compressed summary
    of older history to stay within budget.
    """

    def __init__(self):
        self._history: deque[dict] = deque(maxlen=MAX_HISTORY_PROMPTS)
        self._summary: str = ""

    # --- Public API ---

    def add_turn(self, role: str, content: str) -> None:
        """Append a conversation turn (role: 'user' | 'assistant')."""
        self._history.append({"role": role, "content": content})
        # If summary budget is not yet seeded, create an initial one
        if not self._summary:
            self._summary = "Session started. Customer has shared expense data."

    def get_context_for_agent(self, customer_name: str, summary_dict: dict) -> str:
        """
        Build the context string passed to the chatbot agent.
        Structure: [compressed summary] + [financial snapshot] + [recent turns].
        """
        financial_snapshot = (
            f"Customer: {customer_name} | "
            f"Income: ₹{summary_dict['income']:,} | "
            f"Total Expense: ₹{summary_dict['total_expense']:,} | "
            f"Savings: ₹{summary_dict['savings']:,} ({summary_dict['savings_pct']}%)"
        )
        recent = "\n".join(
            f"[{t['role'].upper()}]: {t['content']}" for t in self._history
        )
        return (
            f"## Session Summary\n{self._summary}\n\n"
            f"## Financial Snapshot\n{financial_snapshot}\n\n"
            f"## Recent Conversation\n{recent}"
        )

    def update_summary(self, new_insight: str) -> None:
        """Append a compressed insight to the rolling summary, respecting char limit."""
        candidate = f"{self._summary} | {new_insight}"
        if len(candidate) <= SUMMARY_MAX_CHARS:
            self._summary = candidate
        else:
            # Drop oldest segment (before first ' | ') to make room
            parts = self._summary.split(" | ", 1)
            base = parts[1] if len(parts) > 1 else ""
            combined = f"{base} | {new_insight}" if base else new_insight
            # Trim to budget, never splitting in the middle of the leading separator
            self._summary = combined[-SUMMARY_MAX_CHARS:].lstrip(" |").strip()

    def clear(self) -> None:
        self._history.clear()
        self._summary = ""

    @property
    def history(self) -> list[dict]:
        return list(self._history)
