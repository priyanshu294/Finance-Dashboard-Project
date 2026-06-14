"""
Delegation Layer (Step 7) — Single entry point that routes work to sub-agents.

Architecture:
  Orchestrator (app.py)
      │
      ├─► BackendAgent   → data analysis, chatbot
      ├─► FrontendAgent  → chart/visual preparation
      └─► TriageAgent    → review, severity, report

Isolation Context (Step 6):
  Each agent function receives only the minimum data it needs.
  Cross-agent data sharing happens via the structured result dict,
  never via shared mutable globals.
"""

from agents.backend_agent  import analyze_customer, chat_response, clear_session
from agents.frontend_agent import (
    build_donut_chart,
    build_bar_vs_benchmark,
    build_savings_gauge,
    build_trend_sparkline,
)
from agents.triage_agent import run_triage


class FinanceAdvisorOrchestrator:
    """
    Central orchestrator. Delegates work to sub-agents and stitches
    results for the Streamlit frontend.
    """

    def get_full_analysis(self, customer_name: str) -> dict:
        """
        Step 7 delegation: backend analysis → triage review → chart data.
        Returns a unified payload consumed by app.py.
        """
        # Step 1: backend analysis (isolated — receives only customer_name)
        analysis = analyze_customer(customer_name)
        if "error" in analysis:
            return analysis

        # Step 2: P3-Triage review of backend output
        triage = run_triage(analysis)

        # Step 3: frontend agent prepares chart objects
        charts = {
            "donut":     build_donut_chart(analysis["raw_expenses"]),
            "bar":       build_bar_vs_benchmark(
                             analysis["flagged_categories"],
                             analysis["summary"]["income"],
                         ),
            "gauge":     build_savings_gauge(analysis["summary"]["savings_pct"]),
            "sparkline": build_trend_sparkline(analysis["raw_expenses"]),
        }

        return {
            "analysis": analysis,
            "triage":   triage,
            "charts":   charts,
        }

    def chat(self, session_id: str, customer_name: str, user_message: str) -> str:
        """Delegate chat to backend agent."""
        return chat_response(session_id, customer_name, user_message)

    def reset_session(self, session_id: str) -> None:
        clear_session(session_id)


# Singleton orchestrator — app.py imports this
orchestrator = FinanceAdvisorOrchestrator()
