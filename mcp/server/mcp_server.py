"""
MCP Server (Step 13) — exposes finance advisor analysis tools over the
Model Context Protocol (stdio transport, JSON-RPC 2.0).

Run standalone:  python mcp/server/mcp_server.py

Tools exposed:
  - finance/analyze       → full customer analysis
  - finance/chat          → chatbot turn
  - finance/triage_report → triage markdown report
  - finance/list_customers → available customer names
"""

import json
import sys
from agents.delegation import orchestrator
from backend.sample_data import CUSTOMERS

TOOLS = {
    "finance/list_customers": {
        "description": "List all available customer profiles.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "finance/analyze": {
        "description": "Full expense analysis for a customer.",
        "inputSchema": {
            "type": "object",
            "properties": {"customer_name": {"type": "string"}},
            "required": ["customer_name"],
        },
    },
    "finance/chat": {
        "description": "Send a chat message and receive a financial advice response.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id":    {"type": "string"},
                "customer_name": {"type": "string"},
                "message":       {"type": "string"},
            },
            "required": ["session_id", "customer_name", "message"],
        },
    },
    "finance/triage_report": {
        "description": "Get the P3-Triage report in Markdown for a customer.",
        "inputSchema": {
            "type": "object",
            "properties": {"customer_name": {"type": "string"}},
            "required": ["customer_name"],
        },
    },
}


def _handle(request: dict) -> dict:
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "finance-advisor-mcp", "version": "1.0.0"},
            },
        }

    if method == "tools/list":
        tools_list = [
            {"name": name, "description": meta["description"], "inputSchema": meta["inputSchema"]}
            for name, meta in TOOLS.items()
        ]
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools_list}}

    if method == "tools/call":
        tool_name = params.get("name", "")
        args      = params.get("arguments", {})
        try:
            result_text = _dispatch(tool_name, args)
        except Exception as exc:
            return {
                "jsonrpc": "2.0", "id": req_id,
                "error": {"code": -32603, "message": str(exc)},
            }
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {"content": [{"type": "text", "text": result_text}]},
        }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}


def _dispatch(tool_name: str, args: dict) -> str:
    if tool_name == "finance/list_customers":
        return json.dumps(list(CUSTOMERS.keys()))

    if tool_name == "finance/analyze":
        result = orchestrator.get_full_analysis(args["customer_name"])
        # Serialise — drop non-JSON chart objects
        safe = {k: v for k, v in result.items() if k != "charts"}
        if "triage" in safe:
            safe["triage"] = safe["triage"].to_markdown()
        return json.dumps(safe, default=str, indent=2)

    if tool_name == "finance/chat":
        reply = orchestrator.chat(args["session_id"], args["customer_name"], args["message"])
        return reply

    if tool_name == "finance/triage_report":
        result = orchestrator.get_full_analysis(args["customer_name"])
        if "error" in result:
            return result["error"]
        return result["triage"].to_markdown()

    raise ValueError(f"Unknown tool: {tool_name}")


def main():
    """stdio loop — reads JSON-RPC lines from stdin, writes to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = _handle(request)
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
