"""Tests for the expense analyzer module."""

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

import pytest
from backend.analyzer import compute_summary, identify_high_spend, get_saving_suggestions, get_health_score


INCOME = 75000
EXPENSES = {
    "Food": 12000, "Rent": 18000, "Shopping": 8500,
    "Travel": 6000, "EMI": 10000, "Utilities": 3500, "Entertainment": 4000,
}


def test_compute_summary_totals():
    s = compute_summary(INCOME, EXPENSES)
    assert s["total_expense"] == sum(EXPENSES.values())
    assert s["savings"] == INCOME - s["total_expense"]


def test_compute_summary_savings_pct():
    s = compute_summary(INCOME, EXPENSES)
    expected_pct = round(((INCOME - sum(EXPENSES.values())) / INCOME) * 100, 1)
    assert s["savings_pct"] == expected_pct


def test_identify_high_spend_returns_all_categories():
    flagged = identify_high_spend(INCOME, EXPENSES)
    assert len(flagged) == len(EXPENSES)


def test_identify_high_spend_sorted_descending():
    flagged = identify_high_spend(INCOME, EXPENSES)
    overspends = [f["overspend"] for f in flagged]
    assert overspends == sorted(overspends, reverse=True)


def test_get_saving_suggestions_only_overspent():
    flagged = identify_high_spend(INCOME, EXPENSES)
    suggestions = get_saving_suggestions(flagged, top_n=5)
    for s in suggestions:
        assert s["overspend"] > 0


def test_get_saving_suggestions_respects_top_n():
    flagged = identify_high_spend(INCOME, EXPENSES)
    suggestions = get_saving_suggestions(flagged, top_n=2)
    assert len(suggestions) <= 2


def test_health_score_labels():
    assert get_health_score(35)[0] == "Excellent"
    assert get_health_score(25)[0] == "Good"
    assert get_health_score(15)[0] == "Fair"
    assert get_health_score(5)[0]  == "Low"
    assert get_health_score(-5)[0] == "Overspending"


def test_zero_income():
    s = compute_summary(0, EXPENSES)
    assert s["savings_pct"] == 0
