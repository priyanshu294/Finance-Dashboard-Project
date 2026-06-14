"""
Personal Finance Advisor — Streamlit Application
Step 20: POC demonstration entry point.

Architecture:
  app.py  →  FinanceAdvisorOrchestrator (delegation.py)
                 ├── BackendAgent  (analysis + chatbot)
                 ├── FrontendAgent (charts)
                 └── TriageAgent   (review + report)
"""

import streamlit as st
import uuid
import time

from agents.delegation import orchestrator
from backend.sample_data import CUSTOMERS

# ── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Finance Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .metric-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    border: 1px solid #dee2e6;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .metric-value { font-size: 2rem; font-weight: 700; color: #1a73e8; }
  .metric-label { font-size: 0.85rem; color: #6c757d; margin-top: 4px; }
  .health-badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 1rem;
  }
  .triage-box {
    background: #fff8f0;
    border-left: 4px solid #fd7e14;
    border-radius: 8px;
    padding: 16px;
    margin-top: 12px;
  }
  .chat-user { background: #e8f0fe; border-radius: 12px; padding: 10px 14px; margin: 6px 0; }
  .chat-bot  { background: #f0faf0; border-radius: 12px; padding: 10px 14px; margin: 6px 0; }
  .tip-card  { background: #f6ffed; border-left: 3px solid #52c41a; padding: 12px; border-radius: 6px; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state initialisation ─────────────────────────────────────────────
if "session_id"   not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_customer" not in st.session_state:
    st.session_state.last_customer = None


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 Finance Advisor")
    st.markdown("---")
    customer_name = st.selectbox(
        "Select Customer Profile",
        options=list(CUSTOMERS.keys()),
        index=0,
    )
    st.markdown(f"_{CUSTOMERS[customer_name]['profile']}_")
    st.markdown("---")
    st.markdown("### Quick Ask")
    quick_q = st.selectbox(
        "Common questions",
        ["", "How can I save more?", "Where am I spending too much?",
         "What is my saving percentage?", "Give me budget advice."],
        label_visibility="collapsed",
    )
    if quick_q:
        st.session_state._quick_inject = quick_q

    st.markdown("---")
    if st.button("🔄 Reset Session"):
        orchestrator.reset_session(st.session_state.session_id)
        st.session_state.chat_history = []
        st.session_state.session_id   = str(uuid.uuid4())
        st.success("Session reset.")

    st.markdown("---")
    st.caption("Built with Claude Code · Step 20 POC")


# ── Reset chat history when customer changes ─────────────────────────────────
if st.session_state.last_customer != customer_name:
    orchestrator.reset_session(st.session_state.session_id)
    st.session_state.chat_history  = []
    st.session_state.last_customer = customer_name


# ── Load analysis (cached per customer) ─────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=300)
def load_analysis(name: str) -> dict:
    return orchestrator.get_full_analysis(name)


with st.spinner(f"Analysing {customer_name}'s finances…"):
    start = time.time()
    payload = load_analysis(customer_name)
    elapsed = (time.time() - start) * 1000

if "error" in payload:
    st.error(payload["error"])
    st.stop()

analysis = payload["analysis"]
triage   = payload["triage"]
charts   = payload["charts"]
summary  = analysis["summary"]


# ════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════
st.title(f"💰 {customer_name}'s Finance Dashboard")
st.markdown(f"*{analysis['profile']}*")

# Health badge
health_color = analysis["health_color"]
health_label = analysis["health_label"]
st.markdown(
    f'<span class="health-badge" style="background:{health_color}22; color:{health_color}; border:1px solid {health_color};">'
    f'Financial Health: {health_label}</span>',
    unsafe_allow_html=True,
)
st.markdown("")


# ════════════════════════════════════════════════════════
#  METRIC CARDS
# ════════════════════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-value">₹{summary['income']:,}</div>
      <div class="metric-label">Monthly Income</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-value">₹{summary['total_expense']:,}</div>
      <div class="metric-label">Total Expenses</div>
    </div>""", unsafe_allow_html=True)

with c3:
    savings_color = analysis["health_color"]
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-value" style="color:{savings_color}">₹{summary['savings']:,}</div>
      <div class="metric-label">Net Savings</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-value" style="color:{savings_color}">{summary['savings_pct']}%</div>
      <div class="metric-label">Savings Rate</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")


# ════════════════════════════════════════════════════════
#  CHARTS  (Frontend Agent output)
# ════════════════════════════════════════════════════════
st.subheader("📊 Expense Visualisation")
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.plotly_chart(charts["donut"], use_container_width=True)

with row1_col2:
    st.plotly_chart(charts["bar"], use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.plotly_chart(charts["gauge"], use_container_width=True)

with row2_col2:
    st.plotly_chart(charts["sparkline"], use_container_width=True)


# ════════════════════════════════════════════════════════
#  HIGH SPEND TABLE
# ════════════════════════════════════════════════════════
st.subheader("🔍 Category Analysis")
flagged = analysis["flagged_categories"]

table_data = []
for f in flagged:
    status = "🔴 Over" if f["is_high"] else "🟢 OK"
    table_data.append({
        "Category":     f["category"],
        "Spent (₹)":   f"₹{f['amount']:,}",
        "Benchmark (₹)": f"₹{f['benchmark_amount']:,}",
        "Overspend (₹)": f"₹{f['overspend']:,}" if f["is_high"] else "—",
        "% of Income":  f"{f['pct_of_income']}%",
        "Status":       status,
    })
st.dataframe(table_data, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════
#  SAVING SUGGESTIONS
# ════════════════════════════════════════════════════════
st.subheader("💡 Top Saving Suggestions")
suggestions = analysis["suggestions"]
if suggestions:
    for sug in suggestions:
        with st.expander(f"**{sug['category']}** — save ₹{sug['overspend']:,}/month", expanded=True):
            for tip in sug["tips"]:
                st.markdown(f'<div class="tip-card">💡 {tip}</div>', unsafe_allow_html=True)
else:
    st.success("All categories are within recommended benchmarks!")


# ════════════════════════════════════════════════════════
#  TRIAGE REPORT  (P3-Triage-Agent)
# ════════════════════════════════════════════════════════
with st.expander(f"🚦 Triage Report — Overall: **{triage.overall_severity}**", expanded=False):
    st.markdown(f'<div class="triage-box">', unsafe_allow_html=True)
    st.markdown(triage.to_markdown())
    st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  CHATBOT
# ════════════════════════════════════════════════════════
st.subheader("🤖 Finance Advisor Chatbot")
st.caption("Ask anything about your expenses, savings, or budget.")

# Inject quick question from sidebar
if hasattr(st.session_state, "_quick_inject") and st.session_state._quick_inject:
    quick_msg = st.session_state._quick_inject
    st.session_state._quick_inject = ""
    # Add to chat and get response
    response = orchestrator.chat(st.session_state.session_id, customer_name, quick_msg)
    st.session_state.chat_history.append(("user", quick_msg))
    st.session_state.chat_history.append(("assistant", response))

# Render chat history
chat_container = st.container()
with chat_container:
    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f'<div class="chat-user">👤 <strong>You:</strong> {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">🤖 <strong>Advisor:</strong><br>{msg}</div>', unsafe_allow_html=True)

# Input
with st.form(key="chat_form", clear_on_submit=True):
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Message",
            placeholder="e.g. How can I save more? Where am I spending too much?",
            label_visibility="collapsed",
        )
    with col_send:
        submitted = st.form_submit_button("Send ➤")

    if submitted and user_input.strip():
        with st.spinner("Thinking…"):
            response = orchestrator.chat(
                st.session_state.session_id, customer_name, user_input.strip()
            )
        st.session_state.chat_history.append(("user", user_input.strip()))
        st.session_state.chat_history.append(("assistant", response))
        st.rerun()


# ════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════
st.markdown("---")
col_l, col_r = st.columns(2)
with col_l:
    st.caption(f"Session ID: `{st.session_state.session_id[:8]}…`  |  Analysis: {elapsed:.0f}ms")
with col_r:
    st.caption("Personal Finance Advisor · Claude Code Demo · Step 20 POC")
