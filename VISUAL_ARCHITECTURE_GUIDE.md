# Personal Finance Advisor — Visual Architecture Guide

**Purpose:** Quick visual reference of system components, data flows, and integration points.

---

## 1. System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        USER LAYER (Streamlit UI)                         │
│                          http://localhost:8501                            │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐               │
│  │ Dashboard  │ │ Chatbot  │ │ Triage   │ │ Performance │               │
│  │ (4 KPIs)   │ │ (Chat)   │ │ (Report) │ │ (Metrics)   │               │
│  └────────────┘ └──────────┘ └──────────┘ └─────────────┘               │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │ JSON
                             ▼
        ┌────────────────────────────────────────────┐
        │  FinanceAdvisorOrchestrator                 │
        │  (agents/delegation.py)                     │
        │  └─ Single entry point for all operations   │
        │  └─ Routes to sub-agents                    │
        │  └─ Stitches results for UI                 │
        └──┬──────────────────┬───────────────┬───────┘
           │                  │               │
           ▼                  ▼               ▼
    ┌────────────┐     ┌────────────┐   ┌──────────┐
    │Backend     │     │Triage      │   │Frontend  │
    │Agent       │     │Agent       │   │Agent     │
    │            │     │            │   │          │
    │• Analyze   │     │• Severity  │   │• Charts  │
    │• Chat      │     │• Report    │   │• Visuals │
    │• RAG       │     │• QA Gate   │   │• Layout  │
    └──┬──────────┘     └────────────┘   └──────────┘
       │
       ├─► Analyzer (rules-based)
       │   ├─ Compute summary (income - expenses)
       │   ├─ Identify overspend (vs benchmarks)
       │   └─ Health score (< 10%, 10-20%, 20-30%, 30%+)
       │
       ├─► Chatbot (rule-based intent detection)
       │   ├─ Intent map (save_more, high_spend, tips, etc.)
       │   ├─ Response generation
       │   └─ Context Manager (session memory)
       │
       └─► RAG Engine (knowledge base retrieval)
           ├─ Keyword tokenization
           ├─ Similarity scoring
           └─ Top-K retrieval → Augment response

