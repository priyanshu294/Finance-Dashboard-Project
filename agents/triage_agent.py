"""
P3-Triage-Agent (Step 5) — Review and Report.
Validates analysis output, assigns severity labels, and produces a human-readable
triage report. Acts as a quality gate between backend agent output and UI rendering.
"""

from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["P1-Critical", "P2-High", "P3-Medium", "P4-Low", "P5-Healthy"]


@dataclass
class TriageIssue:
    severity: Severity
    category: str
    message: str
    recommended_action: str


@dataclass
class TriageReport:
    customer_name: str
    overall_severity: Severity
    issues: list[TriageIssue] = field(default_factory=list)
    health_summary: str = ""
    pass_count: int = 0
    flag_count: int = 0

    def to_markdown(self) -> str:
        lines = [
            f"## Triage Report — {self.customer_name}",
            f"**Overall Severity:** {self.overall_severity}",
            f"**Issues flagged:** {self.flag_count}  |  **Categories in budget:** {self.pass_count}",
            "",
            f"### Health Summary",
            self.health_summary,
            "",
            "### Issues",
        ]
        if not self.issues:
            lines.append("_No issues found. All categories within benchmark._")
        for issue in sorted(self.issues, key=lambda i: i.severity):
            lines.append(
                f"- **[{issue.severity}] {issue.category}**: {issue.message}\n"
                f"  > Action: {issue.recommended_action}"
            )
        return "\n".join(lines)


def _classify_overspend(overspend: float, amount: float) -> Severity:
    """Assign severity based on how far over benchmark the category is."""
    pct_over = (overspend / amount) * 100 if amount else 0
    if pct_over >= 60:
        return "P1-Critical"
    if pct_over >= 40:
        return "P2-High"
    if pct_over >= 20:
        return "P3-Medium"
    if pct_over > 0:
        return "P4-Low"
    return "P5-Healthy"


_ACTIONS: dict[str, str] = {
    "Food": "Reduce dining out; meal prep twice a week.",
    "Rent": "Consider a flatmate or negotiate lease renewal.",
    "Shopping": "Introduce a spending cap; apply the 24-hour rule.",
    "Travel": "Book ahead; switch to train for short distances.",
    "EMI": "Prepay principal when possible; avoid new loans.",
    "Utilities": "Audit subscriptions; use energy-efficient appliances.",
    "Entertainment": "Share streaming plans; limit impulse bookings.",
}


def run_triage(analysis: dict) -> TriageReport:
    """
    Run the triage agent on a backend_agent.analyze_customer() result.
    Returns a TriageReport.
    """
    name    = analysis["customer_name"]
    summary = analysis["summary"]
    flagged = analysis["flagged_categories"]

    issues: list[TriageIssue] = []
    pass_count = 0
    flag_count = 0

    for item in flagged:
        cat      = item["category"]
        amount   = item["amount"]
        overspend = item["overspend"]

        if not item["is_high"]:
            pass_count += 1
            continue

        flag_count += 1
        sev = _classify_overspend(overspend, amount)
        issues.append(TriageIssue(
            severity=sev,
            category=cat,
            message=(
                f"Spending ₹{amount:,} vs benchmark ₹{item['benchmark_amount']:,} "
                f"(₹{overspend:,} over, {item['pct_of_income']}% of income)"
            ),
            recommended_action=_ACTIONS.get(cat, "Review and reduce spending."),
        ))

    # Overall severity = worst issue or Healthy
    if issues:
        sev_order = ["P1-Critical", "P2-High", "P3-Medium", "P4-Low", "P5-Healthy"]
        overall = sorted(issues, key=lambda i: sev_order.index(i.severity))[0].severity
    else:
        overall = "P5-Healthy"

    health_summary = (
        f"Monthly Income: ₹{summary['income']:,} | "
        f"Total Expenses: ₹{summary['total_expense']:,} | "
        f"Net Savings: ₹{summary['savings']:,} ({summary['savings_pct']}%) — "
        f"{analysis['health_label']}"
    )

    return TriageReport(
        customer_name=name,
        overall_severity=overall,
        issues=issues,
        health_summary=health_summary,
        pass_count=pass_count,
        flag_count=flag_count,
    )
