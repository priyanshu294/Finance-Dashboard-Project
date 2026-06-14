"""
Frontend Sub-Agent (Step 4).
Responsible for all chart/visual data preparation.
Receives raw analysis results from the backend agent; produces chart-ready payloads.
Isolation: knows nothing about DB, chatbot, or RAG internals.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def build_donut_chart(expenses: dict, title: str = "Expense Breakdown"):
    """Donut chart showing category share of total expenses."""
    labels = list(expenses.keys())
    values = list(expenses.values())
    fig = px.pie(
        names=labels,
        values=values,
        hole=0.45,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        showlegend=True,
        margin=dict(t=60, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def build_bar_vs_benchmark(flagged: list[dict], income: float):
    """Grouped bar: actual spend vs benchmark for each category."""
    categories = [f["category"] for f in flagged]
    actual     = [f["amount"] for f in flagged]
    benchmark  = [f["benchmark_amount"] for f in flagged]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Actual Spend", x=categories, y=actual,
                         marker_color="#e74c3c", opacity=0.85))
    fig.add_trace(go.Bar(name="Benchmark", x=categories, y=benchmark,
                         marker_color="#2ecc71", opacity=0.75))
    fig.update_layout(
        barmode="group",
        title="Actual vs Recommended Spend",
        xaxis_title="Category",
        yaxis_title="Amount (₹)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def build_savings_gauge(savings_pct: float):
    """Gauge chart showing savings rate vs 20% target."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=savings_pct,
        delta={"reference": 20, "suffix": "%"},
        title={"text": "Savings Rate (%)"},
        gauge={
            "axis": {"range": [-10, 50]},
            "bar": {"color": "#3498db"},
            "steps": [
                {"range": [-10, 0],  "color": "#e74c3c"},
                {"range": [0,  10],  "color": "#e67e22"},
                {"range": [10, 20],  "color": "#f1c40f"},
                {"range": [20, 50],  "color": "#2ecc71"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 3},
                "thickness": 0.75,
                "value": 20,
            },
        },
        number={"suffix": "%"},
    ))
    fig.update_layout(
        height=260,
        margin=dict(t=40, b=20, l=30, r=30),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def build_trend_sparkline(expenses: dict):
    """Horizontal bar chart sorted by spend — quick visual rank."""
    sorted_items = sorted(expenses.items(), key=lambda x: x[1], reverse=True)
    cats   = [i[0] for i in sorted_items]
    values = [i[1] for i in sorted_items]
    colors = ["#e74c3c" if v == max(values) else "#3498db" for v in values]

    fig = go.Figure(go.Bar(
        x=values, y=cats, orientation="h",
        marker_color=colors,
        text=[f"₹{v:,}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title="Category Spend Rank",
        xaxis_title="Amount (₹)",
        margin=dict(t=50, b=20, l=20, r=80),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