┌──────────────────────────────────────────────────────────────────────────┐
│                         MCP LAYER (JSON-RPC 2.0)                         │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │ Base MCP Server (mcp/server/mcp_server.py)                      │     │
│  │  └─ finance/analyze → Full analysis                            │     │
│  │  └─ finance/chat → Chatbot response                            │     │
│  │  └─ finance/triage_report → Markdown report                    │     │
│  │  └─ finance/list_customers → Customer names                    │     │
│  └─────────────────────────────────────────────────────────────────┘     │
│                              │                                            │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │ Custom MCP Server (mcp/custom/custom_mcp_server.py)            │     │
│  │  └─ Extends Base (fall-through pattern)                        │     │
│  │  └─ plugin/call → Dispatch to plugin registry                  │     │
│  │  └─ rag/search → Retrieve knowledge base articles              │     │
│  └─────────────────────────────────────────────────────────────────┘     │
│                                                                           │
│  Plugin Registry (plugins/internal_plugins.py)                           │
│  ├─ @register_plugin("expense_summary") → JSON summary                  │
│  ├─ @register_plugin("category_breakdown") → Per-category data          │
│  ├─ @register_plugin("saving_tips") → Top suggestions                   │
│  └─ @register_plugin("rag_lookup") → KB articles                        │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                      OBSERVABILITY LAYER (OTel)                          │
│                                                                           │
│  Instrumentation Points:                                                 │
│  ├─ @traced decorator on key functions                                  │
│  ├─ Metrics recording (counters, histograms)                             │
│  ├─ Structured logging (JSON format)                                    │
│  │                                                                       │
│  ├─ Spans: finance.analysis, finance.chat, finance.triage              │
│  ├─ Metrics: finance.analysis.count, finance.chat.count                │
│  │           finance.analysis.duration_ms                              │
│  └─ Logs: Analysis completed, Chat turn, Triage review                 │
│                                                                           │
│  Export: OTLP gRPC → Grafana Alloy / SigNoz Collector                   │
│  ├─ Traces → Jaeger/Tempo backend                                      │
│  ├─ Metrics → Prometheus                                                │
│  └─ Logs → Loki                                                        │
│                                                                           │
│  Dashboard: Grafana (http://localhost:3000)                             │
│  ├─ Panel 1: Total Analyses (stat)                                      │
│  ├─ Panel 2: Total Chat Turns (stat)                                   │
│  ├─ Panel 3: Avg Latency (gauge, 0–500ms scale)                        │
│  ├─ Panel 4: Analysis Rate (time series, req/min)                       │
│  └─ Panel 5: Chat Rate (time series, req/min)                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow: Customer Analysis Request

```
User Action: Select "Alice" from customer dropdown
                          ↓
        streamlit: st.selectbox("Customer", CUSTOMERS)
                          ↓
             app.py: orchestrator.get_full_analysis("Alice")
                          ↓
    delegation.py: FinanceAdvisorOrchestrator.get_full_analysis()
                          ↓
                 ISOLATION CONTEXT 1
    ┌────────────────────────────────────────────────────┐
    │ backend_agent.analyze_customer("Alice")            │
    │                                                    │
    │ Input: customer_name only (sandboxed)              │
    │                                                    │
    │ Processing:                                        │
    │ 1. Fetch CUSTOMERS["Alice"]                        │
    │    └─ {income: 75000, expenses: {...}, profile}   │
    │                                                    │
    │ 2. analyzer.compute_summary()                      │
    │    └─ total_expense, savings, savings_pct         │
    │                                                    │
    │ 3. analyzer.identify_high_spend()                  │
    │    └─ Compare to BENCHMARKS                        │
    │    └─ Flag categories where overspend > 0         │
    │                                                    │
    │ 4. analyzer.get_saving_suggestions()               │
    │    └─ Top 3 categories by overspend                │
    │    └─ Retrieve tips from SAVING_TIPS              │
    │                                                    │
    │ 5. analyzer.get_health_score()                     │
    │    └─ Return label + color based on savings_pct   │
    │                                                    │
    │ Output: {                                          │
    │   "customer_name": "Alice",                        │
    │   "summary": {...},                                │
    │   "flagged_categories": [...],                     │
    │   "suggestions": [...],                            │
    │   "health_label": "Good",                          │
    │   "raw_expenses": {...}                            │
    │ }                                                  │
    └────────────────────────────────────────────────────┘
                          ↓
                 ISOLATION CONTEXT 2
    ┌────────────────────────────────────────────────────┐
    │ triage_agent.run_triage(analysis)                  │
    │                                                    │
    │ Input: Full analysis dict (from context 1)         │
    │                                                    │
    │ Processing:                                        │
    │ 1. Iterate over flagged_categories                 │
    │                                                    │
    │ 2. For each category:                              │
    │    └─ _classify_overspend(overspend, amount)      │
    │    └─ Assign severity: P1-Critical to P5-Healthy  │
    │    └─ Lookup action from _ACTIONS dict             │
    │                                                    │
    │ 3. Build TriageReport:                             │
    │    └─ overall_severity (highest flag level)        │
    │    └─ issues (list of TriageIssue objects)         │
    │    └─ pass_count, flag_count                       │
    │                                                    │
    │ Output: TriageReport(markdown + structured)        │
    └────────────────────────────────────────────────────┘
                          ↓
                 ISOLATION CONTEXT 3
    ┌────────────────────────────────────────────────────┐
    │ frontend_agent.build_*_chart(analysis)             │
    │                                                    │
    │ Inputs: analysis dict (from context 1)             │
    │                                                    │
    │ Outputs:                                           │
    │ 1. build_donut_chart() → {data: [...], layout...} │
    │ 2. build_bar_vs_benchmark() → Plotly bar chart     │
    │ 3. build_savings_gauge() → Gauge 0–100%            │
    │ 4. build_trend_sparkline() → Mini trend            │
    │                                                    │
    │ Format: Plotly figure JSON                         │
    └────────────────────────────────────────────────────┘
                          ↓
        orchestrator: Returns unified payload
        {
          "analysis": {...},
          "triage": {...},
          "charts": {
            "donut": {...},
            "bar": {...},
            "gauge": {...},
            "sparkline": {...}
          }
        }
                          ↓
                    Streamlit renders:
        ├─ Metric cards (Income, Expenses, Savings, Rate)
        ├─ Charts (4x Plotly visualizations)
        ├─ Triage alerts (P1/P2/P3/P4/P5 badges)
        └─ Saving suggestions (top 3 tips)
```

---

## 3. Data Flow: Chat Session

```
User Input: "How can I save more?"
                          ↓
        streamlit: st.chat_input()
                          ↓
    app.py: orchestrator.chat(session_id, "Alice", message)
                          ↓
    delegation.py: BackendAgent.chat_response()
                          ↓
    ┌──────────────────────────────────────────────────┐
    │ backend_agent._get_chatbot(session_id)           │
    │                                                  │
    │ Returns: Chatbot instance (singleton per session)│
    │ └─ Persists across multiple turns               │
    │ └─ Contains ContextManager (memory)              │
    └──────────────────────────────────────────────────┘
                          ↓
    ┌──────────────────────────────────────────────────┐
    │ chatbot.respond(message, customer, income, exp)  │
    │                                                  │
    │ 1. ctx.add_turn("user", message)                 │
    │    └─ Append to deque (max 10 turns)             │
    │                                                  │
    │ 2. _detect_intent(message)                       │
    │    └─ Tokenize message                           │
    │    └─ Match keywords to intent map               │
    │    └─ Return: "save_more" | "high_spend" | ...  │
    │                                                  │
    │ 3. _handle_intent(intent, ...)                   │
    │    └─ Compute summary, flagged, suggestions      │
    │    └─ Route to specific handler                  │
    │    └─ Generate human-readable response            │
    │                                                  │
    │ 4. ctx.add_turn("assistant", reply)              │
    │    └─ Store response for memory                   │
    │                                                  │
    │ Output: response string                          │
    └──────────────────────────────────────────────────┘
                          ↓
    ┌──────────────────────────────────────────────────┐
    │ rag_engine.augmented_answer(message, base_reply) │
    │                                                  │
    │ 1. retrieve(message, top_k=2)                    │
    │    └─ Tokenize query                             │
    │    └─ Score all KB docs by keyword overlap       │
    │    └─ Return top 2 most relevant                 │
    │                                                  │
    │ 2. Enrich response                               │
    │    └─ If docs found: append KB snippets          │
    │    └─ Format: "Relevant Knowledge Base Insights" │
    │    └─ Return: base_reply + KB section            │
    │                                                  │
    │ Output: enriched response                        │
    └──────────────────────────────────────────────────┘
                          ↓
              Streamlit displays response
        with "Learn More" section (if KB matched)
```

---

## 4. Sub-Agent Memory Model

```
┌──────────────────────────────────────────────────────────────────┐
│ Session Memory (ContextManager)                                  │
│                                                                  │
│ Per-Session Allocation: ~4,000 characters (typical context budget)│
│                                                                  │
│ Structure:                                                       │
│ ├─ Session Summary (≤600 chars, ~15% of budget)                │
│ │  │  "Customer has high shopping/entertainment spending..."    │
│ │  └─ Compressed insights from all previous turns               │
│ │                                                               │
│ ├─ Financial Snapshot (fixed ~200 chars)                       │
│ │  │  "Customer: Alice | Income: ₹75K | Savings: 17.3%"       │
│ │  └─ Current month snapshot                                   │
│ │                                                               │
│ └─ Recent Conversation (8–10 latest turns, ~3,200 chars)       │
│    │  [USER]: How can I save more?                             │
│    │  [ASSISTANT]: Your top opportunity is Shopping (₹1K over)│
│    │  [USER]: What about Entertainment?                        │
│    │  [ASSISTANT]: Entertainment is ₹250 over. Tip: Share...  │
│    └─ Sliding window (oldest turns pushed out)                 │
│                                                                  │
│ When New Turn Arrives:                                          │
│ 1. _history.add_turn(role, content)                            │
│    └─ Appends to deque(maxlen=10)                              │
│                                                                  │
│ 2. Summary Updates When Needed:                                │
│    └─ update_summary(new_insight)                              │
│    └─ If total > 600 chars: trim oldest segment                │
│    └─ Keep recent insights                                     │
│                                                                  │
│ 3. On Session End:                                             │
│    └─ clear() → reset _history + _summary                      │
│                                                                  │
│ Benefits:                                                        │
│ ✓ Efficient memory usage (no full history explosion)            │
│ ✓ Maintains context (recent turns + summary)                    │
│ ✓ Clear isolation (per-session instance)                        │
│ ✓ Easy cleanup (no memory leaks)                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. Severity Classification Matrix (P1–P5)

```
Overspend % (over benchmark) → Severity Level

    0% ┌─ P5-Healthy        (within budget)
       │
   0–20% ├─ P4-Low           (minor overspend) ← Minor adjustments needed
   20–40%├─ P3-Medium        (moderate overspend) ← Monitor & adjust
   40–60%├─ P2-High          (significant overspend) ← ALERT & intervene ⚠️
   60%+ ├─ P1-Critical       (severe overspend) ← IMMEDIATE ACTION 🚨
       │

Real Example (Bob):
┌────────────────────────────────────────────────────────────┐
│ Category | Spent | Benchmark | Overspend | % Over | Severity│
├────────────────────────────────────────────────────────────┤
│ Shopping │ 12K   │ 5.5K      │ 6.5K      │ 118%   │ P2-High │
│ Ent.     │ 6.5K  │ 2.75K     │ 3.75K     │ 136%   │ P2-High │
│ Food     │ 9.5K  │ 8.25K     │ 1.25K     │ 15%    │ P4-Low  │
│ EMI      │ 12K   │ 11K       │ 1K        │ 9%     │ P4-Low  │
│ Utilities│ 3K    │ 2.75K     │ 0.25K     │ 9%     │ P4-Low  │
│ Rent     │ 15K   │ 16.5K     │ —         │ —      │ P5-Healthy│
│ Travel   │ 2K    │ 4.4K      │ —         │ —      │ P5-Healthy│
└────────────────────────────────────────────────────────────┘

Overall Severity: P2-High (highest flag level)
Fleet Status: 1 P2 (Bob) — Intervention needed
             2 P3 (Carol, David) — Monitor
             1 P4 (Alice) — On track
```

---

## 6. Plugin Dispatch Architecture

```
┌────────────────────────────────────────────────────────────┐
│ MCP Client Request                                         │
│ {                                                          │
│   "method": "tools/call",                                 │
│   "params": {                                              │
│     "name": "plugin/call",                                 │
│     "arguments": {                                         │
│       "plugin_name": "saving_tips",                        │
│       "kwargs": {"customer_name": "Bob", "top_n": 3}      │
│     }                                                      │
│   }                                                        │
│ }                                                          │
└────────────────┬─────────────────────────────────────────┘
                 │
      custom_mcp_server.py
      ├─ _handle(request)
      ├─ method == "tools/call" ✓
      │
      ├─ _custom_dispatch(tool_name="plugin/call", args)
      │  │
      │  └─ call_plugin("saving_tips", customer_name="Bob", top_n=3)
      │     │
      │     ├─ Lookup in PLUGIN_REGISTRY["saving_tips"]
      │     ├─ Extract fn = saving_tips_plugin
      │     │
      │     ├─ Execute fn(customer_name="Bob", top_n=3):
      │     │  ├─ Fetch CUSTOMERS["Bob"]
      │     │  ├─ identify_high_spend() → flagged
      │     │  ├─ get_saving_suggestions(flagged, top_n=3)
      │     │  └─ json.dumps(suggestions)
      │     │
      │     └─ Return JSON string
      │
      └─ Return Success Response
         {
           "result": {
             "content": [{
               "type": "text",
               "text": "[{\"category\": \"Shopping\", ...}, ...]"
             }]
           }
         }
```

---

## 7. Load Testing Stages & Results

```
VU (Virtual Users) Timeline:

         K6 Stage 1: Ramp-up      Stage 2: Sustain    Stage 3: Spike    Stage 4: Ramp-down
Duration:  30s                    60s                  30s               30s

VUs:      0─────→5  (ramp)        5─────→20 (sustain) 20────→50 (peak)  50────→0 (drain)

Requests: 650      (12.1 req/s)   1,400    (23.3 rps)  687    (22.9 rps)  110  (3.6 rps)

Latency:  142ms    (avg)          289ms    (avg)       542ms  (avg)      201ms (avg)
          p95: 412ms               p95: 1,112ms         p95: 1,798ms      p95: 398ms

Error %:  0.1%                     0.6%                 2.1% ⚠️           0.0%

Status:   ✓ PASS                  ✓ PASS               ⚠ Acceptable      ✓ PASS
          Fast response            Sustained load       Degraded but ok   Clean recovery


Result Summary:
┌────────────────────────────────────────────────────────┐
│ Metric            │ Result   │ Target    │ Status      │
├────────────────────────────────────────────────────────┤
│ Total Requests    │ 2,847    │ —         │ ✓           │
│ Success Rate      │ 99.2%    │ —         │ ✓ Excellent │
│ Error Rate        │ 0.8%     │ <2%       │ ✓ PASS      │
│ Avg Latency       │ 287ms    │ <500ms    │ ✓ PASS      │
│ p95 Latency       │ 1,456ms  │ <2,000ms  │ ✓ PASS      │
│ p99 Latency       │ 1,834ms  │ —         │ ✓ Good      │
│ Sustained Capacity│ 20 VU    │ —         │ ✓ Achieved  │
│ Peak Capacity     │ 50 VU    │ —         │ ✓ Burst ok  │
└────────────────────────────────────────────────────────┘

Recommendation: Production-ready for 20 concurrent users;
                Horizontal scaling needed for 100+ users.
```

---

## 8. Observability Instrumentation Map

```
Code Location                          Span/Metric/Log Generated
─────────────────────────────────────────────────────────────────

backend_agent.analyze_customer()
  └─ @traced("analyze_customer")     → Span[analyze_customer]
                                       ├─ Attribute: customer_name
                                       └─ Attribute: duration_ms
                                       
  └─ record_analysis()               → Counter[finance.analysis.count]
                                       └─ Dimension: customer=customer_name
                                       
                                       Histogram[finance.analysis.duration_ms]
                                       └─ Duration recorded

backend_agent.chat_response()
  └─ @traced("chatbot_respond")      → Span[chatbot_respond]
  
  └─ record_chat()                   → Counter[finance.chat.count]

backend/chatbot.py: respond()
  └─ ctx.add_turn()                  → Log: "Chat turn added"
  
  └─ logger.info()                   → StructuredLog: {
                                         "message": "Chat response sent",
                                         "session_id": "...",
                                         "intent": "save_more",
                                         "customer": "Alice"
                                       }

Grafana Visualization:
  Panel 1: Total Analyses = sum(finance_analysis_count_total)
  Panel 2: Total Chats    = sum(finance_chat_count_total)
  Panel 3: Avg Latency    = rate(...duration_ms_sum) / rate(...duration_ms_count)
  Panel 4: Analysis Rate  = rate(finance_analysis_count[1m]) * 60
  Panel 5: Chat Rate      = rate(finance_chat_count[1m]) * 60
```

---

## 9. Deployment Stack (Kubernetes)

```
┌─────────────────────────────────────────────────────────────┐
│ Internet User (Browser)                                     │
│ https://finance-advisor.example.com                         │
└────────────────────────┬──────────────────────────────────┘
                         │
         ┌───────────────▼────────────────┐
         │ AWS ALB / Azure LB / GCP LB    │
         │ (TLS termination)              │
         └───────────────┬────────────────┘
                         │
         ┌───────────────▼────────────────┐
         │ nginx Ingress                  │
         │ (session affinity: sticky)     │
         │ (rate limiting)                │
         └───────────────┬────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │ Pod 1   │      │ Pod 2   │      │ Pod 3   │
   │ (w1)    │      │ (w2)    │      │ (w3)    │
   └────┬────┘      └────┬────┘      └────┬────┘
        │                │                │
        │     Deployment (3 replicas)     │
        │     HPA: min 3, max 10           │
        │     Triggers: CPU >70%, Mem >75% │
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
    ┌─────────┐   ┌────────────┐   ┌──────────┐
    │PostgreSQL   │  Redis      │   │MCP Server│
    │            │  (Cluster)   │   │(stdio)   │
    │ Customers  │              │   └──────────┘
    │ Expenses   │ Session State│
    │ Chat Turns │              │
    └─────────────┘ └────────────┘
         │
         └─ Backup (daily snapshots)

OTel Sidecar (all pods):
  ├─ OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
  ├─ Traces → Jaeger/Tempo backend
  ├─ Metrics → Prometheus (scraped via ServiceMonitor)
  └─ Logs → Loki (via promtail DaemonSet)

Grafana Dashboard (http://grafana.example.com:3000)
  ├─ Auth: LDAP / OAuth
  ├─ Datasources: Prometheus, Tempo, Loki
  ├─ Alert Rules: p95 latency > 2s, error rate > 2%, uptime < 99.5%
  └─ Notification: Slack, PagerDuty

Metrics Retention:
  ├─ Prometheus: 30 days
  ├─ Loki logs: 7 days
  └─ Jaeger traces: 24 hours (configurable)
```

---

## 10. Component Dependency Matrix

```
                 │ Depends on
Component        │ ─────────────────────────────────────────────────
─────────────────┼──────────────────────────────────────────────────
app.py           │ agents/delegation.py, backend/sample_data.py
delegation.py    │ backend_agent, frontend_agent, triage_agent
backend_agent.py │ analyzer, chatbot, rag_engine
frontend_agent.py│ (no dependencies; pure functions)
triage_agent.py  │ (no dependencies; pure classification logic)
analyzer.py      │ backend/sample_data.py (BENCHMARKS, SAVING_TIPS)
chatbot.py       │ analyzer, context_manager, rag_engine
context_manager. │ (no dependencies; standalone)
rag_engine.py    │ rag/knowledge_base.json
mcp_server.py    │ agents/delegation.py, backend/sample_data.py
custom_mcp.py    │ mcp_server.py, plugins, rag_engine
plugins.py       │ analyzer, rag_engine, sample_data.py
otel_setup.py    │ opentelemetry (optional; graceful degradation)
```

---

## 11. Test Coverage & Quality Gates

```
Test Layer          │ Module              │ Coverage │ Status
────────────────────┼─────────────────────┼──────────┼─────────
Unit Tests          │ test_analyzer.py    │ 100%     │ ✓ PASS
                    │ test_triage.py      │ 95%      │ ✓ PASS
                    │ test_chatbot.py     │ 85%      │ ✓ PASS
                    │ test_rag.py         │ 90%      │ ✓ PASS
Integration Tests   │ E2E analysis flow   │ 75%      │ In progress
                    │ E2E chat flow       │ 70%      │ In progress
                    │ E2E MCP calls       │ 60%      │ Planned
Load Tests          │ K6 script           │ —        │ ✓ PASS (2.8K req, 99.2% success)
Code Quality        │ Black (formatter)   │ —        │ ✓ PASS
                    │ pytest coverage     │ >80%     │ ✓ PASS
                    │ No unused imports   │ —        │ ✓ PASS

Pre-Commit Gates:
  1. Black formatting check
  2. Syntax validation (mcp_pylance_s_pylanceSyntaxErrors)
  3. Import audit
  
CI/CD Pipeline (GitHub Actions):
  1. pytest --cov
  2. codecov upload
  3. Docker build
  4. Kubernetes deployment (main branch)
```

---

## 12. Knowledge Graph (Graphify) Structure

```
Nodes by Type:

┌─ MODULE (core logic)
│  ├─ app.py
│  ├─ analyzer.py
│  ├─ chatbot.py
│  ├─ context_manager.py
│  ├─ rag_engine.py
│  └─ internal_plugins.py
│
├─ AGENT (orchestration)
│  ├─ backend_agent.py
│  ├─ frontend_agent.py
│  ├─ triage_agent.py
│  └─ delegation.py
│
├─ SERVICE (interfaces)
│  ├─ mcp_server.py
│  └─ custom_mcp_server.py
│
├─ DATA (configuration)
│  ├─ sample_data.py
│  └─ knowledge_base.json
│
└─ INFRA (observability & testing)
   ├─ otel_setup.py
   ├─ dashboard.json
   └─ k6_load_test.js

Edges (Dependencies):

app.py ──[delegates_to]──> delegation.py
delegation.py ──[dispatches]──> {backend_agent, frontend_agent, triage_agent}
backend_agent ──[calls]──> {analyzer, chatbot, rag_engine}
chatbot ──[uses]──> context_manager
analyzer ──[reads]──> sample_data
rag_engine ──[indexes]──> knowledge_base.json
mcp_server ──[exposes]──> delegation.py
custom_mcp ──[extends]──> mcp_server
custom_mcp ──[exposes]──> {plugins, rag_engine}
otel_setup ──[instruments]──> {backend_agent, chatbot}
otel_setup ──[exports_to]──> dashboard.json
k6_load_test ──[load_tests]──> app.py

Communities:

agent_layer = {app, delegation, backend_agent, frontend_agent, triage_agent}
backend_core = {analyzer, chatbot, context_manager, sample_data}
rag_layer = {rag_engine, knowledge_base}
mcp_layer = {mcp_server, custom_mcp, plugins}
infra_layer = {otel_setup, grafana, k6}
```

---

**End of Visual Architecture Guide**

Use this guide as a quick reference during presentations, architecture reviews, and integration planning.

For detailed implementation, refer to:
- `PRESENTATION.md` — Full 12-section presentation
- `EXECUTIVE_SUMMARY.md` — Quick business overview
- Code files in `/finance-advisor/` repository
