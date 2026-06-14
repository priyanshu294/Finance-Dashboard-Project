"""
Expense Analyzer — rule-based financial analysis engine.
Computes totals, savings rate, overspent categories, and ranked suggestions.
"""

from backend.sample_data import BENCHMARKS, SAVING_TIPS


def compute_summary(income: float, expenses: dict) -> dict:
    """Return total expenses, savings amount, and savings percentage."""
    total_expense = sum(expenses.values())
    savings = income - total_expense
    savings_pct = round((savings / income) * 100, 1) if income else 0
    return {
        "income": income,
        "total_expense": total_expense,
        "savings": savings,
        "savings_pct": savings_pct,
    }


def identify_high_spend(income: float, expenses: dict) -> list[dict]:
    """
    Compare each category spend against benchmark ratios.
    Returns list of {category, amount, benchmark_amount, overspend, pct_of_income}
    sorted by overspend descending.
    """
    flagged = []
    for cat, amount in expenses.items():
        benchmark_pct = BENCHMARKS.get(cat, 0.10)
        benchmark_amount = income * benchmark_pct
        pct_of_income = round((amount / income) * 100, 1) if income else 0
        overspend = amount - benchmark_amount
        flagged.append({
            "category": cat,
            "amount": amount,
            "benchmark_amount": round(benchmark_amount),
            "overspend": round(overspend),
            "pct_of_income": pct_of_income,
            "is_high": overspend > 0,
        })
    return sorted(flagged, key=lambda x: x["overspend"], reverse=True)


def get_saving_suggestions(flagged: list[dict], top_n: int = 3) -> list[dict]:
    """
    For each overspent category (top_n by excess), return targeted tips.
    """
    suggestions = []
    overspent = [f for f in flagged if f["is_high"]][:top_n]
    for item in overspent:
        cat = item["category"]
        tips = SAVING_TIPS.get(cat, ["Review this category for opportunities to cut back."])
        suggestions.append({
            "category": cat,
            "overspend": item["overspend"],
            "tips": tips,
        })
    return suggestions


def get_health_score(savings_pct: float) -> tuple[str, str]:
    """Return a simple health label and colour for UI display."""
    if savings_pct >= 30:
        return "Excellent", "#2ecc71"
    if savings_pct >= 20:
        return "Good", "#27ae60"
    if savings_pct >= 10:
        return "Fair", "#f39c12"
    if savings_pct >= 0:
        return "Low", "#e67e22"
    return "Overspending", "#e74c3c"
