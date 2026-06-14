# Finance Advisor — Knowledge Vault (Step 17)
*Obsidian README Mode*

## Overview
This vault documents all architectural decisions and domain knowledge for the Personal Finance Advisor project. Import this folder into Obsidian to activate graph view and README mode.

## Node Map

```
[[App Entry]]          → app.py (Streamlit UI)
[[Orchestrator]]       → agents/delegation.py
[[Backend Agent]]      → agents/backend_agent.py
[[Frontend Agent]]     → agents/frontend_agent.py
[[Triage Agent]]       → agents/triage_agent.py
[[Analyzer]]           → backend/analyzer.py
[[Chatbot]]            → backend/chatbot.py
[[Context Manager]]    → backend/context_manager.py
[[Sample Data]]        → backend/sample_data.py
[[RAG Engine]]         → rag/rag_engine.py
[[Knowledge Base]]     → rag/knowledge_base.json
[[Plugins]]            → plugins/internal_plugins.py
[[MCP Server]]         → mcp/server/mcp_server.py
[[Custom MCP]]         → mcp/custom/custom_mcp_server.py
[[OTel Setup]]         → observability/otel/otel_setup.py
[[Grafana Dashboard]]  → observability/grafana/dashboard.json
[[K6 Load Test]]       → load_testing/k6_load_test.js
```

## Domain Concepts

### [[Expense Categories]]
The 7 categories tracked: Food, Rent, Shopping, Travel, EMI, Utilities, Entertainment.
Each is benchmarked against an ideal % of income (see [[Benchmarks]]).

### [[Benchmarks]]
| Category      | Ideal % |
|---------------|---------|
| Food          | 15%     |
| Rent          | 30%     |
| Shopping      | 10%     |
| Travel        | 8%      |
| EMI           | 20%     |
| Utilities     | 5%      |
| Entertainment | 5%      |

### [[Context Window Budget]]
Sub-agent memory is split: ≤15% compressed summary + latest 8-10 turns verbatim.
Managed by [[Context Manager]].

### [[Triage Severity Levels]]
- P1-Critical: >60% over benchmark
- P2-High: 40-60% over
- P3-Medium: 20-40% over
- P4-Low: 0-20% over
- P5-Healthy: within benchmark

## Step Index
| Step | File/Component      | Description                          |
|------|---------------------|--------------------------------------|
| 1    | (this document)     | Problem statement                    |
| 3    | .claude/            | Skills + Hooks                       |
| 4    | agents/             | Frontend + Backend sub-agents        |
| 5    | agents/triage_agent | P3-Triage review                     |
| 6    | agents/delegation   | Isolation context                    |
| 7    | agents/delegation   | Delegation layer                     |
| 8    | backend/context_mgr | Context trimming                     |
| 10   | plugins/            | Internal + external plugins          |
| 11   | rag/                | RAG engine + knowledge base          |
| 13   | mcp/server/         | MCP server (stdio)                   |
| 14   | mcp/custom/         | Custom reusable MCP server           |
| 15   | observability/      | OTel + Grafana                       |
| 16   | load_testing/       | K6 load test                         |
| 17   | knowledge_vault/    | This Obsidian vault                  |
| 18   | graphify_nodes/     | Graphify relational nodes            |
| 19   | tests/              | Prompt engineering + test suite      |
| 20   | app.py              | POC demonstration                    |
