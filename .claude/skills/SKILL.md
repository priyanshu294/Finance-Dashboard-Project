# Finance Advisor — Claude Code Skills (Step 3)

## Available Skills

### analyze
Run a full customer expense analysis.
```
/analyze <CustomerName>
```
Example: `/analyze Alice`

### chat
Send a chat message to the finance chatbot.
```
/chat <CustomerName> "<message>"
```
Example: `/chat Alice "How can I save more?"`

### triage
Run the P3-Triage-Agent and print the severity report.
```
/triage <CustomerName>
```

### rag-search
Search the knowledge base for financial articles.
```
/rag-search "<query>"
```

### mcp-start
Start the MCP server (stdio transport).
```
/mcp-start
```
Runs: `python mcp/server/mcp_server.py`

### load-test
Run the K6 load test against the running Streamlit app.
```
/load-test
```
Requires K6 installed and app running on localhost:8501.

### otel-check
Verify OpenTelemetry packages are installed and endpoint reachable.
```
/otel-check
```

---
## Step 3 — Hooks Settings
See `.claude/settings.json` for hook configuration.
