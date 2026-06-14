"""Tests for the rule-based chatbot."""

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

import pytest
from backend.chatbot import Chatbot

INCOME   = 75000
EXPENSES = {
    "Food": 12000, "Rent": 18000, "Shopping": 8500,
    "Travel": 6000, "EMI": 10000, "Utilities": 3500, "Entertainment": 4000,
}


@pytest.fixture
def bot():
    return Chatbot()


def test_save_more_intent(bot):
    reply = bot.respond("How can I save more?", "Alice", INCOME, EXPENSES)
    assert "saving" in reply.lower() or "tips" in reply.lower() or "categor" in reply.lower()


def test_high_spend_intent(bot):
    reply = bot.respond("Where am I spending too much?", "Alice", INCOME, EXPENSES)
    assert "spend" in reply.lower() or "categor" in reply.lower()


def test_saving_pct_intent(bot):
    reply = bot.respond("What is my saving percentage?", "Alice", INCOME, EXPENSES)
    assert "%" in reply


def test_unknown_intent_returns_help(bot):
    reply = bot.respond("blah blah random text xyz", "Alice", INCOME, EXPENSES)
    assert "?" in reply or "try" in reply.lower() or "help" in reply.lower()


def test_budget_intent(bot):
    reply = bot.respond("Give me budget advice", "Alice", INCOME, EXPENSES)
    assert "50" in reply or "rule" in reply.lower()


def test_context_history_grows(bot):
    bot.respond("How can I save more?", "Alice", INCOME, EXPENSES)
    bot.respond("What is my income?",   "Alice", INCOME, EXPENSES)
    assert len(bot.ctx.history) == 4  # 2 user + 2 assistant


def test_clear_resets_history(bot):
    bot.respond("tip", "Alice", INCOME, EXPENSES)
    bot.clear_history()
    assert len(bot.ctx.history) == 0
