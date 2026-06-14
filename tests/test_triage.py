"""Tests for the P3-Triage-Agent."""

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from agents.backend_agent import analyze_customer
from agents.triage_agent  import run_triage


def test_triage_runs_without_error():
    analysis = analyze_customer("Alice")
    report   = run_triage(analysis)
    assert report.customer_name == "Alice"


def test_triage_overall_severity_valid():
    analysis = analyze_customer("Alice")
    report   = run_triage(analysis)
    valid = {"P1-Critical", "P2-High", "P3-Medium", "P4-Low", "P5-Healthy"}
    assert report.overall_severity in valid


def test_triage_markdown_output():
    analysis = analyze_customer("Alice")
    report   = run_triage(analysis)
    md = report.to_markdown()
    assert "Triage Report" in md
    assert "Alice" in md


def test_triage_counts_add_up():
    analysis = analyze_customer("Alice")
    report   = run_triage(analysis)
    assert report.flag_count + report.pass_count == len(analysis["raw_expenses"])
