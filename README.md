# Personal Finance Advisor — AI Agent

A full-stack AI agent for banking customers built with Python, Streamlit, and Claude Code. Analyses monthly expenses, identifies high-spend categories, provides rule-based saving suggestions, and supports a natural-language chatbot.

---

## Quick Start

```bash
cd finance-advisor
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.


---

## Architecture

```
app.py  (Streamlit UI)
  └── FinanceAdvisorOrchestrator  (agents/delegation.py)
          ├── BackendAgent    → analysis + chatbot + RAG
          ├── FrontendAgent   → Plotly charts
          └── TriageAgent     → severity review + report
```

### 20-Step Build Process

| Step | Description                               | Location                              |
|------|-------------------------------------------|---------------------------------------|
| 1    | Problem Statement                         | This README                           |
| 2    | AIDLC Planning                            | This README (Architecture section)    |
| 3    | .claude settings + SKILL.md               | `.claude/`                            |
| 4    | Frontend + Backend sub-agents             | `agents/`                             |
| 5    | P3-Triage-Agent                           | `agents/triage_agent.py`              |
| 6    | Isolation context for sub-agents          | `agents/delegation.py`                |
| 7    | Delegation layer                          | `agents/delegation.py`                |
| 8    | Context trimming (sub-agent memory)       | `backend/context_manager.py`          |
| 9    | Reusable setup & configuration            | `requirements.txt`, `.claude/`        |
| 10   | Plugins (internal + external stubs)       | `plugins/internal_plugins.py`         |
| 11   | RAG engine + knowledge base               | `rag/`                                |
| 12   | Test, review, report                      | `tests/` + code-review skill          |
| 13   | MCP server (stdio)                        | `mcp/server/mcp_server.py`            |
| 14   | Custom reusable MCP server                | `mcp/custom/custom_mcp_server.py`     |
| 15   | Observability: OTel + Grafana             | `observability/`                      |
| 16   | Load testing: K6 + dashboard              | `load_testing/`                       |
| 17   | Knowledge vault (Obsidian readme mode)    | `knowledge_vault/`                    |
| 18   | Graphify relational nodes                 | `graphify_nodes/graph_schema.json`    |
| 19   | Test + Prompt Engineering                 | `tests/`                              |
| 20   | POC demonstration                         | `app.py`                              |

---

## Features

### Dashboard
- **4 financial KPI cards**: Income, Total Expenses, Net Savings, Savings Rate
- **4 Plotly charts**: Donut (expense share), Bar (actual vs benchmark), Gauge (savings rate), Horizontal bar (spend rank)
- **Category table**: per-category spend vs benchmark with status indicators
- **Saving suggestions**: top 3 overspent categories with actionable tips

### Chatbot (Step 7 — Rule-Based)
Ask natural-language questions:
- *"How can I save more?"*
- *"Where am I spending too much?"*
- *"What is my saving percentage?"*
- *"Give me budget advice"*
- *"What are my total expenses?"*

### Triage Report (Step 5)
The P3-Triage-Agent classifies each overspent category by severity:
- **P1-Critical** (>60% over benchmark)
- **P2-High** (40-60%)
- **P3-Medium** (20-40%)
- **P4-Low** (0-20%)
- **P5-Healthy** (within benchmark)

### RAG Engine (Step 11)
Keyword-based retrieval from `rag/knowledge_base.json` augments chatbot answers with relevant financial knowledge articles.

### MCP Server (Steps 13-14)
```bash
# Start base MCP server (stdio, JSON-RPC 2.0)
python mcp/server/mcp_server.py

# Start custom MCP server (extends base with plugin + RAG tools)
python mcp/custom/custom_mcp_server.py
```

Tools exposed: `finance/analyze`, `finance/chat`, `finance/triage_report`, `finance/list_customers`, `plugin/call`, `rag/search`

### Observability (Step 15)
Set `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317` to export traces/metrics to Grafana Alloy or SigNoz. Import `observability/grafana/dashboard.json` into Grafana.

### Load Testing (Step 16)
```bash
k6 run load_testing/k6_load_test.js
```
Pass `BASE_URL=http://your-host:8501` to point at a remote deployment. Results saved to `load_testing/results/summary.json`.

---

## Customer Profiles

| Name  | Income  | Profile                                 |
|-------|---------|-----------------------------------------|
| Alice | ₹75,000 | Mid-career engineer, single             |
| Bob   | ₹55,000 | Marketing exec, high discretionary spend|
| Carol | ₹95,000 | Senior manager, frequent traveler       |
| David | ₹40,000 | Junior analyst, careful spender         |

---

## Running Tests (Step 19)

```bash
pytest tests/ -v --cov=backend --cov=rag --cov=agents
```

### Test coverage
| Module           | Tests |
|------------------|-------|
| analyzer.py      | 8     |
| chatbot.py       | 7     |
| triage_agent.py  | 4     |
| rag_engine.py    | 5     |

---

## Project Structure

```
finance-advisor/
├── app.py                          # Streamlit entry point
├── requirements.txt
├── README.md
├── .claude/
│   ├── skills/SKILL.md             # Claude Code skills
│   └── settings.json               # Hooks + permissions
├── agents/
│   ├── backend_agent.py            # Data + chatbot sub-agent
│   ├── frontend_agent.py           # Charts sub-agent
│   ├── triage_agent.py             # P3-Triage-Agent
│   └── delegation.py               # Orchestrator + isolation
├── backend/
│   ├── analyzer.py                 # Financial analysis engine
│   ├── chatbot.py                  # Rule-based chatbot
│   ├── context_manager.py          # Context trimming (Step 8)
│   └── sample_data.py              # Customer profiles + benchmarks
├── rag/
│   ├── rag_engine.py               # Keyword retrieval
│   └── knowledge_base.json         # Financial knowledge articles
├── plugins/
│   └── internal_plugins.py         # Internal + external plugin stubs
├── mcp/
│   ├── server/mcp_server.py        # Base MCP server
│   └── custom/custom_mcp_server.py # Custom reusable MCP server
├── observability/
│   ├── otel/otel_setup.py          # OTel traces + metrics
│   └── grafana/dashboard.json      # Grafana dashboard
├── load_testing/
│   └── k6_load_test.js             # K6 load test script
├── knowledge_vault/
│   └── obsidian_readme.md          # Obsidian knowledge vault
├── graphify_nodes/
│   └── graph_schema.json           # Graphify relational nodes
└── tests/
    ├── test_analyzer.py
    ├── test_chatbot.py
    ├── test_triage.py
    └── test_rag.py
```

---

## Prompt Engineering Notes (Step 19)

The chatbot uses intent detection via keyword matching. To improve:
1. Add more synonym mappings to `INTENT_MAP` in `chatbot.py`
2. Expand the knowledge base in `rag/knowledge_base.json`
3. Tune benchmark percentages in `backend/sample_data.py` to match regional norms

---

*Built with Claude Code — Anthropic*
