"""
Custom Reusable MCP Server (Step 14).
Extends the base MCP server with a plugin-dispatch tool and a RAG search tool,
demonstrating a reusable orchestrated app-dev pattern.
Inherits the base stdio transport; just registers additional tools.
"""

import json
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[2]))

from mcp.server.mcp_server import _handle as _base_handle, TOOLS as BASE_TOOLS
from plugins.internal_plugins import call_plugin
from rag.rag_engine import retrieve

CUSTOM_TOOLS = {
    "plugin/call": {
        "description": "Call any registered internal plugin by name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "plugin_name": {"type": "string"},
                "kwargs":      {"type": "object"},
            },
            "required": ["plugin_name"],
        },
    },
    "rag/search": {
        "description": "Search the knowledge base for financial articles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 2},
            },
            "required": ["query"],
        },
    },
}

ALL_TOOLS = {**BASE_TOOLS, **CUSTOM_TOOLS}


def _custom_dispatch(tool_name: str, args: dict) -> str:
    if tool_name == "plugin/call":
        name   = args["plugin_name"]
        kwargs = args.get("kwargs", {})
        return call_plugin(name, **kwargs)

    if tool_name == "rag/search":
        docs = retrieve(args["query"], top_k=args.get("top_k", 2))
        return json.dumps([{"title": d["title"], "content": d["content"]} for d in docs], indent=2)

    return None  # Signal: not handled here, fall through to base


def _handle(request: dict) -> dict:
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "tools/list":
        tools_list = [
            {"name": name, "description": meta["description"], "inputSchema": meta["inputSchema"]}
            for name, meta in ALL_TOOLS.items()
        ]
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools_list}}

    if method == "tools/call":
        tool_name = params.get("name", "")
        args      = params.get("arguments", {})
        custom_result = _custom_dispatch(tool_name, args)
        if custom_result is not None:
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {"content": [{"type": "text", "text": custom_result}]},
            }

    # Fall through to base server for all other methods/tools
    return _base_handle(request)


def main():
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
