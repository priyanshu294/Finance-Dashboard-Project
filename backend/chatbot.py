"""
Rule-based Chatbot Engine (Step 7).
Answers user questions about spending, savings, and advice without an external LLM.
Integrates with ContextManager for trimmed history (Step 8).
"""

from backend.analyzer import compute_summary, identify_high_spend, get_saving_suggestions
from backend.context_manager import ContextManager

# Keyword → intent mapping
INTENT_MAP = {
    "save more":       "save_more",
    "saving more":     "save_more",
    "how can i save":  "save_more",
    "spending too much": "high_spend",
    "spending most":   "high_spend",
    "where am i spending": "high_spend",
    "saving percentage": "saving_pct",
    "saving percent":  "saving_pct",
    "savings rate":    "saving_pct",
    "total expense":   "total_expense",
    "total spending":  "total_expense",
    "income":          "income",
    "budget":          "budget_advice",
    "tip":             "tips",
    "advice":          "tips",
    "help":            "help",
}


def _detect_intent(message: str) -> str:
    lower = message.lower()
    for keyword, intent in INTENT_MAP.items():
        if keyword in lower:
            return intent
    return "unknown"


def _format_currency(amount: float) -> str:
    return f"₹{int(amount):,}"


class Chatbot:
    def __init__(self):
        self.ctx = ContextManager()

    def respond(self, user_message: str, customer_name: str,
                income: float, expenses: dict) -> str:
        """
        Generate a response to the user message using rule-based logic.
        Updates context window after each turn.
        """
        self.ctx.add_turn("user", user_message)
        summary = compute_summary(income, expenses)
        flagged  = identify_high_spend(income, expenses)
        suggestions = get_saving_suggestions(flagged)

        intent = _detect_intent(user_message)
        reply = self._handle_intent(intent, customer_name, summary, flagged, suggestions)

        self.ctx.add_turn("assistant", reply)
        self.ctx.update_summary(f"User asked about '{intent}'")
        return reply

    def _handle_intent(self, intent, name, summary, flagged, suggestions) -> str:
        if intent == "save_more":
            tips_text = ""
            for s in suggestions:
                tips = "\n  - ".join(s["tips"])
                tips_text += f"\n**{s['category']}** (excess {_format_currency(s['overspend'])}):\n  - {tips}\n"
            return (
                f"Hi {name}! Here are your top saving opportunities:\n{tips_text}"
                f"\nFocusing on just the top 2 categories could save you "
                f"{_format_currency(sum(s['overspend'] for s in suggestions[:2]))} per month!"
            )

        if intent == "high_spend":
            top3 = [f for f in flagged if f["is_high"]][:3]
            if not top3:
                return "Great news! No category is currently above the recommended benchmark."
            lines = "\n".join(
                f"- **{f['category']}**: {_format_currency(f['amount'])} "
                f"(benchmark {_format_currency(f['benchmark_amount'])}, "
                f"excess {_format_currency(f['overspend'])})"
                for f in top3
            )
            return f"Your top overspent categories are:\n{lines}"

        if intent == "saving_pct":
            pct = summary["savings_pct"]
            label = "excellent" if pct >= 30 else "good" if pct >= 20 else "fair" if pct >= 10 else "low"
            return (
                f"Your current saving rate is **{pct}%** — that's {label}.\n"
                f"You save {_format_currency(summary['savings'])} out of "
                f"{_format_currency(summary['income'])} per month.\n"
                f"(Financial advisors recommend at least 20%.)"
            )

        if intent == "total_expense":
            return (
                f"Your total monthly expense is {_format_currency(summary['total_expense'])} "
                f"out of {_format_currency(summary['income'])} income."
            )

        if intent == "income":
            return f"Your recorded monthly income is {_format_currency(summary['income'])}."

        if intent == "budget_advice":
            return (
                "A healthy budget follows the **50-20-30 rule**:\n"
                "- **50%** on Needs (Rent, Food, Utilities, EMI)\n"
                "- **20%** on Savings & Investments\n"
                "- **30%** on Wants (Shopping, Travel, Entertainment)\n"
                f"Based on your income of {_format_currency(summary['income'])}, "
                f"you should aim to save at least {_format_currency(summary['income'] * 0.20)} per month."
            )

        if intent == "tips":
            top = [s for s in suggestions][:2]
            if not top:
                return "You're within budget across all categories. Keep up the great work!"
            tip_lines = []
            for s in top:
                tip_lines.append(f"**{s['category']}**: {s['tips'][0]}")
            return "Quick tips:\n" + "\n".join(f"- {t}" for t in tip_lines)

        if intent == "help":
            return (
                "I can help you with:\n"
                "- **How can I save more?** — personalised saving tips\n"
                "- **Where am I spending too much?** — high-spend categories\n"
                "- **What is my saving percentage?** — savings rate\n"
                "- **Budget advice** — the 50-20-30 rule\n"
                "- **Total expense** or **income** — quick figures"
            )

        # Unknown intent — graceful fallback
        return (
            "I'm not sure I understood that. Try:\n"
            "- 'How can I save more?'\n"
            "- 'Where am I spending too much?'\n"
            "- 'What is my saving percentage?'"
        )

    def clear_history(self):
        self.ctx.clear()
